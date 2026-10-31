"""
Unit Test Suite for Cap Table & Liquidation Preference Waterfall Engine
Validates:
  1. 100% share and dilution conservation
  2. Conservation of capital (sum of payouts == exit valuation)
  3. No-sub-preference conversion invariant (investor never converts into < 1x preference)
  4. Specific benchmark cases ($40M, $50M, $70M, $100M, $200M)
  5. 400-Point Sweep Test ($1M to $400M) verifying zero unilateral regret / Nash stability
"""

import pytest
import numpy as np
from cap_table_waterfall import CapTableWaterfallEngine


@pytest.fixture
def engine():
    e = CapTableWaterfallEngine()
    e.build_standard_venture_cap_table()
    return e


def test_cap_table_dilution_sums_to_100(engine):
    total_pct = sum(h["ownership_pct"] for h in engine.cap_table)
    assert total_pct == pytest.approx(100.0, rel=1e-5)


def test_conservation_of_exit_proceeds(engine):
    test_exits = [5e6, 10e6, 25e6, 37.5e6, 40e6, 50e6, 70e6, 100e6, 250e6, 1000e6]
    for exit_val in test_exits:
        payouts = engine.calculate_exit_waterfall(exit_val, is_participating_preferred=False)
        total_payout = sum(p.proceeds_usd for p in payouts)
        assert total_payout == pytest.approx(exit_val, rel=1e-5), f"Failed conservation at ${exit_val/1e6}M"


def test_no_sub_preference_conversion_invariant(engine):
    """Critical VC Invariant: An investor never converts into less than their preference."""
    test_exits = [10e6, 25e6, 40e6, 50e6, 60e6, 70e6, 80e6, 100e6, 150e6, 500e6]
    for exit_val in test_exits:
        payouts = engine.calculate_exit_waterfall(exit_val, is_participating_preferred=False)
        for p in payouts:
            if p.invested_capital > 0:
                if exit_val >= engine.get_preference_stack_total():
                    assert p.proceeds_usd >= (p.invested_capital - 0.01), (
                        f"At ${exit_val/1e6}M exit, {p.name} received ${p.proceeds_usd/1e6}M (< ${p.invested_capital/1e6}M pref)!"
                    )


def test_400_point_nash_equilibrium_sweep(engine):
    """
    Independent 400-Point Sweep from $1M to $400M.
    Verifies that for every exit valuation, NO preferred investor has unilateral regret:
    Deviating from their conversion decision yields <= their current payout.
    """
    sweep_exits = np.linspace(1e6, 400e6, 400)
    preferred_names = [h["name"] for h in engine.cap_table if h["pref_multiple"] > 0]

    for exit_val in sweep_exits:
        payouts = engine.calculate_exit_waterfall(exit_val, is_participating_preferred=False)
        payout_map = {p.name: p for p in payouts}
        converting_set = {p.name for p in payouts if p.converted_to_common and p.invested_capital > 0}

        # 1. Total conservation
        assert sum(p.proceeds_usd for p in payouts) == pytest.approx(exit_val, rel=1e-5)

        # 2. Bilateral Unilateral Non-Regret Check
        for name in preferred_names:
            p_actual = payout_map[name].proceeds_usd

            if name in converting_set:
                # If converted: what if they deviated to preference?
                deviated_set = converting_set - {name}
                dev_payouts = engine._simulate_payout_for_state(exit_val, deviated_set)
                p_dev = dev_payouts[name]
                assert p_actual >= p_dev - 1e-4, (
                    f"Investor {name} has regret converting at ${exit_val/1e6:.2f}M: actual ${p_actual:,.0f} < dev ${p_dev:,.0f}"
                )
            else:
                # If taking preference: what if they deviated to converting?
                deviated_set = converting_set | {name}
                dev_payouts = engine._simulate_payout_for_state(exit_val, deviated_set)
                p_dev = dev_payouts[name]
                assert p_actual >= p_dev - 1e-4, (
                    f"Investor {name} has regret taking pref at ${exit_val/1e6:.2f}M: actual ${p_actual:,.0f} < dev ${p_dev:,.0f}"
                )


def test_specific_replicated_benchmarks(engine):
    # 1. $40M Exit: All preferred take 1.0x preference ($37.5M total stack), remaining $2.5M to Common
    p40 = {p.category: p for p in engine.calculate_exit_waterfall(40e6)}
    assert p40["Seed VC"].proceeds_usd == pytest.approx(2.5e6)
    assert p40["Seed VC"].moic == 1.0
    assert p40["Series A VC"].proceeds_usd == pytest.approx(10.0e6)
    assert p40["Series A VC"].moic == 1.0
    assert p40["Series B VC"].proceeds_usd == pytest.approx(25.0e6)
    assert p40["Series B VC"].moic == 1.0
    assert (p40["Founders"].proceeds_usd + p40["ESOP"].proceeds_usd) == pytest.approx(2.5e6)

    # 2. $50M Exit: Preferred stack is $37.5M. Seed share of ($50M - $35M) = 13.89% * $15M = $2.08M < $2.5M.
    p50 = {p.category: p for p in engine.calculate_exit_waterfall(50e6)}
    assert p50["Seed VC"].proceeds_usd == pytest.approx(2.5e6)
    assert p50["Seed VC"].moic == 1.0
    assert p50["Series A VC"].proceeds_usd == pytest.approx(10.0e6)
    assert p50["Series A VC"].moic == 1.0
    assert p50["Series B VC"].proceeds_usd == pytest.approx(25.0e6)
    assert p50["Series B VC"].moic == 1.0

    # 3. $70M Exit: Seed converts! Series A takes 1.0x preference ($10M) rather than converting to $9M!
    p70 = {p.category: p for p in engine.calculate_exit_waterfall(70e6)}
    assert p70["Series A VC"].proceeds_usd == pytest.approx(10.0e6)
    assert p70["Series A VC"].moic == 1.0
    assert p70["Series A VC"].converted_to_common is False
    assert p70["Seed VC"].converted_to_common is True
    assert p70["Seed VC"].proceeds_usd > 2.5e6

    # 4. $100M Exit: Both Seed and Series A convert. Series B takes 1x preference ($25M).
    p100 = {p.category: p for p in engine.calculate_exit_waterfall(100e6)}
    assert p100["Seed VC"].converted_to_common is True
    assert p100["Series A VC"].converted_to_common is True
    assert p100["Series B VC"].converted_to_common is False
    assert p100["Series B VC"].proceeds_usd == pytest.approx(25.0e6)


def test_participating_preferred_double_dipping(engine):
    """In participating preferred, preferred holders take 1x preference PLUS pro-rata common."""
    p100_part = {p.category: p for p in engine.calculate_exit_waterfall(100e6, is_participating_preferred=True)}
    p100_nonpart = {p.category: p for p in engine.calculate_exit_waterfall(100e6, is_participating_preferred=False)}
    
    assert p100_part["Series B VC"].proceeds_usd > p100_nonpart["Series B VC"].proceeds_usd
    assert p100_part["Founders"].proceeds_usd < p100_nonpart["Founders"].proceeds_usd
