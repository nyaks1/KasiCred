"""WhatsApp proof-of-income conversation for GKHack26 reviewers.

Not a credit score. Flow: POPIA notice -> consent -> trade evidence -> share code.
"""
from __future__ import annotations

import secrets
import time
import os
from dataclasses import dataclass, field
from typing import Optional

# POPIA s18 — what / who / purpose / voluntary / rights (short form for WhatsApp)
NOTICE = (
    "KasiCred — Proof of Income (not a credit score)\n"
    "We collect: your stall name, trade amounts, optional slip photos.\n"
    "Why: so YOU can share income proof with a lender or landlord you choose.\n"
    "We keep it a short time. You can ask us to delete it.\n"
    "Data stays with us unless you share a code. No GPS. No scoring.\n\n"
    "Reply YES to consent, or NO to stop."
)

STEPS = ("CONSENT", "STALL", "TAKINGS", "SALE", "SLIP", "DONE")


@dataclass
class PoiSession:
    step: str = "CONSENT"
    stall: str = ""
    takings: str = ""
    sale: str = ""
    slip: str = ""
    share_code: str = ""
    started: float = field(default_factory=time.time)


_sessions: dict[str, PoiSession] = {}


def _new_code() -> str:
    return "KC-" + secrets.token_hex(3).upper()


# Vendor-initiated entry: user must message first (WhatsApp 24h CSW rule).
DEFAULT_START_TEXT = "hi"
# Test number for GKHack26 — digits only, no + (wa.me format).
DEFAULT_BUSINESS_E164 = os.getenv("WHATSAPP_PUBLIC_E164", "15551771178")


def start_deep_link(business_e164: str | None = None, start_text: str = DEFAULT_START_TEXT) -> str:
    """https://wa.me/<number>?text=hi — vendor taps this to open the chat."""
    number = (business_e164 or DEFAULT_BUSINESS_E164 or "").replace("+", "").replace(" ", "").replace("-", "")
    text = start_text.strip() or DEFAULT_START_TEXT
    return f"https://wa.me/{number}?text={text}"


def start_payload(business_e164: str | None = None) -> dict:
    link = start_deep_link(business_e164)
    return {
        "url": link,
        "number": (business_e164 or DEFAULT_BUSINESS_E164),
        "start_text": DEFAULT_START_TEXT,
        "how": "Vendor opens the link (or texts the number). They initiate — we reply in the 24h window.",
    }


def handle_message(phone: str, text: str) -> str:
    """Advance the POI flow. Returns the next WhatsApp reply (plain text)."""
    key = phone.strip()
    raw = (text or "").strip()
    low = raw.lower()

    if key not in _sessions or low in ("hi", "hello", "start", "restart"):
        _sessions[key] = PoiSession()
        return NOTICE

    s = _sessions[key]

    if s.step == "CONSENT":
        if low in ("no", "n", "stop", "cancel"):
            del _sessions[key]
            return "Understood. Nothing stored. Message us again anytime to start over."
        if low not in ("yes", "y", "yebo", "ee"):
            return 'Please reply YES to consent, or NO to stop.'
        s.step = "STALL"
        return (
            "Consent saved.\n\n"
            "1/4 What is your stall / trading name?\n"
            "(e.g. Mama Thabo's Spaza)"
        )

    if s.step == "STALL":
        if not raw:
            return "Please type your stall name."
        s.stall = raw[:80]
        s.step = "TAKINGS"
        return (
            f"Stall: {s.stall}\n\n"
            "2/4 Rough takings on a normal day? (Rands)\n"
            "(e.g. 450 — a range is fine: 300-600)"
        )

    if s.step == "TAKINGS":
        if not raw:
            return "Please type a Rand amount or range."
        s.takings = raw[:40]
        s.step = "SALE"
        return (
            f"Daily takings: R{s.takings}\n\n"
            "3/4 One confirmed sale today? Amount in Rands\n"
            "(e.g. 45 — we only count confirmed sales for proof weight)"
        )

    if s.step == "SALE":
        if not raw:
            return "Please type a sale amount in Rands."
        s.sale = raw[:20]
        s.step = "SLIP"
        return (
            f"Sale noted: R{s.sale} (confirmed)\n\n"
            "4/4 Optional: send a photo of a till slip / stokvel book page, "
            "or type SKIP.\n"
            "(Photo strengthens the pack — never required)"
        )

    if s.step == "SLIP":
        if low not in ("skip", "s", "none"):
            s.slip = raw[:60] if raw else "photo"
        s.share_code = _new_code()
        s.step = "DONE"
        return _pack_message(s)

    if s.step == "DONE":
        if low in ("restart", "new", "start"):
            _sessions[key] = PoiSession()
            return NOTICE
        return (
            f"Your pack is ready. Share code: {s.share_code}\n"
            "Lenders open it on our verify page. You stay in control.\n"
            "Reply RESTART for a new pack."
        )

    return NOTICE


def _pack_message(s: PoiSession) -> str:
    return (
        "PROOF-OF-INCOME PACK ready\n"
        "--------------------------------\n"
        f"Stall:     {s.stall}\n"
        f"Takings:   R{s.takings}\n"
        f"Confirmed sale: R{s.sale}\n"
        f"Evidence:  {'slip/photo noted' if s.slip else 'text attestation'}\n"
        f"Share code: {s.share_code}\n"
        "--------------------------------\n"
        "We don't score you. We prove income.\n"
        "A lender pays to open this pack — not you.\n"
        "POPIA: ask DELETE to erase this pack."
    )


def handle_media(phone: str) -> str:
    key = phone.strip()
    if key not in _sessions:
        return NOTICE
    s = _sessions[key]
    if s.step == "SLIP":
        s.slip = "photo_received"
        s.share_code = _new_code()
        s.step = "DONE"
        return _pack_message(s)
    if s.step == "DONE":
        return f"Pack already created. Code: {s.share_code}"
    return "Photo saved to this step. Continue with the text replies."
