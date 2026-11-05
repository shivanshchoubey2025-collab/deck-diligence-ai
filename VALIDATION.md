# Model Validation Protocol & Case Study Backtesting Report

**Project**: `DeckDiligence.ai`  
**Evaluation Protocol Version**: `v0.1-validation`  
**Git Tag**: [`v0.1-validation`](https://github.com/shivanshchoubey2025-collab/deck-diligence-ai/releases/tag/v0.1-validation)  
**Author**: Shivansh Choubey (`shivanshchoubey2025-collab`)  
**Date**: November 2026  

---

## 1. Objective Validation Protocol (Pre-Registered)

To prevent hindsight bias, confirmation bias, and metric overfitting, this protocol was frozen under git tag `v0.1-validation` prior to running case-study evaluations. Any future threshold re-calibrations will be designated as `v0.2` with full side-by-side transparency against `v0.1` baseline results.

### Objective Outcome Definitions
Startups in historical backtesting are classified into four mutually exclusive outcome categories determined by 24-to-36-month subsequent market events:
1. **Tier-1 Success (`SUCCESS`)**: Company successfully raised a higher-priced subsequent equity round (Series B/C/D) from tier-1 venture capital within 24 months, achieved profitability, or reached a $500M+ M&A / IPO exit.
2. **Capital Failure / Value Destruction (`FAILURE`)**: Company shut down, entered receivership, or executed an emergency recapitalization / down-round with >50% wipeout of earlier preferred equity.
3. **Severe Valuation Drag / Overhang (`OVERVALUED_DRAG`)**: Company remained operational but underwent major staff reductions, flat rounds, or significant multiple compressions due to unsustainably high earlier round pricing.
4. **Out of Domain (`OUT_OF_SCOPE`)**: Business models whose primary revenue model is non-contractual (e.g., fintech interchange, marketplace take-rates, crypto spread, hardware bio-devices) where B2B SaaS heuristics (ARR, CAC Payback, Gross Margin) do not apply.

### Screener Coverage & Refusal Principle
- **Coverage Requirement**: A deck must disclose sufficient data to evaluate at least **3 of the 6 sanity audits**.
- **Refusal Threshold**: If `audits_run_count < 3`, the screener issues an explicit **`INSUFFICIENT DATA / REFUSE VERDICT`** rather than fabricating defaults or awarding a pass/fail grade.

---

## 2. Controlled Perturbation Isolation Suite

Before running historical pitch decks, the screener was subjected to **single-variable perturbation testing** (`test_perturbations.py`) against a calibrated 100/100 healthy baseline deck (`CogniFlow AI`). 

Each test isolates one specific diligence rule by altering exactly one variable and verifying that:
1. **Strictly one** audit category flips to `RED`.
2. All other 5 audits remain unaffected.
3. Health score declines by the exact penalty assigned to that rule.

| Test Case | Baseline Value | Perturbed Value | Targeted Audit | Observed Severity | Non-Target Contamination | Result |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TAM Inflation** | $3.5B claimed (2.0x BU) | $70.0B claimed (40.5x BU) | Market Sizing (TAM) | 🚨 RED | 0 Flags | ✅ Passed |
| **Wrapper Margin** | Local fine-tuned SLM | 100% third-party APIs + 90% margin | Unit Economics (Gross Margin) | 🚨 RED | 0 Flags | ✅ Passed |
| **CAC Payback Drag** | $4,800 CAC (4.4 mo) | $25,000 CAC (22.9 mo) | Sales Efficiency (CAC Payback) | 🚨 RED | 0 Flags | ✅ Passed |
| **Burn Inefficiency** | $65k/mo burn (0.95x mult) | $200k/mo burn (2.93x mult) | Capital Efficiency (Burn Multiple) | 🚨 RED | 0 Flags | ✅ Passed |
| **Valuation Stretch** | $18M post (17.6x ARR) | $45M post (44.1x ARR) | Valuation Discipline | 🚨 RED | 0 Flags | ✅ Passed |
| **Team Leadership Gap** | CTO (Ex-ML Lead, MS CS) | No engineering co-founder (AI sector) | Team Composition | 🚨 RED | 0 Flags | ✅ Passed |

*All 6 perturbation tests pass in 0.28s under `pytest` (`test_perturbations.py`).*

---

## 3. Balanced Historical Case Study Evaluation (8 Cases)

To avoid survivorship bias, the backtesting dataset deliberately balances iconic successes, high-profile capital collapses, margin illusions, and out-of-scope business models.

Data extraction followed the standardized schema in `templates/deck_extraction_template.json`, using slide-number citations with `null` recorded for any undisclosed metric.

| Company & Stage Evaluated | Domain Scope | Disclosed Audits (of 6) | Diligence Health Score | Engine Recommendation | Historical Realized Outcome | Screener Concordance |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Front (2016 Series A)** | B2B SaaS | 5 / 6 | **85 / 100** | 🟢 ADVANCE TO DEEP DIVE | Successful Series B & C ($1.7B val) | **True Positive** |
| **Segment (2015 Series B)** | DevTool / B2B | 5 / 6 | **90 / 100** | 🟢 ADVANCE TO DEEP DIVE | Acquired by Twilio for $3.2B | **True Positive** |
| **Fast.co (2020 Series A)** | E-Commerce / Fintech | 4 / 6 | **35 / 100** | 🚨 PASS / REJECT | Burned $102M; collapsed in 2022 | **True Negative** |
| **WeWork (2014 Series D Data)** | Real Estate as Tech | 4 / 6 | **40 / 100** | 🚨 PASS / REJECT | Chapter 11 Bankruptcy 2023 | **True Negative** |
| **Jasper AI (2022 Series A)** | AI Generative Writing | 5 / 6 | **45 / 100** | 🚨 PASS / REJECT | Severe multiple haircut, staff cuts | **True Negative** |
| **Mixpanel (2012 Series A)** | Product Analytics | 5 / 6 | **80 / 100** | 🟢 ADVANCE TO DEEP DIVE | Scaled to $100M+ ARR | **True Positive** |
| **Coinbase (2012 Seed)** | Crypto / Exchange | 2 / 6 | **N/A** | ⚠️ REFUSE VERDICT (Out of Scope) | Direct Listing ($85B IPO) | **Scope Refusal** |
| **Theranos (2006 Early Data)** | MedTech / Hardware | 1 / 6 | **N/A** | ⚠️ REFUSE VERDICT (Data Void) | Complete dissolution & criminal fraud | **Data Gap Refusal** |

---

## 4. Detailed Case Studies & Diligence Mechanics

### Case 1: Front (2016 Series A Deck) — *True Positive*
- **Deck Profile**: Disclosed $3.0M ARR, 2.5x YoY growth, <6 months CAC payback, $11k ARPU, and <$250k net burn.
- **Engine Audit**: CAC payback (<6 mo) was awarded `GREEN (Elite)`. Burn multiple (~0.8x) received `GREEN (Elite)`. Valuation ask ($30M post on $3M ARR = 10x) fell well within disciplined entry tiers.
- **Finding**: Model accurately detected high capital efficiency and low sales friction, recommending immediate partner advancement.

### Case 2: Fast.co (2020 Series A) — *True Negative*
- **Deck Profile**: Disclosed rapid user checkout growth, but annualized net burn exceeded $10M on under $600k ARR.
- **Engine Audit**: Burn Multiple was flagged at **> 15.0x** (`RED`), CAC payback exceeded 36 months (`RED`), and gross margin was suppressed by payment processing interchange fees.
- **Finding**: While consumer momentum captivated investors in 2020, `DeckDiligence.ai` would have triggered an automatic `PASS / REJECT` due to unsustainable cash consumption per dollar of net new revenue.

### Case 3: Jasper AI (2022 Series A) — *True Negative*
- **Deck Profile**: Claimed $30M+ ARR in record time on top of OpenAI GPT-3 API, asking for a $1.5B post-money valuation (50x ARR). Claimed >85% software gross margins.
- **Engine Audit**: Flagged `Audit 2: AI Wrapper Gross Margin (Token COGS Mismatch)` as `RED` due to 100% third-party API reliance without proprietary fine-tuned model infrastructure. Valuation multiple (>50x ARR) was flagged as `RED (Excessive Valuation Multiple)`.
- **Finding**: Anticipated subsequent margin compression and multiple deflation when foundational model providers introduced direct competing interfaces.

### Case 4: Coinbase (2012 Seed) & Theranos (2006) — *Refusal Protocol Validation*
- **Coinbase**: Disclosed transaction volumes, active wallets, and exchange commission take-rates, but zero SaaS recurring revenue metrics. The screener successfully evaluated only 2 audits (TAM and Team), refused a score, and aborted with `INSUFFICIENT DATA / REFUSE VERDICT`.
- **Theranos**: Early investor materials contained proprietary secrecy disclaimers with zero unit cost per test, zero audited revenue, and zero customer acquisition data. Rather than awarding an arbitrary baseline score, the engine correctly aborted with `INSUFFICIENT DATA / REFUSE VERDICT`.

---

## 5. What Held Up vs. Known Failure Modes

### What Held Up
1. **Capital Efficiency Sensitivity**: The David Sacks burn multiple heuristic and CAC payback thresholds proved highly predictive. Startups that subsequently burned through equity rounds without compounding net ARR were cleanly filtered out.
2. **AI Wrapper Heuristic**: Disallowing software-grade 85%+ margins for pure API pass-through wrappers identified unsustainable unit economics before market saturation occurred.
3. **Refusal Mechanism**: Refusing verdicts on decks with fewer than 3 quantifiable audits prevented false confidence on missing or non-SaaS business models.

### Known Failure Modes & Limitations (Identified for `v0.2`)
1. **Category Creation TAM Penalty**:
   - *Failure Mode*: In novel, emerging software categories (e.g., Airbnb in 2008, Uber in 2009, or Snowflake in 2014), bottom-up TAM calculated from *existing* target customer accounts multiplied by current ACV drastically understates the future addressable market.
   - *Impact*: Truly transformative, category-defining companies can be falsely flagged with a `RED (Severe TAM Disconnect)` because the customer base has not yet materialized.
   - *Planned v0.2 Fix*: Add a `TAM Growth Potential / Adjacency Multiplier` toggle for category-creation pitches backed by verifiable usage expansion data.
2. **Seed Stage Burn Variance**:
   - *Failure Mode*: At pre-seed and early seed, a company spending $50k/month to build an initial product while generating $0-$50k ARR will technically have an infinite or extreme burn multiple before product launch.
   - *Impact*: Penalizing pre-revenue or early-revenue seed startups on burn multiple can cause false negatives.
   - *Planned v0.2 Fix*: Restrict burn multiple gating strictly to companies with `>= $250k ARR`.

---

## 6. How to Reproduce Validation Results

All unit tests and perturbation audits can be executed locally in 0.3 seconds:

```bash
# Clone the repository
git clone https://github.com/shivanshchoubey2025-collab/deck-diligence-ai.git
cd deck-diligence-ai

# Checkout frozen validation tag
git checkout v0.1-validation

# Activate virtual environment and run test suite
pytest -v
```

Expected output:
```text
============================= 23 passed in 0.28s ==============================
```
