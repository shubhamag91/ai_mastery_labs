"""Stage 5: the PDFs in data/docs/ and the invoice answer key.

- returns_policy.pdf: 14 numbered sections, each written by DeepSeek from one shared rules
  sheet, so the policy can never disagree with how the tables behave.
- manual_<category>.pdf: six fixed headings per category, written by DeepSeek.
- invoice_01-10.pdf: built by code only. Their numbers must add up exactly, so no LLM is
  involved, and answer_keys/invoices.json is written from the same numbers.

Run: uv run --group datagen python -m scripts.datagen.docs
"""

import hashlib
import json
import random
import re
import sqlite3
import sys
from datetime import date

from fpdf import FPDF

from scripts.datagen import llm
from scripts.datagen.common import DATA_DIR, DB_PATH, FILE_TIME, SEED
from shopai.config import get_settings
from shopai.log import configure_logging, get_logger

log = get_logger(__name__)

DOCS_DIR = DATA_DIR / "docs"
CACHE_PATH = DATA_DIR / ".cache" / "docs.json"
INVOICE_KEY_PATH = DATA_DIR / "answer_keys" / "invoices.json"
# Georgia has the ₹ sign (U+20B9); Arial Unicode is older than the sign and prints a blank box.
FONT = "/System/Library/Fonts/Supplemental/Georgia.ttf"
FONT_BOLD = "/System/Library/Fonts/Supplemental/Georgia Bold.ttf"

# The policy's rules, taken from what the tables actually do (data/SPEC.md, scripts/tables.py).
RULES = """\
- Shop: ShopAI Home, an online shop in India selling small home and kitchen appliances \
(kettles, mixer grinders, air fryers, coffee makers, toasters, headphones). Prices in rupees.
- Delivery normally takes 1 to 10 days after ordering.
- Return window: 10 days from the delivery date. Requests made after 10 days are rejected.
- Return reasons accepted: damaged in transit, defective, wrong item, not as described, and \
change of mind. Change-of-mind returns must be unused, in original condition, and are more \
often rejected after inspection.
- A return is approved, rejected, or pending while it is inspected.
- Refunds are paid within 10 days of the return being requested and approved.
- Refund method: UPI, card and net banking orders are refunded to the original payment \
method. Cash-on-delivery orders are refunded as store credit. Any customer may choose store \
credit instead.
- Refunds never exceed what the customer paid for the order.
- If delivery takes 8 days or more, the shop may give a goodwill store credit of about 10% of \
the order value.
- Orders can be cancelled before they are dispatched.
- Warranty: 1 year from delivery on all products; 2 years on mixer grinder motors.
- Customers should keep photos of damage: damaged-in-transit claims need a photo.
- Contact: support@shopai-home.example, or the chat on the website. Never give a phone number."""

POLICY_SECTIONS = [
    "About this policy",
    "Who can return an item",
    "The 10-day return window",
    "Items that cannot be returned",
    "Items damaged in transit",
    "Defective items",
    "Wrong or incomplete items",
    "Returns for a change of mind",
    "How to request a return",
    "Pickup and inspection",
    "Refunds: methods and timelines",
    "Late deliveries and goodwill credit",
    "Warranty claims after the return window",
    "Cancelling an order and contacting us",
]
MANUAL_HEADINGS = ["Safety", "Setup", "Everyday use", "Cleaning and care", "Troubleshooting",
                   "Warranty"]  # fmt: skip
CATEGORY_NAMES = {
    "kettle": "electric kettles", "mixer_grinder": "mixer grinders", "air_fryer": "air fryers",
    "coffee_maker": "coffee makers", "toaster": "toasters and sandwich makers",
    "headphones": "headphones and earbuds",
}  # fmt: skip

SYSTEM = f"""You write customer-facing documents for ShopAI Home, a fictional Indian online \
shop. Write in clear, plain British English, the way a real shop's help pages are written. \
Follow these rules exactly and never contradict them:

{RULES}

Never mention real brands, real companies, URLs other than the contact address above, or \
phone numbers. Use plain text: paragraphs separated by blank lines, and lists as lines \
starting with "- ". No Markdown headings, bold or tables.

Reply with JSON only."""

DAY_WINDOW_RE = re.compile(r"(\d+)[- ]day (?:return|window)", re.IGNORECASE)


