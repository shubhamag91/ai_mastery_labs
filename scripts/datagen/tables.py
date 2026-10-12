"""Stage 2: build the five structured tables in data/shop.db.

Faker and a fixed seed only, no LLM: this stage is free, and it produces identical output
on every run as long as the Faker version pinned in uv.lock doesn't change.

Run: uv run --group datagen python -m scripts.datagen.tables
"""

import random
import sqlite3
import sys
from datetime import date, timedelta

from faker import Faker

from scripts.datagen.common import (
    DB_PATH,
    ORDERS_END,
    ORDERS_START,
    RETURN_WINDOW_DAYS,
    SEED,
    SNAPSHOT,
)

# The database enforces whatever part of the spec SQL can express: a last line of defence.
SCHEMA = """
CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    name        TEXT NOT NULL,
    email       TEXT NOT NULL UNIQUE,
    phone       TEXT NOT NULL UNIQUE,
    city        TEXT NOT NULL,
    signup_date TEXT NOT NULL
);
CREATE TABLE products (
    product_id  INTEGER PRIMARY KEY,
    sku         TEXT NOT NULL UNIQUE,
    name        TEXT NOT NULL UNIQUE,
    brand       TEXT NOT NULL,
    category    TEXT NOT NULL CHECK (category IN (
        'kettle', 'mixer_grinder', 'air_fryer', 'coffee_maker', 'toaster', 'headphones')),
    price_inr   INTEGER NOT NULL CHECK (price_inr BETWEEN 499 AND 14999 AND price_inr % 100 = 99),
    launch_date TEXT NOT NULL
);
CREATE TABLE orders (
    order_id       INTEGER PRIMARY KEY,
    order_number   TEXT NOT NULL UNIQUE,
    customer_id    INTEGER NOT NULL REFERENCES customers (customer_id),
    product_id     INTEGER NOT NULL REFERENCES products (product_id),
    quantity       INTEGER NOT NULL CHECK (quantity BETWEEN 1 AND 3),
    unit_price_inr INTEGER NOT NULL CHECK (unit_price_inr > 0),
    order_date     TEXT NOT NULL,
    status         TEXT NOT NULL CHECK (status IN ('delivered', 'cancelled')),
    delivered_date TEXT,
    payment_method TEXT NOT NULL CHECK (payment_method IN ('upi', 'card', 'cod', 'netbanking')),
    CHECK ((status = 'cancelled') = (delivered_date IS NULL))
);
CREATE TABLE returns (
    return_id      INTEGER PRIMARY KEY,
    order_id       INTEGER NOT NULL UNIQUE REFERENCES orders (order_id),
    requested_date TEXT NOT NULL,
    reason         TEXT NOT NULL CHECK (reason IN (
        'damaged_in_transit', 'defective', 'wrong_item', 'not_as_described', 'changed_mind')),
    status         TEXT NOT NULL CHECK (status IN ('approved', 'rejected', 'pending')),
    photo_file     TEXT
);
CREATE TABLE refunds (
    refund_id   INTEGER PRIMARY KEY,
    order_id    INTEGER NOT NULL REFERENCES orders (order_id),
    return_id   INTEGER REFERENCES returns (return_id),
    amount_inr  INTEGER NOT NULL CHECK (amount_inr > 0),
    refund_date TEXT NOT NULL,
    method      TEXT NOT NULL CHECK (method IN ('original_payment', 'store_credit'))
);
"""

CITIES = [
    "Mumbai", "Delhi", "Bengaluru", "Hyderabad", "Chennai", "Kolkata",
    "Pune", "Ahmedabad", "Jaipur", "Lucknow", "Kochi", "Chandigarh",
]  # fmt: skip
CITY_WEIGHTS = [16, 15, 12, 10, 9, 8, 7, 6, 5, 4, 4, 4]
EMAIL_DOMAINS = ["example.com", "example.net", "example.org"]  # reserved: never a real address

