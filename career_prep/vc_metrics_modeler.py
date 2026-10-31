"""
========================================================================================
VENTURE CAPITAL (VC) METRICS & FUND RETURN MODELER
----------------------------------------------------------------------------------------
Purpose: Institutional toolkit for evaluating tech startups and fund-level returns.
Designed for: CSE -> Venture Capital (VC) Analyst / Associate Transition.
========================================================================================
Covers:
  1. SaaS / Tech Unit Economics (CAC, LTV, CAC Payback, Net Retention, Rule of 40)
  2. Capital Efficiency & Burn Multiple (David Sacks / Craft Ventures Benchmark)
  3. Cap Table & Ownership Dilution Modeling across Seed -> Series A -> Series B
  4. The VC "Power Law" Fund Return Math (Calculating exit valuation needed to return fund)
========================================================================================
"""

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class StartupMetrics:
    startup_name: str
    mrr_usd: float              # Monthly Recurring Revenue ($)
    arr_usd: float              # Annual Recurring Revenue ($)
    net_new_arr_ttm: float      # Net New ARR added in last 12 months
    gross_margin_pct: float     # e.g., 0.78 for 78%
    monthly_churn_pct: float    # e.g., 0.015 for 1.5%
    cac_usd: float              # Customer Acquisition Cost ($)
    arpu_monthly_usd: float     # Average Revenue Per User / Account per month
    gross_burn_monthly: float   # Monthly cash spent
    net_burn_monthly: float     # Monthly cash burn (Spend - Revenue)
    cash_in_bank_usd: float     # Current bank balance
    expansion_arr_pct: float    # Expansion revenue from existing customers (e.g., 0.20 for 20%)


class VCMetricsEvaluator:
    def __init__(self, metrics: StartupMetrics):
        self.m = metrics

    def calculate_unit_economics(self) -> Dict[str, float]:
        """Calculates core venture capital SaaS metrics."""
        # Customer Lifetime (Months) = 1 / Churn Rate
        customer_lifetime_months = 1.0 / self.m.monthly_churn_pct if self.m.monthly_churn_pct > 0 else 100.0

        # LTV = ARPU * Gross Margin * Customer Lifetime
        ltv_usd = self.m.arpu_monthly_usd * self.m.gross_margin_pct * customer_lifetime_months

        # LTV:CAC Ratio (Benchmark: >3.0x is great, >5.0x is world-class)
        ltv_cac_ratio = ltv_usd / self.m.cac_usd if self.m.cac_usd > 0 else 0.0

        # CAC Payback Period (Months) = CAC / (ARPU * Gross Margin)
        monthly_gross_profit_per_user = self.m.arpu_monthly_usd * self.m.gross_margin_pct
        cac_payback_months = self.m.cac_usd / monthly_gross_profit_per_user if monthly_gross_profit_per_user > 0 else 0.0

        # Net Dollar Retention (NDR) ~ 100% - Churn + Expansion
        ndr_pct = (1.0 - (self.m.monthly_churn_pct * 12.0) + self.m.expansion_arr_pct) * 100.0

        # Burn Multiple = Net Burn / Net New ARR (Craft Ventures metric)
        # Benchmark: < 1.0x is Amazing, 1.0x - 1.5x is Good, > 2.0x is Suspect
        annual_net_burn = self.m.net_burn_monthly * 12.0
        burn_multiple = annual_net_burn / self.m.net_new_arr_ttm if self.m.net_new_arr_ttm > 0 else float('inf')

        # Runway in Months
        runway_months = self.m.cash_in_bank_usd / self.m.net_burn_monthly if self.m.net_burn_monthly > 0 else 999.0

        # Rule of 40: YoY Growth Rate % + Free Cash Flow Margin %
        # Simplified: YoY ARR Growth % - (Net Burn % of Revenue)
        yoy_growth_pct = (self.m.net_new_arr_ttm / max(1.0, (self.m.arr_usd - self.m.net_new_arr_ttm))) * 100.0
        fcf_margin_pct = -(self.m.net_burn_monthly / max(1.0, self.m.mrr_usd)) * 100.0
        rule_of_40_score = yoy_growth_pct + fcf_margin_pct

        return {
            "ltv_usd": ltv_usd,
            "ltv_cac_ratio": ltv_cac_ratio,
            "cac_payback_months": cac_payback_months,
            "ndr_pct": ndr_pct,
            "burn_multiple": burn_multiple,
            "runway_months": runway_months,
            "yoy_growth_pct": yoy_growth_pct,
            "rule_of_40_score": rule_of_40_score
        }

    def print_teardown(self):
        res = self.calculate_unit_economics()
        print("=" * 80)
        print(f" VC INVESTMENT TEARDOWN & UNIT ECONOMICS: {self.m.startup_name}")
        print("=" * 80)
        print(f" ARR: ${self.m.arr_usd:,.0f} | MRR: ${self.m.mrr_usd:,.0f} | Gross Margin: {self.m.gross_margin_pct*100:.1f}%")
        print(f" Monthly Net Burn: ${self.m.net_burn_monthly:,.0f} | Runway: {res['runway_months']:.1f} Months")
        print("-" * 80)
        print(f"{'Metric':<30} {'Value':<18} {'VC Benchmark':<20} {'Status'}")
        print("-" * 80)

        # LTV:CAC check
        status_ltv = "ELITE" if res["ltv_cac_ratio"] >= 4.0 else ("HEALTHY" if res["ltv_cac_ratio"] >= 3.0 else "POOR")
        print(f"{'LTV : CAC Ratio':<30} {res['ltv_cac_ratio']:.2f}x{'':<13} {'> 3.0x':<20} {status_ltv}")

        # CAC Payback
        status_payback = "ELITE" if res["cac_payback_months"] <= 12.0 else ("HEALTHY" if res["cac_payback_months"] <= 18.0 else "SLOW")
        print(f"{'CAC Payback Period':<30} {res['cac_payback_months']:.1f} Months{'':<7} {'< 12 Months':<20} {status_payback}")

        # NDR
        status_ndr = "ELITE" if res["ndr_pct"] >= 120.0 else ("HEALTHY" if res["ndr_pct"] >= 105.0 else "LEAKY")
        print(f"{'Net Dollar Retention (NDR)':<30} {res['ndr_pct']:.1f}%{'':<12} {'> 115%':<20} {status_ndr}")

        # Burn Multiple
        status_burn = "ELITE" if res["burn_multiple"] <= 1.0 else ("HEALTHY" if res["burn_multiple"] <= 1.5 else "HIGH BURN")
        print(f"{'Burn Multiple':<30} {res['burn_multiple']:.2f}x{'':<13} {'< 1.2x':<20} {status_burn}")

        # Rule of 40
        status_r40 = "TOP TIER" if res["rule_of_40_score"] >= 40.0 else "SUB-PAR"
        print(f"{'Rule of 40 Score':<30} {res['rule_of_40_score']:.1f}%{'':<12} {'> 40.0%':<20} {status_r40}")
        print("=" * 80)


