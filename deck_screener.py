"""
========================================================================================
DECKDILIGENCE.AI — AI PITCH DECK SCREENER & DILIGENCE COPILOT
----------------------------------------------------------------------------------------
Purpose: Automated quantitative screening and "bullshit detection" for VC pitch decks.
Target Role: Venture Capital (VC) Analyst / Associate
Framework: NYU Stern, Y Combinator, and Craft Ventures (David Sacks) SaaS Benchmarks
========================================================================================
Features:
  1. Automated Deck Ingestion & Extraction (JSON / Text / Structured specs)
  2. Quantitative Venture Metric Synthesis (LTV, CAC Payback, Burn Multiple, Runway)
  3. 6-Point Heuristic "Bullshit Detector" & Sanity Audit:
     - Top-down vs. Bottom-up TAM Disconnect
     - AI API Token Pass-Through vs. Claimed Gross Margins
     - CAC Payback & Churn Viability
     - Burn Multiple & Capital Efficiency
     - Valuation-to-ARR Multiple Discipline
     - Technical Founder Moat & Execution Risk
  4. Automatic 1-Page Investment Committee (IC) Screening Memo Generation (Markdown)
  5. Executive Terminal Scorecard with Health Score (0-100) & Actionable Verdict
========================================================================================
"""

import sys
import os
import json
import math
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional


@dataclass
class AuditFlag:
    category: str
    severity: str  # "RED", "YELLOW", "GREEN"
    title: str
    finding: str
    benchmark: str
    impact: str


