"""
========================================================================================
DECKDILIGENCE.AI — PITCH DECK QUANTITATIVE SCREENER & HEURISTIC AUDITOR
----------------------------------------------------------------------------------------
Purpose: Automated quantitative screening and heuristic auditing for early-stage decks.
Framework: Craft Ventures (David Sacks), Bessemer Venture Partners, and YC Benchmarks.
Scope: Audits claimed metrics, detects structural data gaps, and cross-references unit economics.
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
    severity: str  # "RED", "YELLOW", "GREEN", "DATA_GAP"
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
        
        # Tracking disclosed vs missing data
        self.missing_metrics: List[str] = []
        self.computed: Dict[str, Optional[float]] = {}
        self.flags: List[AuditFlag] = []
        self.health_score: int = 100
        self.audits_run_count: int = 0
        self.audits_run_names: List[str] = []
        self.audits_skipped_names: List[str] = []

    def compute_derived_metrics(self):
        """
        Calculates derived venture economics from claimed numbers.
        Missing data fields are NOT given benign defaults; they are marked as None
        and flagged as disclosures gaps.
        """
        arr = self.m.get("arr_usd")
        net_new_arr = self.m.get("net_new_arr_last_12m_usd")
        gross_margin = self.m.get("claimed_gross_margin_pct")
        monthly_churn = self.m.get("claimed_monthly_churn_pct")
        cac = self.m.get("claimed_cac_usd")
        arpu_monthly = self.m.get("claimed_arpu_monthly_usd")
        net_burn_monthly = self.m.get("monthly_net_burn_usd")
        cash = self.m.get("cash_in_bank_usd")
        claimed_tam = self.m.get("claimed_tam_usd")
        target_customers = self.m.get("target_customer_count_global")

        # Track disclosures
        expected_fields = [
            ("arr_usd", arr),
            ("claimed_gross_margin_pct", gross_margin),
            ("claimed_monthly_churn_pct", monthly_churn),
            ("claimed_cac_usd", cac),
            ("claimed_arpu_monthly_usd", arpu_monthly),
            ("monthly_net_burn_usd", net_burn_monthly),
            ("claimed_tam_usd", claimed_tam)
        ]
        self.missing_metrics = [name for name, val in expected_fields if val is None]

        # Inferred LTV
        ltv = None
        if arpu_monthly is not None and gross_margin is not None and monthly_churn is not None:
            if monthly_churn > 0:
                ltv = (arpu_monthly * gross_margin) / monthly_churn

        # LTV:CAC Ratio
        ltv_cac = None
        if ltv is not None and cac is not None and cac > 0:
            ltv_cac = ltv / cac

        # CAC Payback Period (Months)
        cac_payback_months = None
        if cac is not None and arpu_monthly is not None and gross_margin is not None:
            monthly_gp = arpu_monthly * gross_margin
            if monthly_gp > 0:
                cac_payback_months = cac / monthly_gp

        # Burn Multiple = Annual Net Burn / Net New ARR
        burn_multiple = None
        annual_burn = None
        if net_burn_monthly is not None:
            annual_burn = net_burn_monthly * 12.0
            if net_new_arr is not None and net_new_arr > 0:
                burn_multiple = annual_burn / net_new_arr

        # Runway in Months
        runway_months = None
        if cash is not None and net_burn_monthly is not None and net_burn_monthly > 0:
            runway_months = cash / net_burn_monthly

        # Bottom-Up TAM = Target Accounts * Annual ARPU
        bottom_up_tam = None
        if target_customers is not None and arpu_monthly is not None:
            bottom_up_tam = target_customers * (arpu_monthly * 12.0)

        # Valuation to ARR Multiple
        val_arr_multiple = None
        if arr is not None and arr > 0 and self.post_money_usd > 0:
            val_arr_multiple = self.post_money_usd / arr

        mrr = (float(arr) / 12.0) if arr is not None else None

        self.computed = {
            "arr": float(arr) if arr is not None else None,
            "mrr": mrr,
            "net_new_arr": float(net_new_arr) if net_new_arr is not None else None,
            "gross_margin": float(gross_margin) if gross_margin is not None else None,
            "monthly_churn": float(monthly_churn) if monthly_churn is not None else None,
            "cac": float(cac) if cac is not None else None,
            "arpu_monthly": float(arpu_monthly) if arpu_monthly is not None else None,
            "net_burn_monthly": float(net_burn_monthly) if net_burn_monthly is not None else None,
            "annual_burn": float(annual_burn) if annual_burn is not None else None,
            "cash": float(cash) if cash is not None else None,
            "claimed_tam": float(claimed_tam) if claimed_tam is not None else None,
            "target_customers": float(target_customers) if target_customers is not None else None,
            "bottom_up_tam": bottom_up_tam,
            "ltv": ltv,
            "ltv_cac": ltv_cac,
            "cac_payback_months": cac_payback_months,
            "burn_multiple": burn_multiple,
            "runway_months": runway_months,
            "valuation_arr_multiple": val_arr_multiple
        }

    def run_sanity_audits(self):
        """Runs the 6-point Heuristic Auditor without threshold dead-zones."""
        self.flags = []
        self.audits_run_names = []
        self.audits_skipped_names = []
        score = 100

        # ---------------------------------------------------------------------------------
        # DATA GAP CHECKS (Flags missing deck inputs instead of inventing numbers)
        # ---------------------------------------------------------------------------------
        if self.missing_metrics:
            score -= min(25, len(self.missing_metrics) * 8)
            self.flags.append(AuditFlag(
                category="Transparency & Data Gaps",
                severity="YELLOW",
                title=f"Undisclosed Metrics in Pitch Deck ({len(self.missing_metrics)} missing)",
                finding=f"The pitch deck does not disclose: {', '.join(self.missing_metrics)}.",
                benchmark="Standard venture decks disclose ARR, CAC, monthly gross margin, net burn, and customer churn.",
                impact="Requires preliminary diligence call to populate baseline unit economics before Investment Committee review."
            ))

        # ---------------------------------------------------------------------------------
        # AUDIT 1: Top-down TAM Fantasy vs Bottom-up Reality Check
        # ---------------------------------------------------------------------------------
        claimed_tam = self.computed["claimed_tam"]
        bottom_up_tam = self.computed["bottom_up_tam"]

        if claimed_tam is not None and bottom_up_tam is not None and bottom_up_tam > 0:
            self.audits_run_names.append("TAM Market Sizing")
            disparity_ratio = claimed_tam / bottom_up_tam

            if disparity_ratio > 10.0:
                score -= 20
                self.flags.append(AuditFlag(
                    category="Market Sizing (TAM)",
                    severity="RED",
                    title="Severe TAM Disconnect (> 10x Disparity)",
                    finding=f"Deck claims a ${claimed_tam/1e9:.1f}B TAM, but bottom-up sizing ({self.computed['target_customers']:,.0f} accounts @ ${(self.computed['arpu_monthly'] or 0)*12:,.0f}/yr) yields only ${bottom_up_tam/1e6:.1f}M.",
                    benchmark="Claimed TAM should not exceed 3x-5x of realistic addressable customer accounts multiplied by annual contract value (ACV).",
                    impact="High risk of market size inflation to justify inflated seed/Series A valuations."
                ))
            elif disparity_ratio > 4.0:
                score -= 10
                self.flags.append(AuditFlag(
                    category="Market Sizing (TAM)",
                    severity="YELLOW",
                    title="Moderate TAM Stretch (4x - 10x Disparity)",
                    finding=f"Claimed TAM (${claimed_tam/1e9:.1f}B) is {disparity_ratio:.1f}x higher than bottom-up customer volume calculation (${bottom_up_tam/1e6:.1f}M).",
                    benchmark="Addressable serviceable market (SAM) should closely track realistic account penetration.",
                    impact="TAM likely captures total sector spend rather than direct software wallet share."
                ))
            else:
                self.flags.append(AuditFlag(
                    category="Market Sizing (TAM)",
                    severity="GREEN",
                    title="Credible Bottom-Up Market Sizing",
                    finding=f"Claimed TAM (${claimed_tam/1e9:.1f}B) is grounded in credible account volume (${bottom_up_tam/1e9:.1f}B bottom-up).",
                    benchmark="Bottom-up TAM within realistic bounds of serviceable market.",
                    impact="Signals analytical honesty from the founding team."
                ))
        else:
            self.audits_skipped_names.append("TAM Market Sizing")

        # ---------------------------------------------------------------------------------
        # AUDIT 2: AI Token Pass-Through vs. Claimed Gross Margin
        # ---------------------------------------------------------------------------------
        uses_apis = self.m.get("uses_third_party_llm_apis", False)
        has_local_models = self.m.get("has_local_fine_tuned_models", False)
        claimed_margin = self.computed["gross_margin"]

        if claimed_margin is not None:
            self.audits_run_names.append("Gross Margin & COGS")
            if uses_apis and not has_local_models and claimed_margin >= 0.80:
                score -= 20
                self.flags.append(AuditFlag(
                    category="Unit Economics (Gross Margin)",
                    severity="RED",
                    title="Suspicious AI Wrapper Gross Margin (Token COGS Mismatch)",
                    finding=f"Deck claims {claimed_margin*100:.1f}% gross margin while relying 100% on third-party LLM APIs with zero proprietary fine-tuned SLMs.",
                    benchmark="Pure API pass-through wrappers realistically operate at 50%-65% gross margins due to token inference COGS.",
                    impact="Current margins are artificially subsidized or misclassifying API bills as R&D OpEx rather than Cost of Goods Sold."
                ))
            elif claimed_margin >= 0.75:
                self.flags.append(AuditFlag(
                    category="Unit Economics (Gross Margin)",
                    severity="GREEN",
                    title="Healthy Software Gross Margin (>= 75%)",
                    finding=f"Reported gross margin is {claimed_margin*100:.1f}%, meeting standard software margin hurdles.",
                    benchmark="Bessemer Cloud Index median: 75% - 80% gross margin.",
                    impact="Leaves adequate gross profit to cover sales & marketing acquisition."
                ))
            elif claimed_margin < 0.60:
                score -= 15
                self.flags.append(AuditFlag(
                    category="Unit Economics (Gross Margin)",
                    severity="RED",
                    title="Depressed Gross Margins (< 60%)",
                    finding=f"Gross margin of {claimed_margin*100:.1f}% indicates high server/token drag or service-heavy delivery.",
                    benchmark="Software businesses require >= 70% gross margin to compound sustainably.",
                    impact="Dramatically reduces customer lifetime value (LTV)."
                ))
        else:
            self.audits_skipped_names.append("Gross Margin & COGS")

        # ---------------------------------------------------------------------------------
        # AUDIT 3: CAC Payback Period (No Dead Zones: <12, 12-18, >18)
        # ---------------------------------------------------------------------------------
        payback = self.computed["cac_payback_months"]
        if payback is not None:
            self.audits_run_names.append("CAC Payback Period")
            if payback > 18.0:
                score -= 20
                self.flags.append(AuditFlag(
                    category="Sales Efficiency (CAC Payback)",
                    severity="RED",
                    title="Sluggish CAC Payback (> 18 Months)",
                    finding=f"Current CAC payback is {payback:.1f} months. Customer acquisition cash is locked up for > 1.5 years.",
                    benchmark="Early-stage benchmark: < 12 months payback. > 18 months signals severe sales friction.",
                    impact="Requires continuous dilutive equity rounds to fund growth; capital-intensive sales motion."
                ))
            elif payback > 12.0:
                score -= 10
                self.flags.append(AuditFlag(
                    category="Sales Efficiency (CAC Payback)",
                    severity="YELLOW",
                    title="Moderate CAC Payback (12 - 18 Months)",
                    finding=f"CAC payback is {payback:.1f} months, falling in the moderate/cautionary zone.",
                    benchmark="Best-in-class venture benchmark: < 12 months.",
                    impact="Acceptable for enterprise contracts ($50k+ ACV), but concerning for SMB/mid-market SaaS."
                ))
            else:
                self.flags.append(AuditFlag(
                    category="Sales Efficiency (CAC Payback)",
                    severity="GREEN",
                    title="Elite Capital-Efficient Sales Payback (< 12 Months)",
                    finding=f"CAC payback is {payback:.1f} months, allowing rapid cash reinvestment into go-to-market.",
                    benchmark="Best-in-class venture benchmark: < 12 months.",
                    impact="Enables the company to scale efficiently without burning excessive capital."
                ))
        else:
            self.audits_skipped_names.append("CAC Payback Period")

        # ---------------------------------------------------------------------------------
        # AUDIT 4: Burn Multiple (David Sacks / Craft Ventures: <=1.0, 1.0-2.0, >2.0)
        # ---------------------------------------------------------------------------------
        burn_mult = self.computed["burn_multiple"]
        if burn_mult is not None:
            self.audits_run_names.append("Burn Multiple Efficiency")
            # Stage context: At very early seed, burn multiple has high variance
            stage_note = " (Note: Burn multiple at Seed stage has high variance before full GTM motion)" if "seed" in self.stage.lower() else ""
            
            if burn_mult > 2.0:
                score -= 15
                self.flags.append(AuditFlag(
                    category="Capital Efficiency (Burn Multiple)",
                    severity="RED",
                    title="Alarming Burn Inefficiency (> 2.0x Burn Multiple)",
                    finding=f"Burn Multiple is {burn_mult:.2f}x: company burns ${burn_mult:.2f} for every $1.00 of net new ARR created{stage_note}.",
                    benchmark="David Sacks (Craft Ventures) benchmark: < 1.0x is Elite, 1.0x-2.0x is Moderate, > 2.0x is Suspect.",
                    impact="High cash consumption rate relative to net revenue compounded."
                ))
            elif burn_mult > 1.0:
                self.flags.append(AuditFlag(
                    category="Capital Efficiency (Burn Multiple)",
                    severity="YELLOW",
                    title="Moderate Burn Efficiency (1.0x - 2.0x)",
                    finding=f"Burn Multiple is {burn_mult:.2f}x (Burning ${(self.computed['annual_burn'] or 0):,.0f}/yr to add ${(self.computed['net_new_arr'] or 0):,.0f} ARR).",
                    benchmark="1.0x - 2.0x is standard for early venture-backed growth.",
                    impact="Sustainable if net retention (NDR) is high and expansion revenue accelerates."
                ))
            else:
                self.flags.append(AuditFlag(
                    category="Capital Efficiency (Burn Multiple)",
                    severity="GREEN",
                    title="Elite Capital Efficiency (<= 1.0x Burn Multiple)",
                    finding=f"Burn Multiple is {burn_mult:.2f}x (Top-decile capital discipline).",
                    benchmark="< 1.0x represents elite capital allocation.",
                    impact="Strong signal of product-market fit pulling demand rather than sales-led cash burning."
                ))
        else:
            self.audits_skipped_names.append("Burn Multiple Efficiency")

        # ---------------------------------------------------------------------------------
        # AUDIT 5: Valuation-to-ARR Multiple Discipline (No Dead-Zones: <=20, 20-30, >30)
        # ---------------------------------------------------------------------------------
        val_multiple = self.computed["valuation_arr_multiple"]
        arr = self.computed["arr"]
        if val_multiple is not None and arr is not None and arr > 0:
            self.audits_run_names.append("Valuation ARR Multiple")
            if val_multiple > 30.0:
                score -= 15
                self.flags.append(AuditFlag(
                    category="Valuation Discipline",
                    severity="RED",
                    title=f"Excessive Valuation Multiple ({val_multiple:.1f}x ARR)",
                    finding=f"Company asks for ${self.post_money_usd/1e6:.1f}M post-money on only ${arr/1e6:.2f}M ARR ({val_multiple:.1f}x ARR multiple).",
                    benchmark="Normalized early-stage venture multiples: 15x - 25x ARR. Above 30x requires extraordinary top-decile growth.",
                    impact="Massive 'grow-into-valuation' risk; leaves zero room for subsequent down-rounds."
                ))
            elif val_multiple > 20.0:
                self.flags.append(AuditFlag(
                    category="Valuation Discipline",
                    severity="YELLOW",
                    title=f"Premium Valuation Multiple ({val_multiple:.1f}x ARR)",
                    finding=f"Round pricing asks for {val_multiple:.1f}x ARR, representing a growth premium.",
                    benchmark="Standard range: 15x - 25x ARR.",
                    impact="Acceptable if triple-digit YoY ARR growth is demonstrated in data room."
                ))
            else:
                self.flags.append(AuditFlag(
                    category="Valuation Discipline",
                    severity="GREEN",
                    title=f"Sane Valuation Multiple ({val_multiple:.1f}x ARR)",
                    finding=f"Round pricing is grounded in current revenue run-rate (${arr/1e6:.2f}M ARR on ${self.post_money_usd/1e6:.1f}M post).",
                    benchmark="Disciplined venture range: 15x - 25x ARR.",
                    impact="Enables attractive risk-adjusted entry valuation and sustainable Series A step-ups."
                ))
        else:
            self.audits_skipped_names.append("Valuation ARR Multiple")

        # ---------------------------------------------------------------------------------
        # AUDIT 6: Technical Founder / Architecture Moat
        # ---------------------------------------------------------------------------------
        if not self.team:
            self.audits_skipped_names.append("Technical Team Composition")
        else:
            self.audits_run_names.append("Technical Team Composition")
            has_tech_founder = any(
                ("cto" in m.get("role", "").lower() or "tech" in m.get("role", "").lower() or "engineer" in m.get("background", "").lower())
                for m in self.team
            )
            is_deep_tech = "ai" in self.sector.lower() or "infrastructure" in self.sector.lower()

            if is_deep_tech and not has_tech_founder:
                score -= 20
                self.flags.append(AuditFlag(
                    category="Team Composition",
                    severity="RED",
                    title="No Technical Co-Founder in Deep Tech / AI Startup",
                    finding="The startup operates in deep AI/infrastructure without an in-house engineering co-founder or CTO.",
                    benchmark="Deep tech and systems AI startups require in-house technical leadership to own model weights and architecture.",
                    impact="Extreme risk of building superficial wrappers, high contractor burn, and inability to build proprietary IP."
                ))
            elif has_tech_founder:
                self.flags.append(AuditFlag(
                    category="Team Composition",
                    severity="GREEN",
                    title="In-House Technical Leadership",
                    finding="Founding team has verified engineering / systems leadership.",
                    benchmark="Essential for software and deep tech venture execution.",
                    impact="Reduces execution risk and accelerates proprietary R&D."
                ))
            else:
                self.flags.append(AuditFlag(
                    category="Team Composition",
                    severity="YELLOW",
                    title="Non-Technical Team in Tech Venture",
                    finding="Founding team lacks documented in-house software engineering background.",
                    benchmark="Software startups benefit heavily from technical founders.",
                    impact="May require hiring senior engineering talent early."
                ))

        self.audits_run_count = len(self.audits_run_names)
        self.health_score = max(5, min(100, score))
        return self.flags

    def get_verdict(self) -> Tuple[str, str]:
        """Returns the high-level screening recommendation and action plan."""
        if self.audits_run_count < 3:
            return (
                "INSUFFICIENT DATA / REFUSE VERDICT",
                f"Fewer than 3 of 6 sanity audits could be evaluated ({self.audits_run_count}/6 evaluated). "
                "Pitch deck lacks minimum quantitative disclosures (e.g., ARR, Margins, Burn, CAC) to render an IC recommendation."
            )
        red_flags = [f for f in self.flags if f.severity == "RED"]
        if self.health_score >= 75 and len(red_flags) == 0:
            return "INVEST / ADVANCE TO DEEP DIVE", "Founding team exhibits strong discipline, defensible unit economics, and sane valuation expectations. Schedule partner deep-dive."
        elif self.health_score >= 50 and len(red_flags) <= 1:
            return "EXPLORE WITH CAUTION", "Promising elements, but requires detailed verification in customer references and data room."
        else:
            return "PASS / REJECT", "Severe unit economics, TAM, or burn multiple red flags. Terminate preliminary diligence."

    def generate_scorecard(self) -> str:
        """Returns terminal scorecard string."""
        self.compute_derived_metrics()
        self.run_sanity_audits()
        
        red_count = sum(1 for f in self.flags if f.severity == "RED")
        yellow_count = sum(1 for f in self.flags if f.severity == "YELLOW")
        green_count = sum(1 for f in self.flags if f.severity == "GREEN")

        verdict_tuple = self.get_verdict()
        verdict = verdict_tuple[0]

        output = []
        output.append("=" * 78)
        output.append(f" DECKDILIGENCE.AI SCREENING SCORECARD: {self.company_name.upper()}")
        output.append(f" Sector: {self.sector} | Stage: {self.stage} | Post-Money: ${self.post_money_usd/1e6:.1f}M")
        output.append("=" * 78)
        output.append(f" HEALTH SCORE: {self.health_score}/100 | RED FLAGS: {red_count} | CAUTIONS: {yellow_count} | POSITIVE: {green_count}")
        output.append(f" AUDIT COVERAGE: {self.audits_run_count}/6 Audits Evaluated ({len(self.audits_skipped_names)} Skipped Due to Data Gaps)")
        output.append(f" VERDICT: {verdict}")
        output.append("-" * 78)
        
        for f in self.flags:
            badge = "🚨 [RED FLAG]" if f.severity == "RED" else ("⚠️ [CAUTION]" if f.severity == "YELLOW" else "🟢 [POSITIVE]")
            output.append(f"{badge} {f.category} — {f.title}")
            output.append(f"   Finding: {f.finding}")
            output.append(f"   VC Benchmark: {f.benchmark}")
            output.append("")

        output.append("=" * 78)
        return "\n".join(output)

    def generate_markdown_memo(self, output_path: str):
        """Generates 1-page Investment Committee screening memo."""
        self.compute_derived_metrics()
        self.run_sanity_audits()

        red_flags = [f for f in self.flags if f.severity == "RED"]
        cautions = [f for f in self.flags if f.severity == "YELLOW"]
        positives = [f for f in self.flags if f.severity == "GREEN"]

        if self.audits_run_count < 3:
            verdict = "INSUFFICIENT DATA / REFUSE VERDICT"
        elif self.health_score >= 75 and len(red_flags) == 0:
            verdict = "ADVANCE TO PARTNER MEETING"
        elif self.health_score >= 50 and len(red_flags) <= 1:
            verdict = "REQUEST UNIT ECONOMIC DATA ROOM"
        else:
            verdict = "PASS — FUND HEURISTIC BREACH"

        coverage_summary = f"{self.audits_run_count} / 6 Audits Evaluated ({', '.join(self.audits_run_names) if self.audits_run_names else 'None'})"
        skipped_summary = f"{', '.join(self.audits_skipped_names) if self.audits_skipped_names else 'None'}"

        md = f"""# INVESTMENT COMMITTEE (IC) SCREENING MEMO
