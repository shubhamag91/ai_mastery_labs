"""Stage 7: product and damaged-return photos, chosen and labelled by a person.

    fetch: search Openverse for candidates, download them, and make one numbered contact
           sheet per category plus scripts/datagen/image_selection.csv to fill in.
    build: copy the chosen photos into data/images/, link damaged ones to returns, and write
           images/sources.csv and answer_keys/damage_labels.csv.

The damage labels are ground truth, so a person decides them by looking at each photo.

Deferred to Lab 1.4 (data/SPEC.md, P11 and P12): while DEFERRED is True, build skips and
changes nothing. To finish the photos, choose them, set DEFERRED = False, and run build.

Run: uv run --group datagen python -m scripts.datagen.images fetch   (then fill in the CSV)
     uv run --group datagen python -m scripts.datagen.images build
"""

import argparse
import csv
import io
import json
import sqlite3
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from scripts.datagen.common import DATA_DIR, DB_PATH, ROOT

# A deliberate switch rather than "skip when nothing is chosen": an accidentally emptied
# selection must still fail loudly. manifest.py reads this to list P11 and P12 as pending.
DEFERRED = True

CANDIDATES_DIR = DATA_DIR / ".cache" / "image_candidates"
SELECTION_PATH = ROOT / "scripts" / "datagen" / "image_selection.csv"
IMAGES_DIR = DATA_DIR / "images"
LABELS_PATH = DATA_DIR / "answer_keys" / "damage_labels.csv"
API = "https://api.openverse.org/v1/images/"
USER_AGENT = "ai-mastery-labs-datagen/0.1 (learning project)"

# (category, product searches, damaged searches). Free-image search is literal: "blender"
# alone finds the 3D software, so the queries spell out the kitchen object.
SEARCHES = [
    ("kettle", ["electric kettle"], ["broken kettle", "damaged kettle"]),
    ("mixer_grinder", ["kitchen blender", "food processor"], ["broken blender", "cracked blender"]),
    ("air_fryer", ["air fryer"], ["broken air fryer", "broken deep fryer"]),
    ("coffee_maker", ["coffee maker", "coffee machine"],
     ["broken coffee maker", "broken coffee machine", "broken espresso machine"]),
    ("toaster", ["toaster"], ["broken toaster", "damaged toaster"]),
    ("headphones", ["headphones"], ["broken headphones", "broken earphones"]),
]  # fmt: skip
PRODUCT_LICENCES = "cc0,pdm"  # no credit needed
DAMAGED_LICENCES = "cc0,pdm,by"  # CC BY is fine as long as the author is credited
PER_PRODUCT_SEARCH = 6
PER_DAMAGED_SEARCH = 8
KIND_NAMES = {"P": "product", "D": "damaged"}
DAMAGE_TYPES = {"cracked", "dented", "scratched", "broken_part", "none"}
SEVERITIES = {"none", "minor", "moderate", "severe"}
FIELDS = [
    "candidate_id", "kind", "category", "use", "damage_type", "severity", "title", "author",
    "licence", "source", "image_url",
]  # fmt: skip


