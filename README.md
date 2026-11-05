# DeckDiligence.ai — Pitch Deck Screener & Cap Table Diligence Engine

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.42%2B-FF4B4B.svg?logo=streamlit)](https://streamlit.io)
[![Tests](https://github.com/shivanshchoubey2025-collab/deck-diligence-ai/actions/workflows/tests.yml/badge.svg)](https://github.com/shivanshchoubey2025-collab/deck-diligence-ai/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An open-source **Pitch Deck Screener & Venture Diligence Engine** designed for early-stage B2B SaaS and AI startups. Benchmarked against established venture underwriting frameworks (Craft Ventures, Bessemer Cloud Index, Y Combinator, and NVCA term sheet conventions).

The toolkit automates preliminary quantitative sanity audits on pitch deck claims, reconciles dependency manifests against Python source code ASTs to identify API pass-through risk, and models multi-round cap table dilution and liquidation preference exit waterfalls ($1M to $1 Billion).

---

## 🏛️ Core Modules & Functionality

### 1. 🔍 Quantitative Sanity Auditor (`deck_screener.py`)
- Cross-references claimed startup metrics against venture benchmarks:
  - **Audit Coverage & Refusal**: Enforces a minimum quantitative coverage threshold ($\ge 3$ of 6 sanity audits required to render an IC verdict; fewer than 3 triggers an explicit `INSUFFICIENT DATA / REFUSE VERDICT`).
  - **TAM Reality Check**: Flags top-down vs. bottom-up market sizing disconnects ($>10\times$ disparity triggers red flag; $4\times\text{--}10\times$ triggers caution).
  - **Gross Margin Diligence**: Flags pure API pass-through GenAI wrappers claiming $>80\%$ gross margins without local inference layers.
  - **CAC Payback Velocity**: Categorizes customer acquisition payback into $<12\text{ mo}$ (Elite), $12\text{--}18\text{ mo}$ (Moderate), and $>18\text{ mo}$ (Sluggish).
  - **Burn Multiple (David Sacks / Craft Ventures)**: Evaluates capital efficiency ($\text{Annual Net Burn} / \text{Net New ARR}$) across $\le 1.0\times$ (Elite), $1.0\times\text{--}2.0\times$ (Acceptable / Good), and $>2.0\times$ (Inefficient).
  - **Valuation Multiple Discipline**: Evaluates round pricing across $\le 20\times$ (Disciplined), $20\times\text{--}30\times$ (Growth Premium), and $>30\times$ (Excessive).
  - **Data Disclosure Gaps**: Explicitly flags omitted unit economics as unverified data gaps rather than fabricating benign fallback defaults.
- Generates a structured **1-Page Investment Committee (IC) Screening Memo** in Markdown.

### 2. 🔬 Dependency & AST Architecture Auditor (`tech_moat_scanner.py`)
- Uses Python's standard `ast` module (`ast.NodeVisitor`) to inspect verified code import sites (`ast.Import`, `ast.ImportFrom`), ignoring comments and string documentation.
- Enforces **Declared vs. Used Reconciliation**: declared manifest dependencies only receive architectural credit if they are actually imported in the provided source code.
- Maps PyPI package names to canonical Python import modules (e.g., `scikit-learn` $\rightarrow$ `sklearn`, `langchain-core` $\rightarrow$ `langchain_core`, `flash-attn` $\rightarrow$ `flash_attn`). Excludes general utility libraries (`numpy`, `redis`, `docker`) from deeptech moat scoring.
- Flags unparseable source code snippets with explicit syntax errors rather than falling back to regex.
- Incurs benchmarked gross margin ceilings (55% for pure API wrappers, 68% for hybrid, 80% for self-hosted/kernel systems) reflecting token COGS drag.

### 3. 💰 Cap Table Dilution & Liquidation Preference Waterfall (`cap_table_waterfall.py`)
- Models multi-round equity progression: **Founders (100%) → Seed ($2.5M) → Series A ($10M) → Series B ($25M)** with unallocated option pool (ESOP) dilution.
- Executes an **equilibrium-based liquidation preference waterfall** across all $2^N$ conversion states:
  - **1x Non-Participating Preferred**: Solves the exact bilateral Nash Equilibrium condition where no preferred investor has unilateral regret (converting if and only if pro-rata common payout strictly exceeds liquidation preference).
  - **1x Participating Preferred ("Double Dipping")**: Simulates terms where investors take 1x preference plus pro-rata common proceeds.
  - Computes the aggregate **$37.5M Senior Preference Stack Floor** where common stock is wiped out at exits $\le \$37.5\text{M}$.
  - Verified by a 400-point sweep test ($1M to $400M) confirming zero unilateral regret across all exit levels.

---

## ⚠️ Diligence Limitations & Scope Boundaries

1. **Preliminary Quantitative Filter**: This tool is designed for top-of-funnel screening and Investment Committee memo preparation. It does not replace qualitative customer reference calls, founder background checks, or commercial legal diligence.
2. **Architectural vs. Commercial Moats**: Dependency and AST scanning measures technical architecture, inference cost exposure, and foundation model dependency. It cannot measure commercial moats such as high switching costs, regulatory licensing, enterprise workflow stickiness, or proprietary dataset network effects.
3. **Conversion Crossover Interpretation**: The standard theoretical crossover formula ($X^* = \text{Invested} / \text{Ownership}\%$) represents the hurdle when all preferred shareholders convert. For mixed-outcome exits, the engine models the full equilibrium across seniority tranches.
4. **Option Pool (ESOP) Simplification**: The engine models the option pool as issued common equity at exit; it does not model option strike price exercise cash inflows or cancellation of unvested options returning to common.

---

## 📂 Repository Contents

```text
├── app.py                         # 6-Tab Streamlit Interactive VC Diligence Dashboard
├── cap_table_waterfall.py         # Cap Table & Liquidation Preference Waterfall Engine
├── tech_moat_scanner.py           # Dependency & AST Architecture Auditor
├── deck_screener.py               # Quantitative Pitch Deck Screener & IC Memo Generator
├── pdf_deck_parser.py             # Binary PDF Pitch Deck Ingestion & Extraction Engine
├── generate_sample_pdf_deck.py    # ReportLab 16:9 Landscape Dark-Mode Pitch Deck Generator
├── Sample_Pitch_Deck_CogniFlow.pdf# Generated 11-Slide Benchmark PDF Pitch Deck
├── sample_deck_cogniflow.json     # Test Case 1: High-conviction AI infrastructure
├── sample_deck_fluff.json         # Test Case 2: Hype-driven AI wrapper
├── test_cap_table_waterfall.py    # Unit tests for Cap Table & Waterfall Engine (incl. 400-point sweep)
├── test_deck_screener.py          # Unit tests for Pitch Deck Screener & Sanity Auditor
├── test_perturbations.py          # Controlled 6-variable audit perturbation test suite
├── test_tech_moat_scanner.py      # Unit tests for AST & Dependency Auditor
├── VALIDATION.md                  # Pre-registered validation protocol & 8-case backtesting report
├── templates/                     # Objective extraction schemas & slide citation templates
│   └── deck_extraction_template.json
├── requirements.txt               # Pinned dependencies
├── LICENSE                        # MIT License
├── .github/workflows/tests.yml    # Continuous Integration (CI) Pytest Workflow
├── career_prep/                   # Candidate career assets & financial valuation scripts
│   ├── vc_resume_template.md
│   ├── cold_outreach_templates.md
│   ├── vc_investment_memo_sample.md
│   ├── valuation_engine.py
│   └── vc_metrics_modeler.py
└── README.md                     # Documentation
```

---

## 🧪 Running the Unit Test Suite

Run the full pytest suite (23 automated test cases covering mathematical invariants, AST parsing, threshold boundaries, audit coverage refusal, and single-variable perturbation isolation):

```bash
pytest -v
```

---

## 📋 Model Validation & Backtesting

See [`VALIDATION.md`](VALIDATION.md) for the complete pre-registered validation protocol (frozen under git tag `v0.1-validation`), including:
1. **Perturbation Test Suite**: Verification of audit orthogonality (6 single-variable perturbations flipping strictly the targeted audit with zero cross-contamination).
2. **Balanced 8-Case Backtesting Dataset**: Front (2016 Series A), Segment (2015 Series B), Fast.co (2020 Series A), WeWork (2014 S-1), Jasper AI (2022 Series A), Mixpanel (2012 Series A), Coinbase (2012 Seed — Out of Scope), and Theranos (2006 — Data Void).
3. **What Held Up vs. Known Failure Modes**: Analysis of category-creation TAM penalties and seed-stage burn multiple variance.

---

## 🚀 Running the Interactive Web Dashboard (Streamlit)

```bash
pip install -r requirements.txt
streamlit run app.py
```

### Dashboard Tabs:
1. **🔍 Quantitative Sanity Auditor**: Red flags, data disclosure gaps, and unit economics audits.
2. **📊 Core Venture Metrics**: LTV/CAC, Payback months, NDR, Magic Number, and Burn Multiple.
3. **🎴 11-Slide Deck Studio**: 16:9 presentation slides with real-time financial overrides.
4. **🔬 Tech Moat Code Scanner**: Dependency AST analysis, Wrapper Index %, and Gross Margin ceiling.
5. **💰 Cap Table & Exit Waterfall**: Interactive Exit Slider ($5M–$1B), 1x Non-Participating vs. Participating toggles, and payout ledgers.
6. **📄 1-Page Investment Memo**: Instant markdown IC memo with 1-click download.

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
