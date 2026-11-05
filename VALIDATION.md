# Model Validation & Refusal-Rate Study

**Project**: `DeckDiligence.ai`  
**Protocol Version**: `v0.1-validation`  
**Git Tag**: [`v0.1-validation`](https://github.com/shivanshchoubey2025-collab/deck-diligence-ai/releases/tag/v0.1-validation)  
**Author**: Shivansh Choubey (`shivanshchoubey2025-collab`)  
**Date**: November 2026  

> [!IMPORTANT]
> **Provenance Notice**: All case study extractions in `case_studies/` were checked by hand against the original public pitch deck slides on **2026-11-05** with verbatim slide citations and direct SlideShare URLs.

---

## 1. Quantitative Refusal Rule (`audits_run_count < 3`)

Standard early-stage venture underwriting requires evaluating multiple independent quantitative unit economics (such as ARR multiples, Gross Margin, CAC Payback, Burn Multiple, and TAM grounding).

When evaluating a pitch deck:
- The screener tracks how many of the 6 sanity audits can actually be computed from disclosed figures.
- If fewer than **3 of the 6 audits** can be evaluated due to omitted metrics, the screener strictly refuses to render an automated recommendation (`INVEST`, `EXPLORE`, or `PASS`).
- It triggers an explicit **`INSUFFICIENT DATA / REFUSE VERDICT`** and generates a checklist of unverified metrics (`missing_metrics`) that must be obtained via a preliminary diligence call or financial data room before Investment Committee review.

---

## 2. Controlled Perturbation Isolation Suite

The internal logic of the 6 sanity audits was tested via **single-variable perturbation testing** (`test_perturbations.py`) against a calibrated 100/100 baseline deck (`CogniFlow AI`) where all 6 audits pass with `GREEN` ratings.

Each test alters strictly one input to verify:
1. **Audit Orthogonality**: Strictly the targeted audit category flips to `RED`.
2. **Zero Contamination**: The other 5 audits remain unaffected.
3. **Deterministic Penalty**: The score drops by exactly the intended deduction.

| Test Case | Baseline Input | Perturbed Input | Targeted Audit | Observed Severity | Non-Target Contamination | Result |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TAM Disconnect** | $3.5B claimed (2.0x BU) | $70.0B claimed (40.5x BU) | Market Sizing (TAM) | 🚨 RED | 0 Flags | ✅ Passed |
| **AI Wrapper Margin** | Local fine-tuned SLM | 100% third-party APIs + 90% margin | Unit Economics (Gross Margin) | 🚨 RED | 0 Flags | ✅ Passed |
| **CAC Payback Drag** | $4,800 CAC (4.4 mo) | $25,000 CAC (22.9 mo) | Sales Efficiency (CAC Payback) | 🚨 RED | 0 Flags | ✅ Passed |
| **Burn Inefficiency** | $65k/mo burn (0.95x mult) | $200k/mo burn (2.93x mult) | Capital Efficiency (Burn Multiple) | 🚨 RED | 0 Flags | ✅ Passed |
| **Valuation Stretch** | $18M post (17.6x ARR) | $45M post (44.1x ARR) | Valuation Discipline | 🚨 RED | 0 Flags | ✅ Passed |
| **Team Leadership Gap** | CTO (Ex-ML Lead, MS CS) | No engineering co-founder (AI sector) | Team Composition | 🚨 RED | 0 Flags | ✅ Passed |

*All 6 perturbation tests pass in CI via `pytest test_perturbations.py`.*

---

## 3. Empirical Refusal-Rate Study on 3 Public Pitch Decks

To evaluate how the screener behaves on real-world pitch decks, three iconic, publicly available decks were extracted slide-by-slide:
1. **Airbnb Seed Pitch Deck (2009, 14 slides)**: [SlideShare Source](https://www.slideshare.net/slideshow/airbnbs-first-pitch-deck-15031214/45763955)
2. **Buffer Seed Pitch Deck (2011, 13 slides)**: [SlideShare Source](https://www.slideshare.net/Bufferapp/buffer-seed-deck-47449800)
3. **Front Series A Pitch Deck (2016, 21 slides)**: [SlideShare Source](https://www.slideshare.net/MathildeCollin/front-series-a-deck-64596550)

Every figure was extracted verbatim from its slide. Metrics not explicitly printed on a slide were recorded strictly as `null` (not backfilled from subsequent S-1 filings or interviews).

### Execution Results (`case_studies/run_case_studies.py`)

| Company & Stage Evaluated | Verified Deck URL | Audits Evaluated | Omitted Metrics (Data Gaps) | Health Score | Engine Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Airbnb Seed (2009)** | [SlideShare (14 slides)](https://www.slideshare.net/slideshow/airbnbs-first-pitch-deck-15031214/45763955) | **1 / 6** | ARR, Margin, Churn, CAC, ARPU, Burn | **N/A** *(Refused)* | ⚠️ **INSUFFICIENT DATA / REFUSE VERDICT** |
| **Buffer Seed (2011)** | [SlideShare (13 slides)](https://www.slideshare.net/Bufferapp/buffer-seed-deck-47449800) | **2 / 6** | Burn, CAC, Post-Valuation, Dollar TAM | **N/A** *(Refused)* | ⚠️ **INSUFFICIENT DATA / REFUSE VERDICT** |
| **Front Series A (2016)** | [SlideShare (21 slides)](https://www.slideshare.net/MathildeCollin/front-series-a-deck-64596550) | **2 / 6** | Margin, CAC, ARPU, Post-Valuation, TAM | **N/A** *(Refused)* | ⚠️ **INSUFFICIENT DATA / REFUSE VERDICT** |

---

### Detailed Slide-by-Slide Extraction Notes

#### 1. Airbnb Seed Pitch Deck (2009, 14 Slides)
* **Verbatim Disclosures**:
  - Funding Ask: Slide 14 verbatim: *"We are looking for $500,000 angel financing to reach 12 months runway."*
  - Business Model: Slide 7 verbatim: *"We take a 10% commission on each transaction."*
  - Market Size: Slide 5 verbatim (standard draft variant): *"1.9 Billion+ Trips Booked (Worldwide) | 532M Budget & Online Trips | 10.6M Trips w/ AB&B"*. (Note: An alternative widely circulated SlideShare draft shows *"2 Billion+ Trips Booked | 560M Budget & Online Trips | 84M Trips w/ AB&B"*). Crucially, **neither variant states a dollar ($) TAM figure on Slide 5**, only transaction unit volumes.
  - Financial Milestone Ask: Slide 14 verbatim: *"We are looking for $500,000 angel financing to reach 12 months runway. 80,000 trips, $25 avg fee, $2,000,000 revenue."*
  - Team: Slide 11 verbatim: *"Brian Chesky: Co-founder & CEO (Industrial Design, RISD)"* | *"Joe Gebbia: Co-founder (Industrial Design, RISD)"* | *"Nathan Blecharczyk: Co-founder & CTO (Computer Science, Harvard)"*.
* **Omissions**: Pre-revenue marketplace. Discloses zero historical ARR, gross margins, net burn, or paid customer acquisition costs.
* **Audit Execution**:
  - `Technical Team Composition`: Evaluates to `GREEN` (Nathan Blecharczyk verified as technical CTO).
  - 5 of 6 audits skipped due to missing quantitative metrics.
  - Coverage: **1 / 6** → Triggers **`INSUFFICIENT DATA / REFUSE VERDICT`**.

#### 2. Buffer Seed Pitch Deck (2011, 13 Slides)
* **Verbatim Disclosures**:
  - Revenue Run Rate: Slide 5 verbatim: *"$150,000 annual revenue run rate"*.
  - Paying Customers: Slide 5 verbatim: *"800 Paying Users"*.
  - Gross Margin: Slide 5 verbatim: *"97% margins"*.
  - Growth Rate: Slide 5 verbatim: *"Growing 40% month-over-month"*.
  - Net New Revenue: Slide 6 verbatim: *"January 2011: Launched web app | October 2011: 55,000 users ($150K revenue run rate)"* ($150k net new ARR over 10 months).
  - Churn: Slide 7 verbatim: *"5% churn equates to a Lifetime Value (LTV) of $240"*.
  - Team: Slide 12 verbatim: *"Joel Gascoigne (Co-Founder) - took the idea to revenue in 7 weeks"* | *"Leo Widrich (Co-Founder)"*.
  - Funding Ask: Deck subtitle / Slide 13: *"The slide deck we used to raise half a million dollars"* ($500,000).
* **Omissions**: Monthly net burn, cash in bank, paid customer acquisition cost (CAC), post-money valuation, and dollar TAM are not printed on any of the 13 slides.
* **Audit Execution**:
  - `Gross Margin & COGS`: Evaluates to `GREEN` (97% software margin).
  - `Technical Team Composition`: Evaluates to `GREEN` (Joel Gascoigne verified as developer).
  - 4 of 6 audits skipped (TAM, Payback, Burn, Valuation multiple).
  - Coverage: **2 / 6** → Triggers **`INSUFFICIENT DATA / REFUSE VERDICT`**.

#### 3. Front Series A Pitch Deck (2016, 21 Slides)
* **Verbatim Disclosures**:
  - Capital Efficiency & Revenue: Slide 14 verbatim: *"$1.4M in ARR achieved"*, *"$1.3M spent in 18 months"*, *"$90k Monthly burn"*, *"$1.8M Left from our last seed round"*, and *"5 months time to profitability"*.
  - Net New Revenue: **Derived** from Slide 8 (*"MRR grew 5.4 times in the past 12 months"*) applied to Slide 14 ($1.4M ARR): $1.4M - ($1.4M / 5.4) = $1,140,741 net new ARR over prior 12 months. (The 0.95x burn multiple rests on this derived denominator, as net new ARR was not printed as a standalone figure).
  - Churn: Slide 9 verbatim: *"~3% monthly user churn"* and *"Negative Net MRR Churn"*. **Diligence Distinction**: Slide 9 reports user/seat-level churn (~3%/mo), whereas contractual B2B diligence distinguishes user churn from logo/account churn or net revenue retention (NRR). Front explicitly noted that expansion outpaced churn, generating negative net revenue churn.
  - Funding Ask: Slide 15 verbatim: *"RAISING $10M SERIES A TO ACCELERATE GROWTH."* (Ask is on Slide 15, not Slide 21).
  - Seed Investor: Slide 19 verbatim: *"Led by SoftTech VC"* (seed lead, not Social Capital).
  - Team: Slide 16 verbatim: *"Mathilde Collin - CEO, Co-founder"* | *"Laurent Perrin - CTO, Co-founder"*. (No academic degrees are printed on the slide).
* **Omissions**: Post-money valuation was negotiated during the round and not stated on slides. Gross margin percentage, paid CAC, and total dollar TAM were omitted from the deck. All retrospective commentary has been stripped from citations to ensure slide-only provenance.
* **Audit Execution**:
  - `Capital Efficiency (Burn Multiple)`: Evaluates to `GREEN` (0.95x burn multiple, $1.08M annual burn / $1.14M derived net new ARR).
  - `Technical Team Composition`: Evaluates to `GREEN` (Laurent Perrin verified as technical CTO).
  - 4 of 6 audits skipped (TAM, Gross Margin, CAC Payback, Valuation multiple).
  - Coverage: **2 / 6** → Triggers **`INSUFFICIENT DATA / REFUSE VERDICT`**.

---

## 4. Key Diligence Finding: The Need for a Data-Request Step

Running the screener on raw pitch decks demonstrates that **the tool cannot render automated investment recommendations from pitch deck slides alone**:
1. **Pitch decks are narrative marketing collateral**: Real seed and Series A decks rarely disclose gross margin, CAC, or monthly net burn. Even celebrated decks (Front, Buffer, Airbnb) disclose at most 1 or 2 of the 6 required quantitative unit economics in the slides.
2. **Refusal prevents false certainty**: A screener that attempts to score a deck with 4 or 5 missing metrics will either fabricate defaults or give an unjustified grade. Refusing a verdict and outputting a checklist of `missing_metrics` protects the diligence team.
3. **Product Workflow Implication**: The screener serves as a top-of-funnel intake filter that generates an automated **Data Request Checklist** for the founder call, rather than a standalone decision-maker.

---

## 5. Known Failure Modes & Architectural Limitations

1. **Category-Creation TAM Penalty**:
   - In emerging software markets (e.g., initial pitches for Snowflake, Datadog, or Airbnb), bottom-up TAM calculated from *existing* discrete customer counts multiplied by initial ACV severely understates the future addressable market.
   - *Planned v0.2 Fix*: Add a `Category Creation Adjacency Multiplier` toggle for foundational market shifts.
2. **Seed-Stage Burn Multiple Volatility**:
   - For early seed startups spending $30k–$60k/month to build product while generating $0–$50k ARR, the burn multiple produces extreme or near-infinite values before full go-to-market rollout.
   - *Planned v0.2 Fix*: Restrict burn multiple gating strictly to companies with $\ge \$250\text{k}$ ARR.
3. **Non-Contractual Business Models**:
   - Applying contractual B2B SaaS benchmarks (ARR, CAC Payback, Software Gross Margin) to fintech interchange, marketplaces, or usage tokens misclassifies revenue quality.
   - *Planned v0.2 Fix*: Introduce distinct underwriting profiles for Marketplaces (GMV / Take Rate) and Fintech (Interchange / Net Interest Margin).

---

## 6. How to Reproduce All Results

```bash
# 1. Run the full unit, perturbation, and case study test suite (33 tests in 0.4s)
pytest -v

# 2. Run the refusal-rate case study script on the 3 public pitch decks
python case_studies/run_case_studies.py

# 3. View the generated screening memos, scorecards, and results JSON
ls case_studies/outputs/
```