# (SKU code, category, lowest price, highest price)
CATEGORIES = [
    ("KET", "kettle", 699, 2499),
    ("MXG", "mixer_grinder", 1999, 7999),
    ("AFR", "air_fryer", 3499, 12999),
    ("COF", "coffee_maker", 2499, 14999),
    ("TST", "toaster", 999, 3999),
    ("HPH", "headphones", 499, 9999),
]
# Invented brands. Every brand sells in at least two categories.
BRANDS = {
    "Zestro": ["kettle", "mixer_grinder", "toaster", "headphones"],
    "Homiva": ["kettle", "air_fryer", "coffee_maker"],
    "Kitchora": ["mixer_grinder", "air_fryer", "toaster"],
    "Brewnest": ["coffee_maker", "kettle", "toaster"],
    "Voltara": ["headphones", "air_fryer", "mixer_grinder"],
}
SERIES = ["Neo", "Prime", "Lite", "Plus", "Pro", "Max", "Ace", "Edge", "Nova", "Zen"]
# Product name = brand, series, one option from each list, then the noun.
NAME_PARTS = {
    "kettle": (["1.2 L", "1.5 L", "1.7 L", "1.8 L"], ["Steel", "Glass", "Cool-Touch"], "Kettle"),
    "mixer_grinder": (["500 W", "600 W", "750 W", "1000 W"], ["2-Jar", "3-Jar", "4-Jar"],
                      "Mixer Grinder"),
    "air_fryer": (["2.5 L", "4.2 L", "5 L", "6.2 L"], ["Digital", "Manual", "Dual-Basket"],
                  "Air Fryer"),
    "coffee_maker": (["Drip", "Espresso", "Filter", "Cold Brew"], ["Compact", "Steel", "Smart"],
                     "Coffee Maker"),
    "toaster": (["2-Slice", "4-Slice", "Long-Slot"], ["Pop-Up", "Grill", "Sandwich"], "Toaster"),
    "headphones": (["Wireless", "Bluetooth", "Noise-Cancelling"],
                   ["Over-Ear", "In-Ear", "Neckband"], "Headphones"),
}  # fmt: skip

N_CUSTOMERS = 500
N_NO_ORDER_CUSTOMERS = 25  # 5%: inside the spec's 3-8%
N_ORDERS = 3000
RETURN_RATE = 0.08
N_UNREFUNDED_APPROVED = 12  # spec P14 needs at least 10
N_GOODWILL_REFUNDS = 10
PLANTED_DELIVERED_ORDER = 2417  # spec P2
PLANTED_EARLY_SKU = "AFR-0007"  # spec P1: must have plenty of orders


def random_date(rng: random.Random, start: date, end: date) -> date:
    return start + timedelta(days=rng.randint(0, (end - start).days))


def price_ending_in_99(raw: int) -> int:
    return raw // 100 * 100 + 99


def make_products(rng: random.Random) -> list[dict]:
    products = []
    for code, category, low, high in CATEGORIES:
        brands = [brand for brand, cats in BRANDS.items() if category in cats]
        options_a, options_b, noun = NAME_PARTS[category]
        for i in range(10):
            sku = f"{code}-{i + 1:04d}"
            brand = brands[i % len(brands)]
            name = f"{brand} {SERIES[i]} {rng.choice(options_a)} {rng.choice(options_b)} {noun}"
            if rng.random() < 0.8:
                launch = random_date(rng, date(2023, 1, 1), date(2025, 3, 31))
            else:
                launch = random_date(rng, ORDERS_START, date(2026, 6, 30))
            if sku == PLANTED_EARLY_SKU:
                launch = min(launch, date(2024, 6, 1))
            products.append(
                {
                    "product_id": len(products) + 1,
                    "sku": sku,
                    "name": name,
                    "brand": brand,
                    "category": category,
                    "price_inr": price_ending_in_99(rng.randint(low, high)),
                    "launch_date": launch,
                    "popularity": rng.uniform(0.3, 3.0),
                }
            )
    return products