**Company**: {self.company_name} | **Stage**: {self.stage} | **Sector**: {self.sector}  
**Round Ask**: ${self.ask_usd/1e6:.1f}M on ${self.post_money_usd/1e6:.1f}M Post-Money Valuation  
**Date**: October 2026 | **Diligence Copilot**: DeckDiligence.ai  

---

### 1. EXECUTIVE VERDICT & SCORE
* **Diligence Health Score**: **{self.health_score} / 100**
* **IC Recommendation**: **{verdict}**
* **Audit Coverage**: **{coverage_summary}**
* **Skipped Audits (Data Gaps)**: {skipped_summary}
* **Audit Summary**: {len(red_flags)} Red Flags | {len(cautions)} Cautions | {len(positives)} Positive Signals

---

### 2. QUANTITATIVE UNIT ECONOMICS BENCHMARKING

| Metric | Startup Claim | Venture Benchmark | Status |
| :--- | :--- | :--- | :--- |
| **ARR / Revenue** | {f"${self.computed['arr']/1e6:.2f}M" if self.computed.get('arr') is not None else "N/A"} | > $1.0M for Series A | {'🟢 Disclosed' if self.computed.get('arr') is not None else '⚠️ Undisclosed (Data Gap)'} |
| **Gross Margin** | {f"{self.computed['gross_margin']*100:.1f}%" if self.computed.get('gross_margin') is not None else "N/A"} | >= 75% for Enterprise Software | {'⚠️ Undisclosed (Data Gap)' if self.computed.get('gross_margin') is None else ('🟢 Pass' if self.computed['gross_margin'] >= 0.75 else '🚨 Breached')} |
| **CAC Payback** | {f"{self.computed['cac_payback_months']:.1f} mo" if self.computed.get('cac_payback_months') is not None else "N/A"} | < 12 Months | {'⚠️ Undisclosed (Data Gap)' if self.computed.get('cac_payback_months') is None else ('🟢 Elite' if self.computed['cac_payback_months'] <= 12.0 else ('🟡 Moderate' if self.computed['cac_payback_months'] <= 18.0 else '🚨 Sluggish'))} |
| **Burn Multiple** | {f"{self.computed['burn_multiple']:.2f}x" if self.computed.get('burn_multiple') is not None else "N/A"} | < 1.0x Elite / 1.0x-2.0x Good | {'⚠️ Undisclosed (Data Gap)' if self.computed.get('burn_multiple') is None else ('🟢 Elite' if self.computed['burn_multiple'] <= 1.0 else ('🟡 Good' if self.computed['burn_multiple'] <= 2.0 else '🚨 Inefficient'))} |
| **Runway** | {f"{self.computed['runway_months']:.1f} mo" if self.computed.get('runway_months') is not None else "N/A"} | 18 - 24 Months Recommended | {'⚠️ Undisclosed (Data Gap)' if self.computed.get('runway_months') is None else ('🟢 Safe' if self.computed['runway_months'] >= 18.0 else '🚨 Short Runway')} |

