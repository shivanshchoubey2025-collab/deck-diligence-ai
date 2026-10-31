# Venture Capital & Tech Due Diligence Toolkit (DeckDiligence.ai)

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python)](https://python.org)
[![Focus](https://img.shields.io/badge/Domain-Venture%20Capital%20%26%20Tech%20Diligence-emerald.svg)](https://github.com)
[![License](https://img.shields.io/badge/License-MIT-orange.svg)](LICENSE)

An institutional-grade **Venture Capital Diligence & Screening Engine** built for evaluating early-stage tech, B2B SaaS, and Generative AI startups. Designed to automate pitch deck screening, audit startup unit economics against venture benchmarks, and run power law fund-return simulations.

---

## 📂 Repository Contents

```text
├── deck_screener.py              # DeckDiligence.ai: Automated Pitch Deck Screener & Sanity Auditor
├── vc_metrics_modeler.py         # SaaS Unit Economics & Power Law Fund Return Engine
├── valuation_engine.py           # Institutional DCF Valuation Engine for Indian Equities
├── sample_deck_cogniflow.json    # Test Case 1: High-conviction AI infrastructure pitch deck
├── sample_deck_fluff.json        # Test Case 2: Hype-driven AI wrapper with economic red flags
├── IC_Screening_Memo_CogniFlow.md# Generated 1-Page Investment Committee Screening Memo (Green)
├── IC_Screening_Memo_HyperBuzz.md# Generated 1-Page Investment Committee Screening Memo (Rejected)
├── vc_investment_memo_sample.md  # Deep-dive Series A IC Memo template
├── vc_resume_template.md         # WSO/Harvard 1-page VC Candidate Resume template
├── cold_outreach_templates.md    # High-conversion cold email templates for Indian VCs
└── README.md                     # This documentation
```

---

## 🚀 Running the Interactive Web Dashboard (Streamlit)

Launch the interactive dark-mode dashboard in your browser:

```powershell
cd C:\Users\harsh\.gemini\antigravity\scratch\finance_career_transition
.\.venv\Scripts\streamlit run app.py
```

### Dashboard Features:
- **Benchmark Selector**: Toggle between *CogniFlow AI* (High-Conviction) and *HyperBuzz AI* (Hype Wrapper), or upload a custom pitch deck JSON.
- **Live Term Sheet Overrides**: Interactive sliders for Round Ask, Post-Money Valuation, and Gross Margins with instant re-calculation.
- **Visual Health Score & Verdict Banner**: Dynamic green/yellow/red color-coded status.
- **Heuristic Red Flag Breakdown**: Expandable diagnostic cards for TAM, CAC, Burn Multiples, and Moats.
- **1-Click IC Memo Export**: Download the generated 1-Page Investment Committee Memo in Markdown.

---

## ⚡ Running via Command-Line Interface (CLI)

### The 6-Point Heuristic "Bullshit Detector"
`deck_screener.py` runs a multi-point quantitative sanity check on every pitch deck:
1. **TAM Reality Check**: Flags mathematical disconnects between claimed top-down TAM and bottom-up customer volume $\times$ ACV.
2. **AI Margin Diligence**: Detects artificial gross margins on pure third-party LLM API pass-through wrappers vs. defensible local SLM fine-tuning.
3. **CAC Payback Velocity**: Audits payback periods against the venture benchmark ($<12\text{ months}$).
4. **Burn Multiple (David Sacks / Craft Ventures)**: Measures capital efficiency ($\text{Net Burn} / \text{Net New ARR}$).
5. **Valuation Multiple Discipline**: Benchmarks round ask against normalized Seed/Series A ARR multiples ($15\times - 25\times$).
6. **Technical Founder Moat**: Checks for engineering/systems leadership in deeptech ventures.

---

## 📊 Running the VC Metrics & Fund Return Modeler

```bash
python vc_metrics_modeler.py
```

### What It Calculates:
* **LTV : CAC Ratio & Payback**: Customer lifetime derived from monthly churn, gross margins, and ARPU.
* **Net Dollar Retention (NDR)**: Account expansion vs. contraction over annual cohorts.
* **Power Law Fund Return Math**: Computes exact exit valuations required to return 1x or 3x on a \$100M venture fund accounting for subsequent round dilution.

---

## 📈 Running the Indian Equities DCF Valuation Engine

```bash
python valuation_engine.py
```

* Computes **WACC** under Indian macro conditions (10-Yr G-Sec yield, Damodaran India ERP, beta).
* Projects 5-year **Unlevered Free Cash Flows (UFCF)**.
* Evaluates **Dual Terminal Value** (Gordon Growth vs. Exit Multiple) with a 2D sensitivity matrix.

---

## 👤 Author

**Shivansh Choubey**  
- GitHub: [@shivanshchoubey2025-collab](https://github.com/shivanshchoubey2025-collab)  
- Focus: Computer Science & Engineering, Tech Due Diligence, Venture Capital
