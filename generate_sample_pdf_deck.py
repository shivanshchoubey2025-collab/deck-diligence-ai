"""
Generates an institutional 11-slide PDF pitch deck for CogniFlow AI
using reportlab to serve as an instant test file for PDF ingestion.
"""

import os
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


def build_sample_pdf(output_path: str):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=landscape(letter),
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'SlideTitle',
        parent=styles['Heading1'],
        fontSize=26,
        leading=32,
        textColor=colors.HexColor('#1a365d'),
        spaceAfter=15
    )
    
    sub_style = ParagraphStyle(
        'SlideSubtitle',
        parent=styles['Normal'],
        fontSize=15,
        leading=20,
        textColor=colors.HexColor('#2b6cb0'),
        spaceAfter=20
    )
    
    body_style = ParagraphStyle(
        'SlideBody',
        parent=styles['Normal'],
        fontSize=13,
        leading=18,
        textColor=colors.HexColor('#2d3748'),
        spaceAfter=12
    )

    story = []

    slides_content = [
        # Slide 1
        ("CogniFlow AI", "Autonomous Multi-Agent Reliability & Enterprise QA Platform", [
            "Category: Enterprise Software & GenAI Infrastructure",
            "Round: Series Seed | Raising $2.5M at $18.0M Post-Money Valuation",
            "Founders: Aarav Sharma (Ex-Postman) & Neha Verma (Stanford MS CS)"
        ]),
        # Slide 2
        ("The Hair-On-Fire Problem", "Enterprises Are Bleeding Money on Failed Production Agents", [
            "Critical Pain Point: Enterprise LLM agents fail in production >45% of the time.",
            "Database Corruption: Non-deterministic agent hallucinated SQL writes corrupt production state.",
            "Wasted Capital: Fortune 500 enterprises burn over $300K/quarter on redundant token inference loops."
        ]),
        # Slide 3
        ("The 10x Mechanism", "Active Kernel-Level Interception with Zero-Downtime State Rollback", [
            "Our Solution: A lightweight runtime observability SDK that intercepts agent tool calls in under 12ms.",
            "Tracks distributed execution trees and automatically rolls back corrupted database state.",
            "Zero Downtime: Eliminates 6 hours of average engineer manual rollback downtime per incident."
        ]),
        # Slide 4
        ("Why Now?", "The Macro Inflection Point in Multi-Agent Reasoning", [
            "1. Reasoning Models (o1/Sonnet/Gemini) just made autonomous multi-step agents viable in 2026.",
            "2. Enterprise GenAI spending is shifting from prompt toys to compliance, reliability, and infrastructure.",
            "3. eBPF kernel tracing maturity in Kubernetes enables near-zero latency traffic inspection."
        ]),
        # Slide 5
        ("Market Sizing (Bottom-Up Math)", "From a $2.1B Beachhead to a $95.0B Global TAM", [
            "Claimed TAM: $95.0B Global Enterprise Observability & AI Governance Software.",
            "Serviceable Obtainable Market (SOM): $2.16B (120,000 mid-to-large dev teams @ $18,000 ACV).",
            "Bottom-up math grounded in developer team volume and enterprise software pricing power."
        ]),
        # Slide 6
        ("Technical Moat & Defensibility", "Why Foundation Models Cannot Replicate Our Infrastructure", [
            "Kernel-Level eBPF Probes: Runs inside customer VPCs with zero latency overhead.",
            "Proprietary Local SLM Arbiter: Fine-tuned 3B local model replaces external API calls, cutting COGS by 76%.",
            "Runtime Lock-In: Deeply embedded in CI/CD pipeline test gates with high enterprise switching costs."
        ]),
        # Slide 7
        ("Compounding Traction & Economics", "Demonstrated Capital-Efficient Software Scale", [
            "Financial Traction: $1,020,000 ARR ($85,000 MRR) growing at 5.7x YoY.",
            "Sales Efficiency: CAC is $4,800 with an elite 4.4 Months CAC Payback Period.",
            "Unit Economics: Inferred LTV:CAC of 25.28x with 91.0% Gross Margin and 0.9% monthly churn.",
            "Capital Discipline: Burn Multiple is 0.95x with 11.5 Months of Cash Runway ($750K in bank)."
        ]),
        # Slide 8
        ("Go-To-Market Flywheel", "Product-Led Developer Land & Enterprise Expand", [
            "1. Land: Free open-source Python/TypeScript agent SDK drives bottom-up adoption by engineering teams.",
            "2. Expand: Usage-based pricing tiers charging per 100K monitored agent executions.",
            "3. Lock: Enterprise air-gapped VPC deployments with SOC2 Type II, RBAC, and PII redaction."
        ]),
        # Slide 9
        ("Competitor Landscape (2x2)", "Positioned at Active State Protection with Low Inference COGS", [
            "Y-Axis: Active Runtime Rollback vs. Passive Log Ingestion.",
            "X-Axis: Lightweight Local SLM vs. Expensive Third-Party API Bills.",
            "Legacy APMs (Datadog/Dynatrace): High cost, passive logging only.",
            "OpenAI API Wrappers: High latency, 90% gross margin illusion, zero enterprise data privacy."
        ]),
        # Slide 10
        ("Founding Team & Earned Secrets", "Systems Architects with Proven Execution Pedigree", [
            "Aarav Sharma (CEO & Co-Founder): Ex-Staff Engineer at Postman. 2 US patents in distributed tracing.",
            "Neha Verma (CTO & Co-Founder): Ex-Machine Learning Lead at BrowserStack. M.S. CS from Stanford University.",
            "Advisors: Former VP of Infrastructure at Datadog and Lead Architect at HashiCorp."
        ]),
        # Slide 11
        ("The Ask & 18-Month Milestones", "Raising $2.5M Series Seed to Compound to $3.5M ARR", [
            "Round Structure: Raising $2,500,000 Series Seed for 24 months of runway.",
            "Use of Funds: 70% Core Engineering (eBPF & distributed systems), 20% DevRel GTM, 10% GPU Cluster.",
            "Series A Milestones: Scale from $1.02M ARR to $3.5M ARR with 150+ Enterprise Accounts."
        ])
    ]

    for i, (title, subtitle, bullets) in enumerate(slides_content, 1):
        story.append(Paragraph(f"SLIDE {i:02d} // {title.upper()}", sub_style))
        story.append(Paragraph(title, title_style))
        story.append(Paragraph(subtitle, sub_style))
        story.append(Spacer(1, 15))
        for b in bullets:
            story.append(Paragraph(f"&bull; {b}", body_style))
        if i < len(slides_content):
            story.append(PageBreak())

    doc.build(story)
    print(f"[+] Sample pitch deck PDF generated successfully at: {output_path}")


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(base_dir, "Sample_Pitch_Deck_CogniFlow.pdf")
    build_sample_pdf(out)
