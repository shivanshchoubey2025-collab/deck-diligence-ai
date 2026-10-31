"""
Unit tests for PitchDeckScreener
Validates:
  1. Missing input fields are not populated with benign fabricated defaults
  2. Missing inputs display 'Undisclosed (Data Gap)' in IC memo table rather than 'Breached/Sluggish'
  3. Burn Multiple thresholds (<1.0, 1.0-2.0, >2.0) operate without dead zones
  4. CAC Payback thresholds (<12, 12-18, >18) operate without dead zones
  5. Valuation multiple tiers (<=20, 20-30, >30) operate without dead zones
"""

import os
import pytest
from deck_screener import PitchDeckScreener


def test_missing_data_disclosure_flags_and_memo():
    # Deck with completely blank claimed_metrics
    sparse_deck = {
        "company_name": "Ghost AI",
        "stage": "Seed",
        "claimed_metrics": {}
    }
    screener = PitchDeckScreener(sparse_deck)
    screener.compute_derived_metrics()
    screener.run_sanity_audits()
    
    # Missing metrics should not be given invented numbers
    assert screener.computed["arr"] is None
    assert screener.computed["cac"] is None
    assert screener.computed["monthly_churn"] is None
    assert screener.computed["gross_margin"] is None
    
    # Must emit a data disclosure gap flag
    data_gap_flags = [f for f in screener.flags if f.category == "Transparency & Data Gaps"]
    assert len(data_gap_flags) > 0

    # Verify memo does NOT label missing metrics as "Breached" or "Sluggish"
    temp_memo = "temp_memo_test.md"
    try:
        screener.generate_markdown_memo(temp_memo)
        with open(temp_memo, "r", encoding="utf-8") as f:
            content = f.read()
        assert "🚨 Breached" not in content
        assert "🚨 Sluggish" not in content
        assert "⚠️ Undisclosed (Data Gap)" in content
    finally:
        if os.path.exists(temp_memo):
            os.remove(temp_memo)


def test_cac_payback_deadzone_eliminated():
    deck_15mo = {
        "company_name": "MidPayback Co",
        "claimed_metrics": {
            "claimed_cac_usd": 1500.0,
            "claimed_arpu_monthly_usd": 125.0,
            "claimed_gross_margin_pct": 0.80, # 125 * 0.80 = $100/mo -> Payback = 15 months
            "claimed_tam_usd": 1e9,
            "target_customer_count_global": 10000
        }
    }
    s = PitchDeckScreener(deck_15mo)
    s.compute_derived_metrics()
    s.run_sanity_audits()
    
    payback_flags = [f for f in s.flags if f.category == "Sales Efficiency (CAC Payback)"]
    assert len(payback_flags) == 1
    assert payback_flags[0].severity == "YELLOW"


def test_burn_multiple_thresholds():
    deck_1_5x = {
        "company_name": "Growing Co",
        "claimed_metrics": {
            "monthly_net_burn_usd": 50000.0,  # $600k/yr
            "net_new_arr_last_12m_usd": 400000.0,  # Burn multiple = 600/400 = 1.5x
            "claimed_tam_usd": 1e9,
            "target_customer_count_global": 10000
        }
    }
    s = PitchDeckScreener(deck_1_5x)
    s.compute_derived_metrics()
    s.run_sanity_audits()
    
    burn_flags = [f for f in s.flags if f.category == "Capital Efficiency (Burn Multiple)"]
    assert len(burn_flags) == 1
    assert burn_flags[0].severity == "YELLOW"


def test_valuation_multiple_no_deadzones():
    # 25x multiple (in the middle tier 20x - 30x)
    deck_25x = {
        "company_name": "Premium Co",
        "claimed_post_money_valuation_usd": 25000000.0,
        "claimed_metrics": {
            "arr_usd": 1000000.0,  # 25x multiple
            "claimed_tam_usd": 1e9,
            "target_customer_count_global": 10000
        }
    }
    s = PitchDeckScreener(deck_25x)
    s.compute_derived_metrics()
    s.run_sanity_audits()
    
    val_flags = [f for f in s.flags if f.category == "Valuation Discipline"]
    assert len(val_flags) == 1
    assert val_flags[0].severity == "YELLOW"
