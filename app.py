r"""
========================================================================================
DECKDILIGENCE.AI — STREAMLIT INTERACTIVE VC DUE DILIGENCE DASHBOARD
----------------------------------------------------------------------------------------
Target: Venture Capital (VC) Partners, Associates & Analysts
Framework: Y Combinator, Craft Ventures (David Sacks), and Bessemer Cloud Benchmarks
========================================================================================
Run via:
  .\.venv\Scripts\streamlit run app.py
========================================================================================
"""

import os
import json
import streamlit as st
import pandas as pd
import altair as alt
from deck_screener import PitchDeckScreener, AuditFlag
from pdf_deck_parser import PDFPitchDeckParser
from tech_moat_scanner import (
    TechMoatScanner,
    COGNIFLOW_REQUIREMENTS,
    COGNIFLOW_CODE_SAMPLE,
    HYPERBUZZ_REQUIREMENTS,
    HYPERBUZZ_CODE_SAMPLE
)
from cap_table_waterfall import CapTableWaterfallEngine

st.set_page_config(
    page_title="DeckDiligence.ai | VC Pitch Deck Screener",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .metric-card {
        background-color: #1e2130;
        padding: 1.2rem;
        border-radius: 10px;
        border: 1px solid #2e344e;
        margin-bottom: 1rem;
    }
    .score-green {
        color: #00E676;
        font-size: 2.2rem;
        font-weight: 800;
    }
    .score-yellow {
        color: #FFD600;
        font-size: 2.2rem;
        font-weight: 800;
    }
    .score-red {
        color: #FF1744;
        font-size: 2.2rem;
        font-weight: 800;
    }
    .verdict-box {
        padding: 1rem 1.5rem;
        border-radius: 8px;
        font-weight: 700;
        font-size: 1.2rem;
        margin-bottom: 1.5rem;
    }
    .slide-card {
        background: linear-gradient(135deg, #16192b 0%, #1c223a 100%);
        padding: 2.2rem;
        border-radius: 14px;
        border: 2px solid #3b4568;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
        margin: 1.5rem 0;
        color: #f7fafc;
    }
    .slide-header {
        color: #63b3ed;
        font-size: 1.1rem;
        letter-spacing: 2px;
        font-weight: 800;
        text-transform: uppercase;
    }
    .slide-title {
        color: #ffffff;
        font-size: 2.0rem;
        font-weight: 800;
        margin-top: 0.5rem;
        margin-bottom: 1.5rem;
    }
    .slide-content {
        font-size: 1.15rem;
        line-height: 1.7;
        color: #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)

# Directory Setup
base_dir = os.path.dirname(os.path.abspath(__file__))
cogniflow_path = os.path.join(base_dir, "sample_deck_cogniflow.json")
fluff_path = os.path.join(base_dir, "sample_deck_fluff.json")
sample_pdf_path = os.path.join(base_dir, "Sample_Pitch_Deck_CogniFlow.pdf")

# -----------------------------------------------------------------------------
# SIDEBAR: Startup Selection & Real-Time Parameter Overrides
# -----------------------------------------------------------------------------
st.sidebar.title("💼 DeckDiligence.ai")
st.sidebar.caption("Automated VC Pitch Deck Diligence & Sanity Engine")

demo_choice = st.sidebar.selectbox(
    "Select Input Source:",
    [
        "CogniFlow AI (High-Conviction Series Seed)",
        "HyperBuzz AI (Hype-Driven AI Wrapper)",
        "📄 Sample PDF Pitch Deck (11-Slide PDF Parser)",
        "📤 Upload Pitch Deck (.pdf or .json)"
    ]
)

deck_data = {}
if demo_choice == "CogniFlow AI (High-Conviction Series Seed)":
    with open(cogniflow_path, "r", encoding="utf-8") as f:
        deck_data = json.load(f)
elif demo_choice == "HyperBuzz AI (Hype-Driven AI Wrapper)":
    with open(fluff_path, "r", encoding="utf-8") as f:
        deck_data = json.load(f)
elif demo_choice == "📄 Sample PDF Pitch Deck (11-Slide PDF Parser)":
    parser = PDFPitchDeckParser(sample_pdf_path)
    deck_data = parser.parse_to_structured_deck()
    st.sidebar.success(f"✅ Extracted {parser.total_slides} slides from PDF!")
else:
    uploaded_file = st.sidebar.file_uploader("Upload Pitch Deck (PDF or JSON)", type=["pdf", "json"])
    if uploaded_file is not None:
        if uploaded_file.name.lower().endswith(".pdf"):
            parser = PDFPitchDeckParser(uploaded_file)
            deck_data = parser.parse_to_structured_deck()
            st.sidebar.success(f"✅ Extracted {parser.total_slides} slides from `{uploaded_file.name}`!")
        else:
            deck_data = json.load(uploaded_file)
            st.sidebar.success("✅ Loaded JSON spec successfully!")
    else:
        with open(cogniflow_path, "r", encoding="utf-8") as f:
            deck_data = json.load(f)

# Interactive Overrides in Sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Live Term Sheet Adjustments")

col_sb1, col_sb2 = st.sidebar.columns(2)
with col_sb1:
    ask_input = st.number_input("Round Ask ($M)", value=float(deck_data.get("funding_ask_usd", 2.5e6)) / 1e6, step=0.5)
with col_sb2:
    val_input = st.number_input("Post-Money ($M)", value=float(deck_data.get("claimed_post_money_valuation_usd", 18.0e6)) / 1e6, step=1.0)

deck_data["funding_ask_usd"] = ask_input * 1e6
deck_data["claimed_post_money_valuation_usd"] = val_input * 1e6

claimed_metrics = deck_data.get("claimed_metrics", {})
gross_margin_slider = st.sidebar.slider(
    "Claimed Gross Margin (%)",
    min_value=40, max_value=99,
    value=int(claimed_metrics.get("claimed_gross_margin_pct", 0.85) * 100)
)
claimed_metrics["claimed_gross_margin_pct"] = gross_margin_slider / 100.0

tech_founder_toggle = st.sidebar.toggle("Has Technical Founder?", value=bool(claimed_metrics.get("has_technical_founder", True)))
claimed_metrics["has_technical_founder"] = tech_founder_toggle

local_slm_toggle = st.sidebar.toggle("Has Local SLM / Fine-Tuned Layer?", value=bool(claimed_metrics.get("has_local_fine_tuned_models", True)))
claimed_metrics["has_local_fine_tuned_models"] = local_slm_toggle

# -----------------------------------------------------------------------------
# ENGINE EXECUTION
# -----------------------------------------------------------------------------
screener = PitchDeckScreener(deck_data)
screener.compute_derived_metrics()
screener.run_sanity_audits()
verdict, verdict_desc = screener.get_verdict()

# -----------------------------------------------------------------------------
# MAIN DASHBOARD VIEW
# -----------------------------------------------------------------------------
st.title(f"🚀 {screener.company_name}")
st.write(f"*{screener.tagline}*")
st.caption(f"**Sector**: {screener.sector} | **Stage**: {screener.stage} | **Location**: {deck_data.get('headquarters', 'Global')}")

# Top KPI Summary Cards
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    score = screener.health_score
    color_class = "score-green" if score >= 75 else ("score-yellow" if score >= 50 else "score-red")
    st.markdown(f"""
    <div class="metric-card">
        <div style="font-size: 0.9rem; color: #a0aec0;">DILIGENCE HEALTH SCORE</div>
        <div class="{color_class}">{score} <span style="font-size: 1.2rem; color: #718096;">/ 100</span></div>
    </div>
    """, unsafe_allow_html=True)

with kpi2:
    st.markdown(f"""
    <div class="metric-card">
        <div style="font-size: 0.9rem; color: #a0aec0;">ARR / REVENUE RUN-RATE</div>
        <div style="font-size: 1.8rem; font-weight: 700; color: #e2e8f0;">${screener.computed['arr']:,.0f}</div>
        <div style="font-size: 0.8rem; color: #718096;">MRR: ${screener.computed['mrr']:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)

with kpi3:
    ltv_cac = screener.computed['ltv_cac']
    ltv_color = "#00E676" if ltv_cac >= 3.0 else "#FF1744"
    st.markdown(f"""
    <div class="metric-card">
        <div style="font-size: 0.9rem; color: #a0aec0;">INFERRED LTV : CAC</div>
        <div style="font-size: 1.8rem; font-weight: 700; color: {ltv_color};">{ltv_cac:.1f}x</div>
        <div style="font-size: 0.8rem; color: #718096;">Benchmark: > 3.0x</div>
    </div>
    """, unsafe_allow_html=True)

with kpi4:
    burn_mult = screener.computed['burn_multiple']
    burn_color = "#00E676" if burn_mult <= 1.2 else "#FF1744"
    st.markdown(f"""
    <div class="metric-card">
        <div style="font-size: 0.9rem; color: #a0aec0;">BURN MULTIPLE</div>
        <div style="font-size: 1.8rem; font-weight: 700; color: {burn_color};">{burn_mult:.2f}x</div>
        <div style="font-size: 0.8rem; color: #718096;">Net Burn / Net New ARR</div>
    </div>
    """, unsafe_allow_html=True)

# Verdict Banner
if verdict == "PRIORITY PARTNER CALL":
    st.success(f"### ✅ VERDICT: [{verdict}]\n**Action Plan**: {verdict_desc}")
elif verdict == "EXPLORE WITH CAUTION":
    st.warning(f"### ⚠️ VERDICT: [{verdict}]\n**Action Plan**: {verdict_desc}")
else:
    st.error(f"### 🚨 VERDICT: [{verdict}]\n**Action Plan**: {verdict_desc}")

# -----------------------------------------------------------------------------
# TABS: Diligence Findings, Metrics, 11-Slide Studio, Tech Moat, Waterfall, Memo
# -----------------------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🔍 Quantitative Sanity Auditor",
    "📊 Core Venture Metrics",
    "🎴 11-Slide Deck Studio",
    "🔬 Tech Moat Code Scanner",
    "💰 Cap Table & Exit Waterfall",
    "📄 1-Page Investment Memo"
])

with tab1:
    st.subheader("Automated Sanity Audits & Red Flags")
    st.write("Cross-referencing claimed numbers against early-stage benchmarks:")

    for i, flag in enumerate(screener.flags, 1):
        if flag.severity == "RED":
            with st.expander(f"🚨 **RED FLAG {i}**: {flag.category} — {flag.title}", expanded=True):
                st.error(f"**Finding**: {flag.finding}")
                st.info(f"**VC Benchmark**: {flag.benchmark}")
                st.caption(f"**Investment Impact**: {flag.impact}")
        elif flag.severity == "YELLOW":
            with st.expander(f"⚠️ **CAUTION {i}**: {flag.category} — {flag.title}", expanded=False):
                st.warning(f"**Finding**: {flag.finding}")
                st.info(f"**VC Benchmark**: {flag.benchmark}")
                st.caption(f"**Investment Impact**: {flag.impact}")
        else:
            with st.expander(f"🟢 **POSITIVE SIGNAL {i}**: {flag.category} — {flag.title}", expanded=False):
                st.success(f"**Finding**: {flag.finding}")
                st.info(f"**VC Benchmark**: {flag.benchmark}")
                st.caption(f"**Investment Impact**: {flag.impact}")

with tab2:
    st.subheader("Quantitative Health Metrics Comparison")
    
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.markdown("#### Sales Efficiency & Unit Economics")
        st.table({
            "Metric": ["Current ARR", "Monthly MRR", "Customer LTV", "Customer CAC", "CAC Payback Period", "Cash Runway"],
            "Startup Value": [
                f"${screener.computed['arr']:,.0f}",
                f"${screener.computed['mrr']:,.0f}",
                f"${screener.computed['ltv']:,.0f}",
                f"${claimed_metrics.get('claimed_cac_usd',0):,.0f}",
                f"{screener.computed['cac_payback_months']:.1f} Months",
                f"{screener.computed['runway_months']:.1f} Months"
            ],
            "VC Benchmark": ["Scale dependent", "Scale dependent", "High compounding", "Channel dependent", "< 12 Months", "> 18 Months"]
        })

    with col_m2:
        st.markdown("#### Valuation & Market Disparity")
        st.table({
            "Metric": ["Claimed Top-Down TAM", "Bottom-Up Realistic Addressable", "Ask Post-Money Valuation", "Valuation / ARR Multiple", "Burn Multiple"],
            "Startup Value": [
                f"${screener.computed['claimed_tam']/1e9:.1f} Billion",
                f"${screener.computed['bottom_up_tam']/1e6:.1f} Million",
                f"${screener.post_money_usd/1e6:.1f} Million",
                f"{screener.computed['valuation_arr_multiple']:.1f}x ARR",
                f"{screener.computed['burn_multiple']:.2f}x"
            ],
            "VC Benchmark": ["Check bottom-up", "Target volume * ACV", "Stage aligned", "15x - 25x ARR", "< 1.2x"]
        })

with tab3:
    st.subheader("🎴 The 'Market Capturer' 11-Slide Pitch Deck Studio")
    st.caption("Standard venture capital heuristic framework for screening early-stage pitch deck slides.")

    slides_list = [
        "Slide 01: The Category Hook (One-Liner)",
        "Slide 02: The Bleeding Neck (The Hair-on-Fire Problem)",
        "Slide 03: The 10x Mechanism (Radical Solution)",
        "Slide 04: Why Now? (Macro Inflection Point)",
        "Slide 05: Market Sizing (Bottom-Up Math)",
        "Slide 06: Secret Sauce & Technical Moat",
        "Slide 07: Compounding Traction & Unit Economics",
        "Slide 08: Go-To-Market (GTM) Flywheel",
        "Slide 09: The Competitor 2x2 Matrix",
        "Slide 10: The Unfair Team (Earned Secrets)",
        "Slide 11: The Ask & 18-Month Milestones"
    ]
    
    selected_slide = st.selectbox("Select Pitch Deck Slide to Inspect:", slides_list)
    slide_idx = int(selected_slide.split(":")[0].replace("Slide ", ""))
    
    col_slide_preview, col_vc_feedback = st.columns([1.5, 1.0])

    with col_slide_preview:
        st.markdown(f"#### 🖥️ Slide {slide_idx} Live Visual Preview")
        
        if slide_idx == 1:
            st.markdown(f"""
            <div class="slide-card">
                <div class="slide-header">SLIDE 01 // CATEGORY DEFINITION</div>
                <div class="slide-title">{screener.company_name}</div>
                <div class="slide-content">
                    <p style="font-size: 1.4rem; font-weight: 700; color: #63b3ed;">"{screener.tagline}"</p>
                    <hr style="border-color: #2d3748; margin: 1.5rem 0;" />
                    <p><b>Target Category</b>: {screener.sector}</p>
                    <p><b>Round & Ask</b>: {screener.stage} | Raising <b>${screener.ask_usd/1e6:.2f}M</b></p>
                    <p><b>Headquarters</b>: {deck_data.get('headquarters', 'Global')}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        elif slide_idx == 2:
            st.markdown(f"""
            <div class="slide-card">
                <div class="slide-header">SLIDE 02 // THE HAIR-ON-FIRE PROBLEM</div>
                <div class="slide-title">Enterprises are Bleeding Money on Failed Systems</div>
                <div class="slide-content">
                    <p style="font-size: 1.2rem; color: #fc8181;"><b>The Critical Pain Point:</b></p>
                    <p>{deck_data.get('problem_statement', 'N/A')}</p>
                    <ul style="margin-top: 1rem;">
                        <li><b>45% Failure Rate</b>: Production multi-agent loops hang in infinite non-deterministic cycles.</li>
                        <li><b>Database Corruption</b>: Hallucinated SQL writes destroy critical customer state.</li>
                        <li><b>Uncontrolled API Bills</b>: $300K+ wasted annually on redundant token inference.</li>
                    </ul>
                </div>
            </div>
            """, unsafe_allow_html=True)

        elif slide_idx == 3:
            st.markdown(f"""
            <div class="slide-card">
                <div class="slide-header">SLIDE 03 // THE 10x MECHANISM</div>
                <div class="slide-title">Active Runtime Interception & Zero-Downtime Rollback</div>
                <div class="slide-content">
                    <p style="font-size: 1.15rem; color: #68d391;"><b>The Solution Architecture:</b></p>
                    <p>{deck_data.get('solution_statement', 'N/A')}</p>
                    <div style="background: #111424; padding: 1rem; border-radius: 8px; margin-top: 1rem; border: 1px solid #2d3748;">
                        <p style="color: #cbd5e0; margin: 0;"><b>Before:</b> Unmonitored Agent &rarr; Corrupted Tables &rarr; 6 Hours Dev Downtime</p>
                        <p style="color: #68d391; margin: 0.5rem 0 0 0;"><b>With Us:</b> Agent Tool Call &rarr; <b>eBPF Interceptor (&lt;12ms)</b> &rarr; Clean State Rollback</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        elif slide_idx == 4:
            st.markdown(f"""
            <div class="slide-card">
                <div class="slide-header">SLIDE 04 // WHY NOW?</div>
                <div class="slide-title">The Macro Inflection Point in AI Infrastructure</div>
                <div class="slide-content">
                    <ol>
                        <li><b>Reasoning Models Are Here</b>: Multi-step models (o1/Sonnet/Gemini) have made agentic workflows viable in production for the first time in 2026.</li>
                        <li><b>Budget Shift</b>: Enterprise GenAI spending is shifting from prompt toys to mission-critical infrastructure & compliance.</li>
                        <li><b>eBPF Maturity</b>: Kernel-level tracing now runs in Kubernetes with near-zero latency overhead.</li>
                    </ol>
                </div>
            </div>
            """, unsafe_allow_html=True)

        elif slide_idx == 5:
            st.markdown(f"""
            <div class="slide-card">
                <div class="slide-header">SLIDE 05 // BOTTOM-UP MARKET SIZING</div>
                <div class="slide-title">A $2.1B Beachhead Expanding to a $43B Global TAM</div>
                <div class="slide-content">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 1rem;">
                        <div style="background: #1a202c; padding: 1rem; border-radius: 8px; width: 48%;">
                            <span style="color: #63b3ed; font-size: 0.9rem;">SOM (Serviceable Obtainable)</span>
                            <div style="font-size: 1.6rem; font-weight: 800;">${screener.computed['bottom_up_tam']/1e6:,.1f}M</div>
                            <span style="font-size: 0.8rem; color: #a0aec0;">{deck_data.get('claimed_metrics',{}).get('target_customer_count_global',0):,} Accounts @ ACV</span>
                        </div>
                        <div style="background: #1a202c; padding: 1rem; border-radius: 8px; width: 48%;">
                            <span style="color: #68d391; font-size: 0.9rem;">CLAIMED GLOBAL TAM</span>
                            <div style="font-size: 1.6rem; font-weight: 800;">${screener.computed['claimed_tam']/1e9:,.1f}B</div>
                            <span style="font-size: 0.8rem; color: #a0aec0;">Global Observability & AI QA</span>
                        </div>
                    </div>
                    <p style="font-size: 0.95rem; color: #cbd5e0;">No hand-waving: Grounded in realistic volume of enterprise engineering teams deploying agentic microservices.</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

        elif slide_idx == 6:
            st.markdown(f"""
            <div class="slide-card">
                <div class="slide-header">SLIDE 06 // SECRET SAUCE & DEFENSIBILITY</div>
                <div class="slide-title">Why Foundation Models Can't Replicate Our Moat</div>
                <div class="slide-content">
                    <ul>
                        <li><b>Kernel-Level eBPF Probes</b>: Zero-dependency runtime inspection running inside customer VPCs.</li>
                        <li><b>Local SLM Inference Arbiter</b>: Replaces $30K/mo OpenAI evaluation bills with fine-tuned 3B local models, cutting COGS by 76%.</li>
                        <li><b>Runtime Lock-In</b>: Embedded in developer CI/CD test gates. Ripping us out breaks enterprise compliance.</li>
                    </ul>
                </div>
            </div>
            """, unsafe_allow_html=True)

        elif slide_idx == 7:
            st.markdown(f"""
            <div class="slide-card">
                <div class="slide-header">SLIDE 07 // TRACTION & COMPELLING ECONOMICS</div>
                <div class="slide-title">Compounding Capital-Efficient Growth</div>
                <div class="slide-content">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 1rem;">
                        <div>
                            <span style="color: #a0aec0;">ANNUAL RUN-RATE (ARR)</span>
                            <div style="font-size: 1.6rem; font-weight: 800; color: #68d391;">${screener.computed['arr']:,.0f}</div>
                        </div>
                        <div>
                            <span style="color: #a0aec0;">LTV : CAC RATIO</span>
                            <div style="font-size: 1.6rem; font-weight: 800; color: #63b3ed;">{screener.computed['ltv_cac']:.1f}x</div>
                        </div>
                        <div>
                            <span style="color: #a0aec0;">CAC PAYBACK</span>
                            <div style="font-size: 1.6rem; font-weight: 800; color: #faf089;">{screener.computed['cac_payback_months']:.1f} Mo</div>
                        </div>
                        <div>
                            <span style="color: #a0aec0;">BURN MULTIPLE</span>
                            <div style="font-size: 1.6rem; font-weight: 800; color: #e2e8f0;">{screener.computed['burn_multiple']:.2f}x</div>
                        </div>
                    </div>
                    <p style="color: #cbd5e0;">Demonstrating top-quartile sales efficiency and high gross margins ({claimed_metrics.get('claimed_gross_margin_pct',0)*100:.0f}%).</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

        elif slide_idx == 8:
            st.markdown(f"""
            <div class="slide-card">
                <div class="slide-header">SLIDE 08 // GO-TO-MARKET FLYWHEEL</div>
                <div class="slide-title">Developer Land & Enterprise Expand</div>
                <div class="slide-content">
                    <p><b>1. LAND (Product-Led Growth)</b>: Free open-source Python/TypeScript agent SDK drives bottom-up adoption by engineering teams on GitHub.</p>
                    <p><b>2. EXPAND (Usage-Based Tiers)</b>: Automatically charges per 100K monitored agent executions as production traffic scales.</p>
                    <p><b>3. LOCK (Enterprise Air-Gap)</b>: Dedicated VPC deployments with SOC2, GDPR, and automated PII redaction for Fortune 2000 buyers.</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

        elif slide_idx == 9:
            st.markdown(f"""
            <div class="slide-card">
                <div class="slide-header">SLIDE 09 // COMPETITOR 2x2 MATRIX</div>
                <div class="slide-title">Positioned at Active State Protection with Low COGS</div>
                <div class="slide-content">
                    <div style="background: #111424; padding: 1.2rem; border-radius: 8px; border: 1px solid #2d3748;">
                        <p style="color: #e2e8f0;"><b>Y-Axis:</b> Active Runtime Rollback vs. Passive Log Ingestion</p>
                        <p style="color: #e2e8f0;"><b>X-Axis:</b> Lightweight Local SLM vs. Expensive Third-Party API Bills</p>
                        <hr style="border-color: #2d3748; margin: 0.8rem 0;" />
                        <p style="color: #cbd5e0; margin: 0;">&bull; <b>Legacy APMs (Datadog/Dynatrace):</b> High cost, passive logging only (can't rollback LLM states).</p>
                        <p style="color: #cbd5e0; margin: 0.3rem 0 0 0;">&bull; <b>OpenAI API Wrappers:</b> High latency, 90% gross margin illusion, zero enterprise data privacy.</p>
                        <p style="color: #68d391; margin: 0.3rem 0 0 0;">&bull; <b>{screener.company_name} (Top-Right Leader):</b> Active kernel interception with zero-token-overhead local arbitration.</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        elif slide_idx == 10:
            st.markdown(f"""
            <div class="slide-card">
                <div class="slide-header">SLIDE 10 // UNFAIR ADVANTAGE & TEAM</div>
                <div class="slide-title">Founders with Deep Earned Secrets</div>
                <div class="slide-content">
            """, unsafe_allow_html=True)
            for m in screener.team:
                st.markdown(f"""
                <div style="background: #1a202c; padding: 0.8rem 1rem; border-radius: 6px; margin-bottom: 0.8rem;">
                    <b style="color: #63b3ed;">{m.get('name')}</b> — <i>{m.get('role')}</i><br />
                    <span style="color: #cbd5e0; font-size: 0.95rem;">{m.get('background')}</span>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div></div>", unsafe_allow_html=True)

        elif slide_idx == 11:
            st.markdown(f"""
            <div class="slide-card">
                <div class="slide-header">SLIDE 11 // THE ASK & 18-MONTH MILESTONES</div>
                <div class="slide-title">Raising ${screener.ask_usd/1e6:.2f}M to Scale to $3.5M ARR</div>
                <div class="slide-content">
                    <p><b>Round Structure</b>: {screener.stage} | Post-Money Valuation: <b>${screener.post_money_usd/1e6:.2f}M</b></p>
                    <p><b>Runway Provided</b>: 24 Months of capital efficiency</p>
                    <hr style="border-color: #2d3748; margin: 0.8rem 0;" />
                    <p><b>Use of Funds:</b></p>
                    <ul>
                        <li><b>70% Core Engineering</b>: Distributed systems & eBPF kernel engineers in Bengaluru.</li>
                        <li><b>20% Developer Go-To-Market</b>: Technical DevRel, hackathon sponsorships, and US enterprise outbound.</li>
                        <li><b>10% Cloud & GPU Cluster</b>: Dedicated local SLM fine-tuning pipelines.</li>
                    </ul>
                    <p style="color: #68d391; font-weight: 700; margin-top: 1rem;">Target for Series A: Scale from ${screener.computed['arr']/1e6:.2f}M ARR to $3.5M ARR with 150+ Enterprise Accounts.</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with col_vc_feedback:
        st.markdown("#### 🧠 VC Partner Evaluation Matrix")
        
        vc_rubric = {
            1: {
                "trigger": "Can I understand what they do in 5 seconds?",
                "amateur": "Vague buzzwords: 'Revolutionizing digital enterprise synergies with AI.'",
                "capturer": "Specific ICP + Exact Mechanism + Category replaced.",
                "pass": True if len(screener.tagline) > 10 else False
            },
            2: {
                "trigger": "Is this a real hair-on-fire pain, or a nice-to-have vitamin?",
                "amateur": "Complaining about broad philosophical issues with no quantifiable business loss.",
                "capturer": "Quantified dollar waste ($300K/quarter) and exact downtime mechanics.",
                "pass": True if len(deck_data.get('problem_statement','')) > 20 else False
            },
            3: {
                "trigger": "Is this a 10x better mechanism or an incremental 10% feature?",
                "amateur": "Showing 15 screenshots of generic dashboard buttons.",
                "capturer": "Showing the architectural before vs. after workflow.",
                "pass": True if len(deck_data.get('solution_statement','')) > 20 else False
            },
            4: {
                "trigger": "Why couldn't this be built 3 years ago? Why can't we wait 2 years?",
                "amateur": "Saying 'Because AI is booming right now.'",
                "capturer": "Pinpointing technical inflection (reasoning models + eBPF kernel maturity).",
                "pass": True
            },
            5: {
                "trigger": "Is this market math realistic or hand-waving fantasy?",
                "amateur": "Drawing a generic $500B circle from a Gartner headline report.",
                "capturer": "Bottom-up ACV calculation grounded in realistic customer account volume.",
                "pass": True if (screener.computed['claimed_tam']/max(1.0, screener.computed['bottom_up_tam'])) <= 4.0 else False
            },
            6: {
                "trigger": "What stops OpenAI, Google, or AWS from killing you tomorrow?",
                "amateur": "Saying 'We have first-mover advantage and great UI.'",
                "capturer": "Architectural lock-in: local SLMs, eBPF probes, and runtime CI/CD switching costs.",
                "pass": True if claimed_metrics.get("has_local_fine_tuned_models", False) else False
            },
            7: {
                "trigger": "Are they burning cash efficiently, or is it a leaky bucket?",
                "amateur": "Focusing on cumulative website visits or unverified signups.",
                "capturer": "Sub-12 month CAC Payback, LTV:CAC > 3x, and Burn Multiple < 1.0x.",
                "pass": True if screener.computed['burn_multiple'] <= 1.2 and screener.computed['cac_payback_months'] <= 12 else False
            },
            8: {
                "trigger": "Can they acquire customers profitably without hiring 100 salespeople?",
                "amateur": "Saying 'We will run paid Google & Meta ads.'",
                "capturer": "Product-led developer adoption on GitHub converting to enterprise usage tiers.",
                "pass": True
            },
            9: {
                "trigger": "Do they respect competitors, or are they naive?",
                "amateur": "Putting yourself in the top-right corner with 10 green checks and everyone else red.",
                "capturer": "2x2 matrix with clear architectural trade-offs.",
                "pass": True
            },
            10: {
                "trigger": "Does this team have earned secrets and technical founder-market fit?",
                "amateur": "Listing college degrees with no engineering depth or patents.",
                "capturer": "Ex-hyperscaler leads, distributed systems architects, and patent holders.",
                "pass": True if claimed_metrics.get("has_technical_founder", False) else False
            },
            11: {
                "trigger": "Do they know what milestone de-risks the next funding round?",
                "amateur": "Asking for money 'for marketing and general corporate purposes.'",
                "capturer": "Targeting specific ARR compounding ($1M -> $3.5M) for Series A.",
                "pass": True if screener.computed['valuation_arr_multiple'] <= 25.0 else False
            }
        }

        r = vc_rubric.get(slide_idx, {})
        
        status_badge = "✅ **PASSES VC BAR**" if r.get("pass") else "🚨 **NEEDS HARDENING**"
        status_color = "#00E676" if r.get("pass") else "#FF1744"
        
        st.markdown(f"""
        <div style="background: #1e2130; padding: 1.2rem; border-radius: 10px; border-left: 5px solid {status_color};">
            <div style="color: {status_color}; font-weight: 800; font-size: 1.1rem; margin-bottom: 0.5rem;">{status_badge}</div>
            <p><b>VC Psychological Trigger:</b><br /><i>"{r.get('trigger')}"</i></p>
            <hr style="border-color: #2d3748; margin: 0.8rem 0;" />
            <p><b style="color: #fc8181;">Amateur Mistake:</b><br /><span style="font-size: 0.9rem; color: #cbd5e0;">{r.get('amateur')}</span></p>
            <p><b style="color: #68d391;">Market Capturer Move:</b><br /><span style="font-size: 0.9rem; color: #cbd5e0;">{r.get('capturer')}</span></p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    
    # Generate complete 11-slide markdown presentation spec for download
    full_deck_spec = f"""# THE 11-SLIDE INVESTOR PRESENTATION SPEC: {screener.company_name}
Sector: {screener.sector} | Round: {screener.stage} | Ask: ${screener.ask_usd/1e6:.2f}M at ${screener.post_money_usd/1e6:.2f}M Post-Money

================================================================================
SLIDE 01: THE CATEGORY HOOK
Title: {screener.company_name}
Tagline: "{screener.tagline}"
Round Details: {screener.stage} raising ${screener.ask_usd/1e6:.2f}M

SLIDE 02: THE HAIR-ON-FIRE PROBLEM
Pain Point: {deck_data.get('problem_statement', 'N/A')}
- 45% production multi-agent failure rate
- Database corruption from hallucinated SQL tool calls
- $300K+ wasted annually per enterprise on redundant inference

SLIDE 03: THE 10X MECHANISM
Solution: {deck_data.get('solution_statement', 'N/A')}
- Active eBPF runtime interception in under 12ms
- Automated zero-downtime database state rollback

SLIDE 04: WHY NOW?
1. Reasoning models (o1/Sonnet/Gemini) just enabled multi-step agents in 2026.
2. Enterprise GenAI spending moved from prompt toys to compliance & infra.
3. eBPF kernel maturity in Kubernetes.

SLIDE 05: BOTTOM-UP MARKET SIZING
- SOM: ${screener.computed['bottom_up_tam']/1e6:.1f}M ({deck_data.get('claimed_metrics',{}).get('target_customer_count_global',0):,} accounts @ ACV)
- Claimed TAM: ${screener.computed['claimed_tam']/1e9:.1f}B

SLIDE 06: SECRET SAUCE & TECHNICAL MOAT
- Kernel-level eBPF probes inside customer VPC
- Proprietary local SLM inference arbiter cutting COGS by 76%
- Deep CI/CD developer workflow lock-in

SLIDE 07: TRACTION & UNIT ECONOMICS
- ARR: ${screener.computed['arr']:,.0f} | MRR: ${screener.computed['mrr']:,.0f}
- LTV : CAC: {screener.computed['ltv_cac']:.1f}x
- CAC Payback: {screener.computed['cac_payback_months']:.1f} Months
- Burn Multiple: {screener.computed['burn_multiple']:.2f}x (David Sacks Benchmark: < 1.0x)

SLIDE 08: GO-TO-MARKET FLYWHEEL
- Land: Open-source developer SDK on GitHub
- Expand: Usage-based per-100K monitored agent executions
- Lock: Enterprise air-gapped VPC & compliance tiers

SLIDE 09: COMPETITOR 2X2 MATRIX
- Y-Axis: Active State Rollback vs Passive Logging
- X-Axis: Local Lightweight SLM vs Expensive Third-Party APIs
- Position: Top-Right Leader

SLIDE 10: THE UNFAIR TEAM
- Aarav Sharma (CEO): Ex-Staff Engineer @ Postman (2 US patents)
- Neha Verma (CTO): Ex-ML Lead @ BrowserStack (Stanford MS CS)

SLIDE 11: THE ASK & 18-MONTH MILESTONES
- Raising: ${screener.ask_usd/1e6:.2f}M Series Seed for 24 months runway
- Milestone: Scale from ${screener.computed['arr']/1e6:.2f}M ARR to $3.5M ARR with 150+ Enterprise Accounts.
================================================================================
"""
    st.download_button(
        label="📥 Download Complete 11-Slide Pitch Deck Spec (.md)",
        data=full_deck_spec,
        file_name=f"11_Slide_Pitch_Deck_{screener.company_name.replace(' ', '_')}.md",
        mime="text/markdown"
    )

with tab4:
    st.subheader("🔬 Tier-1 VC Technical Due Diligence & Code Moat Auditor")
    st.caption("Inspects startup code repositories and package manifests to distinguish between defensible deeptech infrastructure vs. vulnerable OpenAI wrappers.")

    moat_scanner = TechMoatScanner(company_name=screener.company_name)

    audit_source_choice = st.radio(
        "Select Codebase Manifest to Audit:",
        [
            f"Active Startup Manifest ({screener.company_name})",
            "CogniFlow AI Benchmark (eBPF + vLLM + PyTorch)",
            "HyperBuzz AI Benchmark (LangChain + CrewAI Wrapper)",
            "Paste Custom requirements.txt / package.json"
        ],
        horizontal=True
    )

    reqs_text = ""
    code_snippet_text = ""

    if audit_source_choice == f"Active Startup Manifest ({screener.company_name})":
        if "cogni" in screener.company_name.lower():
            reqs_text = COGNIFLOW_REQUIREMENTS
            code_snippet_text = COGNIFLOW_CODE_SAMPLE
        else:
            reqs_text = HYPERBUZZ_REQUIREMENTS
            code_snippet_text = HYPERBUZZ_CODE_SAMPLE
    elif audit_source_choice == "CogniFlow AI Benchmark (eBPF + vLLM + PyTorch)":
        reqs_text = COGNIFLOW_REQUIREMENTS
        code_snippet_text = COGNIFLOW_CODE_SAMPLE
    elif audit_source_choice == "HyperBuzz AI Benchmark (LangChain + CrewAI Wrapper)":
        reqs_text = HYPERBUZZ_REQUIREMENTS
        code_snippet_text = HYPERBUZZ_CODE_SAMPLE
    else:
        reqs_text = st.text_area(
            "Paste Python requirements.txt or Node package.json:",
            value=HYPERBUZZ_REQUIREMENTS,
            height=150
        )
        code_snippet_text = st.text_area(
            "Paste Core Architecture / Kernel / Model Code Snippet (Optional):",
            value="",
            height=100
        )

    # Run Code Audit
    audit_rep = moat_scanner.audit_manifests(
        requirements_txt=reqs_text,
        code_snippets=code_snippet_text
    )

    # Top KPI Metrics for Code Audit
    tm1, tm2, tm3, tm4 = st.columns(4)
    with tm1:
        moat_score = audit_rep.defensibility_score
        moat_color = "#00E676" if moat_score >= 75 else ("#FFD600" if moat_score >= 50 else "#FF1744")
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 0.85rem; color: #a0aec0;">ARCHITECTURAL DEFENSE</div>
            <div style="font-size: 1.8rem; font-weight: 800; color: {moat_color};">{moat_score} <span style="font-size: 1rem; color: #718096;">/ 100</span></div>
            <div style="font-size: 0.75rem; color: #cbd5e0;">{audit_rep.tier_classification}</div>
        </div>
        """, unsafe_allow_html=True)

    with tm2:
        ext_color = "#00E676" if "LOW" in audit_rep.extinction_risk else ("#FFD600" if "MODERATE" in audit_rep.extinction_risk else "#FF1744")
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 0.85rem; color: #a0aec0;">PLATFORM EXTINCTION RISK</div>
            <div style="font-size: 1.3rem; font-weight: 800; color: {ext_color};">{audit_rep.extinction_risk.split('//')[0].strip()}</div>
            <div style="font-size: 0.75rem; color: #718096;">OpenAI/Hyperscaler Risk</div>
        </div>
        """, unsafe_allow_html=True)

    with tm3:
        margin_ceil = audit_rep.gross_margin_ceiling_pct
        mg_color = "#00E676" if margin_ceil >= 80 else "#FF1744"
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 0.85rem; color: #a0aec0;">EST. GROSS MARGIN CAP</div>
            <div style="font-size: 1.8rem; font-weight: 800; color: {mg_color};">~{margin_ceil:.0f}%</div>
            <div style="font-size: 0.75rem; color: #718096;">Token COGS Drag Limit</div>
        </div>
        """, unsafe_allow_html=True)

    with tm4:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 0.85rem; color: #a0aec0;">SYSTEMS MOAT VS WRAPPER</div>
            <div style="font-size: 1.8rem; font-weight: 800; color: #38bdf8;">{audit_rep.systems_moat_pct:.0f}% <span style="font-size: 0.9rem; color: #f43f5e;">/ {audit_rep.wrapper_index_pct:.0f}%</span></div>
            <div style="font-size: 0.75rem; color: #718096;">Proprietary vs Wrapper %</div>
        </div>
        """, unsafe_allow_html=True)

    # Technical Findings Breakdown
    st.markdown("#### 🔬 Diagnostic Findings & Technical Defensibility")
    
    col_deps, col_ic_notes = st.columns([1.2, 1.0])
    
    with col_deps:
        st.markdown("**Dependency Ecosystem Breakdown:**")
        
        # Badges for Wrapper vs Deeptech
        if audit_rep.wrapper_libraries_found:
            st.error(f"🚨 **Third-Party API Pass-Through Wrappers Detected ({len(audit_rep.wrapper_libraries_found)})**:\n`{'`, `'.join(audit_rep.wrapper_libraries_found)}`")
        else:
            st.success("🟢 **Zero Superficial Wrapper Frameworks Detected**")

        if audit_rep.deeptech_libraries_found:
            st.success(f"🟢 **Native Deeptech / Compiled ML Layers ({len(audit_rep.deeptech_libraries_found)})**:\n`{'`, `'.join(audit_rep.deeptech_libraries_found)}`")
        else:
            st.warning("⚠️ **No Native Deeptech / GPU / Local Model Infrastructure Detected**")

        if audit_rep.infrastructure_libraries_found:
            st.info(f"🔵 **Distributed Infrastructure & Queues ({len(audit_rep.infrastructure_libraries_found)})**:\n`{'`, `'.join(audit_rep.infrastructure_libraries_found)}`")

    with col_ic_notes:
        st.markdown("**Investment Committee Technical Verdict:**")
        if audit_rep.defensibility_score >= 75:
            st.success(f"### 🛡️ TIER-1 DEEP TECH MOAT\n**IC Technical Verdict**: {audit_rep.ic_recommendation}")
        elif audit_rep.defensibility_score >= 50:
            st.warning(f"### ⚠️ WORKFLOW MOAT / HYBRID\n**IC Technical Verdict**: {audit_rep.ic_recommendation}")
        else:
            st.error(f"### 🚨 LETHAL PLATFORM RISK\n**IC Technical Verdict**: {audit_rep.ic_recommendation}")

    with st.expander("📄 View Audited Manifest Raw Content"):
        st.code(reqs_text, language="text")

with tab5:
    st.subheader("💰 Tier-1 Cap Table Dilution & Liquidation Preference Waterfall")
    st.markdown(
        "Institutional exit proceeds modeler across multi-round financing tranches (Seed → Series A → Series B). "
        "Evaluates **1x Non-Participating vs. Participating Preferred**, conversion crossover hurdles, and downside preference floors."
    )

    # 1. Configuration & Scenarios
    col_w_top1, col_w_top2 = st.columns([1.5, 1.0])
    with col_w_top1:
        exit_val_m = st.slider(
            "Hypothetical M&A / Exit Valuation ($ Millions):",
            min_value=5.0,
            max_value=1000.0,
            value=100.0,
            step=5.0,
            help="Simulate the total cash proceeds returned at company sale or trade sale."
        )
    with col_w_top2:
        pref_term = st.radio(
            "Liquidation Preference Structure:",
            options=[
                "1x Non-Participating Preferred (NVCA / Tier-1 Market Standard)",
                "1x Participating Preferred ('Double Dipping' - Off-Market)"
            ],
            index=0,
            help="1x Non-Participating: Investor gets MAX(1x Capital, Pro-Rata Common). Participating: Investor gets 1x Capital PLUS Pro-Rata of remainder."
        )
    
    is_participating = "Participating" in pref_term and "Non-Participating" not in pref_term

    # Round parameters customization
    with st.expander("⚙️ Customize Financing Rounds & Pre/Post-Money Valuations"):
        rf_c1, rf_c2, rf_c3 = st.columns(3)
        with rf_c1:
            st.markdown("**Seed Round**")
            seed_cap = st.number_input("Seed Capital ($M)", min_value=0.5, max_value=10.0, value=2.5, step=0.5) * 1e6
            seed_post = st.number_input("Seed Post-Money ($M)", min_value=5.0, max_value=30.0, value=18.0, step=1.0) * 1e6
        with rf_c2:
            st.markdown("**Series A Round**")
            sa_cap = st.number_input("Series A Capital ($M)", min_value=2.0, max_value=30.0, value=10.0, step=1.0) * 1e6
            sa_post = st.number_input("Series A Post-Money ($M)", min_value=20.0, max_value=100.0, value=50.0, step=5.0) * 1e6
        with rf_c3:
            st.markdown("**Series B Round**")
            sb_cap = st.number_input("Series B Capital ($M)", min_value=5.0, max_value=100.0, value=25.0, step=5.0) * 1e6
            sb_post = st.number_input("Series B Post-Money ($M)", min_value=50.0, max_value=400.0, value=150.0, step=10.0) * 1e6

    # Instantiate Engine
    wf_engine = CapTableWaterfallEngine()
    wf_engine.build_standard_venture_cap_table(
        seed_capital=seed_cap,
        seed_post_val=seed_post,
        series_a_capital=sa_cap,
        series_a_post_val=sa_post,
        series_b_capital=sb_cap,
        series_b_post_val=sb_post
    )

    exit_usd = exit_val_m * 1e6
    payouts = wf_engine.calculate_exit_waterfall(
        exit_valuation_usd=exit_usd,
        is_participating_preferred=is_participating
    )
    pref_stack = wf_engine.get_preference_stack_total()
    crossover_hurdles = wf_engine.get_crossover_hurdles()

    # Find key shareholders
    f_payout = next((p for p in payouts if p.category == "Founders"), None)
    esop_payout = next((p for p in payouts if p.category == "ESOP"), None)
    seed_payout = next((p for p in payouts if p.category == "Seed VC"), None)
    sa_payout = next((p for p in payouts if p.category == "Series A VC"), None)
    sb_payout = next((p for p in payouts if p.category == "Series B VC"), None)

    # 2. Executive KPI Cards
    st.markdown("#### 🏆 Exit Proceeds Summary at $" + f"{exit_val_m:.1f}M Exit")
    kp1, kp2, kp3, kp4, kp5 = st.columns(5)
    with kp1:
        f_val = f_payout.proceeds_usd / 1e6 if f_payout else 0.0
        f_pct = (f_val / exit_val_m) * 100 if exit_val_m > 0 else 0
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 0.85rem; color: #a0aec0;">FOUNDERS PROCEEDS</div>
            <div style="font-size: 1.8rem; font-weight: 800; color: #00E676;">${f_val:.2f}M</div>
            <div style="font-size: 0.75rem; color: #718096;">{f_pct:.1f}% of total exit pool</div>
        </div>
        """, unsafe_allow_html=True)

    with kp2:
        seed_val = seed_payout.proceeds_usd / 1e6 if seed_payout else 0.0
        seed_moic = seed_payout.moic if seed_payout else 0.0
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 0.85rem; color: #a0aec0;">SEED VC RETURN</div>
            <div style="font-size: 1.8rem; font-weight: 800; color: #38bdf8;">${seed_val:.2f}M</div>
            <div style="font-size: 0.75rem; color: #718096;">{seed_moic:.2f}x MoIC (${seed_cap/1e6:.1f}M cost)</div>
        </div>
        """, unsafe_allow_html=True)

    with kp3:
        sa_val = sa_payout.proceeds_usd / 1e6 if sa_payout else 0.0
        sa_moic = sa_payout.moic if sa_payout else 0.0
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 0.85rem; color: #a0aec0;">SERIES A VC RETURN</div>
            <div style="font-size: 1.8rem; font-weight: 800; color: #6366f1;">${sa_val:.2f}M</div>
            <div style="font-size: 0.75rem; color: #718096;">{sa_moic:.2f}x MoIC (${sa_cap/1e6:.1f}M cost)</div>
        </div>
        """, unsafe_allow_html=True)

    with kp4:
        sb_val = sb_payout.proceeds_usd / 1e6 if sb_payout else 0.0
        sb_moic = sb_payout.moic if sb_payout else 0.0
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 0.85rem; color: #a0aec0;">SERIES B VC RETURN</div>
            <div style="font-size: 1.8rem; font-weight: 800; color: #ec4899;">${sb_val:.2f}M</div>
            <div style="font-size: 0.75rem; color: #718096;">{sb_moic:.2f}x MoIC (${sb_cap/1e6:.1f}M cost)</div>
        </div>
        """, unsafe_allow_html=True)

    with kp5:
        esop_val = esop_payout.proceeds_usd / 1e6 if esop_payout else 0.0
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 0.85rem; color: #a0aec0;">ESOP POOL VALUE</div>
            <div style="font-size: 1.8rem; font-weight: 800; color: #f59e0b;">${esop_val:.2f}M</div>
            <div style="font-size: 0.75rem; color: #718096;">Employee Wealth Created</div>
        </div>
        """, unsafe_allow_html=True)

    # 3. Conversion Crossover & Downside Protection Analysis
    st.markdown("#### ⚡ Liquidation Preference Seniority & Conversion Crossover Hurdles")
    if exit_usd <= pref_stack:
        st.error(
            f"🚨 **DOWNSIDE LOSS ZONE**: The aggregate preferred liquidation preference stack is **${pref_stack/1e6:.2f}M**. "
            f"Because this exit (${exit_val_m:.1f}M) is less than or equal to the preference stack, "
            f"all proceeds are consumed by senior preferred investors. **Common shareholders (Founders & Employees) receive $0.00**."
        )
    else:
        st.success(
            f"🟢 **COMMON VALUE CREATION ZONE**: Exit (${exit_val_m:.1f}M) clears the aggregate preference stack of **${pref_stack/1e6:.2f}M**. "
            f"Common shareholders participate in the remaining ${ (exit_usd - pref_stack)/1e6:.2f}M+ pool."
        )

    # Crossover Table
    hurdle_cols = st.columns(3)
    for idx, h in enumerate(crossover_hurdles):
        with hurdle_cols[idx]:
            is_converted = exit_usd >= h["crossover_exit_valuation"]
            status_badge = "✅ CONVERTED TO COMMON" if is_converted else "🛡️ EXERCISING 1X PREFERENCE"
            badge_color = "#00E676" if is_converted else "#FFD600"
            st.markdown(f"""
            <div style="background-color: #1a202c; padding: 1rem; border-radius: 8px; border-left: 4px solid {badge_color};">
                <div style="font-weight: 700; color: #e2e8f0;">{h['class_name']}</div>
                <div style="font-size: 0.85rem; color: #a0aec0;">Ownership: {h['ownership_pct']:.2f}% | Invested: ${h['invested_capital']/1e6:.2f}M</div>
                <div style="font-size: 1.1rem; font-weight: 800; color: #63b3ed; margin: 0.4rem 0;">Crossover Hurdle: ${h['crossover_exit_valuation']/1e6:.1f}M</div>
                <div style="font-size: 0.8rem; font-weight: 700; color: {badge_color};">{status_badge}</div>
            </div>
            """, unsafe_allow_html=True)

    # 4. Detailed Payout Ledger & Altair Visualization
    st.markdown("#### 📊 Current Exit Shareholder Distribution Ledger")
    
    ledger_data = []
    chart_data = []
    for p in payouts:
        status_label = "Converted to Common" if p.converted_to_common else "1x Liquidation Preference"
        if p.category in ["Founders", "ESOP"]:
            status_label = "Common Shares"
        
        ledger_data.append({
            "Shareholder": p.name,
            "Class": "Common" if p.category in ["Founders", "ESOP"] else "Preferred",
            "Fully Diluted %": f"{p.ownership_pct:.2f}%",
            "Capital Invested": f"${p.invested_capital/1e6:.2f}M",
            "Exercise Status": status_label,
            "Net Proceeds ($M)": round(p.proceeds_usd / 1e6, 2),
            "MoIC": f"{p.moic:.2f}x" if p.invested_capital > 0 else "N/A"
        })
        chart_data.append({
            "Shareholder": p.name.split(" ")[0] + (" (ESOP)" if "ESOP" in p.name else " (VC)" if "VC" in p.name else "s"),
            "Proceeds ($M)": round(p.proceeds_usd / 1e6, 2),
            "Category": p.category
        })

    df_ledger = pd.DataFrame(ledger_data)
    
    col_table, col_chart = st.columns([1.3, 1.0])
    with col_table:
        st.dataframe(df_ledger, use_container_width=True, hide_index=True)
    
    with col_chart:
        df_chart = pd.DataFrame(chart_data)
        chart = alt.Chart(df_chart).mark_bar(cornerRadiusTopRight=6, cornerRadiusBottomRight=6).encode(
            x=alt.X('Proceeds ($M):Q', title='Net Exit Proceeds ($M)'),
            y=alt.Y('Shareholder:N', sort='-x', title='Shareholder Group'),
            color=alt.Color('Category:N', scale=alt.Scale(
                domain=['Founders', 'Seed VC', 'Series A VC', 'Series B VC', 'ESOP'],
                range=['#00E676', '#38bdf8', '#6366f1', '#ec4899', '#f59e0b']
            ), legend=None),
            tooltip=['Shareholder', 'Proceeds ($M)']
        ).properties(height=240)
        st.altair_chart(chart, use_container_width=True)

    # 5. Multi-Exit Scenario Simulation Matrix ($10M to $1 Billion)
    st.markdown("#### 🌐 Institutional Multi-Exit Return Matrix ($10M to $1,000M)")
    st.write("Cross-evaluating proceeds and cash-on-cash multiples across typical exit outcomes:")

    scenarios = [10_000_000, 25_000_000, 50_000_000, 100_000_000, 200_000_000, 350_000_000, 500_000_000, 1_000_000_000]
    matrix_raw = wf_engine.run_multi_exit_matrix(scenarios)
    
    matrix_rows = []
    for r in matrix_raw:
        exit_val_display = f"${r['exit_valuation']/1e6:.0f}M"
        f_proceeds = f"${r.get('Founders_proceeds', 0)/1e6:.1f}M"
        seed_res = f"${r.get('Seed VC_proceeds', 0)/1e6:.1f}M ({r.get('Seed VC_moic', 0):.1f}x)"
        sa_res = f"${r.get('Series A VC_proceeds', 0)/1e6:.1f}M ({r.get('Series A VC_moic', 0):.1f}x)"
        sb_res = f"${r.get('Series B VC_proceeds', 0)/1e6:.1f}M ({r.get('Series B VC_moic', 0):.1f}x)"
        esop_res = f"${r.get('ESOP_proceeds', 0)/1e6:.1f}M"

        matrix_rows.append({
            "Exit Valuation": exit_val_display,
            "Founders Payout": f_proceeds,
            "Seed VC ($ / MoIC)": seed_res,
            "Series A VC ($ / MoIC)": sa_res,
            "Series B VC ($ / MoIC)": sb_res,
            "ESOP Pool": esop_res
        })

    df_matrix = pd.DataFrame(matrix_rows)
    st.dataframe(df_matrix, use_container_width=True, hide_index=True)

    st.info(
        "💡 **Venture Capital Key Takeaway**: Notice that at a **$50M Exit**, Series B ($25M invested) only returns **1.0x MoIC** "
        "and Series A ($10M invested) only returns **1.0x MoIC**, leaving almost zero upside beyond principal protection. "
        "However, at **$350M+ exits**, the power law unlocks: Seed VC achieves **13.0x - 37.0x MoIC**, transforming the fund's DPI (Distributed to Paid-In Capital). "
        "This structural math dictates why Tier-1 VC Investment Committees pass on good $30M businesses to chase outlier $500M+ outcomes."
    )

with tab6:
    st.subheader("Generated Investment Committee (IC) Screening Memo")
    
    temp_memo_path = os.path.join(base_dir, f"IC_Screening_Memo_{screener.company_name.replace(' ', '_')}.md")
    screener.generate_markdown_memo(temp_memo_path)
    
    with open(temp_memo_path, "r", encoding="utf-8") as f:
        memo_content = f.read()

    st.markdown(memo_content)

    st.download_button(
        label="📥 Download 1-Page IC Memo (.md)",
        data=memo_content,
        file_name=f"IC_Screening_Memo_{screener.company_name.replace(' ', '_')}.md",
        mime="text/markdown"
    )

st.markdown("---")
st.caption("Engineered by Shivansh Choubey | Computer Science & Tech Due Diligence | VIT Chennai")
