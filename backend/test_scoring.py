import unittest
from datetime import datetime, timedelta

from backend.scoring import (
    SaleEvent,
    amount_weight,
    evaluate,
    repeat_weight,
    review_contribution,
    vendor_evidence_score,
)

T0 = datetime(2026, 9, 1, 12, 0, 0)


def ev(days_ago: int, rating: int = 5, amount: float = 50.0, confirmed: bool = True, buyer: str = "0711111111") -> SaleEvent:
    return SaleEvent(
        buyer_id=buyer,
        rating=rating,
        amount_rands=amount,
        confirmed=confirmed,
        created_at=T0 - timedelta(days=days_ago),
    )


class TestAmountWeight(unittest.TestCase):
    def test_unit_sale(self):
        self.assertEqual(amount_weight(50.0), 1.0)

    def test_cap_on_large_sale(self):
        self.assertEqual(amount_weight(10_000), 3.0)

    def test_small_sale(self):
        self.assertAlmostEqual(amount_weight(25.0), 0.5)


class TestRepeatWeight(unittest.TestCase):
    def test_first_timer(self):
        self.assertEqual(repeat_weight(0), 1.0)

    def test_returning_rises(self):
        self.assertGreater(repeat_weight(2), 1.0)

    def test_capped_not_linear_forever(self):
        self.assertEqual(repeat_weight(100), 2.5)


class TestGate(unittest.TestCase):
    def test_unconfirmed_is_zero(self):
        e = ev(0, confirmed=False)
        self.assertEqual(review_contribution(e, prior_confirmed=0), 0.0)

    def test_confirmed_scores(self):
        e = ev(0, confirmed=True, amount=50.0, rating=5)
        self.assertEqual(review_contribution(e, prior_confirmed=0), 5.0)


class TestEvaluate(unittest.TestCase):
    def test_repeat_buyer_gets_more_weight(self):
        history = [ev(30, buyer="071"), ev(20, buyer="071")]
        result = evaluate(ev(0, buyer="071"), history)
        self.assertEqual(result["prior_confirmed"], 2)
        self.assertGreater(result["repeat_weight"], 1.0)


class TestVendorScore(unittest.TestCase):
    def test_empty_is_zero(self):
        out = vendor_evidence_score([], as_of=T0)
        self.assertEqual(out["score_0_100"], 0.0)
        self.assertFalse(out["stabilised"])

    def test_unconfirmed_only_is_zero(self):
        out = vendor_evidence_score([ev(10, confirmed=False)], as_of=T0)
        self.assertEqual(out["score_0_100"], 0.0)

    def test_window_excludes_old_sales(self):
        old = ev(200, amount=200.0, rating=5)
        out = vendor_evidence_score([old], as_of=T0)
        self.assertEqual(out["score_0_100"], 0.0)

    def test_good_history_scores_higher_than_one_off(self):
        repeat = [ev(120), ev(90), ev(60), ev(30), ev(10)]
        one_off = [ev(10)]
        hi = vendor_evidence_score(repeat, as_of=T0)
        lo = vendor_evidence_score(one_off, as_of=T0)
        self.assertGreater(hi["score_0_100"], lo["score_0_100"])
        self.assertTrue(hi["stabilised"])


if __name__ == "__main__":
    unittest.main()
