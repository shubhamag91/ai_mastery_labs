"""Lab 0.3 break test: send the same 5 review briefs to DeepSeek twice and compare the replies.

Same model, same prompt, same settings as the generator (temperature 1.0, thinking off), and
no cache, so both runs really call the API. Writes results/rerun_diff.md.

Run from the repo root:
    PYTHONPATH=. uv run --group datagen python labs/lab-00-foundation/experiments/rerun_diff.py
"""

import difflib
import random
import sqlite3
from pathlib import Path

from scripts.datagen import llm
from scripts.datagen import reviews as rv
from scripts.datagen.common import DB_PATH, SEED
from shopai.log import configure_logging

PILOT_IDS = [3, 9, 13, 24, 29]  # one review each from five themes, already seen in the pilot
RESULTS = Path(__file__).resolve().parents[1] / "results" / "rerun_diff.md"


def similarity(a: str, b: str) -> float:
    """Share of words the two texts have in common, in order (1.0 = identical)."""
    return difflib.SequenceMatcher(None, a.split(), b.split()).ratio()


def main() -> None:
    configure_logging("INFO")
    with sqlite3.connect(DB_PATH) as con:
        rows = rv.plan(random.Random(SEED), rv.load_orders(con))
    picks = [rows[i - 1] for i in PILOT_IDS]
    prompt = "Write one item for each brief below. Return json.\n\n"
    prompt += "\n".join(rv.brief(r) for r in picks)

    runs = []
    for _ in range(2):
        reply = llm.chat_json(rv.SYSTEM, prompt, max_tokens=4000)
        runs.append({str(item["id"]): item["text"] for item in reply["items"]})

    lines = [
        "# Break test: the same briefs, sent twice",
        "",
        "Model `deepseek-v4-pro`, temperature 1.0, thinking off; identical prompt both times.",
        "",
        "| Row | Words, run 1 | Words, run 2 | Word overlap | Identical? |",
        "|---|---|---|---|---|",
    ]
    for row in picks:
        a, b = runs[0][str(row["review_id"])], runs[1][str(row["review_id"])]
        lines.append(
            f"| {row['review_id']} | {len(a.split())} | {len(b.split())} | "
            f"{similarity(a, b):.0%} | {'yes' if a == b else 'no'} |"
        )
    lines += ["", "## The texts", ""]
    for row in picks:
        lines += [
            f"### Row {row['review_id']}",
            "",
            f"_Brief:_ {rv.brief(row)}",
            "",
            f"**Run 1:** {runs[0][str(row['review_id'])]}",
            "",
            f"**Run 2:** {runs[1][str(row['review_id'])]}",
            "",
        ]
    lines.append(f"_Cost: at most ${llm.cost_usd():.4f} for {llm.usage['calls']} calls._")
    RESULTS.parent.mkdir(parents=True, exist_ok=True)
    RESULTS.write_text("\n".join(lines) + "\n")
    print(f"Wrote {RESULTS.relative_to(Path.cwd())}")


if __name__ == "__main__":
    main()
