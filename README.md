# DeckDiligence.ai — Venture Capital Screening & Tech Due Diligence Copilot

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.42%2B-FF4B4B.svg?logo=streamlit)](https://streamlit.io)
[![Tests](https://img.shields.io/badge/Tests-12%20Passed-brightgreen.svg)](test_cap_table_waterfall.py)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An open-source **Venture Capital Diligence & Screening Copilot** designed for early-stage B2B SaaS, developer tools, and AI startups. Benchmarked against established venture underwriting frameworks (Craft Ventures, Bessemer Cloud Index, Y Combinator, and NVCA standards).

The engine automates preliminary pitch deck sanity auditing, analyzes dependency manifests via Python AST parsing to assess OpenAI API pass-through risk, and simulates multi-round cap table dilution and liquidation preference waterfalls ($5M to $1 Billion).

---

## 🏛️ Core Modules & Functionality

### 1. 🔍 Heuristic Pitch Deck Auditor (`deck_screener.py`)
- Cross-references claimed startup metrics against venture benchmarks:
  - **TAM Reality Check**: Flags top-down vs. bottom-up market sizing disconnects ($>10\times$ disparity triggers red flag).
  - **Gross Margin Diligence**: Flags pure API pass-through GenAI wrappers claiming $>80\%$ gross margins without local inference layers.
  - **CAC Payback Velocity**: Categorizes customer acquisition payback into $<12\text{ mo}$ (Elite), $12\text{--}18\text{ mo}$ (Moderate), and $>18\text{ mo}$ (Sluggish).
  - **Burn Multiple (David Sacks / Craft Ventures)**: Evaluates capital efficiency ($\text{Annual Net Burn} / \text{Net New ARR}$) across $\le 1.0\times$ (Elite), $1.0\times\text{--}2.0\times$ (Acceptable), and $>2.0\times$ (Inefficient).
  - **Data Disclosure Gaps**: Explicitly flags omitted unit economics rather than fabricating benign fallback defaults.
- Generates a structured **1-Page Investment Committee (IC) Screening Memo** in Markdown.

### 2. 🔬 Dependency & AST Architecture Auditor (`tech_moat_scanner.py`)
- Uses Python's standard `ast` module (`ast.NodeVisitor`) to inspect verified code import sites (`ast.Import`, `ast.ImportFrom`), ignoring comments and string documentation.
- Scans `requirements.txt`, `package.json`, and source code to identify pass-through wrappers (LangChain, OpenAI, CrewAI) vs. native systems/deeptech layers (vLLM, Triton, PyTorch, bcc/eBPF, Ray).
- Computes an **AI Wrapper Index (%)**, platform commoditization risk, and benchmarked gross margin ceilings (50–65% for pure API wrappers vs. 75–85% for self-hosted/hybrid compute).

### 3. 💰 Cap Table Dilution & Liquidation Preference Waterfall (`cap_table_waterfall.py`)
- Models multi-round equity progression: **Founders (100%) → Seed ($2.5M) → Series A ($10M) → Series B ($25M)** with unallocated option pool (ESOP) dilution.
- Executes an **equilibrium-based liquidation preference waterfall** across all $2^N$ conversion states:
  - **1x Non-Participating Preferred**: Solves the exact conversion equilibrium ensuring no preferred investor rationally converts into less than their 1x preference.
  - **1x Participating Preferred ("Double Dipping")**: Simulates off-market terms where investors take 1x preference plus pro-rata common proceeds.
  - Computes the aggregate **$37.5M Senior Preference Stack Floor** where common stock is wiped out at exits $\le \$37.5\text{M}$.

---

## ⚠️ Diligence Limitations & Scope Boundaries

1. **Preliminary Quantitative Filter**: This tool is designed for top-of-funnel screening and Investment Committee memo preparation. It does not replace qualitative customer reference calls, founder background checks, or commercial diligence.
2. **Architectural vs. Business Moats**: Dependency and AST scanning measures technical architecture, inference cost exposure, and foundation model dependency. It cannot measure commercial moats such as high switching costs, regulatory licensing, enterprise workflow stickiness, or proprietary dataset network effects.
3. **Conversion Crossover Interpretation**: The standard theoretical crossover formula ($X^* = \text{Invested} / \text{Ownership}\%$) represents the hurdle when all preferred shareholders convert. For mixed-outcome exits, the engine models the full equilibrium across seniority tranches.

---

## 📂 Repository Contents

```text
├── app.py                         # 6-Tab Streamlit Interactive VC Diligence Dashboard
├── cap_table_waterfall.py         # Institutional Cap Table & Liquidation Preference Waterfall Engine
├── tech_moat_scanner.py           # Dependency & AST Architecture Auditor
├── deck_screener.py               # 6-Point Heuristic Pitch Deck Auditor & IC Memo Generator
├── pdf_deck_parser.py             # Binary PDF Pitch Deck Ingestion & Extraction Engine
├── generate_sample_pdf_deck.py    # ReportLab 16:9 Landscape Dark-Mode Pitch Deck Generator
├── Sample_Pitch_Deck_CogniFlow.pdf# Generated 11-Slide Benchmark PDF Pitch Deck
├── sample_deck_cogniflow.json     # Test Case 1: High-conviction AI infrastructure
├── sample_deck_fluff.json         # Test Case 2: Hype-driven AI wrapper
├── test_cap_table_waterfall.py    # Unit tests for Cap Table & Waterfall Engine
├── test_deck_screener.py          # Unit tests for Pitch Deck Screener & Sanity Auditor
├── test_tech_moat_scanner.py      # Unit tests for AST & Dependency Auditor
├── requirements.txt               # Pinned dependencies
├── LICENSE                        # MIT License
└── README.md                     # Documentation
```

---

## 🧪 Running the Unit Test Suite

Run the full pytest suite (12 test cases covering mathematical invariants, AST parsing, and threshold boundaries):

```bash
pytest -v
```

---

## 🚀 Running the Interactive Web Dashboard (Streamlit)

```bash
pip install -r requirements.txt
streamlit run app.py
```

### Dashboard Tabs:
1. **🔍 Heuristic Bullshit Detector**: Red flags, data disclosure gaps, and unit economics audits.
2. **📊 Core Venture Metrics**: LTV/CAC, Payback months, NDR, Magic Number, and Burn Multiple.
3. **🎴 11-Slide Deck Studio**: 16:9 presentation slides with real-time financial overrides.
4. **🔬 Tech Moat Code Scanner**: Dependency AST analysis, Wrapper Index %, and Gross Margin ceiling.
5. **💰 Cap Table & Exit Waterfall**: Interactive Exit Slider ($5M–$1B), 1x Non-Participating vs. Participating toggles, and payout ledgers.
6. **📄 1-Page Investment Memo**: Instant markdown IC memo with 1-click download.

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
