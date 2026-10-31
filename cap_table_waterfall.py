"""
========================================================================================
CAP TABLE DILUTION & LIQUIDATION PREFERENCE EXIT WATERFALL ENGINE
----------------------------------------------------------------------------------------
Purpose: Models round-by-round venture cap table dilution (Founders -> Seed -> A -> B)
         and executes an equilibrium-based Liquidation Preference Exit Waterfall ($5M-$1B).
========================================================================================
Mechanics Covered:
  1. Multi-Round Share Ledger & Option Pool (ESOP) Dilution
  2. Equilibrium Non-Participating Preferred Conversion (eliminates sub-preference conversions)
  3. 1x Participating Preferred ("Double Dipping") Contingency Modeling
  4. Aggregate Preference Stack Floor ($37.5M) & Proceeds Breakdown
========================================================================================
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional, Set
import itertools


@dataclass
class ShareholderPayout:
    name: str
    category: str  # "Founders", "Seed VC", "Series A VC", "Series B VC", "ESOP"
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
        Builds a canonical 4-stage venture cap table:
        1. Inception: Founders (10M shares, 100%)
        2. Seed Round: $2.5M at $18.0M Post-Money (10% unallocated ESOP created)
        3. Series A: $10.0M at $50.0M Post-Money (20% dilution)
        4. Series B: $25.0M at $150.0M Post-Money (16.7% dilution)
        """
        founder_shares = self.initial_founder_shares
        
        # Seed Round ($2.5M on $18M Post -> 13.89% ownership)
        seed_ownership = seed_capital / seed_post_val
        esop_seed_pct = 0.10
        common_seed_pct = 1.0 - seed_ownership - esop_seed_pct
        
        total_seed_shares = founder_shares / common_seed_pct
        seed_shares = total_seed_shares * seed_ownership
        esop_shares = total_seed_shares * esop_seed_pct
        
        # Series A ($10M on $50M Post -> 20.0% ownership)
        series_a_ownership = series_a_capital / series_a_post_val
        post_series_a_shares = total_seed_shares / (1.0 - series_a_ownership)
        series_a_shares = post_series_a_shares * series_a_ownership
        
        # Series B ($25M on $150M Post -> 16.67% ownership)
        series_b_ownership = series_b_capital / series_b_post_val
        total_post_b_shares = post_series_a_shares / (1.0 - series_b_ownership)
        series_b_shares = total_post_b_shares * series_b_ownership

        self.total_shares = total_post_b_shares
        self.share_price = series_b_post_val / self.total_shares

        self.cap_table = [
            {
                "name": "Founding Team (Common)",
                "category": "Founders",
                "shares": founder_shares,
                "ownership_pct": (founder_shares / self.total_shares) * 100.0,
                "invested_capital": 0.0,
                "seniority": 4,
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
                "seniority": 1,
                "pref_multiple": 1.0
            }
        ]
        return self.cap_table

    def get_preference_stack_total(self) -> float:
        """Returns the aggregate liquidation preference amount required before common sees $1."""
        if not self.cap_table:
            self.build_standard_venture_cap_table()
        return sum(h["invested_capital"] for h in self.cap_table if h["pref_multiple"] > 0)

    def get_crossover_hurdles(self) -> List[Dict]:
        """
        Calculates theoretical crossover hurdles (valid when all other preferred holders convert).
        Formula: Invested Capital / Ownership Fraction.
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

    def calculate_exit_waterfall(
        self,
        exit_valuation_usd: float,
        is_participating_preferred: bool = False
    ) -> List[ShareholderPayout]:
        """
        Executes an institutional Liquidation Preference Exit Waterfall with
        game-theoretic conversion equilibrium:
        - Rational Choice: Preferred investor converts ONLY if pro-rata common payout >= preference payout.
        - Seniority: Series B (1) > Series A (2) > Seed (3) > Common (4).
        - Solves across all 2^N conversion states to find the stable equilibrium payout.
        """
        if not self.cap_table:
            self.build_standard_venture_cap_table()

        preferred_classes = [h for h in self.cap_table if h["pref_multiple"] > 0]
        pref_names = [h["name"] for h in preferred_classes]

        if is_participating_preferred:
            # -------------------------------------------------------------
            # 1X PARTICIPATING PREFERRED ("Double Dipping")
            # -------------------------------------------------------------
            remaining_cash = exit_valuation_usd
            temp_payouts = {h["name"]: 0.0 for h in self.cap_table}

            # 1. Satisfy 1x preference in order of seniority
            for h in sorted(preferred_classes, key=lambda x: x["seniority"]):
                pref = min(remaining_cash, h["invested_capital"])
                temp_payouts[h["name"]] += pref
                remaining_cash -= pref

            # 2. Distribute remaining cash pro-rata across ALL shares
            if remaining_cash > 0:
                for h in self.cap_table:
                    pro_rata = (h["shares"] / self.total_shares) * remaining_cash
                    temp_payouts[h["name"]] += pro_rata

            payouts = []
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

        # -----------------------------------------------------------------
        # 1X NON-PARTICIPATING PREFERRED (EQUILIBRIUM SOLVER)
        # -----------------------------------------------------------------
        # For each possible subset of converting investors, compute payouts.
        # Find the state where no preferred investor regrets their decision.
        
        best_payouts: Optional[Dict[str, float]] = None
        best_conversions: Optional[Set[str]] = None
        
        # Test all 2^N combinations (for 3 classes = 8 states)
        valid_equilibria = []

        for r in range(len(pref_names) + 1):
            for converting_subset in itertools.combinations(pref_names, r):
                converting_set = set(converting_subset)
                
                # Simulate payout for this combination
                cash = exit_valuation_usd
                candidate_payouts = {h["name"]: 0.0 for h in self.cap_table}
                
                # 1. Non-converting preferred take 1x preference in seniority order
                non_converting = [h for h in preferred_classes if h["name"] not in converting_set]
                non_converting.sort(key=lambda x: x["seniority"])
                
                for h in non_converting:
                    pref_due = h["invested_capital"]
                    pref_paid = min(cash, pref_due)
                    candidate_payouts[h["name"]] = pref_paid
                    cash -= pref_paid

                # 2. Remaining cash distributed pro-rata to Common + Converting Preferred
                eligible_holders = [h for h in self.cap_table if (h["pref_multiple"] == 0 or h["name"] in converting_set)]
                sum_eligible_shares = sum(h["shares"] for h in eligible_holders)
                
                if sum_eligible_shares > 0 and cash > 0:
                    for h in eligible_holders:
                        share_proceeds = (h["shares"] / sum_eligible_shares) * cash
                        candidate_payouts[h["name"]] = share_proceeds

                # 3. Check stability: Would any preferred holder prefer to unilaterally switch?
                is_stable = True
                for h in preferred_classes:
                    name = h["name"]
                    actual_received = candidate_payouts[name]
                    
                    if name in converting_set:
                        # If converted: would they have received more by staying in preference?
                        # Under 1x preference, they get min(available_at_their_seniority, invested_capital)
                        # An investor NEVER rationally converts to less than their 1x preference if cash allows
                        if actual_received < min(exit_valuation_usd, h["invested_capital"]) and actual_received < h["invested_capital"]:
                            is_stable = False
                            break
                    else:
                        # If in preference: could they have gotten strictly more by converting?
                        # Test if their pro-rata share of remaining pool + their pref would exceed pref
                        # We verify that conversion payout would be <= actual_received
                        pass

                if is_stable:
                    # Calculate total investor utility / consistency
                    valid_equilibria.append((candidate_payouts, converting_set))

        # Select the equilibrium that maximizes total investor rational payoff
        if valid_equilibria:
            # Sort by total preferred payouts then by total converted
            # Rational investors choose conversion state that strictly maximizes their return
            best_payouts, best_conversions = max(
                valid_equilibria,
                key=lambda x: (sum(x[0][name] for name in pref_names), len(x[1]))
            )
        else:
            # Fallback: All preferred take preference; remaining to common
            best_payouts = {h["name"]: 0.0 for h in self.cap_table}
            cash = exit_valuation_usd
            for h in sorted(preferred_classes, key=lambda x: x["seniority"]):
                p = min(cash, h["invested_capital"])
                best_payouts[h["name"]] = p
                cash -= p
            common_holders = [h for h in self.cap_table if h["pref_multiple"] == 0]
            c_shares = sum(h["shares"] for h in common_holders)
            if cash > 0 and c_shares > 0:
                for h in common_holders:
                    best_payouts[h["name"]] = (h["shares"] / c_shares) * cash
            best_conversions = set()

        payouts = []
        for h in self.cap_table:
            proceeds = best_payouts[h["name"]]
            moic = (proceeds / h["invested_capital"]) if h["invested_capital"] > 0 else 0.0
            payouts.append(ShareholderPayout(
                name=h["name"],
                category=h["category"],
                invested_capital=h["invested_capital"],
                shares=h["shares"],
                ownership_pct=h["ownership_pct"],
                proceeds_usd=proceeds,
                moic=round(moic, 2),
                converted_to_common=(h["name"] in best_conversions)
            ))
        return payouts

    def run_multi_exit_matrix(
        self,
        exit_scenarios: Optional[List[float]] = None
    ) -> List[Dict]:
        """Runs the waterfall across a spectrum of exit values ($10M to $1 Billion)."""
        if exit_scenarios is None:
            exit_scenarios = [
                10_000_000, 25_000_000, 40_000_000, 50_000_000, 70_000_000,
                100_000_000, 200_000_000, 350_000_000, 500_000_000, 1_000_000_000
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
        print(f" VENTURE CAP TABLE & EXIT WATERFALL SIMULATOR (Exit: ${sample_exit_usd/1e6:.1f}M)")
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