def calculate_fund_return_math(fund_size_usd=100_000_000, initial_check_usd=2_000_000, entry_post_money_usd=12_000_000):
    """
    Simulates VC Power Law:
    Calculates how much an investment must exit for to return 1x or 3x the entire fund,
    accounting for subsequent round dilution (e.g. 20% in Series A, 15% in Series B).
    """
    initial_ownership = initial_check_usd / entry_post_money_usd  # e.g., 16.67%
    # Typical dilution: 20% in Series A, 15% in Series B, 10% ESOP expansion
    dilution_factor = (1 - 0.20) * (1 - 0.15) * (1 - 0.10)
    ownership_at_exit = initial_ownership * dilution_factor

    exit_for_1x_fund = fund_size_usd / ownership_at_exit
    exit_for_3x_fund = (fund_size_usd * 3) / ownership_at_exit

    print("\n" + "=" * 80)
    print(f" VC FUND RETURN POWER LAW ANALYSIS (Fund Size: ${fund_size_usd/1e6:.1f}M)")
    print("=" * 80)
    print(f" Initial Check: ${initial_check_usd/1e6:.2f}M at ${entry_post_money_usd/1e6:.1f}M Post-Money Valuation")
    print(f" Initial Ownership: {initial_ownership*100:.2f}% | Diluted Ownership at Exit: {ownership_at_exit*100:.2f}%")
    print("-" * 80)
    print(f" Required Exit Valuation to return 1x of the ENTIRE Fund (${fund_size_usd/1e6:.0f}M): ${exit_for_1x_fund/1e6:,.1f} Million")
    print(f" Required Exit Valuation to return 3x of the ENTIRE Fund (${fund_size_usd*3/1e6:.0f}M): ${exit_for_3x_fund/1e6:,.1f} Million")
    print("=" * 80)
    print(" INSIGHT: This is why VCs reject 95% of 'good' small businesses.")
    print(" In a $100M fund, an investment MUST have a realistic shot at an exit of >$800M+ to move the needle!")
    print("=" * 80)


if __name__ == "__main__":
    # Benchmark: Fast-growing Indian B2B AI / Developer Tooling Startup
    sample_startup = StartupMetrics(
        startup_name="KubeDeploy.ai (Sample Series A Indian Tech Deal)",
        mrr_usd=185_000.0,
        arr_usd=2_220_000.0,
        net_new_arr_ttm=1_420_000.0,
        gross_margin_pct=0.82,          # 82% software gross margins
        monthly_churn_pct=0.008,        # 0.8% monthly logo churn (very sticky)
        cac_usd=4_200.0,
        arpu_monthly_usd=1_150.0,
        gross_burn_monthly=165_000.0,
        net_burn_monthly=85_000.0,
        cash_in_bank_usd=2_100_000.0,
        expansion_arr_pct=0.28          # 28% expansion via usage-based pricing
    )

    evaluator = VCMetricsEvaluator(sample_startup)
    evaluator.print_teardown()
    calculate_fund_return_math(fund_size_usd=100_000_000, initial_check_usd=2_500_000, entry_post_money_usd=15_000_000)
