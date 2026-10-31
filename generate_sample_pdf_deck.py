"""
========================================================================================
VENTURE CAPITALIST FRIENDLY PITCH DECK GENERATOR
----------------------------------------------------------------------------------------
Generates an executive, dark-mode, high-contrast 16:9 landscape PDF pitch deck
styled after tier-1 Silicon Valley & Bengaluru tech decks (Linear, Stripe, Vercel).
Includes visual KPI metric tiles, competitor 2x2 grids, and architectural callouts.
========================================================================================
"""

import os
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


# Dark Modern Theme Colors
BG_COLOR = colors.HexColor("#0A0E1A")        # Deep Dark Canvas
CARD_BG = colors.HexColor("#141C2E")         # Elevated Container
CARD_BORDER = colors.HexColor("#2A3756")     # Border stroke
CYAN_ACCENT = colors.HexColor("#38BDF8")     # Primary Accent
EMERALD_GREEN = colors.HexColor("#10B981")   # Metrics / Traction Accent
ROSE_RED = colors.HexColor("#F43F5E")        # Problem Accent
AMBER_YELLOW = colors.HexColor("#FBBF24")    # Milestone Accent
TEXT_WHITE = colors.HexColor("#FFFFFF")      # Main Headers
TEXT_SLATE = colors.HexColor("#94A3B8")      # Subtext / Captions
TEXT_LIGHT = colors.HexColor("#E2E8F0")      # Body text


def draw_slide_background(canvas, doc):
    """Draws sleek dark canvas background, header brand pill, and footer on every page."""
    canvas.saveState()
    width, height = doc.pagesize  # 792 x 612 points

    # 1. Fill Dark Background
    canvas.setFillColor(BG_COLOR)
    canvas.rect(0, 0, width, height, fill=1, stroke=0)

    # 2. Top Accent Line (Cyan Gradient Simulation)
    canvas.setFillColor(CYAN_ACCENT)
    canvas.rect(0, height - 4, width, 4, fill=1, stroke=0)

    # 3. Header Watermark / Confidentiality Tag
    canvas.setFont("Helvetica-Bold", 8)
    canvas.setFillColor(TEXT_SLATE)
    canvas.drawString(40, height - 26, "COGNIFLOW AI // CONFIDENTIAL INVESTOR PRESENTATION // SERIES SEED")

    # 4. Footer Slide Number & Brand
    canvas.drawString(40, 20, "STRICTLY PRIVATE & CONFIDENTIAL")
    page_num = doc.page
    canvas.drawRightString(width - 40, 20, f"SLIDE {page_num:02d} OF 11")

    canvas.restoreState()