def make_customers(rng: random.Random, fake: Faker) -> list[dict]:
    no_order = set(rng.sample(range(1, N_CUSTOMERS + 1), N_NO_ORDER_CUSTOMERS))
    emails, phones, customers = set(), set(), []
    for customer_id in range(1, N_CUSTOMERS + 1):
        first, last = fake.first_name(), fake.last_name()
        local = "".join(ch for ch in f"{first}.{last}".lower() if ch.isalnum() or ch == ".")
        email, n = f"{local}@{rng.choice(EMAIL_DOMAINS)}", 1
        while email in emails:
            n += 1
            email = f"{local}{n}@{email.split('@')[1]}"
        emails.add(email)

        phone = None
        while phone is None or phone in phones:
            digits = rng.choice("6789") + "".join(rng.choices("0123456789", k=9))
            phone = f"+91 {digits[:5]} {digits[5:]}"
        phones.add(phone)

        latest_signup = date(2026, 9, 30) if customer_id in no_order else date(2026, 8, 31)
        customers.append(
            {
                "customer_id": customer_id,
                "name": f"{first} {last}",
                "email": email,
                "phone": phone,
                "city": rng.choices(CITIES, CITY_WEIGHTS)[0],
                "signup_date": random_date(rng, date(2024, 1, 1), latest_signup),
                "orders_at_all": customer_id not in no_order,
                "loyalty": rng.paretovariate(1.5),  # a few customers order far more than most
            }
        )
    return customers


def day_weight(day: date) -> float:
    months_in = (day.year - ORDERS_START.year) * 12 + day.month - ORDERS_START.month
    weight = 1 + 0.03 * months_in  # the shop grows about 3% a month
    if (day.year, day.month) in {(2025, 10), (2025, 11)}:
        weight *= 1.8  # Diwali sales
    elif day.month == 1:
        weight *= 1.2  # Republic Day sales
    return weight


def make_orders(rng: random.Random, customers: list[dict], products: list[dict]) -> list[dict]:
    active = [c for c in customers if c["orders_at_all"]]
    # Every active customer orders at least once, so "never ordered" is exactly the planned 5%.
    drafts = [
        (random_date(rng, max(c["signup_date"], ORDERS_START), ORDERS_END), c["customer_id"])
        for c in active
    ]
    days = [ORDERS_START + timedelta(days=i) for i in range((ORDERS_END - ORDERS_START).days + 1)]
    for day in rng.choices(days, [day_weight(d) for d in days], k=N_ORDERS - len(active)):
        eligible = [c for c in active if c["signup_date"] <= day]
        customer = rng.choices(eligible, [c["loyalty"] for c in eligible])[0]
        drafts.append((day, customer["customer_id"]))
    drafts.sort()  # order IDs rise with the order date, as in a real shop

    orders = []
    for order_id, (day, customer_id) in enumerate(drafts, start=1):
        launched = [p for p in products if p["launch_date"] <= day]
        product = rng.choices(launched, [p["popularity"] for p in launched])[0]
        cancelled = rng.random() < 0.05 and order_id != PLANTED_DELIVERED_ORDER
        delivery_days = rng.choices(range(1, 11), [5, 20, 25, 20, 12, 7, 5, 3, 2, 1])[0]
        orders.append(
            {
                "order_id": order_id,
                "order_number": f"SA-{100000 + order_id}",
                "customer_id": customer_id,
                "product_id": product["product_id"],
                "quantity": rng.choices([1, 2, 3], [85, 11, 4])[0],
                "unit_price_inr": product["price_inr"],
                "order_date": day,
                "status": "cancelled" if cancelled else "delivered",
                "delivered_date": None if cancelled else day + timedelta(days=delivery_days),
                "payment_method": rng.choices(
                    ["upi", "card", "cod", "netbanking"], [50, 25, 15, 10]
                )[0],
            }
        )
    return orders


