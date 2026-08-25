import os
import sqlite3

DB_PATH = os.getenv("KASICRED_DB_PATH", os.path.join(os.path.dirname(__file__), "kasicred.db"))

SCHEMA = """
CREATE TABLE IF NOT EXISTS vendors (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    phone           TEXT NOT NULL UNIQUE,
    store_name      TEXT NOT NULL,
    market_area     TEXT NOT NULL DEFAULT 'Unknown',
    category_items  TEXT NOT NULL DEFAULT 'General Merchandise',
    wallet_address  TEXT NOT NULL,
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS reviews (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    vendor_id    INTEGER NOT NULL REFERENCES vendors(id) ON DELETE CASCADE,
    buyer_phone  TEXT,
    review_text  TEXT,
    issue        TEXT,
    score        INTEGER NOT NULL CHECK (score BETWEEN 1 AND 5),
    tx_hash      TEXT,
    source       TEXT NOT NULL DEFAULT 'direct' CHECK (source IN ('direct', 'whatsapp')),
    created_at   TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_reviews_vendor ON reviews(vendor_id);
CREATE INDEX IF NOT EXISTS idx_vendors_phone  ON vendors(phone);
"""


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.executescript(SCHEMA)


def ensure_vendor(phone: str, wallet_address: str, store_name: str = "Unregistered Stall",
                  market_area: str = "Unknown", category_items: str = "General Merchandise") -> int:
    """Returns the vendor id, creating a placeholder row if needed."""
    with get_connection() as conn:
        row = conn.execute("SELECT id FROM vendors WHERE phone = ?", (phone,)).fetchone()
        if row:
            return row["id"]
        cur = conn.execute(
            "INSERT INTO vendors (phone, store_name, market_area, category_items, wallet_address) "
            "VALUES (?, ?, ?, ?, ?)",
            (phone, store_name, market_area, category_items, wallet_address),
        )
        return cur.lastrowid


def upsert_vendor(phone: str, store_name: str, market_area: str,
                  category_items: str, wallet_address: str) -> dict:
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO vendors (phone, store_name, market_area, category_items, wallet_address) "
            "VALUES (?, ?, ?, ?, ?) "
            "ON CONFLICT(phone) DO UPDATE SET "
            "store_name = excluded.store_name, "
            "market_area = excluded.market_area, "
            "category_items = excluded.category_items, "
            "wallet_address = excluded.wallet_address",
            (phone, store_name, market_area, category_items, wallet_address),
        )
    return get_vendor(phone)


def get_vendor(phone: str) -> dict | None:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM vendors WHERE phone = ?", (phone,)).fetchone()
        return dict(row) if row else None


def insert_review(vendor_phone: str, score: int, buyer_phone: str | None = None,
                  review_text: str | None = None, issue: str | None = None,
                  tx_hash: str | None = None, source: str = "direct") -> int:
    with get_connection() as conn:
        row = conn.execute("SELECT id FROM vendors WHERE phone = ?", (vendor_phone,)).fetchone()
        if not row:
            raise ValueError(f"Vendor '{vendor_phone}' is not registered; call ensure_vendor first.")
        cur = conn.execute(
            "INSERT INTO reviews (vendor_id, buyer_phone, review_text, issue, score, tx_hash, source) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (row["id"], buyer_phone, review_text, issue, score, tx_hash, source),
        )
        return cur.lastrowid


def get_recent_reviews(vendor_phone: str, limit: int = 10) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT r.score, r.review_text, r.issue, r.source, r.tx_hash, r.created_at "
            "FROM reviews r JOIN vendors v ON v.id = r.vendor_id "
            "WHERE v.phone = ? ORDER BY r.created_at DESC, r.id DESC LIMIT ?",
            (vendor_phone, limit),
        ).fetchall()
        return [dict(r) for r in rows]
