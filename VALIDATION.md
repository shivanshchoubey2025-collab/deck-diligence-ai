# Model Validation & Diligence Refusal Report

**Project**: `DeckDiligence.ai`  
**Evaluation Protocol Version**: `v0.1-validation`  
**Git Tag**: [`v0.1-validation`](https://github.com/shivanshchoubey2025-collab/deck-diligence-ai/releases/tag/v0.1-validation)  
**Author**: Shivansh Choubey (`shivanshchoubey2025-collab`)  
**Date**: November 2026  

---

## 1. Diligence Protocol & Coverage Refusal Principle

To prevent confirmation bias, hallucinated defaults, and subjective scoring, the screener enforces strict quantitative data gating:

### The Refusal Rule (`audits_run_count < 3`)
- Standard venture diligence requires evaluating multiple independent unit economics (e.g., ARR multiples, Gross Margin, CAC Payback, Burn Multiple, and TAM grounding).
- If a pitch deck discloses fewer than **3 of the 6 sanity audits**, the engine strictly refuses to render an investment verdict (`INVEST`, `EXPLORE`, or `PASS`).
- It outputs an explicit **`INSUFFICIENT DATA / REFUSE VERDICT`** along with a transparent list of the omitted metrics that must be gathered during preliminary partner diligence calls or data-room reviews.

---

## 2. Controlled Perturbation Isolation Suite

Before testing real-world decks, the screener was verified using **single-variable perturbation testing** (`test_perturbations.py`) against a calibrated 100/100 baseline deck (`CogniFlow AI`) where all 6 audits pass with `GREEN` ratings.

Each test modifies strictly one input parameter to prove:
1. **Audit Orthogonality**: Strictly the targeted audit category flips to `RED`.
2. **Zero Contamination**: The remaining 5 audits remain completely unaffected.
3. **Deterministic Scoring**: The health score decreases by exactly the calibrated rule deduction.

| Test Case | Baseline Input | Perturbed Input | Targeted Audit | Observed Severity | Non-Target Contamination | Result |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TAM Disconnect** | $3.5B claimed (2.0x BU) | $70.0B claimed (40.5x BU) | Market Sizing (TAM) | 🚨 RED | 0 Flags | ✅ Passed |
| **AI Wrapper Margin** | Local fine-tuned SLM | 100% third-party APIs + 90% margin | Unit Economics (Gross Margin) | 🚨 RED | 0 Flags | ✅ Passed |
| **CAC Payback Drag** | $4,800 CAC (4.4 mo) | $25,000 CAC (22.9 mo) | Sales Efficiency (CAC Payback) | 🚨 RED | 0 Flags | ✅ Passed |
| **Burn Inefficiency** | $65k/mo burn (0.95x mult) | $200k/mo burn (2.93x mult) | Capital Efficiency (Burn Multiple) | 🚨 RED | 0 Flags | ✅ Passed |
| **Valuation Stretch** | $18M post (17.6x ARR) | $45M post (44.1x ARR) | Valuation Discipline | 🚨 RED | 0 Flags | ✅ Passed |
| **Team Leadership Gap** | CTO (Ex-ML Lead, MS CS) | No engineering co-founder (AI sector) | Team Composition | 🚨 RED | 0 Flags | ✅ Passed |

*All 6 perturbation tests pass deterministically in CI via `pytest test_perturbations.py`.*

---

## 3. Empirical Case Studies on Public Pitch Decks

To evaluate how the screener behaves on actual, publicly available pitch decks without hindsight, three famous historical decks were extracted slide-by-slide into standardized JSON files (`case_studies/`):
1. **Airbnb Seed Pitch Deck (2008)** — 12 slides
2. **Front Series A Pitch Deck (2016)** — 21 slides
3. **Brex Series B Pitch Deck (2018)** — 19 slides

Extraction followed strict rules: figures were recorded only if explicitly printed on a slide, with the slide number cited. Any metric not stated on a slide was recorded strictly as `null` (never backfilled from retrospective blog posts or S-1 filings).

### Case Study Execution Results

The script `case_studies/run_case_studies.py` runs the screener against each case and writes the screening memos and terminal scorecards to `case_studies/outputs/`:

| Company & Stage Evaluated | Business Model | Disclosed Audits (of 6) | Omitted Metrics (Data Gaps) | Diligence Health Score | Engine Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Airbnb Seed (2008)** | Consumer Travel Marketplace | **1 / 6** | ARR, Margin, Churn, CAC, ARPU, Burn | 75 / 100 | ⚠️ **INSUFFICIENT DATA / REFUSE VERDICT** |
| **Front Series A (2016)** | B2B Collaboration SaaS | **1 / 6** | Margin, CAC, ARPU, Burn, Post-Valuation | 75 / 100 | ⚠️ **INSUFFICIENT DATA / REFUSE VERDICT** |
| **Brex Series B (2018)** | Commercial Card / Fintech | **1 / 6** | ARR, Margin, Churn, CAC, ARPU, Burn | 75 / 100 | ⚠️ **INSUFFICIENT DATA / REFUSE VERDICT** |

---

### Detailed Slide Extraction Analysis

#### Case 1: Airbnb Seed Pitch Deck (2008) — 12 Slides
- **Extracted Claims**:
  - Funding Ask: $500,000 for 12 months runway (Slide 12).
  - Market Size: 1.9B+ trips booked worldwide, 560M budget/online market, 84M serviceable trips (Slide 3).
  - Business Model: 10% commission on each transaction = projected $84M revenue (Slide 6).
  - Team: Brian Chesky, Joe Gebbia, Nathan Blecharczyk (CTO / Harvard CS) (Slide 10).
- **Omitted Metrics**: Pre-revenue marketplace. Discloses zero historical ARR, gross margins, net burn, or paid customer acquisition costs.
- **Engine Behavior**:
  - `Technical Team Composition` evaluates to `GREEN` (Nathan Blecharczyk verified as technical CTO).
  - `TAM Market Sizing` is skipped because bottom-up calculation requires target customer counts and realized ARPU.
  - Audits run: **1 / 6**. Refusal threshold triggers: **`INSUFFICIENT DATA / REFUSE VERDICT`**.

#### Case 2: Front Series A Pitch Deck (2016) — 21 Slides
- **Extracted Claims**:
  - Revenue: Hit $100k MRR milestone ($1.2M ARR run-rate) (Slide 8).
  - Growth: Scaled from ~$15k to $100k MRR over previous 12 months (~$1.02M net new ARR) (Slide 8).
  - Churn & Retention: Low logo churn (Slide 9); cohort expansion showing customers spend 50% more after 12 months (Slide 13).
  - Capital Efficiency: $1.3M total capital spent to reach $1.2M ARR (Slide 14).
  - Team: Mathilde Collin (CEO) & Laurent Perrin (CTO / Software Engineer) (Slides 15-17).
  - Funding Ask: Raising $10M Series A (Slide 21).
- **Omitted Metrics**: Post-money valuation was negotiated with lead investor Social Capital and not printed on slides. Monthly run-rate net burn, gross margin percentage, and paid CAC were omitted from the deck (Mathilde Collin noted in her retrospective that organic growth made outbound CAC an open question).
- **Engine Behavior**:
  - `Technical Team Composition` evaluates to `GREEN`.
  - Valuation multiple and CAC payback audits cannot run without post-money valuation and explicit CAC figures.
  - Audits run: **1 / 6**. Refusal threshold triggers: **`INSUFFICIENT DATA / REFUSE VERDICT`**.

#### Case 3: Brex Series B Pitch Deck (2018) — 19 Slides
- **Extracted Claims**:
  - Funding Ask: $50M Series B (Slide 19).
  - Market Size: $101B global B2B payments opportunity, $5.2B US venture-backed segment (Slide 7).
  - Traction: 1,000+ tech companies onboarded with high card volume across AWS, ads, and SaaS (Slides 9-10).
  - Team: Henrique Dubugras & Pedro Franceschi (CTO / Engineering Lead, ex-Pagar.me) (Slide 3).
- **Omitted Metrics**: Revenue model is interchange fee volume rather than subscription software. Zero contractual ARR, subscription gross margin, or SaaS churn appears on the slides.
- **Engine Behavior**:
  - `Technical Team Composition` evaluates to `GREEN`.
  - Non-contractual payment business model leaves 5 of 6 SaaS audits unevaluated.
  - Audits run: **1 / 6**. Refusal threshold triggers: **`INSUFFICIENT DATA / REFUSE VERDICT`**.

---

### Core Insight: Pitch Decks vs. Underwriting Data Rooms

The empirical results reveal an essential reality of venture capital diligence:
1. **Pitch decks are narrative storytelling collateral, not financial models**: Even the most celebrated, legendary pitch decks in technology history (Front, Brex, Airbnb) omit the majority of quantitative unit economics from their slide presentations.
2. **Refusal is the correct institutional behavior**: An automated screener that forces a "PASS" or "INVEST" recommendation on a raw pitch deck with 5 missing metrics is hallucinating. Refusing a verdict and generating a checklist of required metrics (`missing_metrics`) protects the Investment Committee from premature conclusions.
3. **Role of Synthetic Benchmarks**: Full 6-audit evaluations are demonstrated using structured benchmark data rooms (`sample_deck_cogniflow.json` and `test_perturbations.py`), representing what an analyst compiles *after* the initial founder call and metrics sheet review.

---

## 4. Known Failure Modes & Architectural Limitations

1. **Category-Creation TAM Penalty**:
   - *Failure Mode*: In novel, category-defining software markets (e.g., initial pitches for Snowflake, Datadog, or Airbnb), bottom-up TAM calculated from *existing* discrete customer counts multiplied by initial ACV severely understates the future addressable market.
   - *Impact*: Transformative startups can be prematurely flagged with a `RED (Severe TAM Disconnect)` because their future customer base does not exist yet.
   - *Planned v0.2 Fix*: Add a `Category Creation Adjacency Multiplier` toggle for foundational market shifts.
2. **Seed-Stage Burn Multiple Volatility**:
   - *Failure Mode*: For early seed startups spending $30k–$60k/month to build product while generating $0–$50k ARR, the burn multiple ($\text{Annual Net Burn} / \text{Net New ARR}$) produces extreme or near-infinite values before full go-to-market rollout.
   - *Planned v0.2 Fix*: Restrict burn multiple gating strictly to companies with $\ge \$250\text{k}$ ARR.
3. **Non-Contractual Business Models**:
   - *Failure Mode*: Applying contractual B2B SaaS benchmarks (ARR, CAC Payback, Software Gross Margin) to fintech interchange, marketplaces, or usage tokens misclassifies revenue quality.
   - *Planned v0.2 Fix*: Introduce distinct underwriting profiles for Marketplaces (GMV / Take Rate) and Fintech (Interchange / Net Interest Margin).

---

## 5. How to Reproduce All Results

```bash
# 1. Run the full unit and perturbation test suite (23 tests in 0.3s)
pytest -v

# 2. Run the empirical case studies on real pitch decks
python case_studies/run_case_studies.py

# 3. View the generated screening memos and scorecards
ls case_studies/outputs/
```
