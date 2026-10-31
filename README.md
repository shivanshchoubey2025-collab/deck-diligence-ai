# Venture Capital Diligence & Screening Engine (DeckDiligence.ai)

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.42%2B-FF4B4B.svg?logo=streamlit)](https://streamlit.io)
[![Focus](https://img.shields.io/badge/Domain-Venture%20Capital%20%26%20Tech%20Diligence-emerald.svg)](https://github.com)
[![License](https://img.shields.io/badge/License-MIT-orange.svg)](LICENSE)

An institutional-grade **Venture Capital Diligence & Tech Audit Platform** engineered for Tier-1 Venture Capital firms (Peak XV, Founders Fund, Accel, Lightspeed, Bessemer). Designed to automate pitch deck ingestion, uncover economic and unit-economic red flags, audit codebase technical defensibility (AI wrapper vs. proprietary systems moat), and simulate multi-round cap table dilution and liquidation preference exit waterfalls ($5M to $1 Billion).

---

## 🏛️ Core Architectural Pillars & Features

DeckDiligence.ai is organized into **4 Tier-1 Venture Upgrades**:

### 1. 🔍 Heuristic Bullshit Detector & 11-Slide Deck Studio (`deck_screener.py`, `app.py`)
- Cross-references claimed metrics against institutional venture benchmarks (Bessemer, Craft Ventures, YC).
- Implements the **6-Point Sanity Audit**: TAM validation, token COGS gross margin ceiling, CAC payback velocity, Burn Multiple ($Net\ Burn / Net\ New\ ARR$), ARR multiple discipline, and technical founder leverage.
- Interactive 11-Slide Deck Studio rendering Sequoia-style executive slides with dynamic metric overlays.

### 2. 📑 End-to-End PDF Pitch Deck Ingestion & VC Generator (`pdf_deck_parser.py`, `generate_sample_pdf_deck.py`)
- Direct ingestion and parsing of binary PDF pitch decks using structured regex and page extraction.
- Automatic extraction of ARR, burn rate, cash runaway, TAM, customer count, and round terms.
- Bundled ReportLab generator producing `Sample_Pitch_Deck_CogniFlow.pdf`, a dark-mode 16:9 executive presentation formatted for institutional Investment Committees.

### 3. 🔬 Tier-1 Tech Moat & AI Wrapper Code Scanner (`tech_moat_scanner.py`)
- Institutional code audit engine analyzing repository dependencies (`requirements.txt`, `pyproject.toml`) and source files (`main.py`, backend pipelines).
- Calculates the **AI Wrapper Index (%)**, **OpenAI Extinction Risk Level**, **Gross Margin Ceiling Cap (%)**, and **Defensibility Score (0-100)**.
- Distinguishes superficial third-party API pass-through wrappers (LangChain, OpenAI, LiteLLM) from true proprietary deeptech infrastructure (vLLM, TensorRT-LLM, Triton, ONNX Runtime, eBPF, Ray).

### 4. 💰 Cap Table Dilution & Liquidation Preference Exit Waterfall (`cap_table_waterfall.py`)
- Models multi-round equity dilution progression: **Founders (100%) → Seed ($2.5M) → Series A ($10M) → Series B ($25M)** with option pool (ESOP) shuffle dynamics.
- Implements senior-to-junior liquidation preference waterwalls:
  - **1x Non-Participating Preferred (NVCA Standard)**: Automatically models the **Conversion Crossover Hurdle** ($X^* = \text{Invested} / \text{Ownership}\%$) where preferred converts to common.
  - **1x Participating Preferred ("Double Dipping")**: Simulates aggressive term sheets where investors take preference plus pro-rata common pool.
- Computes aggregate **$37.5M Downside Preference Stack** and runs multi-exit scenarios ($10M, $25M, $50M, $100M, $200M, $350M, $500M, $1 Billion) with Multiple on Invested Capital (MoIC) across all tranches.

---

## 📂 Repository Contents

```text
├── app.py                         # 6-Tab Streamlit Interactive VC Diligence Dashboard
├── cap_table_waterfall.py         # Institutional Cap Table & Liquidation Preference Waterfall Engine
├── tech_moat_scanner.py           # AST & Dependency Tech Moat & AI Wrapper Auditor
├── pdf_deck_parser.py             # Binary PDF Pitch Deck Ingestion & Extraction Engine
├── generate_sample_pdf_deck.py    # ReportLab 16:9 Landscape Dark-Mode Pitch Deck Generator
├── Sample_Pitch_Deck_CogniFlow.pdf# Generated 11-Slide Institutional PDF Pitch Deck
├── deck_screener.py               # 6-Point Heuristic Sanity Auditor & IC Memo Generator
├── vc_metrics_modeler.py          # SaaS Venture Economics & Power Law Fund Return Engine
├── valuation_engine.py            # Indian Equities DCF & WACC Sensitivity Modeler
├── sample_deck_cogniflow.json     # Benchmark Pitch Deck 1: High-conviction AI infrastructure
├── sample_deck_fluff.json         # Benchmark Pitch Deck 2: Hype-driven AI wrapper
├── IC_Screening_Memo_CogniFlow.md # Generated 1-Page Investment Committee Screening Memo (Invest)
├── IC_Screening_Memo_HyperBuzz.md # Generated 1-Page Investment Committee Screening Memo (Pass)
├── vc_resume_template.md          # WSO/Harvard 1-page VC Candidate Resume template
├── cold_outreach_templates.md     # High-conversion cold email templates for Indian VCs
└── requirements.txt               # Locked Python dependencies
```

---

## 🚀 Running the Interactive Dashboard (Streamlit)

Launch the interactive dark-mode dashboard in your browser:

```powershell
cd C:\Users\harsh\.gemini\antigravity\scratch\finance_career_transition
.\.venv\Scripts\streamlit run app.py
```

### Dashboard Tabs:
1. **🔍 Heuristic Bullshit Detector**: Red flags, unit economics audits, and VC benchmark alerts.
2. **📊 Core Venture Metrics**: LTV/CAC, Payback months, NDR, Magic Number, and David Sacks Burn Multiple.
3. **🎴 11-Slide Deck Studio**: 16:9 executive presentation cards with real-time financial overrides.
4. **🔬 Tech Moat Code Scanner**: Automated dependency audit, Wrapper Index %, and Gross Margin ceiling.
5. **💰 Cap Table & Exit Waterfall**: Interactive Exit Slider ($5M–$1B), 1x Non-Participating vs Participating toggles, conversion crossover hurdles, and shareholder return charts.
6. **📄 1-Page Investment Memo**: Instant institutional markdown IC memo with 1-click download.

---

## ⚡ Running Standalone CLI Engines

### Cap Table & Exit Waterfall Engine
```powershell
.\.venv\Scripts\python cap_table_waterfall.py
```

### Tech Moat Code Scanner
```powershell
.\.venv\Scripts\python tech_moat_scanner.py
```

### PDF Deck Ingestion & ReportLab Generation
```powershell
.\.venv\Scripts\python generate_sample_pdf_deck.py
.\.venv\Scripts\python pdf_deck_parser.py
```

### SaaS Economics & Power Law Fund Math
```powershell
.\.venv\Scripts\python vc_metrics_modeler.py
```

### Indian Equities DCF Valuation Engine
```powershell
.\.venv\Scripts\python valuation_engine.py
```

---

## 👤 Author

**Shivansh Choubey**  
- GitHub: [@shivanshchoubey2025-collab](https://github.com/shivanshchoubey2025-collab)  
- Focus: Computer Science & Engineering, Tech Due Diligence, Venture Capital  
- Institution: Vellore Institute of Technology (VIT), Chennai