def build_vc_friendly_pdf(output_path: str):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=landscape(letter),
        leftMargin=40,
        rightMargin=40,
        topMargin=42,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Typography Hierarchy
    cat_style = ParagraphStyle(
        'CategoryTag',
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=CYAN_ACCENT,
        spaceAfter=4
    )

    title_style = ParagraphStyle(
        'DeckTitle',
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=TEXT_WHITE,
        spaceAfter=14
    )

    lead_style = ParagraphStyle(
        'DeckLead',
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=TEXT_LIGHT,
        spaceAfter=12
    )

    card_label_style = ParagraphStyle(
        'CardLabel',
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=TEXT_SLATE,
        spaceAfter=3
    )

    card_metric_style = ParagraphStyle(
        'CardMetric',
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=EMERALD_GREEN,
        spaceAfter=2
    )

    card_body_style = ParagraphStyle(
        'CardBody',
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=TEXT_LIGHT
    )

    problem_body_style = ParagraphStyle(
        'ProblemBody',
        fontName='Helvetica',
        fontSize=9.5,
        leading=13,
        textColor=TEXT_LIGHT
    )

    story = []

    # =========================================================================
    # SLIDE 1: THE CATEGORY HOOK
    # =========================================================================
    story.append(Paragraph("SLIDE 01 // CATEGORY HOOK", cat_style))
    story.append(Paragraph("CogniFlow AI", title_style))
    story.append(Paragraph("Autonomous Multi-Agent Reliability & Enterprise QA Platform", ParagraphStyle('Hook', fontName='Helvetica-Bold', fontSize=16, leading=20, textColor=CYAN_ACCENT, spaceAfter=20)))
    
    s1_data = [
        [
            Paragraph("<b>Target Category</b><br/><font color='#e2e8f0'>Enterprise Software / GenAI Infrastructure</font>", card_body_style),
            Paragraph("<b>Current Round</b><br/><font color='#10b981'><b>Raising $2.5M Series Seed</b></font>", card_body_style),
            Paragraph("<b>Post-Money Valuation</b><br/><font color='#e2e8f0'>$18.0M Post-Money Cap</font>", card_body_style),
            Paragraph("<b>Headquarters</b><br/><font color='#e2e8f0'>Bengaluru & San Francisco</font>", card_body_style)
        ]
    ]
    s1_table = Table(s1_data, colWidths=[175, 175, 175, 175])
    s1_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), CARD_BG),
        ('BOX', (0,0), (-1,-1), 1, CARD_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, CARD_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 14),
        ('BOTTOMPADDING', (0,0), (-1,-1), 14),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(s1_table)
    story.append(Spacer(1, 25))
    story.append(Paragraph("<b>The One-Liner</b>: CogniFlow intercepts non-deterministic agent tool calls at the Linux kernel level in under 12ms, eliminating database corruption and automated hallucination cascades for Fortune 500 engineering teams.", lead_style))
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 2: THE BLEEDING NECK (PROBLEM)
    # =========================================================================
    story.append(Paragraph("SLIDE 02 // THE HAIR-ON-FIRE PROBLEM", cat_style))
    story.append(Paragraph("Enterprises Are Bleeding Money on Broken Agent Loops", title_style))
    story.append(Paragraph("Critical Pain Point: Multi-agent workflows are failing in production due to 3 catastrophic vulnerabilities:", lead_style))

    p_data = [
        [
            Paragraph("<font color='#f43f5e'><b>45% EXECUTION FAILURE RATE</b></font><br/><br/>Multi-agent loops get trapped in circular reasoning calls, causing enterprise web workers to hang indefinitely.", problem_body_style),
            Paragraph("<font color='#f43f5e'><b>DATABASE CORRUPTION</b></font><br/><br/>Hallucinated SQL and API writes corrupt production customer data, requiring an average of 6 hours of dev rollback downtime.", problem_body_style),
            Paragraph("<font color='#f43f5e'><b>$300K+ WASTED TOKENS / QTR</b></font><br/><br/>Uncontrolled recursive LLM tool calls burn enterprise cloud budgets on redundant API pass-through calls.", problem_body_style)
        ]
    ]
    p_table = Table(p_data, colWidths=[233, 233, 234])
    p_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), CARD_BG),
        ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor("#7F1D1D")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, CARD_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 16),
        ('BOTTOMPADDING', (0,0), (-1,-1), 16),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(p_table)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 3: THE 10X MECHANISM (SOLUTION)
    # =========================================================================
    story.append(Paragraph("SLIDE 03 // THE 10x MECHANISM", cat_style))
    story.append(Paragraph("Active Runtime Interception & Zero-Downtime State Rollback", title_style))
    
    sol_data = [
        [
            Paragraph("<font color='#f43f5e'><b>WITHOUT COGNIFLOW (THE STATUS QUO)</b></font><br/><br/>"
                      "&bull; Agent initiates uncontrolled SQL / API mutation<br/>"
                      "&bull; Database corrupts user account balances or records<br/>"
                      "&bull; Incident triggers on PagerDuty 4 hours later<br/>"
                      "&bull; Engineering team manually runs database restores<br/>"
                      "&bull; <b>Average Loss: $65,000 per incident</b>", card_body_style),
            Paragraph("<font color='#10b981'><b>WITH COGNIFLOW (THE 10X MECHANISM)</b></font><br/><br/>"
                      "&bull; <b>Kernel-Level eBPF Probe intercepts tool call in &lt;12ms</b><br/>"
                      "&bull; Local SLM Arbiter checks execution tree determinism<br/>"
                      "&bull; Hallucinated state change is isolated & rolled back instantly<br/>"
                      "&bull; Zero customer impact; full telemetry trace logged in CI/CD<br/>"
                      "&bull; <b>Zero downtime & 100% compliance SLA</b>", card_body_style)
        ]
    ]
    sol_table = Table(sol_data, colWidths=[350, 350])
    sol_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), colors.HexColor("#191321")),
        ('BACKGROUND', (1,0), (1,0), colors.HexColor("#0f2420")),
        ('BOX', (0,0), (0,0), 1, colors.HexColor("#7F1D1D")),
        ('BOX', (1,0), (1,0), 1.5, EMERALD_GREEN),
        ('TOPPADDING', (0,0), (-1,-1), 14),
        ('BOTTOMPADDING', (0,0), (-1,-1), 14),
        ('LEFTPADDING', (0,0), (-1,-1), 14),
        ('RIGHTPADDING', (0,0), (-1,-1), 14),
    ]))
    story.append(sol_table)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 4: WHY NOW?
    # =========================================================================
    story.append(Paragraph("SLIDE 04 // MACRO INFLECTION POINT", cat_style))
    story.append(Paragraph("Why This Couldn't Exist 3 Years Ago", title_style))
    story.append(Paragraph("Three structural tailwinds make 2026-2027 the exact window to capture this market:", lead_style))

    why_data = [
        [
            Paragraph("<font color='#38bdf8'><b>1. REASONING MODELS ARRIVED</b></font><br/><br/>Multi-step reasoning models (o1, Sonnet, Gemini) just made autonomous agentic loops viable in enterprise production.", card_body_style),
            Paragraph("<font color='#38bdf8'><b>2. BUDGET INFLECTION POINT</b></font><br/><br/>Enterprise GenAI budgets have moved from 'exploratory prompt experiments' to 'production infrastructure & compliance SLAs'.", card_body_style),
            Paragraph("<font color='#38bdf8'><b>3. eBPF KERNEL MATURITY</b></font><br/><br/>Linux kernel tracing probes now run inside enterprise Kubernetes clusters with near-zero latency overhead (&lt;12ms).", card_body_style)
        ]
    ]
    why_table = Table(why_data, colWidths=[233, 233, 234])
    why_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), CARD_BG),
        ('BOX', (0,0), (-1,-1), 1, CARD_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, CARD_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 16),
        ('BOTTOMPADDING', (0,0), (-1,-1), 16),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(why_table)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 5: MARKET SIZING (BOTTOM-UP MATH)
    # =========================================================================
    story.append(Paragraph("SLIDE 05 // BOTTOM-UP MARKET SIZING", cat_style))
    story.append(Paragraph("A $2.1B Beachhead Expanding to a $95B Global TAM", title_style))

    tam_data = [
        [
            Paragraph("<font color='#94a3b8'><b>SOM (BEACHHEAD MARKET)</b></font><br/><br/>"
                      "<font size='18' color='#38bdf8'><b>$2.16 BILLION</b></font><br/><br/>"
                      "120,000 Mid-to-Large Engineering Teams &times; $18,000 Initial ACV.<br/>"
                      "Target: US/EU SaaS and Indian Global Capability Centers (GCCs).", card_body_style),
            Paragraph("<font color='#94a3b8'><b>SAM (SERVICEABLE ADDRESSABLE)</b></font><br/><br/>"
                      "<font size='18' color='#10b981'><b>$8.64 BILLION</b></font><br/><br/>"
                      "Fortune 2000 Enterprises deploying multi-agent workflows across production databases with dedicated VPC air-gaps.", card_body_style),
            Paragraph("<font color='#94a3b8'><b>TAM (TOTAL GLOBAL MARKET)</b></font><br/><br/>"
                      "<font size='18' color='#ffffff'><b>$95.0 BILLION</b></font><br/><br/>"
                      "Total Enterprise Observability, Automated QA, and AI Governance Software by 2030 (Gartner / IDC forecast).", card_body_style)
        ]
    ]
    tam_table = Table(tam_data, colWidths=[233, 233, 234])
    tam_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), CARD_BG),
        ('BOX', (0,0), (-1,-1), 1, CARD_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, CARD_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 16),
        ('BOTTOMPADDING', (0,0), (-1,-1), 16),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(tam_table)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 6: TECHNICAL MOAT & SECRET SAUCE
    # =========================================================================
    story.append(Paragraph("SLIDE 06 // TECHNICAL DEFENSIBILITY", cat_style))
    story.append(Paragraph("Why Foundation Models & Wrappers Can't Copy Us", title_style))

    moat_data = [
        [
            Paragraph("<font color='#38bdf8'><b>1. KERNEL-LEVEL eBPF PROBES</b></font><br/><br/>"
                      "Unlike Python wrapper tools (LangSmith, basic logging), our interceptor runs as an eBPF probe at the Linux OS layer inside customer VPCs. Zero network latency overhead.", card_body_style),
            Paragraph("<font color='#38bdf8'><b>2. LOCAL SLM ARBITER</b></font><br/><br/>"
                      "Replaced expensive $30K/mo OpenAI evaluation bills with fine-tuned 3B parameter local models running on customer hardware, <b>slashing token COGS by 76%</b>.", card_body_style),
            Paragraph("<font color='#38bdf8'><b>3. RUNTIME CI/CD LOCK-IN</b></font><br/><br/>"
                      "Embedded directly into developer testing pipelines and deployment gates. Ripping out CogniFlow creates immediate enterprise compliance vulnerabilities.", card_body_style)
        ]
    ]
    moat_table = Table(moat_data, colWidths=[233, 233, 234])
    moat_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), CARD_BG),
        ('BOX', (0,0), (-1,-1), 1, CARD_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, CARD_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 16),
        ('BOTTOMPADDING', (0,0), (-1,-1), 16),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(moat_table)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 7: TRACTION & COMPOUNDING UNIT ECONOMICS
    # =========================================================================
    story.append(Paragraph("SLIDE 07 // TRACTION & COMPOUNDING ECONOMICS", cat_style))
    story.append(Paragraph("Demonstrated Capital-Efficient Software Scale", title_style))

    metrics_tiles = [
        [
            Paragraph("<font color='#94a3b8'>ANNUAL RECURRING REVENUE</font><br/><font size='20' color='#10b981'><b>$1,020,000 ARR</b></font><br/><font size='8' color='#94a3b8'>$85,000 MRR | 5.7x YoY Growth</font>", card_body_style),
            Paragraph("<font color='#94a3b8'>LTV : CAC RATIO</font><br/><font size='20' color='#38bdf8'><b>25.3x</b></font><br/><font size='8' color='#94a3b8'>Benchmark: > 3.0x (Elite)</font>", card_body_style),
            Paragraph("<font color='#94a3b8'>CAC PAYBACK PERIOD</font><br/><font size='20' color='#fbbf24'><b>4.4 MONTHS</b></font><br/><font size='8' color='#94a3b8'>Fast cash flow recycling</font>", card_body_style),
            Paragraph("<font color='#94a3b8'>BURN MULTIPLE</font><br/><font size='20' color='#10b981'><b>0.95x</b></font><br/><font size='8' color='#94a3b8'>David Sacks Metric: &lt; 1.0x</font>", card_body_style),
        ]
    ]
    m_table = Table(metrics_tiles, colWidths=[175, 175, 175, 175])
    m_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), CARD_BG),
        ('BOX', (0,0), (-1,-1), 1.5, EMERALD_GREEN),
        ('INNERGRID', (0,0), (-1,-1), 0.5, CARD_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 14),
        ('BOTTOMPADDING', (0,0), (-1,-1), 14),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(m_table)
    story.append(Spacer(1, 20))
    story.append(Paragraph("<b>Customer Health</b>: 91.0% Software Gross Margins, 0.9% Monthly Logo Churn, and 11.5 Months of existing cash runway ($750K in bank).", lead_style))
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 8: GO-TO-MARKET FLYWHEEL
    # =========================================================================
    story.append(Paragraph("SLIDE 08 // GO-TO-MARKET FLYWHEEL", cat_style))
    story.append(Paragraph("Developer Land & Enterprise Expand Engine", title_style))

    gtm_data = [
        [
            Paragraph("<font color='#38bdf8'><b>PHASE 1: LAND (PLG)</b></font><br/><br/>Free open-source Python and TypeScript agent SDK drives grassroots adoption among developers on GitHub.", card_body_style),
            Paragraph("<font color='#10b981'><b>PHASE 2: EXPAND (USAGE)</b></font><br/><br/>Automated transition to usage-based pricing ($0.05 per 100K monitored agent executions) as applications enter production.", card_body_style),
            Paragraph("<font color='#ffffff'><b>PHASE 3: LOCK (ENTERPRISE)</b></font><br/><br/>Annual Enterprise Contracts ($25K - $100K ACV) for air-gapped VPC deployments, SOC2 Type II, RBAC, and PII redaction.", card_body_style)
        ]
    ]
    gtm_table = Table(gtm_data, colWidths=[233, 233, 234])
    gtm_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), CARD_BG),
        ('BOX', (0,0), (-1,-1), 1, CARD_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, CARD_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 16),
        ('BOTTOMPADDING', (0,0), (-1,-1), 16),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(gtm_table)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 9: COMPETITOR 2x2 MATRIX
    # =========================================================================
    story.append(Paragraph("SLIDE 09 // COMPETITIVE LANDSCAPE", cat_style))
    story.append(Paragraph("Positioned at Active State Protection with Low Inference COGS", title_style))

    comp_data = [
        [
            Paragraph("<b>COMPETITIVE QUADRANT</b>", card_label_style),
            Paragraph("<b>HIGH INFERENCE COGS (API CALLS)</b>", card_label_style),
            Paragraph("<b>LOW INFERENCE COGS (LOCAL SLM)</b>", card_label_style),
        ],
        [
            Paragraph("<b>ACTIVE RUNTIME ROLLBACK</b>", card_label_style),
            Paragraph("<font color='#f43f5e'><b>API Wrappers</b></font><br/>High latency, 90% margin illusion, breaks when OpenAI changes API.", card_body_style),
            Paragraph("<font color='#10b981'><b>COGNIFLOW AI (LEADER)</b></font><br/>Kernel eBPF interception (&lt;12ms), zero-token-overhead SLM, active rollback.", card_body_style)
        ],
        [
            Paragraph("<b>PASSIVE LOGGING ONLY</b>", card_label_style),
            Paragraph("<font color='#f43f5e'><b>Legacy APMs (Datadog/Dynatrace)</b></font><br/>Very high cost, passive logs only; cannot rollback state.", card_body_style),
            Paragraph("<font color='#94a3b8'><b>Open Source Logging (Prometheus)</b></font><br/>Raw metrics, zero agent understanding, manual debugging.", card_body_style)
        ]
    ]
    comp_table = Table(comp_data, colWidths=[180, 260, 260])
    comp_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), CARD_BG),
        ('BACKGROUND', (2,1), (2,1), colors.HexColor("#0f2922")),
        ('BOX', (0,0), (-1,-1), 1, CARD_BORDER),
        ('BOX', (2,1), (2,1), 1.5, EMERALD_GREEN),
        ('INNERGRID', (0,0), (-1,-1), 0.5, CARD_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 12),
        ('BOTTOMPADDING', (0,0), (-1,-1), 12),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(comp_table)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 10: FOUNDING TEAM & EARNED SECRETS
    # =========================================================================
    story.append(Paragraph("SLIDE 10 // UNFAIR ADVANTAGE & TEAM", cat_style))
    story.append(Paragraph("Systems Architects with Deep Execution Pedigree", title_style))

    team_data = [
        [
            Paragraph("<font color='#38bdf8'><b>AARAV SHARMA</b></font> &mdash; <i>CEO & Co-Founder</i><br/><br/>"
                      "&bull; <b>Ex-Staff Engineer @ Postman</b>: Built distributed tracing pipelines handling 25M developers.<br/>"
                      "&bull; <b>Patents</b>: Holds 2 granted US patents in runtime execution interception.<br/>"
                      "&bull; <b>Education</b>: B.Tech Computer Science (IIT Bombay).", card_body_style),
            Paragraph("<font color='#38bdf8'><b>NEHA VERMA</b></font> &mdash; <i>CTO & Co-Founder</i><br/><br/>"
                      "&bull; <b>Ex-ML Lead @ BrowserStack</b>: Architected distributed testing clusters running 100K jobs/hour.<br/>"
                      "&bull; <b>Specialization</b>: Published researcher in small language model fine-tuning.<br/>"
                      "&bull; <b>Education</b>: M.S. Computer Science (Stanford University).", card_body_style)
        ]
    ]
    team_table = Table(team_data, colWidths=[350, 350])
    team_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), CARD_BG),
        ('BOX', (0,0), (-1,-1), 1, CARD_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, CARD_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 14),
        ('BOTTOMPADDING', (0,0), (-1,-1), 14),
        ('LEFTPADDING', (0,0), (-1,-1), 14),
        ('RIGHTPADDING', (0,0), (-1,-1), 14),
    ]))
    story.append(team_table)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 11: THE ASK & 18-MONTH MILESTONES
    # =========================================================================
    story.append(Paragraph("SLIDE 11 // THE ASK & MILESTONES", cat_style))
    story.append(Paragraph("Raising $2,500,000 to Scale to $3.5M ARR", title_style))

    ask_data = [
        [
            Paragraph("<font color='#94a3b8'>CAPITAL ALLOCATION (USE OF FUNDS)</font><br/><br/>"
                      "&bull; <b>70% Core Distributed Systems Engineering</b>: Hiring senior eBPF kernel engineers in Bengaluru.<br/>"
                      "&bull; <b>20% Developer Go-To-Market</b>: Technical DevRel, developer hackathons, and US enterprise sales.<br/>"
                      "&bull; <b>10% Dedicated GPU Cluster</b>: Local SLM model fine-tuning and benchmark clusters.", card_body_style),
            Paragraph("<font color='#10b981'><b>18-MONTH SERIES A MILESTONES</b></font><br/><br/>"
                      "&bull; <b>ARR Target</b>: Scale from <b>$1.02M ARR to $3.5M ARR</b>.<br/>"
                      "&bull; <b>Enterprise Logos</b>: Expand from 71 to <b>150+ Enterprise Accounts</b>.<br/>"
                      "&bull; <b>Net Retention</b>: Maintain &gt;130% Net Dollar Retention (NDR).<br/>"
                      "&bull; <b>Series A Ready</b>: Positioned for a $12M - $15M round at top-decile valuation.", card_body_style)
        ]
    ]
    ask_table = Table(ask_data, colWidths=[350, 350])
    ask_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), CARD_BG),
        ('BOX', (0,0), (-1,-1), 1.5, AMBER_YELLOW),
        ('INNERGRID', (0,0), (-1,-1), 0.5, CARD_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 14),
        ('BOTTOMPADDING', (0,0), (-1,-1), 14),
        ('LEFTPADDING', (0,0), (-1,-1), 14),
        ('RIGHTPADDING', (0,0), (-1,-1), 14),
    ]))
    story.append(ask_table)

    # Build Document with custom onFirstPage and onLaterPages callback
    doc.build(story, onFirstPage=draw_slide_background, onLaterPages=draw_slide_background)
    print(f"[+] Venture Capitalist Friendly Pitch Deck compiled at: {output_path}")


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    out_pdf = os.path.join(base_dir, "Sample_Pitch_Deck_CogniFlow.pdf")
    build_vc_friendly_pdf(out_pdf)