def make_returns(rng: random.Random, orders: list[dict]) -> list[dict]:
    delivered = [o for o in orders if o["status"] == "delivered"]
    can_return = [o for o in delivered if o["delivered_date"] < SNAPSHOT]
    chosen = sorted(
        rng.sample(can_return, round(RETURN_RATE * len(delivered))), key=lambda o: o["order_id"]
    )

    returns = []
    for order in chosen:
        days_left = (SNAPSHOT - order["delivered_date"]).days
        late = rng.random() < 0.07
        if late:
            wait = rng.randint(RETURN_WINDOW_DAYS + 1, 25)
        else:
            wait = rng.randint(1, RETURN_WINDOW_DAYS)
        if wait > days_left:  # can't be requested after the snapshot date
            wait = rng.randint(1, min(days_left, RETURN_WINDOW_DAYS))
        requested = order["delivered_date"] + timedelta(days=wait)
        reason = rng.choices(
            ["damaged_in_transit", "defective", "wrong_item", "not_as_described", "changed_mind"],
            [25, 30, 12, 13, 20],
        )[0]
        if wait > RETURN_WINDOW_DAYS:
            status = "rejected"  # outside the policy's window
        elif (SNAPSHOT - requested).days <= 14 and rng.random() < 0.6:
            status = "pending"  # recent requests are often still being processed
        else:
            approve_rate = 0.65 if reason == "changed_mind" else 0.92
            status = "approved" if rng.random() < approve_rate else "rejected"
        returns.append(
            {
                "order_id": order["order_id"],
                "requested_date": requested,
                "reason": reason,
                "status": status,
                "photo_file": None,  # set by the images stage, which matches photos to categories
            }
        )
    returns.sort(key=lambda r: (r["requested_date"], r["order_id"]))
    for return_id, ret in enumerate(returns, start=1):
        ret["return_id"] = return_id
    return returns


def make_refunds(rng: random.Random, orders: list[dict], returns: list[dict]) -> list[dict]:
    by_id = {o["order_id"]: o for o in orders}
    approved = [r for r in returns if r["status"] == "approved"]  # already sorted by date
    refunds = []
    for ret in approved[:-N_UNREFUNDED_APPROVED]:  # the most recent approvals aren't paid yet
        order = by_id[ret["order_id"]]
        refund_date = ret["requested_date"] + timedelta(days=rng.randint(2, 10))
        if refund_date > SNAPSHOT:
            continue
        if order["payment_method"] == "cod" or rng.random() < 0.15:
            method = "store_credit"  # cash on delivery can't be refunded to the original payment
        else:
            method = "original_payment"
        refunds.append(
            {
                "order_id": order["order_id"],
                "return_id": ret["return_id"],
                "amount_inr": order["quantity"] * order["unit_price_inr"],
                "refund_date": refund_date,
                "method": method,
            }
        )

    # Goodwill refunds: 10% back on slow deliveries that weren't returned.
    returned = {r["order_id"] for r in returns}
    slow = [
        o
        for o in orders
        if o["status"] == "delivered"
        and (o["delivered_date"] - o["order_date"]).days >= 8
        and o["order_id"] not in returned
        and o["delivered_date"] < SNAPSHOT
    ]
    for order in sorted(rng.sample(slow, N_GOODWILL_REFUNDS), key=lambda o: o["order_id"]):
        value = order["quantity"] * order["unit_price_inr"]
        refund_date = min(order["delivered_date"] + timedelta(days=rng.randint(1, 5)), SNAPSHOT)
        refunds.append(
            {
                "order_id": order["order_id"],
                "return_id": None,
                "amount_inr": max(50, round(value * 0.1 / 10) * 10),
                "refund_date": refund_date,
                "method": "store_credit",
            }
        )

    refunds.sort(key=lambda r: (r["refund_date"], r["order_id"]))
    for refund_id, refund in enumerate(refunds, start=1):
        refund["refund_id"] = refund_id
    return refunds