def cached_call(cache: dict, key: str, prompt: str, check) -> dict:
    """Call DeepSeek unless an accepted reply for this exact prompt is cached."""
    digest = hashlib.sha256((SYSTEM + prompt).encode()).hexdigest()[:16]
    if cache.get(key, {}).get("hash") == digest:
        return cache[key]["reply"]
    for attempt in range(1, 4):
        reply = llm.chat_json(SYSTEM, prompt, max_tokens=8000)
        why = check(reply)
        if why is None:
            cache[key] = {"hash": digest, "reply": reply}
            CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
            CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False, indent=1))
            return reply
        log.info("doc_rejected", key=key, attempt=attempt, reason=why)
    sys.exit(f"No acceptable text for {key} after 3 attempts")


def wrong_window(text: str) -> str | None:
    windows = {int(n) for n in DAY_WINDOW_RE.findall(text)}
    return f"mentions a {windows - {10}}-day window" if windows - {10} else None


def policy_texts(cache: dict) -> list[tuple[str, str]]:
    sections = []
    for n, title in enumerate(POLICY_SECTIONS, start=1):
        prompt = (
            f"Write section {n} of 14 of ShopAI Home's returns and refunds policy, titled "
            f'"{title}". Other sections cover: {"; ".join(POLICY_SECTIONS)}. Stay on this '
            "section's topic, give concrete examples and edge cases, and write 650 to 850 "
            'words. Return json: {"text": "..."}'
        )

        def check(reply: dict) -> str | None:
            text = reply.get("text", "")
            words = len(text.split())
            if not 550 <= words <= 1000:
                return f"{words} words"
            return wrong_window(text)

        sections.append((f"{n}. {title}", cached_call(cache, f"policy_{n}", prompt, check)["text"]))
    return sections


def manual_texts(cache: dict, category: str) -> list[tuple[str, str]]:
    prompt = (
        f"Write the user manual for ShopAI Home's {CATEGORY_NAMES[category]}. It covers every "
        "model in the range, so stay general rather than naming a model. Use exactly these "
        f"sections, in this order: {', '.join(MANUAL_HEADINGS)}. Write 250 to 350 words per "
        "section; Troubleshooting should list common problems with their fixes. Return json: "
        '{"sections": {"Safety": "...", "Setup": "...", ...}}'
    )

    def check(reply: dict) -> str | None:
        sections = reply.get("sections", {})
        if list(sections) != MANUAL_HEADINGS:
            return f"headings were {list(sections)}"
        words = sum(len(t.split()) for t in sections.values())
        return None if 1000 <= words <= 2500 else f"{words} words"

    reply = cached_call(cache, f"manual_{category}", prompt, check)
    return list(reply["sections"].items())