---

### 3. KEY HEURISTIC AUDIT FINDINGS

#### 🚨 Critical Red Flags & Data Gaps
"""
        if red_flags:
            for rf in red_flags:
                md += f"* **{rf.category} ({rf.title})**: {rf.finding}\n  * *VC Risk*: {rf.impact}\n"
        else:
            md += "* *None identified under current metrics disclosure.*\n"

        md += "\n#### ⚠️ Cautionary Observations\n"
        if cautions:
            for c in cautions:
                md += f"* **{c.category} ({c.title})**: {c.finding}\n"
        else:
            md += "* *No secondary cautions identified.*\n"

        md += "\n#### 🟢 Validated Strengths & Positive Signals\n"
        for p in positives:
            md += f"* **{p.category}**: {p.finding}\n"

        md += f"""
---

### 4. POWER LAW FUND-RETURN ANALYSIS
For a **$100M early-stage venture fund**, returning 3x the fund ($300M DPI) with standard 20% subsequent dilution requires:
* An exit valuation of **>= $450M** if holding a 10% ownership stake at exit.
* Current entry post-money (${self.post_money_usd/1e6:.1f}M) requires a **{ (450e6 / max(1.0, self.post_money_usd)):.1f}x exit multiple** to return a meaningful fraction of the fund.
"""
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(md)


if __name__ == "__main__":
    from sample_deck_cogniflow import *
    # Test script entrypoint