COLUMNS = {
    "customers": ["customer_id", "name", "email", "phone", "city", "signup_date"],
    "products": ["product_id", "sku", "name", "brand", "category", "price_inr", "launch_date"],
    "orders": [
        "order_id", "order_number", "customer_id", "product_id", "quantity", "unit_price_inr",
        "order_date", "status", "delivered_date", "payment_method",
    ],
    "returns": ["return_id", "order_id", "requested_date", "reason", "status", "photo_file"],
    "refunds": ["refund_id", "order_id", "return_id", "amount_inr", "refund_date", "method"],
}  # fmt: skip


def write_db(tables: dict[str, list[dict]]) -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    DB_PATH.unlink(missing_ok=True)  # rebuilt from scratch every time
    with sqlite3.connect(DB_PATH) as con:
        con.execute("PRAGMA foreign_keys = ON")
        con.executescript(SCHEMA)
        for table, columns in COLUMNS.items():
            placeholders = ", ".join("?" for _ in columns)
            rows = [
                [r[c].isoformat() if isinstance(r[c], date) else r[c] for c in columns]
                for r in tables[table]
            ]
            con.executemany(
                f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})", rows
            )


# Each check is (rule from the spec, SQL returning 1 when it holds, SQL returning the value shown).
CHECKS = [
    ("500 customers", "SELECT COUNT(*) = 500 FROM customers", "SELECT COUNT(*) FROM customers"),
    ("60 products, 10 per category",
     "SELECT COUNT(*) = 6 FROM (SELECT category FROM products"
     " GROUP BY category HAVING COUNT(*) = 10)",
     "SELECT COUNT(*) FROM products"),
    ("every brand in 2+ categories",
     "SELECT MIN(n) >= 2 FROM (SELECT COUNT(DISTINCT category) n FROM products GROUP BY brand)",
     "SELECT COUNT(DISTINCT brand) || ' brands' FROM products"),
    ("3,000 orders", "SELECT COUNT(*) = 3000 FROM orders", "SELECT COUNT(*) FROM orders"),
    ("93-97% delivered",
     "SELECT AVG(status = 'delivered') BETWEEN 0.93 AND 0.97 FROM orders",
     "SELECT ROUND(100.0 * AVG(status = 'delivered'), 1) || '%' FROM orders"),
    ("80%+ of orders have quantity 1",
     "SELECT AVG(quantity = 1) >= 0.8 FROM orders",
     "SELECT ROUND(100.0 * AVG(quantity = 1), 1) || '%' FROM orders"),
    ("3-8% of customers never ordered",
     "SELECT AVG(customer_id NOT IN (SELECT customer_id FROM orders)) BETWEEN 0.03 AND 0.08"
     " FROM customers",
     "SELECT ROUND(100.0 * AVG(customer_id NOT IN (SELECT customer_id FROM orders)), 1) || '%'"
     " FROM customers"),
    ("orders on/after launch and signup",
     "SELECT COUNT(*) = 0 FROM orders o JOIN products p USING (product_id)"
     " JOIN customers c USING (customer_id)"
     " WHERE o.order_date < p.launch_date OR o.order_date < c.signup_date",
     "SELECT 'checked'"),
    ("200-260 returns", "SELECT COUNT(*) BETWEEN 200 AND 260 FROM returns",
     "SELECT COUNT(*) FROM returns"),
    ("90%+ of returns within 10 days",
     "SELECT AVG(julianday(r.requested_date) - julianday(o.delivered_date) <= 10) >= 0.9"
     " FROM returns r JOIN orders o USING (order_id)",
     "SELECT ROUND(100.0 * AVG(julianday(r.requested_date) - julianday(o.delivered_date) <= 10), 1)"
     " || '%' FROM returns r JOIN orders o USING (order_id)"),
    ("late returns are all rejected",
     "SELECT COUNT(*) = 0 FROM returns r JOIN orders o USING (order_id)"
     " WHERE julianday(r.requested_date) - julianday(o.delivered_date) > 10"
     " AND r.status != 'rejected'",
     "SELECT 'checked'"),
    ("150-220 refunds", "SELECT COUNT(*) BETWEEN 150 AND 220 FROM refunds",
     "SELECT COUNT(*) FROM refunds"),
    ("refunds only on approved returns",
     "SELECT COUNT(*) = 0 FROM refunds f JOIN returns r USING (return_id)"
     " WHERE r.status != 'approved'",
     "SELECT 'checked'"),
    ("10+ approved returns not yet refunded (P14)",
     "SELECT COUNT(*) >= 10 FROM returns WHERE status = 'approved'"
     " AND return_id NOT IN (SELECT return_id FROM refunds WHERE return_id IS NOT NULL)",
     "SELECT COUNT(*) FROM returns WHERE status = 'approved'"
     " AND return_id NOT IN (SELECT return_id FROM refunds WHERE return_id IS NOT NULL)"),
    ("refunds never exceed the order's value",
     "SELECT COUNT(*) = 0 FROM (SELECT o.order_id FROM refunds f JOIN orders o USING (order_id)"
     " GROUP BY o.order_id HAVING SUM(f.amount_inr) > MAX(o.quantity * o.unit_price_inr))",
     "SELECT 'checked'"),
    ("order 2417 is delivered (P2)",
     "SELECT status = 'delivered' FROM orders WHERE order_id = 2417",
     "SELECT order_number FROM orders WHERE order_id = 2417"),
    ("AFR-0007 has delivered orders (P1)",
     "SELECT COUNT(*) > 0 FROM orders JOIN products USING (product_id)"
     " WHERE sku = 'AFR-0007' AND status = 'delivered'",
     "SELECT COUNT(*) || ' orders' FROM orders JOIN products USING (product_id)"
     " WHERE sku = 'AFR-0007'"),
    ("no date after the 2026-10-10 snapshot",
     "SELECT MAX(d) <= '2026-10-10' FROM (SELECT signup_date d FROM customers"
     " UNION ALL SELECT delivered_date FROM orders UNION ALL SELECT requested_date FROM returns"
     " UNION ALL SELECT refund_date FROM refunds)",
     "SELECT MAX(d) FROM (SELECT delivered_date d FROM orders UNION ALL SELECT refund_date"
     " FROM refunds)"),
]  # fmt: skip


