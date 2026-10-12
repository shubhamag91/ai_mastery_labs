"""Stage 6: ten support-call recordings in data/audio/ and their transcripts.

Code picks ten real orders and decides each call's issue and outcome from what the tables say
happened to the order; DeepSeek writes the dialogue; macOS `say` voices it, Python's `wave`
module joins the lines, and `afconvert` compresses the result to AAC.

Run: uv run --group datagen python -m scripts.datagen.calls
"""

import hashlib
import json
import random
import re
import sqlite3
import struct
import subprocess
import sys
import tempfile
import wave
from datetime import UTC, datetime
from pathlib import Path

from scripts.datagen import llm
from scripts.datagen.common import DATA_DIR, DB_PATH, FILE_TIME, SEED
from shopai.config import get_settings
from shopai.log import configure_logging, get_logger

log = get_logger(__name__)

AUDIO_DIR = DATA_DIR / "audio"
CACHE_PATH = DATA_DIR / ".cache" / "calls.json"
KEY_PATH = DATA_DIR / "answer_keys" / "calls.json"
VOICES = {"Agent": "Samantha", "Customer": "Rishi"}
PAUSE_SECONDS = 0.4
ORDER_RE = re.compile(r"SA-\d{6}")
MP4_EPOCH = datetime(1904, 1, 1, tzinfo=UTC)  # .m4a clocks count seconds from 1904

SYSTEM = """You write realistic phone calls between a customer support agent at ShopAI \
Home, a fictional Indian online shop for home and kitchen appliances, and an Indian customer.

Rules:
- 10 to 16 lines in total, 160 to 260 words, alternating between Agent and Customer and \
starting with the Agent greeting the caller.
- The customer says their order number, exactly as given, once, early in the call.
- Stay consistent with the facts about the order, and end with the outcome you are given.
- Natural spoken language: short sentences, small hesitations ("um", "actually"), no stage \
directions, no names, no email addresses or phone numbers.

Reply with JSON only: {"lines": [{"speaker": "Agent", "text": "..."}, \
{"speaker": "Customer", "text": "..."}]}"""


def pick_calls(con: sqlite3.Connection, rng: random.Random) -> list[dict]:
    """Ten delivered orders with different problems, each with its issue and outcome."""
    con.row_factory = sqlite3.Row
    orders = [
        dict(r)
        for r in con.execute(
            """SELECT o.order_id, o.order_number, o.order_date, o.delivered_date,
                      p.name AS product, r.reason, r.status AS return_status,
                      (SELECT COUNT(*) FROM refunds f WHERE f.order_id = o.order_id) AS refunds,
                      julianday(o.delivered_date) - julianday(o.order_date) AS delivery_days
               FROM orders o JOIN products p USING (product_id)
               LEFT JOIN returns r USING (order_id)
               WHERE o.status = 'delivered'
               ORDER BY o.order_id"""
        )
    ]
    wanted = [  # (how to find a suitable order, issue theme, how many calls)
        (lambda o: o["reason"] == "damaged_in_transit", "damaged_on_arrival", 2),
        (lambda o: o["reason"] == "defective", "product_defect", 2),
        (lambda o: o["reason"] == "wrong_item", "wrong_item", 1),
        (lambda o: o["reason"] in ("not_as_described", "changed_mind"), "returns_refunds", 2),
        (lambda o: o["reason"] is None and o["delivery_days"] >= 8, "delivery_delay", 2),
        (lambda o: o["reason"] is None, "customer_service", 1),
    ]
    calls = []
    for test, issue, count in wanted:
        for order in rng.sample([o for o in orders if test(o)], count):
            status = order["return_status"]
            if status == "approved" and not order["refunds"] and issue != "returns_refunds":
                outcome = "replacement"  # approved, nothing refunded: the item is being replaced
            elif status == "approved":
                outcome = "refund"
            elif status == "pending":
                outcome = "escalated"
            elif status == "rejected":
                outcome = "no_resolution"
            elif issue == "delivery_delay":
                outcome = "refund" if order["refunds"] else "escalated"
            else:
                outcome = "no_resolution"
            calls.append(order | {"issue": issue, "outcome": outcome})
    return calls


def order_facts(call: dict) -> str:
    facts = [f"ordered {call['order_date']}, delivered {call['delivered_date']}"]
    if call["reason"]:
        facts.append(
            f"a return was requested ({call['reason'].replace('_', ' ')}), "
            f"status {call['return_status']}"
        )
    if call["refunds"]:
        facts.append("a refund or store credit has been paid")
    return "; ".join(facts)


def outcome_text(outcome: str) -> str:
    return {
        "refund": "the agent confirms a refund (or store credit) and when it arrives",
        "replacement": "the agent arranges a replacement",
        "escalated": "the agent escalates the case to a specialist team and promises a call back",
        "no_resolution": "the agent explains why nothing more can be done; the customer is unhappy",
    }[outcome]


def script_problem(lines: list[dict], order_number: str) -> str | None:
    if not 10 <= len(lines) <= 16:
        return f"{len(lines)} lines"
    if {line.get("speaker") for line in lines} != set(VOICES):
        return "speakers must be exactly Agent and Customer"
    text = " ".join(line.get("text", "") for line in lines)
    if not 140 <= len(text.split()) <= 300:
        return f"{len(text.split())} words"
    if ORDER_RE.findall(text) != [order_number]:
        return f"order numbers said: {ORDER_RE.findall(text)}"
    return None