class PitchDeckScreener:
    def __init__(self, deck_data: Dict):
        self.data = deck_data
        self.company_name = deck_data.get("company_name", "Unknown Startup")
        self.tagline = deck_data.get("tagline", "")
        self.sector = deck_data.get("sector", "General Tech")
        self.stage = deck_data.get("stage", "Seed")
        self.ask_usd = float(deck_data.get("funding_ask_usd", 0.0))
        self.post_money_usd = float(deck_data.get("claimed_post_money_valuation_usd", 0.0))
        self.team = deck_data.get("team", [])
        self.m = deck_data.get("claimed_metrics", {})
        
        # Computed metrics container
        self.computed: Dict[str, float] = {}
        self.flags: List[AuditFlag] = []
        self.health_score: int = 100

    def compute_derived_metrics(self):
        """Calculates derived venture economics from claimed numbers."""
        arr = float(self.m.get("arr_usd", 0.0))
        mrr = float(self.m.get("mrr_usd", 0.0))
        net_new_arr = float(self.m.get("net_new_arr_last_12m_usd", 0.0))
        gross_margin = float(self.m.get("claimed_gross_margin_pct", 0.75))
        monthly_churn = float(self.m.get("claimed_monthly_churn_pct", 0.02))
        cac = float(self.m.get("claimed_cac_usd", 1000.0))
        arpu_monthly = float(self.m.get("claimed_arpu_monthly_usd", 100.0))
        net_burn_monthly = float(self.m.get("monthly_net_burn_usd", 10000.0))
        cash = float(self.m.get("cash_in_bank_usd", 100000.0))
        claimed_tam = float(self.m.get("claimed_tam_usd", 1e9))
        target_customers = float(self.m.get("target_customer_count_global", 10000.0))

        # Inferred LTV = (ARPU * Gross Margin) / Monthly Churn
        monthly_gp_per_customer = arpu_monthly * gross_margin
        customer_lifetime_months = (1.0 / monthly_churn) if monthly_churn > 0 else 100.0
        ltv = monthly_gp_per_customer * customer_lifetime_months

        # LTV:CAC Ratio
        ltv_cac = (ltv / cac) if cac > 0 else 0.0

        # CAC Payback Period (Months) = CAC / Monthly Gross Profit per customer
        cac_payback_months = (cac / monthly_gp_per_customer) if monthly_gp_per_customer > 0 else 999.0

        # Burn Multiple = Annual Net Burn / Net New ARR (Craft Ventures metric)
        annual_burn = net_burn_monthly * 12.0
        burn_multiple = (annual_burn / net_new_arr) if net_new_arr > 0 else 99.0

        # Runway in Months
        runway_months = (cash / net_burn_monthly) if net_burn_monthly > 0 else 999.0

        # Realistic Bottom-Up TAM = Target Customers * (ARPU * 12)
        annual_arpu = arpu_monthly * 12.0
        bottom_up_tam = target_customers * annual_arpu

        # Valuation to ARR Multiple
        valuation_arr_multiple = (self.post_money_usd / arr) if arr > 0 else 999.0

        self.computed = {
            "arr": arr,
            "mrr": mrr,
            "net_new_arr": net_new_arr,
            "ltv": ltv,
            "ltv_cac": ltv_cac,
            "cac_payback_months": cac_payback_months,
            "burn_multiple": burn_multiple,
            "runway_months": runway_months,
            "bottom_up_tam": bottom_up_tam,
            "claimed_tam": claimed_tam,
            "valuation_arr_multiple": valuation_arr_multiple,
            "annual_burn": annual_burn
        }

    def run_sanity_audits(self):
        """Runs the 6-point Heuristic Bullshit Detector against the pitch deck claims."""
        self.flags = []
        score = 100

        # ---------------------------------------------------------------------------------
        # AUDIT 1: Top-down TAM Fantasy vs Bottom-up Reality Check
        # ---------------------------------------------------------------------------------
        claimed_tam = self.computed["claimed_tam"]
        bottom_up_tam = self.computed["bottom_up_tam"]
        disparity_ratio = claimed_tam / max(1.0, bottom_up_tam)

        if disparity_ratio > 10.0:
            score -= 20
            self.flags.append(AuditFlag(
                category="Market Sizing (TAM)",
                severity="RED",
                title="Severe TAM Disconnect (Fantasy Top-down TAM)",
                finding=f"Deck claims a ${claimed_tam/1e9:.1f}B TAM, but realistic bottom-up sizing ({self.m.get('target_customer_count_global',0):,} target accounts @ ${self.m.get('claimed_arpu_monthly_usd',0)*12:,.0f}/yr) yields only ${bottom_up_tam/1e6:.1f}M.",
                benchmark="Claimed TAM should not exceed 3x-5x of realistic addressable customer accounts multiplied by annual contract value (ACV).",
                impact="High risk of market size exaggeration or TAM hallucination to justify unjustifiable seed valuations."
            ))
        elif disparity_ratio <= 3.5:
            self.flags.append(AuditFlag(
                category="Market Sizing (TAM)",
                severity="GREEN",
                title="Credible Bottom-Up Market Sizing",
                finding=f"Claimed TAM (${claimed_tam/1e9:.1f}B) is closely anchored to credible customer volume and ACV (${bottom_up_tam/1e9:.1f}B bottom-up).",
                benchmark="Bottom-up TAM within realistic bounds of serviceable market.",
                impact="Signals analytical honesty from the founding team."
            ))

        # ---------------------------------------------------------------------------------
        # AUDIT 2: AI Token Pass-Through vs. Claimed Gross Margin
        # ---------------------------------------------------------------------------------
        uses_apis = self.m.get("uses_third_party_llm_apis", False)
        has_local_models = self.m.get("has_local_fine_tuned_models", False)
        claimed_margin = self.m.get("claimed_gross_margin_pct", 0.8)

        if uses_apis and not has_local_models and claimed_margin >= 0.88:
            score -= 20
            self.flags.append(AuditFlag(
                category="Unit Economics (Gross Margin)",
                severity="RED",
                title="Suspicious AI Wrapper Gross Margin",
                finding=f"Deck claims {claimed_margin*100:.1f}% gross margin while relying 100% on third-party LLM APIs with zero proprietary fine-tuned SLMs.",
                benchmark="Pure API pass-through GenAI wrappers realistically operate at 60%-72% gross margins due to token inference COGS.",
                impact="Current margins are artificially subsidized or misclassifying cloud API bills as R&D OpEx rather than COGS."
            ))
        elif has_local_models and claimed_margin >= 0.80:
            self.flags.append(AuditFlag(
                category="Unit Economics (Gross Margin)",
                severity="GREEN",
                title="Defensible Software Gross Margin with SLM Layer",
                finding=f"Healthy {claimed_margin*100:.1f}% gross margin supported by local/fine-tuned inference arbitration to suppress third-party API costs.",
                benchmark="Top-quartile enterprise software maintains >80% gross margin.",
                impact="Protects unit economics as enterprise customer token usage scales."
            ))

        # ---------------------------------------------------------------------------------
        # AUDIT 3: CAC Payback Period & Retention Reality
        # ---------------------------------------------------------------------------------
        payback = self.computed["cac_payback_months"]
        monthly_churn = self.m.get("claimed_monthly_churn_pct", 0.02)
        annualized_churn = monthly_churn * 12.0

        if payback > 18.0:
            score -= 20
            self.flags.append(AuditFlag(
                category="Sales Efficiency (CAC Payback)",
                severity="RED",
                title="Sluggish CAC Payback (> 18 Months)",
                finding=f"Current CAC payback is {payback:.1f} months. Combined with {annualized_churn*100:.1f}% annual churn, customers may churn before recovering acquisition cost.",
                benchmark="Seed/Series A software benchmark is < 12 months payback.",
                impact="Requires continuous external capital injection to fuel growth; leaky sales bucket."
            ))
        elif payback <= 10.0:
            self.flags.append(AuditFlag(
                category="Sales Efficiency (CAC Payback)",
                severity="GREEN",
                title="Elite Capital-Efficient Sales Payback",
                finding=f"CAC payback is only {payback:.1f} months, generating fast cash flow recycling into growth.",
                benchmark="Best-in-class venture benchmark: < 12 months.",
                impact="Allows startup to grow without burning excessive venture capital on marketing."
            ))

        # ---------------------------------------------------------------------------------
        # AUDIT 4: Burn Multiple & Capital Discipline (Craft Ventures / David Sacks)
        # ---------------------------------------------------------------------------------
        burn_mult = self.computed["burn_multiple"]
        runway = self.computed["runway_months"]

        if burn_mult > 2.2:
            score -= 15
            self.flags.append(AuditFlag(
                category="Capital Efficiency (Burn Multiple)",
                severity="RED",
                title="Alarming Burn Inefficiency",
                finding=f"Burn Multiple is {burn_mult:.2f}x (Burning ${self.computed['annual_burn']:,.0f}/yr to add only ${self.computed['net_new_arr']:,.0f} of new ARR).",
                benchmark="David Sacks benchmark: < 1.0x is Elite, 1.0x-1.5x is Good, > 2.0x is Suspect.",
                impact="High cash consumption rate; startup burns capital much faster than it compounds revenue."
            ))
        elif burn_mult <= 1.0:
            self.flags.append(AuditFlag(
                category="Capital Efficiency (Burn Multiple)",
                severity="GREEN",
                title="Elite Capital Efficiency (< 1.0x Burn Multiple)",
                finding=f"Burn Multiple is {burn_mult:.2f}x (Burning only ${burn_mult:.2f} for every $1.00 of net new ARR created).",
                benchmark="< 1.0x is elite top-decile efficiency.",
                impact="Exceptional founder capital allocation discipline."
            ))

        # ---------------------------------------------------------------------------------
        # AUDIT 5: Valuation-to-ARR Multiple Discipline
        # ---------------------------------------------------------------------------------
        val_multiple = self.computed["valuation_arr_multiple"]
        if val_multiple > 35.0 and self.stage.lower() in ["seed", "series seed"]:
            score -= 15
            self.flags.append(AuditFlag(
                category="Deal Terms & Valuation",
                severity="YELLOW",
                title="Rich Seed Entry Valuation Multiple",
                finding=f"Ask implies a {val_multiple:.1f}x Post-Money/ARR multiple (${self.post_money_usd/1e6:.1f}M valuation on ${self.computed['arr']/1e6:.2f}M ARR).",
                benchmark="Normalized Seed-stage market multiples range between 15x and 25x ARR.",
                impact="Compresses fund-level returns (requires an exit > $1.2B to return a standard $100M fund)."
            ))
        elif val_multiple <= 20.0:
            self.flags.append(AuditFlag(
                category="Deal Terms & Valuation",
                severity="GREEN",
                title="Attractive & Disciplined Entry Multiple",
                finding=f"Reasonable {val_multiple:.1f}x Post-Money/ARR multiple offers strong downside protection and headroom for fund return upside.",
                benchmark="Market standard: 15x - 22x ARR.",
                impact="Maximizes fund-level Multiple on Invested Capital (MoIC)."
            ))

        # ---------------------------------------------------------------------------------
        # AUDIT 6: Technical Founder Moat & Team Pedigree
        # ---------------------------------------------------------------------------------
        has_tech = self.m.get("has_technical_founder", False)
        if not has_tech and "ai" in self.sector.lower():
            score -= 25
            self.flags.append(AuditFlag(
                category="Team & Defensibility Moat",
                severity="RED",
                title="Zero Technical Founders in an AI Infrastructure Venture",
                finding="The founding team has no engineering, ML, or systems architecture co-founder leading technical product development.",
                benchmark="Early-stage deeptech and AI infrastructure ventures require native engineering co-founders.",
                impact="Severe vulnerability to outsourced dev-shop debt, slow ship velocity, and inability to build proprietary IP."
            ))
        elif has_tech:
            self.flags.append(AuditFlag(
                category="Team & Defensibility Moat",
                severity="GREEN",
                title="Strong Technical Founder Pedigree",
                finding="Founding team possesses native engineering leadership, patents, and prior hyperscaler/scaleup systems experience.",
                benchmark="Founder-market fit is the primary predictor of early-stage software outperformance.",
                impact="High velocity execution and ability to recruit top-tier engineering talent."
            ))

        self.health_score = max(5, min(100, score))

    def get_verdict(self) -> Tuple[str, str]:
        if self.health_score >= 75:
            return "PRIORITY PARTNER CALL", "Fast-track to Investment Committee meeting. Clean unit economics, defensible technical moat, and disciplined burn."
        elif self.health_score >= 50:
            return "EXPLORE WITH CAUTION", "Significant questions regarding market sizing or valuation multiples. Require partner review and sensitivity stress-testing."
        else:
            return "PASS (REJECT)", "Multiple critical red flags detected. Exaggerated market claims, high burn multiple, or lack of technical defensibility."

    def print_terminal_scorecard(self):
        verdict, verdict_desc = self.get_verdict()

        print("=" * 84)
        print(" DECKDILIGENCE.AI - VC PITCH DECK SCREENING SCORECARD")
        print("=" * 84)
        print(f" Target Company:  {self.company_name}")
        print(f" Tagline:         {self.tagline}")
        print(f" Sector / Stage:  {self.sector} | {self.stage}")
        print(f" Round Terms:     Ask: ${self.ask_usd/1e6:.2f}M | Post-Money Valuation: ${self.post_money_usd/1e6:.2f}M")
        print("-" * 84)
        print(f" DILIGENCE HEALTH SCORE: {self.health_score} / 100")
        print(f" SCREENER VERDICT:       [{verdict}]")
        print(f" Recommendation:         {verdict_desc}")
        print("=" * 84)
        
        print("\n--- SYNTHESIZED VENTURE METRICS ---")
        print(f" * Current ARR:          ${self.computed['arr']:,.0f} (MRR: ${self.computed['mrr']:,.0f})")
        print(f" * LTV : CAC Ratio:      {self.computed['ltv_cac']:.2f}x  (LTV: ${self.computed['ltv']:,.0f} vs CAC: ${self.m.get('claimed_cac_usd',0):,.0f})")
        print(f" * CAC Payback Period:   {self.computed['cac_payback_months']:.1f} Months (Benchmark: < 12.0 Months)")
        print(f" * Burn Multiple:        {self.computed['burn_multiple']:.2f}x (Benchmark: < 1.2x)")
        print(f" * Current Runway:       {self.computed['runway_months']:.1f} Months (Cash: ${self.m.get('cash_in_bank_usd',0):,.0f})")
        print(f" * Claimed vs Real TAM:  Claimed: ${self.computed['claimed_tam']/1e9:.1f}B  |  Bottom-Up Addressable: ${self.computed['bottom_up_tam']/1e6:.1f}M")
        print(f" * Valuation Multiple:   {self.computed['valuation_arr_multiple']:.1f}x ARR (Market Benchmark: 15x - 25x)")
        print("-" * 84)

        print("\n--- SANITY AUDIT & HEURISTIC FINDINGS ---")
        for i, flag in enumerate(self.flags, 1):
            symbol = "[RED FLAG]" if flag.severity == "RED" else ("[CAUTION]" if flag.severity == "YELLOW" else "[GREEN SIGNAL]")
            print(f"\n{i}. {symbol} {flag.category}: {flag.title}")
            print(f"   * Finding:   {flag.finding}")
            print(f"   * Benchmark: {flag.benchmark}")
            print(f"   * Impact:    {flag.impact}")

        print("\n" + "=" * 84)

    def generate_markdown_memo(self, output_filepath: str):
        verdict, verdict_desc = self.get_verdict()
        
        memo = f"""# VENTURE CAPITAL PRELIMINARY SCREENING MEMO

**Target Company**: {self.company_name}  
**Sector / Industry**: {self.sector}  
**Stage**: {self.stage} | **Round Ask**: ${self.ask_usd/1e6:.2f}M at ${self.post_money_usd/1e6:.2f}M Post-Money Valuation  
**Diligence Health Score**: **{self.health_score} / 100**  
**Screener Verdict**: **[{verdict}]**  
**Executive Summary**: {verdict_desc}  

---

## 1. Company & Problem Overview
* **Tagline**: {self.tagline}
* **Problem**: {self.data.get('problem_statement', 'N/A')}
* **Proposed Solution**: {self.data.get('solution_statement', 'N/A')}

---

## 2. Core Unit Economics & Performance Metrics

| Metric | Startup Claim | VC Industry Benchmark | Diligence Status |
| :--- | :---: | :---: | :---: |
| **Annual Recurring Revenue (ARR)** | ${self.computed['arr']:,.0f} | N/A | Current Scale |
| **LTV : CAC Ratio** | {self.computed['ltv_cac']:.2f}x | > 3.0x | {'Elite' if self.computed['ltv_cac']>=4 else ('Healthy' if self.computed['ltv_cac']>=3 else 'Underperforming')} |
| **CAC Payback Period** | {self.computed['cac_payback_months']:.1f} Months | < 12.0 Months | {'Top-Decile' if self.computed['cac_payback_months']<=12 else 'Slow Payback'} |
| **Burn Multiple (Net Burn / Net New ARR)** | {self.computed['burn_multiple']:.2f}x | < 1.2x | {'Capital Disciplined' if self.computed['burn_multiple']<=1.2 else 'High Cash Burn'} |
| **Claimed TAM vs. Bottom-Up Reality** | ${self.computed['claimed_tam']/1e9:.1f}B | Bottom-up: ${self.computed['bottom_up_tam']/1e6:.1f}M | {'Credible' if (self.computed['claimed_tam']/max(1.0, self.computed['bottom_up_tam'])) <= 4 else 'Exaggerated TAM'} |
| **Valuation Multiple (Post-Money / ARR)** | {self.computed['valuation_arr_multiple']:.1f}x ARR | 15.0x - 25.0x ARR | {'Disciplined' if self.computed['valuation_arr_multiple']<=25 else 'Expensive'} |

---

## 3. The "Bullshit Detector" & Heuristic Audit Findings

"""
        for i, flag in enumerate(self.flags, 1):
            badge = "🚨 **RED FLAG**" if flag.severity == "RED" else ("⚠️ **CAUTION**" if flag.severity == "YELLOW" else "🟢 **POSITIVE SIGNAL**")
            memo += f"""### {i}. {badge}: {flag.title}
* **Category**: {flag.category}
* **Specific Finding**: {flag.finding}
* **VC Standard Benchmark**: {flag.benchmark}
* **Investment Impact**: {flag.impact}

"""

        memo += f"""---

## 4. Founding Team Evaluation
"""
        for member in self.team:
            memo += f"- **{member.get('name', 'Founder')} ({member.get('role', 'Executive')})**: {member.get('background', 'N/A')}\n"

        memo += f"""
---

## 5. Recommendation for Investment Committee
**Action**: **{verdict}**  
{verdict_desc}  

*Generated by DeckDiligence.ai — Automated VC Due Diligence & Screening Engine.*
"""
        with open(output_filepath, "w", encoding="utf-8") as f:
            f.write(memo)