class Doc(FPDF):
    def __init__(self, title: str) -> None:
        super().__init__(format="A4")
        self.add_font("body", fname=FONT)
        self.add_font("body", style="B", fname=FONT_BOLD)  # used by the invoice table headers
        self.set_margins(20, 20, 20)
        self.set_auto_page_break(True, margin=20)
        self.set_title(title)
        self.set_creation_date(FILE_TIME)  # not "now": rebuilds must be byte-identical
        self.doc_title = title
        self.add_page()

    def footer(self) -> None:
        self.set_y(-14)
        self.set_font("body", size=8)
        self.cell(0, 6, f"ShopAI Home · {self.doc_title} · page {self.page_no()}", align="C")

    def heading(self, text: str, size: int = 13) -> None:
        self.set_font("body", size=size)
        self.ln(3)
        self.multi_cell(0, 7, text, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def body(self, text: str) -> None:
        self.set_font("body", size=10)
        for para in (p.strip() for p in text.split("\n") if p.strip()):
            if para.startswith("- "):
                self.multi_cell(0, 5.5, f"•  {para[2:]}", new_x="LMARGIN", new_y="NEXT")
            else:
                self.multi_cell(0, 5.5, para, new_x="LMARGIN", new_y="NEXT")
                self.ln(2)


def write_text_doc(path, title: str, sections: list[tuple[str, str]]) -> int:
    pdf = Doc(title)
    pdf.heading(title, size=18)
    for heading, text in sections:
        pdf.heading(heading)
        pdf.body(text)
    pdf.output(str(path))
    return sum(len(t.split()) for _, t in sections)


SUPPLIERS = {
    "Coastal Kitchenware Distributors": ["kettle", "toaster", "coffee_maker"],
    "Northfield Electricals": ["mixer_grinder", "air_fryer", "kettle"],
    "Bluepeak Audio Supplies": ["headphones"],
    "Saffron Home Traders": ["air_fryer", "coffee_maker", "toaster", "mixer_grinder"],
}


def make_invoices(rng: random.Random, products: list[dict]) -> list[dict]:
    invoices = []
    supplier_names = list(SUPPLIERS)
    for n in range(1, 11):
        supplier = supplier_names[(n - 1) % len(supplier_names)]
        stock = [p for p in products if p["category"] in SUPPLIERS[supplier]]
        items = []
        for p in sorted(
            rng.sample(stock, min(rng.randint(3, 12), len(stock))), key=lambda p: p["sku"]
        ):
            quantity = rng.choice([5, 10, 12, 20, 24, 30, 40, 50])
            unit_cost = round(p["price_inr"] * rng.uniform(0.55, 0.7))  # below the shop's price
            items.append(
                {
                    "sku": p["sku"],
                    "description": p["name"],
                    "quantity": quantity,
                    "unit_cost_inr": unit_cost,
                    "line_total_inr": quantity * unit_cost,
                }
            )
        subtotal = sum(i["line_total_inr"] for i in items)
        gst = int(subtotal * 18 / 100 + 0.5)  # 18%, rounded half up to the nearest rupee
        invoices.append(
            {
                "file": f"invoice_{n:02d}.pdf",
                "invoice_number": f"INV-2026-{n:03d}",
                "supplier": supplier,
                "date": date(2026, rng.randint(1, 9), rng.randint(1, 28)).isoformat(),
                "items": items,
                "subtotal_inr": subtotal,
                "gst_rate": 0.18,
                "gst_inr": gst,
                "total_inr": subtotal + gst,
            }
        )
    return invoices


def money(amount: int) -> str:
    return f"₹{amount:,}"


def write_invoice(invoice: dict) -> None:
    pdf = Doc(f"Tax invoice {invoice['invoice_number']}")
    pdf.heading("TAX INVOICE", size=18)
    pdf.set_font("body", size=10)
    for line in (
        f"Invoice number: {invoice['invoice_number']}",
        f"Invoice date: {invoice['date']}",
        f"Supplier: {invoice['supplier']}",
        "Bill to: ShopAI Home, Warehouse 3, Bhiwandi, Maharashtra",
    ):
        pdf.cell(0, 6, line, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    widths = (26, 74, 14, 28, 28)
    with pdf.table(col_widths=widths, text_align=("LEFT", "LEFT", "RIGHT", "RIGHT", "RIGHT")) as t:
        t.row(["SKU", "Description", "Qty", "Unit cost", "Line total"])
        for item in invoice["items"]:
            t.row(
                [
                    item["sku"],
                    item["description"],
                    str(item["quantity"]),
                    money(item["unit_cost_inr"]),
                    money(item["line_total_inr"]),
                ]
            )
    pdf.ln(4)
    for label, amount in (
        ("Subtotal", invoice["subtotal_inr"]),
        ("GST at 18%", invoice["gst_inr"]),
        ("Total", invoice["total_inr"]),
    ):
        pdf.cell(140, 6, label, align="R")
        pdf.cell(30, 6, money(amount), align="R", new_x="LMARGIN", new_y="NEXT")
    pdf.output(str(DOCS_DIR / invoice["file"]))


def main() -> None:
    configure_logging(get_settings().log_level)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    cache = json.loads(CACHE_PATH.read_text()) if CACHE_PATH.exists() else {}

    words = write_text_doc(
        DOCS_DIR / "returns_policy.pdf", "Returns and Refunds Policy", policy_texts(cache)
    )
    print(f"returns_policy.pdf: {words:,} words")
    for category in CATEGORY_NAMES:
        title = f"User Manual: {CATEGORY_NAMES[category].capitalize()}"
        words = write_text_doc(
            DOCS_DIR / f"manual_{category}.pdf", title, manual_texts(cache, category)
        )
        print(f"manual_{category}.pdf: {words:,} words")

    with sqlite3.connect(DB_PATH) as con:
        con.row_factory = sqlite3.Row
        products = [dict(r) for r in con.execute("SELECT * FROM products ORDER BY product_id")]
    invoices = make_invoices(random.Random(SEED), products)
    for invoice in invoices:
        write_invoice(invoice)
    INVOICE_KEY_PATH.parent.mkdir(parents=True, exist_ok=True)
    INVOICE_KEY_PATH.write_text(json.dumps(invoices, indent=1) + "\n")
    print(f"{len(invoices)} invoices and answer_keys/invoices.json")
    print(f"DeepSeek: {llm.usage['calls']} calls, at most ${llm.cost_usd():.3f}")


if __name__ == "__main__":
    main()
