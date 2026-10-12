"""Constants shared by every generator stage. Each value comes from data/SPEC.md."""

from datetime import UTC, date, datetime, time
from pathlib import Path

SEED = 42

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
DB_PATH = DATA_DIR / "shop.db"

ORDERS_START = date(2025, 4, 1)
ORDERS_END = date(2026, 9, 30)
SNAPSHOT = date(2026, 10, 10)  # no date anywhere may be later than this
# Written inside generated PDFs and audio as their creation time, instead of "now", so a
# rebuild gives byte-identical files and git sees no change.
FILE_TIME = datetime.combine(SNAPSHOT, time(), tzinfo=UTC)
RETURN_WINDOW_DAYS = 10