def get_script(call: dict, cache: dict) -> list[dict]:
    prompt = (
        f"Write the call. Return json.\nProduct: {call['product']}\n"
        f"Order number: {call['order_number']}\nIssue: {call['issue'].replace('_', ' ')}\n"
        f"Facts: {order_facts(call)}\nOutcome: {outcome_text(call['outcome'])}"
    )
    digest = hashlib.sha256((SYSTEM + prompt).encode()).hexdigest()[:16]
    key = call["order_number"]
    if cache.get(key, {}).get("hash") == digest:
        return cache[key]["lines"]
    for attempt in range(1, 4):
        lines = llm.chat_json(SYSTEM, prompt, max_tokens=3000).get("lines", [])
        why = script_problem(lines, call["order_number"])
        if why is None:
            cache[key] = {"hash": digest, "lines": lines}
            CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
            CACHE_PATH.write_text(json.dumps(cache, indent=1))
            return lines
        log.info("script_rejected", order=key, attempt=attempt, reason=why)
    sys.exit(f"No acceptable script for {key}")


def spoken(text: str) -> str:
    """Spell order numbers out for the voice: SA-102417 -> 'S A, 1 0 2 4 1 7'."""
    return ORDER_RE.sub(lambda m: "S A, " + " ".join(m.group()[3:]), text)


def record(lines: list[dict], out_path: Path) -> float:
    """Voice each line, join them with short pauses, compress to AAC. Returns seconds."""
    with tempfile.TemporaryDirectory() as tmp:
        parts = []
        for n, line in enumerate(lines):
            part = Path(tmp) / f"{n:02d}.wav"
            subprocess.run(
                ["say", "-v", VOICES[line["speaker"]], "--file-format=WAVE",
                 "--data-format=LEI16@22050", "-o", str(part), spoken(line["text"])],
                check=True,
            )  # fmt: skip
            parts.append(part)
        joined = Path(tmp) / "call.wav"
        with wave.open(str(joined), "wb") as out:
            out.setnchannels(1)
            out.setsampwidth(2)
            out.setframerate(22050)
            silence = b"\x00\x00" * int(22050 * PAUSE_SECONDS)
            for part in parts:
                with wave.open(str(part), "rb") as w:
                    out.writeframes(w.readframes(w.getnframes()) + silence)
        with wave.open(str(joined), "rb") as w:
            seconds = w.getnframes() / w.getframerate()
        subprocess.run(
            ["afconvert", "-f", "m4af", "-d", "aac", "-c", "1", str(joined), str(out_path)],
            check=True,
        )
    pin_timestamps(out_path)
    return seconds


def pin_timestamps(path: Path) -> None:
    """Replace the "created" and "modified" times afconvert writes (now) with FILE_TIME.

    An .m4a is a tree of boxes, each [size][type][content]. The times sit in mvhd (the file),
    tkhd (the track) and mdhd (the audio), nested inside the moov, trak and mdia boxes.
    """
    data = bytearray(path.read_bytes())
    stamp = int((FILE_TIME - MP4_EPOCH).total_seconds())
    pinned, todo = 0, [(0, len(data))]
    while todo:
        start, end = todo.pop()
        while start < end:
            size, kind = struct.unpack_from(">I4s", data, start)
            if size < 8:  # 0 ("to the end") and 1 (64-bit size): afconvert writes neither
                sys.exit(f"{path.name}: unexpected box size {size}")
            if kind in (b"moov", b"trak", b"mdia"):
                todo.append((start + 8, start + size))
            elif kind in (b"mvhd", b"tkhd", b"mdhd"):
                if data[start + 8] != 0:  # version 1 boxes hold 64-bit times
                    sys.exit(f"{path.name}: unexpected {kind.decode()} version")
                struct.pack_into(">II", data, start + 12, stamp, stamp)  # created, modified
                pinned += 1
            start += size
    if pinned != 3:
        sys.exit(f"{path.name}: expected 3 timestamped boxes, found {pinned}")
    path.write_bytes(data)


def main() -> None:
    configure_logging(get_settings().log_level)
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    cache = json.loads(CACHE_PATH.read_text()) if CACHE_PATH.exists() else {}
    with sqlite3.connect(DB_PATH) as con:
        calls = pick_calls(con, random.Random(SEED))

    key = []
    for n, call in enumerate(calls, start=1):
        lines = get_script(call, cache)
        path = AUDIO_DIR / f"call_{n:02d}.m4a"
        seconds = record(lines, path)
        size_mb = path.stat().st_size / 1_000_000
        print(f"{path.name}: {seconds:.0f} s, {size_mb:.2f} MB, {call['issue']}, {call['outcome']}")
        if not 30 <= seconds <= 120 or size_mb > 2:
            sys.exit(f"{path.name} breaks the spec (30-120 s, at most 2 MB)")
        key.append(
            {
                "file": path.name,
                "order_number": call["order_number"],
                "transcript": "\n".join(f"{line['speaker']}: {line['text']}" for line in lines),
                "issue": call["issue"],
                "outcome": call["outcome"],
                "seconds": round(seconds, 1),
            }
        )
    KEY_PATH.parent.mkdir(parents=True, exist_ok=True)
    KEY_PATH.write_text(json.dumps(key, ensure_ascii=False, indent=1) + "\n")
    print(f"answer_keys/calls.json written. DeepSeek: at most ${llm.cost_usd():.3f}")


if __name__ == "__main__":
    main()
