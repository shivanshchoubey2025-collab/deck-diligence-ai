"""
Perturbation Isolation Test Suite for DeckDiligence.ai Screener.

Protocol:
- Start with a calibrated healthy baseline deck where all 6 audits pass with 100/100 score and 0 RED flags.
- Perturb exactly one input parameter at a time (e.g. 20x TAM, 90% margin on API wrapper, sluggish CAC, 3x burn, 3x valuation, removing CTO).
- Assert that strictly and exclusively the targeted audit category flips to RED, with all other 5 audits remaining intact.
- Proves audit orthogonality, absence of cross-contamination, and deterministic failure isolation.
"""

import copy
import json
import os
import pytest
from deck_screener import PitchDeckScreener


@pytest.fixture
def healthy_baseline_deck():
    """Returns a copy of CogniFlow AI calibrated to 100/100 health score with all 6 audits GREEN."""
    base_path = os.path.join(os.path.dirname(__file__), "sample_deck_cogniflow.json")
    with open(base_path, "r", encoding="utf-8") as f:
        deck = json.load(f)
    # Calibrate claimed TAM to $3.5B vs $1.73B bottom-up (2.0x disparity <= 4.0x -> GREEN)
    deck["claimed_metrics"]["claimed_tam_usd"] = 3500000000
    return deck


def _get_flag_categories_by_severity(screener: PitchDeckScreener, severity: str):
    return [f.category for f in screener.flags if f.severity == severity]


def test_baseline_healthy_deck_has_zero_red_flags(healthy_baseline_deck):
    s = PitchDeckScreener(healthy_baseline_deck)
    s.compute_derived_metrics()
    s.run_sanity_audits()

    assert s.health_score == 100
    assert s.audits_run_count == 6
    assert len(_get_flag_categories_by_severity(s, "RED")) == 0
    assert len(_get_flag_categories_by_severity(s, "YELLOW")) == 0
    assert len(_get_flag_categories_by_severity(s, "GREEN")) == 6


def test_tam_inflation_perturbation_isolates_market_sizing(healthy_baseline_deck):
    # Perturb claimed TAM by 20x ($3.5B -> $70B vs $1.73B bottom-up = 40.5x disparity)
    d = copy.deepcopy(healthy_baseline_deck)
    d["claimed_metrics"]["claimed_tam_usd"] = 70000000000

    s = PitchDeckScreener(d)
    s.compute_derived_metrics()
    s.run_sanity_audits()

    reds = _get_flag_categories_by_severity(s, "RED")
    assert reds == ["Market Sizing (TAM)"], f"Expected only TAM red flag, got {reds}"
    assert s.health_score == 80  # Baseline 100 - 20 pt penalty


def test_ai_wrapper_gross_margin_perturbation_isolates_gross_margin(healthy_baseline_deck):
    # Perturb: Rely 100% on third-party APIs with NO fine-tuned models while claiming 90% margin
    d = copy.deepcopy(healthy_baseline_deck)
    d["claimed_metrics"]["has_local_fine_tuned_models"] = False
    d["claimed_metrics"]["uses_third_party_llm_apis"] = True
    d["claimed_metrics"]["claimed_gross_margin_pct"] = 0.90

    s = PitchDeckScreener(d)
    s.compute_derived_metrics()
    s.run_sanity_audits()

    reds = _get_flag_categories_by_severity(s, "RED")
    assert reds == ["Unit Economics (Gross Margin)"], f"Expected only Gross Margin red flag, got {reds}"
    assert s.health_score == 80


def test_cac_payback_drag_perturbation_isolates_sales_efficiency(healthy_baseline_deck):
    # Perturb CAC from $4,800 to $25,000 (Payback = 25000 / (1200 * 0.91) = 22.9 months > 18 mo)
    d = copy.deepcopy(healthy_baseline_deck)
    d["claimed_metrics"]["claimed_cac_usd"] = 25000.0

    s = PitchDeckScreener(d)
    s.compute_derived_metrics()
    s.run_sanity_audits()

    reds = _get_flag_categories_by_severity(s, "RED")
    assert reds == ["Sales Efficiency (CAC Payback)"], f"Expected only CAC Payback red flag, got {reds}"
    assert s.health_score == 80


def test_excessive_burn_multiple_perturbation_isolates_capital_efficiency(healthy_baseline_deck):
    # Perturb monthly burn from $65k to $200k ($2.4M annual burn / $820k net new ARR = 2.93x > 2.0x)
    d = copy.deepcopy(healthy_baseline_deck)
    d["claimed_metrics"]["monthly_net_burn_usd"] = 200000.0

    s = PitchDeckScreener(d)
    s.compute_derived_metrics()
    s.run_sanity_audits()

    reds = _get_flag_categories_by_severity(s, "RED")
    assert reds == ["Capital Efficiency (Burn Multiple)"], f"Expected only Burn Multiple red flag, got {reds}"
    assert s.health_score == 85  # Baseline 100 - 15 pt penalty


def test_inflated_valuation_multiple_perturbation_isolates_valuation_discipline(healthy_baseline_deck):
    # Perturb post-money from $18M to $45M on $1.02M ARR (44.1x ARR multiple > 30x)
    d = copy.deepcopy(healthy_baseline_deck)
    d["claimed_post_money_valuation_usd"] = 45000000.0

    s = PitchDeckScreener(d)
    s.compute_derived_metrics()
    s.run_sanity_audits()

    reds = _get_flag_categories_by_severity(s, "RED")
    assert reds == ["Valuation Discipline"], f"Expected only Valuation red flag, got {reds}"
    assert s.health_score == 85  # Baseline 100 - 15 pt penalty


def test_non_technical_founder_in_deep_tech_isolates_team_composition(healthy_baseline_deck):
    # Perturb: Remove in-house technical leadership in AI infrastructure company
    d = copy.deepcopy(healthy_baseline_deck)
    d["team"] = [
        {"name": "Aarav Sharma", "role": "CEO & Co-Founder", "background": "Ex-Strategy Consultant; MBA (Wharton)."}
    ]

    s = PitchDeckScreener(d)
    s.compute_derived_metrics()
    s.run_sanity_audits()

    reds = _get_flag_categories_by_severity(s, "RED")
    assert reds == ["Team Composition"], f"Expected only Team Composition red flag, got {reds}"
    assert s.health_score == 80
