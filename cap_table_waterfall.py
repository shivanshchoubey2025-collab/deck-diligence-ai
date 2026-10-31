"""
========================================================================================
CAP TABLE DILUTION & LIQUIDATION PREFERENCE EXIT WATERFALL ENGINE
----------------------------------------------------------------------------------------
Target: Tier-1 Venture Capital (VC) Investment Committees (Peak XV, Founders Fund, Accel)
Purpose: Models round-by-round cap table dilution (Founders -> Seed -> Series A -> Series B)
         and executes an institutional Liquidation Preference Exit Waterfall ($5M to $1B).
========================================================================================
Mechanics Covered:
  1. Multi-Round Share Ledger & Cap Table Dilution Progression
  2. Pre-Money & Post-Money Option Pool (ESOP) Shuffle Calculations
  3. 1x Non-Participating Preferred Stock (Market Standard) with Crossover Conversion Points
  4. Participating Preferred ("Double Dipping") Contingency Modeling
  5. Exit Waterfall Proceeds Distribution & Multiple on Invested Capital (MoIC) across exits
========================================================================================
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional


@dataclass
class RoundDetails:
    round_name: str
    capital_invested_usd: float
    post_money_valuation_usd: float
    esop_target_pct: float = 0.10  # 10% unallocated ESOP pool target
    liquidation_multiple: float = 1.0
    is_participating: bool = False


@dataclass
class ShareholderPayout:
    name: str
    category: str  # "Common / Founders", "Seed VC", "Series A VC", "Series B VC", "ESOP"
    invested_capital: float
    shares: float
    ownership_pct: float
    proceeds_usd: float
    moic: float  # Multiple on Invested Capital (Proceeds / Capital Invested)
    converted_to_common: bool


class CapTableWaterfallEngine:
    def __init__(self, initial_founder_shares: float = 10_000_000.0):
        self.initial_founder_shares = initial_founder_shares
        self.cap_table: List[Dict] = []
        self.total_shares: float = initial_founder_shares
        self.share_price: float = 1.0

    def build_standard_venture_cap_table(
        self,
        seed_capital: float = 2_500_000.0,
        seed_post_val: float = 18_000_000.0,
        series_a_capital: float = 10_000_000.0,
        series_a_post_val: float = 50_000_000.0,
        series_b_capital: float = 25_000_000.0,
        series_b_post_val: float = 150_000_000.0,
    ) -> List[Dict]:
        """
        Builds a canonical 4-stage institutional venture cap table:
        1. Inception: Founders (10M shares, 100%)
        2. Seed Round: $2.5M at $18.0M Post-Money (10% ESOP created)
        3. Series A: $10.0M at $50.0M Post-Money (20% dilution + ESOP refresh)
        4. Series B: $25.0M at $150.0M Post-Money (16.7% dilution)
        """
        # 1. Inception
        founder_shares = self.initial_founder_shares
        
        # 2. Seed Round ($2.5M on $18M Post-Money -> 13.89% ownership)
        seed_ownership = seed_capital / seed_post_val
        esop_seed_pct = 0.10
        common_seed_pct = 1.0 - seed_ownership - esop_seed_pct
        
        # Scaling shares so founder shares equal common_seed_pct
        total_seed_shares = founder_shares / common_seed_pct
        seed_shares = total_seed_shares * seed_ownership
        esop_shares = total_seed_shares * esop_seed_pct
        
        # 3. Series A Round ($10M on $50M Post-Money -> 20.0% ownership)
        series_a_ownership = series_a_capital / series_a_post_val
        post_series_a_shares = (total_seed_shares) / (1.0 - series_a_ownership)
        series_a_shares = post_series_a_shares * series_a_ownership
        
        # 4. Series B Round ($25M on $150M Post-Money -> 16.67% ownership)
        series_b_ownership = series_b_capital / series_b_post_val
        total_post_b_shares = post_series_a_shares / (1.0 - series_b_ownership)
        series_b_shares = total_post_b_shares * series_b_ownership

        self.total_shares = total_post_b_shares
        self.share_price = series_b_post_val / self.total_shares

        # Compile Fully-Diluted Cap Table Ledger
        self.cap_table = [
            {
                "name": "Founding Team (Common)",
                "category": "Founders",
                "shares": founder_shares,
                "ownership_pct": (founder_shares / self.total_shares) * 100.0,
                "invested_capital": 0.0,
                "seniority": 4,  # Common is junior
                "pref_multiple": 0.0
            },
            {
                "name": "Employee Option Pool (ESOP)",
                "category": "ESOP",
                "shares": esop_shares,
                "ownership_pct": (esop_shares / self.total_shares) * 100.0,
                "invested_capital": 0.0,
                "seniority": 4,
                "pref_multiple": 0.0
            },
            {
                "name": "Seed Investors (Preferred)",
                "category": "Seed VC",
                "shares": seed_shares,
                "ownership_pct": (seed_shares / self.total_shares) * 100.0,
                "invested_capital": seed_capital,
                "seniority": 3,
                "pref_multiple": 1.0
            },
            {
                "name": "Series A Lead VC (Preferred)",
                "category": "Series A VC",
                "shares": series_a_shares,
                "ownership_pct": (series_a_shares / self.total_shares) * 100.0,
                "invested_capital": series_a_capital,
                "seniority": 2,
                "pref_multiple": 1.0
            },
            {
                "name": "Series B Growth VC (Preferred)",
                "category": "Series B VC",
                "shares": series_b_shares,
                "ownership_pct": (series_b_shares / self.total_shares) * 100.0,
                "invested_capital": series_b_capital,
                "seniority": 1,  # Senior-most
                "pref_multiple": 1.0
            }
        ]
        return self.cap_table

    def calculate_exit_waterfall(
        self,
        exit_valuation_usd: float,
        is_participating_preferred: bool = False
    ) -> List[ShareholderPayout]:
        """
        Executes a Tier-1 Liquidation Preference Exit Waterfall:
        - Seniority: Series B > Series A > Seed > Common
        - 1x Non-Participating: Investor takes MAX(1x Preference, Pro-Rata Common Share)
        - Participating: Investor takes 1x Preference + Pro-Rata of Remaining Proceeds
        """
        if not self.cap_table:
            self.build_standard_venture_cap_table()

        total_preferred_capital = sum(
            holder["invested_capital"] for holder in self.cap_table if holder["pref_multiple"] > 0
        )

        payouts: List[ShareholderPayout] = []

        if not is_participating_preferred:
            # -----------------------------------------------------------------
            # 1X NON-PARTICIPATING PREFERRED (TIER-1 STANDARD)
            # -----------------------------------------------------------------
            # Each preferred investor checks: Is Pro-Rata Ownership % * Exit > Invested Capital?
            # If Yes -> Convert to Common
            # If No -> Exercise 1x Liquidation Preference
            
            # Step 1: Identify who converts
            converting_holders = set()
            for holder in self.cap_table:
                if holder["pref_multiple"] > 0:
                    pro_rata_value = (holder["ownership_pct"] / 100.0) * exit_valuation_usd
                    if pro_rata_value >= holder["invested_capital"]:
                        converting_holders.add(holder["name"])

            # If all preferred investors convert to common (High Exit valuation)
            all_preferred_names = {h["name"] for h in self.cap_table if h["pref_multiple"] > 0}
            if converting_holders == all_preferred_names:
                for holder in self.cap_table:
                    proceeds = (holder["ownership_pct"] / 100.0) * exit_valuation_usd
                    moic = (proceeds / holder["invested_capital"]) if holder["invested_capital"] > 0 else 0.0
                    payouts.append(ShareholderPayout(
                        name=holder["name"],
                        category=holder["category"],
                        invested_capital=holder["invested_capital"],
                        shares=holder["shares"],
                        ownership_pct=holder["ownership_pct"],
                        proceeds_usd=proceeds,
                        moic=round(moic, 2),
                        converted_to_common=True
                    ))
                return payouts

            # Step 2: Waterfall with Seniority Tranches (Series B -> Series A -> Seed)
            remaining_cash = exit_valuation_usd
            temp_payouts: Dict[str, float] = {h["name"]: 0.0 for h in self.cap_table}
            has_converted: Dict[str, bool] = {h["name"]: False for h in self.cap_table}

            # Senior Preferred Payouts (Non-converting take 1x preference)
            # Sort by seniority (1 is highest)
            preferred_sorted = sorted(
                [h for h in self.cap_table if h["pref_multiple"] > 0],
                key=lambda x: x["seniority"]
            )

            for pref in preferred_sorted:
                if pref["name"] in converting_holders:
                    has_converted[pref["name"]] = True
                    continue  # Will take from common pool later

                # Takes 1x Liquidation Preference up to remaining cash
                pref_amount = min(remaining_cash, pref["invested_capital"])
                temp_payouts[pref["name"]] = pref_amount
                remaining_cash -= pref_amount

            # Remaining cash is distributed pro-rata among Common + Converting Preferred
            converting_and_common_shares = sum(
                h["shares"] for h in self.cap_table if (h["name"] in converting_holders or h["pref_multiple"] == 0)
            )

            if converting_and_common_shares > 0 and remaining_cash > 0:
                for h in self.cap_table:
                    if h["name"] in converting_holders or h["pref_multiple"] == 0:
                        share_of_pool = (h["shares"] / converting_and_common_shares) * remaining_cash
                        temp_payouts[h["name"]] += share_of_pool
                        if h["name"] in converting_holders:
                            has_converted[h["name"]] = True

            for h in self.cap_table:
                proceeds = temp_payouts[h["name"]]
                moic = (proceeds / h["invested_capital"]) if h["invested_capital"] > 0 else 0.0
                payouts.append(ShareholderPayout(
                    name=h["name"],
                    category=h["category"],
                    invested_capital=h["invested_capital"],
                    shares=h["shares"],
                    ownership_pct=h["ownership_pct"],
                    proceeds_usd=proceeds,
                    moic=round(moic, 2),
                    converted_to_common=has_converted[h["name"]]
                ))

        else:
            # -----------------------------------------------------------------
            # PARTICIPATING PREFERRED ("DOUBLE DIPPING" INVESTOR FRIENDLY)
            # -----------------------------------------------------------------
            remaining_cash = exit_valuation_usd
            temp_payouts = {h["name"]: 0.0 for h in self.cap_table}

            # 1. First satisfy all 1x liquidation preferences
            for h in sorted([h for h in self.cap_table if h["pref_multiple"] > 0], key=lambda x: x["seniority"]):
                pref = min(remaining_cash, h["invested_capital"])
                temp_payouts[h["name"]] += pref
                remaining_cash -= pref

            # 2. Then all holders share pro-rata in remaining cash
            if remaining_cash > 0:
                for h in self.cap_table:
                    pro_rata_share = (h["ownership_pct"] / 100.0) * remaining_cash
                    temp_payouts[h["name"]] += pro_rata_share

            for h in self.cap_table:
                proceeds = temp_payouts[h["name"]]
                moic = (proceeds / h["invested_capital"]) if h["invested_capital"] > 0 else 0.0
                payouts.append(ShareholderPayout(
                    name=h["name"],
                    category=h["category"],
                    invested_capital=h["invested_capital"],
                    shares=h["shares"],
                    ownership_pct=h["ownership_pct"],
                    proceeds_usd=proceeds,
                    moic=round(moic, 2),
                    converted_to_common=False
                ))

        return payouts

    def get_preference_stack_total(self) -> float:
        """Returns the aggregate liquidation preference amount required before common sees $1."""
        if not self.cap_table:
            self.build_standard_venture_cap_table()
        return sum(h["invested_capital"] for h in self.cap_table if h["pref_multiple"] > 0)

    def get_crossover_hurdles(self) -> List[Dict]:
        """
        Calculates the conversion crossover exit valuation for each preferred class.
        Crossover Exit = Invested Capital / Ownership Fraction.
        At valuations above this hurdle, the investor earns more by converting to Common.
        """
        if not self.cap_table:
            self.build_standard_venture_cap_table()

        hurdles = []
        for h in self.cap_table:
            if h["pref_multiple"] > 0 and h["ownership_pct"] > 0:
                crossover_val = h["invested_capital"] / (h["ownership_pct"] / 100.0)
                hurdles.append({
                    "class_name": h["name"],
                    "category": h["category"],
                    "invested_capital": h["invested_capital"],
                    "ownership_pct": h["ownership_pct"],
                    "crossover_exit_valuation": crossover_val,
                    "seniority": h["seniority"]
                })
        hurdles.sort(key=lambda x: x["seniority"])
        return hurdles

    def run_multi_exit_matrix(
        self,
        exit_scenarios: Optional[List[float]] = None
    ) -> List[Dict]:
        """Runs the waterfall across a spectrum of exit values ($10M to $1 Billion)."""
        if exit_scenarios is None:
            exit_scenarios = [
                10_000_000, 25_000_000, 50_000_000, 100_000_000,
                200_000_000, 350_000_000, 500_000_000, 1_000_000_000
            ]

        results = []
        for exit_val in exit_scenarios:
            payouts = self.calculate_exit_waterfall(exit_val)
            row = {"exit_valuation": exit_val}
            for p in payouts:
                row[f"{p.category}_proceeds"] = p.proceeds_usd
                row[f"{p.category}_moic"] = p.moic
            results.append(row)
        return results

    def print_terminal_waterfall_summary(self, sample_exit_usd: float = 100_000_000.0):
        if not self.cap_table:
            self.build_standard_venture_cap_table()

        payouts = self.calculate_exit_waterfall(sample_exit_usd)

        print("=" * 84)
        print(f" TIER-1 VC CAP TABLE & EXIT WATERFALL SIMULATOR (Exit: ${sample_exit_usd/1e6:.1f}M)")
        print("=" * 84)
        print(f"{'Shareholder Group':<32} {'Ownership':<12} {'Invested':<14} {'Payout ($M)':<14} {'MoIC':<8}")
        print("-" * 84)
        for p in payouts:
            status = " [Converted]" if p.converted_to_common else ""
            moic_str = f"{p.moic:.2f}x" if p.invested_capital > 0 else "N/A"
            print(f"{p.name + status:<32} {p.ownership_pct:>6.2f}%      ${p.invested_capital/1e6:>5.2f}M       ${p.proceeds_usd/1e6:>6.2f}M       {moic_str:>6}")
        print("=" * 84)

        print("\n--- MULTI-EXIT SCENARIO MATRIX (Proceeds & Multiple on Invested Capital) ---")
        matrix = self.run_multi_exit_matrix()
        print(f"{'Exit Val':<12} {'Founders':<14} {'Seed VC (MoIC)':<18} {'Series A (MoIC)':<18} {'Series B (MoIC)'}")
        print("-" * 84)
        for r in matrix:
            exit_m = f"${r['exit_valuation']/1e6:.0f}M"
            f_payout = f"${r.get('Founders_proceeds',0)/1e6:.1f}M"
            seed_res = f"${r.get('Seed VC_proceeds',0)/1e6:.1f}M ({r.get('Seed VC_moic',0):.1f}x)"
            a_res = f"${r.get('Series A VC_proceeds',0)/1e6:.1f}M ({r.get('Series A VC_moic',0):.1f}x)"
            b_res = f"${r.get('Series B VC_proceeds',0)/1e6:.1f}M ({r.get('Series B VC_moic',0):.1f}x)"
            print(f"{exit_m:<12} {f_payout:<14} {seed_res:<18} {a_res:<18} {b_res}")
        print("=" * 84)


if __name__ == "__main__":
    engine = CapTableWaterfallEngine()
    engine.build_standard_venture_cap_table()
    engine.print_terminal_waterfall_summary(sample_exit_usd=100_000_000.0)
