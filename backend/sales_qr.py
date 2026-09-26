"""Ephemeral sale QR — shown on the vendor phone at the moment of sale.

No printed stickers. Buyer scans the on-screen QR and confirms on WhatsApp.
"""
from __future__ import annotations

import os
import secrets
import time

# sale_id -> record (ephemeral; fine for demo / one dyno)
_sales: dict[str, dict] = {}

DEFAULT_BUSINESS_E164 = os.getenv("WHATSAPP_PUBLIC_E164", "15551771178")
DEFAULT_TTL_SECONDS = 15 * 60  # QR only relevant while the sale is fresh


def new_sale(
    vendor_phone: str,
    amount_rands: float,
    *,
    note: str = "",
    business_e164: str | None = None,
) -> dict:
    """Vendor records a sale. Returns QR + WhatsApp link for the buyer to confirm."""
    sale_id = "S-" + secrets.token_hex(4).upper()
    number = (business_e164 or DEFAULT_BUSINESS_E164 or "").replace("+", "").replace(" ", "").replace("-", "")
    start_text = f"CONFIRM {sale_id}"

    _sales[sale_id] = {
        "sale_id": sale_id,
        "vendor_phone": vendor_phone.strip(),
        "amount_rands": float(amount_rands),
        "note": note[:80],
        "status": "awaiting_confirm",
        "buyer_phone": None,
        "created_at": time.time(),
        "expires_at": time.time() + DEFAULT_TTL_SECONDS,
    }

    wa_link = f"https://wa.me/{number}?text={start_text.replace(' ', '%20')}"
    return {
        **_sales[sale_id],
        "wa_link": wa_link,
        "qr_path": f"/sale/{sale_id}/qr.svg",
        "how": "Show this QR on the vendor phone. Buyer scans and confirms on WhatsApp.",
    }


def get_sale(sale_id: str) -> dict | None:
    return _sales.get(sale_id)


def confirm_sale(sale_id: str, buyer_phone: str) -> tuple[dict | None, bool]:
    """Returns (sale, newly_confirmed)."""
    sale = _sales.get(sale_id)
    if not sale:
        return None, False
    if time.time() > sale["expires_at"]:
        sale["status"] = "expired"
        return sale, False
    if sale["status"] == "confirmed":
        return sale, False
    sale["status"] = "confirmed"
    sale["buyer_phone"] = buyer_phone
    sale["confirmed_at"] = time.time()
    return sale, True


def sale_confirm_reply(sale: dict | None, newly: bool) -> str:
    if not sale:
        return "That sale QR is unknown or expired. Ask the vendor to show the code again after recording the sale."
    if sale["status"] == "expired":
        return "That sale QR expired. Vendor: record the sale again to show a fresh code."
    if not newly:
        return (
            f"Sale already confirmed: R{sale['amount_rands']:.0f}\n"
            "Thanks — this adds behavioural weight to the vendor's proof pack.\n"
            "We don't score you."
        )
    return (
        "SALE CONFIRMED\n"
        f"Amount: R{sale['amount_rands']:.0f}\n"
        "Thanks. This is real trade evidence for the vendor's income pack.\n"
        "Not a credit score. Not a review. A confirmed sale."
    )


def buyer_confirm_message(phone: str, text: str) -> str | None:
    """If the buyer message is CONFIRM <sale_id>, handle it and return a reply."""
    raw = (text or "").strip()
    low = raw.lower()
    if not (low.startswith("confirm ") or low.startswith("confirm")):
        return None
    parts = raw.split()
    sale_id = parts[1] if len(parts) > 1 else ""
    if not sale_id:
        return "Send: CONFIRM S-XXXX (the code under the vendor QR)."
    sale, newly = confirm_sale(sale_id, phone)
    return sale_confirm_reply(sale, newly)
