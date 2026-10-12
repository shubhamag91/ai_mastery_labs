"""Stage 8: write data/manifest.json and check the size budget.

Run: uv run --group datagen python -m scripts.datagen.manifest
"""

import json
import sqlite3
import sys

from scripts.datagen import images, llm
from scripts.datagen.common import DATA_DIR, DB_PATH, SEED, SNAPSHOT

BUDGET_BYTES = 50_000_000  # spec section 2
# The day the LLM text in data/.cache/ was generated. Not "today": rebuilding from the cache
# must give a byte-identical manifest. Update it only when the text is regenerated.
LLM_TEXT_GENERATED = "2026-10-11"


def main() -> None:
    with sqlite3.connect(DB_PATH) as con:
        tables = [t for (t,) in con.execute("SELECT name FROM sqlite_master WHERE type='table'")]
        rows = {t: con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in sorted(tables)}

    # Everything that ships: the git-ignored image candidates don't count.
    shipped = [
        p
        for p in DATA_DIR.rglob("*")
        if p.is_file() and "image_candidates" not in p.parts and p.name != ".DS_Store"
    ]
    total = sum(p.stat().st_size for p in shipped)
    manifest = {
        "seed": SEED,
        "llm_provider": "DeepSeek",
        "llm_model": llm.MODEL,
        "llm_text_generated": LLM_TEXT_GENERATED,
        "snapshot_date": SNAPSHOT.isoformat(),
        "rows": rows,
        "files": {
            "docs": len(list((DATA_DIR / "docs").glob("*.pdf"))),
            "product_images": len(list((DATA_DIR / "images" / "products").glob("*.jpg"))),
            "damaged_images": len(list((DATA_DIR / "images" / "damaged").glob("*.jpg"))),
            "audio": len(list((DATA_DIR / "audio").glob("*.m4a"))),
        },
        # Planted cases knowingly not built yet (spec section 5); 0.P expects these to fail.
        "pending": ["P11", "P12"] if images.DEFERRED else [],
        "total_mb": round(total / 1_000_000, 2),
    }
    (DATA_DIR / "manifest.json").write_text(json.dumps(manifest, indent=1) + "\n")
    print(json.dumps(manifest, indent=1))
    if total > BUDGET_BYTES:
        sys.exit(f"data/ is {total / 1e6:.1f} MB: over the 50 MB budget")


if __name__ == "__main__":
    main()