def http_get(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()


def search(query: str, licences: str, wanted: int) -> list[dict]:
    params = urllib.parse.urlencode(
        {"q": query, "license": licences, "page_size": 20, "mature": "false"}
    )
    results = json.loads(http_get(f"{API}?{params}"))["results"]
    time.sleep(1)  # be polite to a free API
    return results[: wanted * 2]  # extra, because some downloads fail


def shrink(data: bytes, longest: int = 800) -> Image.Image:
    image = Image.open(io.BytesIO(data)).convert("RGB")
    image.thumbnail((longest, longest))
    return image


def contact_sheet(rows: list[dict], path: Path) -> None:
    if not rows:  # a search can come back empty (no free photos of broken air fryers)
        return
    thumbs = []
    for row in rows:
        image = Image.open(CANDIDATES_DIR / f"{row['candidate_id']}.jpg")
        image.thumbnail((300, 300))
        thumbs.append((row["candidate_id"], image))
    cols = 4
    sheet = Image.new("RGB", (cols * 310, ((len(thumbs) + cols - 1) // cols) * 340), "white")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default(size=22)
    for n, (label, image) in enumerate(thumbs):
        x, y = (n % cols) * 310 + 5, (n // cols) * 340 + 5
        sheet.paste(image, (x, y))
        draw.text((x, y + 305), label, fill="black", font=font)
    sheet.save(path, quality=85)


def fetch() -> None:
    CANDIDATES_DIR.mkdir(parents=True, exist_ok=True)
    rows = []
    for category, product_queries, damaged_queries in SEARCHES:
        plan = [("P", q, PRODUCT_LICENCES, PER_PRODUCT_SEARCH) for q in product_queries]
        plan += [("D", q, DAMAGED_LICENCES, PER_DAMAGED_SEARCH) for q in damaged_queries]
        seen = set()
        for kind, query, licences, wanted in plan:
            got = 0
            for result in search(query, licences, wanted):
                if got == wanted or result["id"] in seen:
                    continue
                same = [
                    r for r in rows if r["kind"] == KIND_NAMES[kind] and r["category"] == category
                ]
                n = len(same) + 1
                candidate_id = f"{kind}-{category}-{n:02d}"
                try:
                    shrink(http_get(result["url"])).save(
                        CANDIDATES_DIR / f"{candidate_id}.jpg", quality=85
                    )
                except Exception as error:  # dead links are common; skip and move on
                    print(f"  skipped {result['url'][:70]}: {error}")
                    continue
                seen.add(result["id"])
                got += 1
                licence = f"{result['license']} {result.get('license_version') or ''}".strip()
                rows.append(
                    {
                        "candidate_id": candidate_id,
                        "kind": KIND_NAMES[kind],
                        "category": category,
                        "use": "",
                        "damage_type": "",
                        "severity": "",
                        "title": (result.get("title") or "")[:80],
                        "author": result.get("creator") or "unknown",
                        "licence": licence,
                        "source": result.get("foreign_landing_url") or result["url"],
                        "image_url": result["url"],
                    }
                )
            print(f"{category} / {query}: {got} candidates")
        for kind in ("product", "damaged"):
            batch = [r for r in rows if r["category"] == category and r["kind"] == kind]
            contact_sheet(batch, CANDIDATES_DIR / f"sheet_{kind}_{category}.jpg")

    with open(SELECTION_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"\n{len(rows)} candidates. Contact sheets: {CANDIDATES_DIR.relative_to(ROOT)}/")
    print(f"Fill in: {SELECTION_PATH.relative_to(ROOT)}")


def save_small(source: Path, target: Path) -> None:
    """At most 800 px on the longest side and at most 200 KB (spec section 4)."""
    image = Image.open(source).convert("RGB")
    image.thumbnail((800, 800))
    for quality in (85, 75, 65, 55):
        image.save(target, quality=quality)
        if target.stat().st_size <= 200_000:
            return
    sys.exit(f"{target.name} is still over 200 KB")


def build() -> None:
    if DEFERRED:
        print("Photos deferred to Lab 1.4 (SPEC P11, P12): skipping, nothing changed.")
        return
    with open(SELECTION_PATH, newline="") as f:
        chosen = [r for r in csv.DictReader(f) if r["use"].strip().lower() in {"y", "yes"}]
    products = [r for r in chosen if r["kind"] == "product"]
    damaged = [r for r in chosen if r["kind"] == "damaged"]

    errors = []
    for category, _, _ in SEARCHES:
        n = sum(r["category"] == category for r in products)
        if n != 2:
            errors.append(f"{category}: {n} product photos chosen, need 2")
    if len(damaged) != 20:
        errors.append(f"{len(damaged)} damaged photos chosen, need 20")
    for r in damaged:
        if r["damage_type"] not in DAMAGE_TYPES or r["severity"] not in SEVERITIES:
            errors.append(f"{r['candidate_id']}: label {r['damage_type']!r}/{r['severity']!r}")
        if (r["damage_type"] == "none") != (r["severity"] == "none"):
            errors.append(f"{r['candidate_id']}: 'none' must be both the type and the severity")
    if sum(r["damage_type"] == "none" for r in damaged) != 2:
        errors.append("exactly 2 damaged photos must be labelled none")
    if errors:
        sys.exit("Fix image_selection.csv:\n  " + "\n  ".join(errors))

    for kind_dir in ("products", "damaged"):
        target_dir = IMAGES_DIR / kind_dir
        target_dir.mkdir(parents=True, exist_ok=True)
        for old in target_dir.glob("*.jpg"):
            old.unlink()  # rebuilt from the selection every time

    sources, labels = [], []
    categories = [c for c, _, _ in SEARCHES]
    with sqlite3.connect(DB_PATH) as con:
        for category in categories:
            skus = con.execute(
                "SELECT sku FROM products WHERE category = ? ORDER BY sku LIMIT 2", (category,)
            ).fetchall()
            rows = [r for r in products if r["category"] == category]
            for (sku,), row in zip(skus, rows, strict=True):
                target = IMAGES_DIR / "products" / f"{sku}.jpg"
                save_small(candidate_file(row), target)
                sources.append(source_row(target, row))

        # Each damaged photo goes to a damaged or defective return in the same category,
        # damaged-in-transit returns first, handed out in return_id order.
        eligible = {
            category: [
                return_id
                for (return_id,) in con.execute(
                    """SELECT r.return_id FROM returns r
                       JOIN orders o USING (order_id) JOIN products p USING (product_id)
                       WHERE p.category = ?
                         AND r.reason IN ('damaged_in_transit', 'defective')
                       ORDER BY r.reason = 'damaged_in_transit' DESC, r.return_id""",
                    (category,),
                )
            ]
            for category in categories
        }
        con.execute("UPDATE returns SET photo_file = NULL")
        for row in damaged:
            if not eligible[row["category"]]:
                sys.exit(f"Not enough damaged/defective {row['category']} returns for the photos")
            return_id = eligible[row["category"]].pop(0)
            target = IMAGES_DIR / "damaged" / f"return_{return_id}.jpg"
            save_small(candidate_file(row), target)
            con.execute(
                "UPDATE returns SET photo_file = ? WHERE return_id = ?",
                (f"data/images/damaged/{target.name}", return_id),
            )
            sources.append(source_row(target, row))
            labels.append(
                {
                    "file": target.name,
                    "return_id": return_id,
                    "category": row["category"],
                    "damage_type": row["damage_type"],
                    "severity": row["severity"],
                }
            )

    write_csv(IMAGES_DIR / "sources.csv", ["file", "source", "author", "licence"], sources)
    write_csv(LABELS_PATH, ["file", "return_id", "category", "damage_type", "severity"], labels)
    print(f"{len(products)} product photos, {len(labels)} damaged photos linked to returns.")


def candidate_file(row: dict) -> Path:
    path = CANDIDATES_DIR / f"{row['candidate_id']}.jpg"
    if not path.exists():  # the cache was cleared: download the original again
        CANDIDATES_DIR.mkdir(parents=True, exist_ok=True)
        shrink(http_get(row["image_url"])).save(path, quality=85)
    return path


def source_row(target: Path, row: dict) -> dict:
    return {
        "file": f"{target.parent.name}/{target.name}",
        "source": row["source"],
        "author": row["author"],
        "licence": row["licence"],
    }


def write_csv(path: Path, fields: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("step", choices=["fetch", "build"])
    {"fetch": fetch, "build": build}[parser.parse_args().step]()


if __name__ == "__main__":
    main()
