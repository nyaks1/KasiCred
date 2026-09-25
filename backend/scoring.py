"""Evidence-weighted review logic (fraud resistance).

This is NOT a credit score. It weights confirmed sales so spammy one-offs
cannot dominate a lender-facing evidence signal for a vendor.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Iterable, Optional

# Tunables (hackathon freeze — change only with tests)
AMOUNT_UNIT_RANDS = 50.0
AMOUNT_WEIGHT_CAP = 3.0
REPEAT_WEIGHT_CAP = 2.5
REPEAT_STEP = 0.25
WINDOW_DAYS = 180  # middle of the 3–8 month stabilisation horizon


@dataclass(frozen=True)
class SaleEvent:
    """One confirmed (or claimed) sale that can carry a buyer rating."""

    buyer_id: str
    rating: int  # 1–5
    amount_rands: float
    confirmed: bool
    created_at: datetime
    vendor_id: str = ""


def amount_weight(amount_rands: float, unit_rands: float = AMOUNT_UNIT_RANDS, cap: float = AMOUNT_WEIGHT_CAP) -> float:
    """min(amount / R50, cap) — bigger sales count more, one huge fake cannot dominate."""
    if amount_rands < 0:
        raise ValueError("amount_rands must be >= 0")
    if unit_rands <= 0:
        raise ValueError("unit_rands must be > 0")
    return min(amount_rands / unit_rands, cap)


def repeat_weight(prior_confirmed: int, cap: float = REPEAT_WEIGHT_CAP, step: float = REPEAT_STEP) -> float:
    """Capped, non-linear-ish step for buyers who keep coming back."""
    if prior_confirmed < 0:
        raise ValueError("prior_confirmed must be >= 0")
    if prior_confirmed == 0:
        return 1.0
    return min(1.0 + step * prior_confirmed, cap)


def review_contribution(event: SaleEvent, prior_confirmed: int) -> float:
    """Contribution of one review. Confirmation gate is binary: unconfirmed = 0."""
    if not 1 <= event.rating <= 5:
        raise ValueError("rating must be 1–5")
    if not event.confirmed:
        return 0.0
    return amount_weight(event.amount_rands) * repeat_weight(prior_confirmed) * event.rating


def _parse_when(value: datetime | str) -> datetime:
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(value.replace("Z", "+00:00").split("+")[0].split(".")[0])


def prior_confirmed_count(
    history: Iterable[SaleEvent],
    buyer_id: str,
    before: datetime,
    window_days: int = WINDOW_DAYS,
) -> int:
    """How many confirmed sales this buyer already had with this vendor before `before`."""
    cutoff = before - timedelta(days=window_days)
    n = 0
    for e in history:
        if e.buyer_id != buyer_id or not e.confirmed:
            continue
        when = _parse_when(e.created_at)
        if cutoff <= when < before:
            n += 1
    return n


def vendor_evidence_score(
    history: Iterable[SaleEvent],
    *,
    as_of: Optional[datetime] = None,
    window_days: int = WINDOW_DAYS,
) -> dict:
    """
    Rolling-window vendor evidence score from confirmed, rated sales.

    Score stabilises over the window; individual txs are not decayed.
    Returns display score 0–100 plus parts for debugging / lender UI.
    """
    as_of = as_of or datetime.utcnow()
    cutoff = as_of - timedelta(days=window_days)
    events = []
    for e in history:
        when = _parse_when(e.created_at)
        if cutoff <= when <= as_of:
            events.append((when, e))

    events.sort(key=lambda pair: pair[0])
    contributions: list[float] = []
    confirmed_used = 0

    for when, e in events:
        prior = prior_confirmed_count(
            (ev for _, ev in events),
            buyer_id=e.buyer_id,
            before=when,
            window_days=window_days,
        )
        c = review_contribution(e, prior)
        if e.confirmed:
            confirmed_used += 1
        contributions.append(c)

    active = [c for c in contributions if c > 0]
    if not active:
        return {
            "score_0_100": 0.0,
            "reviews_in_window": len(contributions),
            "confirmed_in_window": confirmed_used,
            "mean_contribution": 0.0,
            "stabilised": False,
        }

    mean_c = sum(active) / len(active)
    # Max theoretical mean ≈ 3.0 * 2.5 * 5 = 37.5 → map to 0–100
    score = min(100.0, (mean_c / 37.5) * 100.0)
    return {
        "score_0_100": round(score, 2),
        "reviews_in_window": len(contributions),
        "confirmed_in_window": confirmed_used,
        "mean_contribution": round(mean_c, 4),
        "stabilised": confirmed_used >= 3 and (as_of - events[0][0]).days >= 90,
    }


def evaluate(event: SaleEvent, history: Iterable[SaleEvent], *, window_days: int = WINDOW_DAYS) -> dict:
    """Score one new event against prior history (same vendor)."""
    when = _parse_when(event.created_at)
    prior = prior_confirmed_count(history, event.buyer_id, before=when, window_days=window_days)
    return {
        "contribution": review_contribution(event, prior),
        "prior_confirmed": prior,
        "amount_weight": amount_weight(event.amount_rands),
        "repeat_weight": repeat_weight(prior),
        "confirmed": event.confirmed,
    }