def run_screener_demo():
    print("=" * 84)
    print(" RUNNING DECKDILIGENCE.AI SCREENER ON TWO OPPOSING TEST DECK SCENARIOS")
    print("=" * 84)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    deck1_path = os.path.join(base_dir, "sample_deck_cogniflow.json")
    deck2_path = os.path.join(base_dir, "sample_deck_fluff.json")

    # 1. Screen CogniFlow AI (High-quality Indian AI infrastructure startup)
    print("\n>>> TEST CASE 1: High-conviction AI Infrastructure Startup (CogniFlow AI)")
    with open(deck1_path, "r", encoding="utf-8") as f:
        data1 = json.load(f)
    screener1 = PitchDeckScreener(data1)
    screener1.compute_derived_metrics()
    screener1.run_sanity_audits()
    screener1.print_terminal_scorecard()
    memo1_path = os.path.join(base_dir, "IC_Screening_Memo_CogniFlow.md")
    screener1.generate_markdown_memo(memo1_path)
    print(f"[+] 1-Page IC Memo successfully generated: {memo1_path}")

    # 2. Screen HyperBuzz AI (Typical hype-driven AI wrapper with bad economics)
    print("\n>>> TEST CASE 2: Hype-driven AI Wrapper with Red Flags (HyperBuzz AI)")
    with open(deck2_path, "r", encoding="utf-8") as f:
        data2 = json.load(f)
    screener2 = PitchDeckScreener(data2)
    screener2.compute_derived_metrics()
    screener2.run_sanity_audits()
    screener2.print_terminal_scorecard()
    memo2_path = os.path.join(base_dir, "IC_Screening_Memo_HyperBuzz.md")
    screener2.generate_markdown_memo(memo2_path)
    print(f"[+] 1-Page IC Memo successfully generated: {memo2_path}")


if __name__ == "__main__":
    run_screener_demo()