def check(con: sqlite3.Connection) -> bool:
    """Print each spec rule with pass/fail. Lab 0.P turns these into proper tests."""
    orphans = con.execute("PRAGMA foreign_key_check").fetchall()
    print(f"  {'PASS' if not orphans else 'FAIL'}  no orphan rows ({len(orphans)} found)")
    all_ok = not orphans
    for rule, holds_sql, value_sql in CHECKS:
        ok = bool(con.execute(holds_sql).fetchone()[0])
        value = con.execute(value_sql).fetchone()[0]
        print(f"  {'PASS' if ok else 'FAIL'}  {rule} ({value})")
        all_ok &= ok
    return all_ok


def main() -> None:
    rng = random.Random(SEED)
    fake = Faker("en_IN")
    fake.seed_instance(SEED)

    products = make_products(rng)
    customers = make_customers(rng, fake)
    orders = make_orders(rng, customers, products)
    returns = make_returns(rng, orders)
    refunds = make_refunds(rng, orders, returns)
    write_db(
        {
            "customers": customers,
            "products": products,
            "orders": orders,
            "returns": returns,
            "refunds": refunds,
        }
    )

    print(f"Wrote {DB_PATH.relative_to(DB_PATH.parents[1])}. Checking it against the spec:")
    with sqlite3.connect(DB_PATH) as con:
        if not check(con):
            sys.exit("Some rules failed: fix the generator, not the spec.")


if __name__ == "__main__":
    main()
