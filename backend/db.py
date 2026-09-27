"""SQLite access + garment_type normalization for Campus Customs.

The DB is read-only from the app's point of view for now (Problem 3). Inventory
and users get written later. Everything funnels through here so the messy
`garment_type` values are cleaned in exactly one place.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

# backend/ lives next to data/ at the project root.
ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "campus_customs.db"
PRODUCTS_DIR = ROOT / "data" / "products"

# Canonical size order — the table stores sizes unordered.
SIZE_ORDER = ["XS", "S", "M", "L", "XL", "XXL"]


def connect() -> sqlite3.Connection:
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Database not found at {DB_PATH}. Unzip data.zip into the project root "
            "so that data/campus_customs.db exists."
        )
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def normalize_garment_type(raw: str) -> str:
    """Collapse 22 raw catalogue spellings into ~8 clean display categories.

    Keyword rules, order matters. Rule-based rather than a lookup table so a new
    catalogue value ("long-sleeve tee") still lands in a sensible bucket.
    """
    t = (raw or "").lower()
    if "t-shirt" in t or "tee" in t:
        return "T-Shirt"
    if "quarter-zip" in t or "1/4-zip" in t or "1-4-zip" in t:
        return "Quarter-Zip"
    if "full-zip" in t and "hood" in t:
        return "Full-Zip Hoodie"
    if "hood" in t:
        return "Hoodie"
    if "mockneck" in t or "mock neck" in t:
        return "Mockneck"
    if "performance" in t:
        return "Performance Shirt"
    if "jacket" in t or "bomber" in t or "fleece" in t:
        return "Jacket"
    if "crew" in t or "raglan" in t:
        return "Crewneck"
    return raw.title()


def _loads(value: str) -> list:
    try:
        parsed = json.loads(value)
        return parsed if isinstance(parsed, list) else []
    except (json.JSONDecodeError, TypeError):
        return []


def _short_description(text: str, limit: int = 110) -> str:
    """A grid-card-length blurb from the full description."""
    text = (text or "").strip()
    if len(text) <= limit:
        return text
    cut = text[:limit].rsplit(" ", 1)[0]
    return cut + "…"


def product_summary(row: sqlite3.Row) -> dict:
    """Card-level shape for the Products grid."""
    return {
        "product_id": row["product_id"],
        "name": row["name"],
        "garment_type": normalize_garment_type(row["garment_type"]),
        "price": row["price"],
        "colors": _loads(row["colors"]),
        "short_description": _short_description(row["description"]),
        "image_url": f"/media/products/{row['product_id']}.jpg",
    }


def list_products() -> list[dict]:
    conn = connect()
    try:
        rows = conn.execute(
            "SELECT product_id, name, garment_type, description, colors, price "
            "FROM catalogue ORDER BY name"
        ).fetchall()
        return [product_summary(r) for r in rows]
    finally:
        conn.close()


def get_product(product_id: str) -> dict | None:
    """Full detail for the single-item page, including per-size stock."""
    conn = connect()
    try:
        row = conn.execute(
            "SELECT product_id, name, garment_type, description, colors, "
            "search_tags, price FROM catalogue WHERE product_id = ?",
            (product_id,),
        ).fetchone()
        if row is None:
            return None

        stock = conn.execute(
            "SELECT size, quantity FROM inventory WHERE product_id = ?",
            (product_id,),
        ).fetchall()
        by_size = {s["size"]: s["quantity"] for s in stock}
        inventory = [
            {"size": size, "quantity": by_size.get(size, 0)}
            for size in SIZE_ORDER
            if size in by_size
        ]

        return {
            "product_id": row["product_id"],
            "name": row["name"],
            "garment_type": normalize_garment_type(row["garment_type"]),
            "description": row["description"],
            "colors": _loads(row["colors"]),
            "search_tags": _loads(row["search_tags"]),
            "price": row["price"],
            "image_url": f"/media/products/{row['product_id']}.jpg",
            "inventory": inventory,
            "total_stock": sum(i["quantity"] for i in inventory),
        }
    finally:
        conn.close()


# --------------------------------------------------------------------------
# Users / auth (Problem 4)
# --------------------------------------------------------------------------

# Documented test credential from the assignment. Its seed hash uses the legacy
# 3-part scheme we can't verify, so we migrate it to our scheme on startup.
TEST_EMAIL = "test@campuscustoms.yale.edu"
TEST_PASSWORD = "password"


def _public_user(row: sqlite3.Row) -> dict:
    """A user shaped for the client — never includes the password hash."""
    return {
        "id": row["id"],
        "email": row["email"],
        "first_name": row["first_name"],
        "last_name": row["last_name"],
        "name": row["name"],
    }


def get_user_by_email(email: str) -> sqlite3.Row | None:
    conn = connect()
    try:
        return conn.execute(
            "SELECT * FROM users WHERE email = ? COLLATE NOCASE", (email.strip(),)
        ).fetchone()
    finally:
        conn.close()


def create_user(first_name: str, last_name: str, email: str, password_hash: str) -> dict:
    """Insert a new user. Raises sqlite3.IntegrityError on a duplicate email."""
    first_name, last_name, email = first_name.strip(), last_name.strip(), email.strip()
    full_name = f"{first_name} {last_name}".strip()
    conn = connect()
    try:
        cur = conn.execute(
            "INSERT INTO users (name, email, password_hash, first_name, last_name) "
            "VALUES (?, ?, ?, ?, ?)",
            (full_name, email, password_hash, first_name, last_name),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM users WHERE id = ?", (cur.lastrowid,)).fetchone()
        return _public_user(row)
    finally:
        conn.close()


def ensure_seed_logins() -> None:
    """Idempotently migrate the documented test account to our hash scheme.

    Runs on startup. The seed test user carries a legacy hash we can't verify; we
    rewrite it (only it) to our scheme using the assignment's documented password, so
    the test login works on any fresh unzip of the database. Other seed users are left
    untouched — their passwords were never provided, so they can't be logged into anyway.
    """
    from auth import ALGORITHM, hash_password

    conn = connect()
    try:
        row = conn.execute(
            "SELECT id, password_hash FROM users WHERE email = ? COLLATE NOCASE",
            (TEST_EMAIL,),
        ).fetchone()
        if row is None:
            return
        # Already in our 4-part scheme? Leave it.
        if row["password_hash"].startswith(f"{ALGORITHM}$") and row["password_hash"].count("$") == 3:
            return
        conn.execute(
            "UPDATE users SET password_hash = ? WHERE id = ?",
            (hash_password(TEST_PASSWORD), row["id"]),
        )
        conn.commit()
    finally:
        conn.close()


# --------------------------------------------------------------------------
# Search (Problem 5 — agent tools)
# --------------------------------------------------------------------------

def search_catalogue(
    query: str = "",
    garment_type: str | None = None,
    color: str | None = None,
    max_price: float | None = None,
    in_stock_only: bool = False,
    limit: int = 8,
) -> list[dict]:
    """Keyword search over the catalogue for the agent.

    Matches `query` tokens against name, description, tags, and colors; optionally
    filters by normalized garment_type, color, and price. Ranks by how many tokens
    hit. Returns compact hits with live stock, never raw hallucinated data.
    """
    conn = connect()
    try:
        rows = conn.execute(
            "SELECT product_id, name, garment_type, description, colors, "
            "search_tags, price FROM catalogue"
        ).fetchall()
        stock_rows = conn.execute(
            "SELECT product_id, size, quantity FROM inventory WHERE quantity > 0"
        ).fetchall()
    finally:
        conn.close()

    in_stock: dict[str, list[str]] = {}
    totals: dict[str, int] = {}
    for s in stock_rows:
        in_stock.setdefault(s["product_id"], []).append(s["size"])
        totals[s["product_id"]] = totals.get(s["product_id"], 0) + s["quantity"]

    tokens = [t for t in query.lower().split() if len(t) > 1]
    want_type = normalize_garment_type(garment_type).lower() if garment_type else None
    want_color = color.lower().strip() if color else None

    hits = []
    for r in rows:
        clean_type = normalize_garment_type(r["garment_type"])
        colors = _loads(r["colors"])
        haystack = " ".join(
            [r["name"], r["description"], clean_type, " ".join(colors), " ".join(_loads(r["search_tags"]))]
        ).lower()

        if want_type and clean_type.lower() != want_type:
            continue
        if want_color and not any(want_color in c.lower() for c in colors):
            continue
        if max_price is not None and r["price"] > max_price:
            continue
        total = totals.get(r["product_id"], 0)
        if in_stock_only and total == 0:
            continue

        # Score: token matches, or 1 if no query (so filters alone still return results).
        score = sum(1 for t in tokens if t in haystack) if tokens else 1
        if tokens and score == 0:
            continue

        sizes = [s for s in SIZE_ORDER if s in in_stock.get(r["product_id"], [])]
        hits.append(
            (
                score,
                {
                    "product_id": r["product_id"],
                    "name": r["name"],
                    "garment_type": clean_type,
                    "price": r["price"],
                    "colors": colors,
                    "short_description": _short_description(r["description"]),
                    "total_stock": total,
                    "available_sizes": sizes,
                },
            )
        )

    hits.sort(key=lambda h: (-h[0], h[1]["price"]))
    return [h[1] for h in hits[:limit]]


def get_user_by_id(user_id: int) -> sqlite3.Row | None:
    conn = connect()
    try:
        return conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    finally:
        conn.close()


def save_chat_message(user_id: int, role: str, content: str, products_json: str | None = None) -> None:
    """Persist one chat turn for a logged-in shopper (used for history / evidence)."""
    conn = connect()
    try:
        conn.execute(
            "INSERT INTO chat_messages (user_id, role, content, products_json) VALUES (?, ?, ?, ?)",
            (user_id, role, content, products_json),
        )
        conn.commit()
    finally:
        conn.close()


def get_chat_history(user_id: int, limit: int = 100) -> list[dict]:
    """Load a logged-in shopper's saved chat turns, oldest first, for reload on return.

    products_json is parsed back into a list so the front end can re-render the cards
    that were shown with each assistant reply.
    """
    conn = connect()
    try:
        rows = conn.execute(
            "SELECT role, content, products_json, created_at FROM chat_messages "
            "WHERE user_id = ? ORDER BY id ASC LIMIT ?",
            (user_id, limit),
        ).fetchall()
    finally:
        conn.close()

    history = []
    for r in rows:
        products = []
        if r["products_json"]:
            try:
                products = json.loads(r["products_json"])
            except (json.JSONDecodeError, TypeError):
                products = []
        history.append(
            {
                "role": r["role"],
                "content": r["content"],
                "products": products,
                "created_at": r["created_at"],
            }
        )
    return history
