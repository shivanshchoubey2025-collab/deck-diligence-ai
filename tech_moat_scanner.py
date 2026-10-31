"""
========================================================================================
TECH MOAT & AI WRAPPER SCANNER — TECHNICAL DUE DILIGENCE ENGINE
----------------------------------------------------------------------------------------
Target: Tier-1 Venture Capital (VC) Investment Committees (Peak XV, Benchmark, Accel)
Purpose: Audits startup codebases & dependency manifests to distinguish between
         defensible deeptech/AI infrastructure vs. thin, vulnerable OpenAI API wrappers.
========================================================================================
Key Metrics Computed:
  1. Wrapper Vulnerability Index (0% to 100%)
  2. Proprietary Systems Moat Score (0% to 100%)
  3. Platform Extinction Risk Level (Low, Moderate, Critical)
  4. Inferred Long-Term Gross Margin Ceiling (% based on third-party API exposure)
  5. Overall Architectural Defensibility Score (0 to 100)
========================================================================================
"""

import os
import re
import json
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional


# -----------------------------------------------------------------------------
# TIER-1 VC DEPENDENCY TAXONOMY
# -----------------------------------------------------------------------------
WRAPPER_INDICATORS = {
    "python": [
        "openai", "anthropic", "langchain", "langchain-core", "langchain-community",
        "langchain-experimental", "crewai", "autogen", "embedchain", "flowise",
        "cohere", "groq", "replicate", "gemini-api"
    ],
    "javascript": [
        "openai", "@anthropic-ai/sdk", "langchain", "@langchain/core", "crewai",
        "ai", "@ai-sdk/openai", "groq-sdk"
    ]
}

DEEPTECH_MOAT_INDICATORS = {
    "python": [
        "torch", "torchvision", "torchaudio", "vllm", "triton", "onnx", "onnxruntime",
        "tensorrt", "bitsandbytes", "accelerate", "deepspeed", "transformers", "peft",
        "bcc", "aya", "bpf", "scikit-learn", "numpy", "cupy", "faiss-gpu", "flash-attn"
    ],
    "infrastructure": [
        "kafka", "confluent-kafka", "nats-py", "redis", "grpcio", "celery", "ray",
        "kubernetes", "docker", "pydantic-core"
    ],
    "javascript": [
        "onnxruntime-node", "@tensorflow/tfjs", "apache-arrow", "kafkajs", "ioredis"
    ]
}


@dataclass
class CodeAuditReport:
    company_name: str
    target_source: str
    defensibility_score: int
    tier_classification: str
    extinction_risk: str
    wrapper_index_pct: float
    systems_moat_pct: float
    gross_margin_ceiling_pct: float
    wrapper_libraries_found: List[str]
    deeptech_libraries_found: List[str]
    infrastructure_libraries_found: List[str]
    audit_findings: List[Dict[str, str]]
    ic_recommendation: str


class TechMoatScanner:
    def __init__(self, company_name: str = "Target Startup"):
        self.company_name = company_name

    def audit_manifests(
        self,
        requirements_txt: Optional[str] = None,
        package_json_str: Optional[str] = None,
        code_snippets: Optional[str] = None
    ) -> CodeAuditReport:
        """
        Audits Python requirements.txt, Node package.json, and raw code text
        to evaluate architectural defensibility and platform extinction risk.
        """
        wrapper_found = set()
        deeptech_found = set()
        infra_found = set()

        all_text = ""

        # 1. Parse requirements.txt
        if requirements_txt:
            all_text += "\n" + requirements_txt
            for line in requirements_txt.splitlines():
                line = line.strip().split("==")[0].split(">=")[0].split("<=")[0].split("~=")[0].strip().lower()
                if not line or line.startswith("#"):
                    continue
                if line in WRAPPER_INDICATORS["python"]:
                    wrapper_found.add(line)
                if line in DEEPTECH_MOAT_INDICATORS["python"]:
                    deeptech_found.add(line)
                if line in DEEPTECH_MOAT_INDICATORS["infrastructure"]:
                    infra_found.add(line)

        # 2. Parse package.json
        if package_json_str:
            all_text += "\n" + package_json_str
            try:
                pkg_data = json.loads(package_json_str)
                deps = {}
                deps.update(pkg_data.get("dependencies", {}))
                deps.update(pkg_data.get("devDependencies", {}))
                for dep in deps.keys():
                    dep_clean = dep.lower()
                    if dep_clean in WRAPPER_INDICATORS["javascript"]:
                        wrapper_found.add(dep_clean)
                    if dep_clean in DEEPTECH_MOAT_INDICATORS["javascript"]:
                        deeptech_found.add(dep_clean)
            except Exception:
                pass

        # 3. Code Snippet Inspection (e.g. eBPF, AST, custom CUDA)
        if code_snippets:
            all_text += "\n" + code_snippets
            code_lower = code_snippets.lower()
            if any(term in code_lower for term in ["bpf_attach", "sec(\"tracepoint", "ebpf", "bpf_program"]):
                deeptech_found.add("ebpf-kernel-probes")
            if any(term in code_lower for term in ["torch.cuda", "custom_kernel", "cuda_malloc", "flash_attention"]):
                deeptech_found.add("custom-cuda-kernels")
            if any(term in code_lower for term in ["small_language_model", "local_slm", "vllm.llm"]):
                deeptech_found.add("local-slm-inference")

        return self._evaluate_metrics(
            wrapper_found=list(wrapper_found),
            deeptech_found=list(deeptech_found),
            infra_found=list(infra_found),
            raw_text=all_text
        )

    def _evaluate_metrics(
        self,
        wrapper_found: List[str],
        deeptech_found: List[str],
        infra_found: List[str],
        raw_text: str
    ) -> CodeAuditReport:
        total_signals = len(wrapper_found) + len(deeptech_found) + len(infra_found)
        findings = []

        # Calculate Wrapper Vulnerability Index
        if total_signals == 0:
            wrapper_index = 0.50
            systems_moat = 0.50
        else:
            wrapper_index = len(wrapper_found) / max(1.0, (len(wrapper_found) + len(deeptech_found) * 1.5))
            systems_moat = (len(deeptech_found) * 1.5 + len(infra_found) * 0.8) / max(1.0, total_signals * 1.2)

        wrapper_index = min(1.0, max(0.0, wrapper_index))
        systems_moat = min(1.0, max(0.0, systems_moat))

        # Base Defensibility Score calculation
        score = int((systems_moat * 70) + ((1.0 - wrapper_index) * 30))

        # Gross Margin Ceiling Estimation
        if wrapper_index >= 0.70 and len(deeptech_found) == 0:
            margin_ceiling = 64.0  # Heavily dragged down by API token bills
        elif wrapper_index >= 0.40:
            margin_ceiling = 75.0
        elif len(deeptech_found) >= 2:
            margin_ceiling = 88.0  # High margin due to local compute & custom models
        else:
            margin_ceiling = 80.0

        # Findings Evaluation
        # 1. Wrapper Inspection
        if len(wrapper_found) > 0 and len(deeptech_found) == 0:
            score = min(score, 35)
            findings.append({
                "severity": "CRITICAL RED FLAG",
                "title": "High-Risk Pass-Through API Wrapper",
                "finding": f"Identified pure wrapper dependencies ({', '.join(wrapper_found)}) with ZERO underlying ML infrastructure or compiled kernels.",
                "vc_impact": "High risk of total extinction if OpenAI or Anthropic releases native tooling; long-term gross margins capped at ~64% due to API token COGS."
            })
        elif len(wrapper_found) > 0 and len(deeptech_found) > 0:
            findings.append({
                "severity": "POSITIVE SIGNAL",
                "title": "Hybrid Architecture with Proprietary Compute",
                "finding": f"Uses external APIs for general reasoning ({', '.join(wrapper_found)}) but balances with native ML / kernel infrastructure ({', '.join(deeptech_found)}).",
                "vc_impact": "Protects gross margins through local inference arbitration while maintaining fast product iteration velocity."
            })
        elif len(deeptech_found) >= 2:
            score = max(score, 82)
            findings.append({
                "severity": "TOP-TIER MOAT",
                "title": "Proprietary Deep Tech & Systems Infrastructure",
                "finding": f"Strong native ML and systems-level dependencies identified ({', '.join(deeptech_found)}). Zero reliance on superficial wrapper frameworks.",
                "vc_impact": "Elite architectural defensibility. High barriers to entry for competitors and complete independence from foundation model platform shifts."
            })

        # 2. Extinction Risk Level
        if score >= 75:
            extinction_risk = "LOW // DEFENSIBLE MOAT"
            tier = "Tier-1 Deep Tech Moat"
            ic_rec = "STRONG TECHNICAL BUY: Codebase shows genuine engineering depth, proprietary infrastructure, and sustainable unit economics."
        elif score >= 55:
            extinction_risk = "MODERATE // WORKFLOW DEFENSE"
            tier = "Tier-2 Workflow & Integration Moat"
            ic_rec = "CONDITIONAL APPROVAL: Verify switching costs and enterprise data gravity during customer reference calls."
        elif score >= 35:
            extinction_risk = "HIGH // PLATFORM DRIFT RISK"
            tier = "Tier-3 Vulnerable Wrapper"
            ic_rec = "HIGH TECHNICAL CAUTION: Startup is exposed to commoditization by foundation model hyperscalers. Require 50% discount on valuation."
        else:
            extinction_risk = "LETHAL // EXTINCTION IMMINENT"
            tier = "Tier-4 Superficial Wrapper"
            ic_rec = "PASS (TECHNICAL REJECT): Zero defensible software IP. High probability of commercial extinction within 12 months."

        score = max(10, min(95, score))

        return CodeAuditReport(
            company_name=self.company_name,
            target_source="Manifest & Codebase Audit",
            defensibility_score=score,
            tier_classification=tier,
            extinction_risk=extinction_risk,
            wrapper_index_pct=round(wrapper_index * 100, 1),
            systems_moat_pct=round(systems_moat * 100, 1),
            gross_margin_ceiling_pct=margin_ceiling,
            wrapper_libraries_found=wrapper_found,
            deeptech_libraries_found=deeptech_found,
            infrastructure_libraries_found=infra_found,
            audit_findings=findings,
            ic_recommendation=ic_rec
        )


# -----------------------------------------------------------------------------
# BENCHMARK TEST MANIFESTS (OPPOSING TECH ARTIFACTS)
# -----------------------------------------------------------------------------
COGNIFLOW_REQUIREMENTS = """
# CogniFlow AI - Enterprise Multi-Agent Observability
torch==2.4.0
vllm==0.5.4
transformers==4.42.0
bcc==0.29.0
triton==3.0.0
fastapi==0.111.0
grpcio==1.64.0
pydantic==2.8.2
redis==5.0.7
"""

COGNIFLOW_CODE_SAMPLE = """
import bcc
from vllm import LLM, SamplingParams

# Kernel eBPF probe interceptor for <12ms agent execution trace
bpf_program = \"\"\"
#include <uapi/linux/ptrace.h>
int trace_agent_tool_dispatch(struct pt_regs *ctx) {
    bpf_trace_printk("Agent tool call intercepted\\n");
    return 0;
}
\"\"\"

# Local Small Language Model (SLM) fine-tuned arbitration layer
local_evaluator = LLM(model="cogniflow-slm-3b-q4", tensor_parallel_size=1)
"""

HYPERBUZZ_REQUIREMENTS = """
# HyperBuzz AI - Autonomous Marketing Wrapper
openai==1.35.0
langchain==0.2.7
langchain-community==0.2.7
crewai==0.36.0
streamlit==1.36.0
requests==2.32.3
python-dotenv==1.0.1
"""

HYPERBUZZ_CODE_SAMPLE = """
from langchain.chat_models import ChatOpenAI
from crewai import Agent, Task, Crew

# Pure pass-through wrapper call
llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
marketing_agent = Agent(role="Social Media Marketer", goal="Write viral posts", llm=llm)
"""


def run_tech_moat_demo():
    print("=" * 84)
    print(" RUNNING TECH MOAT SCANNER: TIER-1 VC TECHNICAL DUE DILIGENCE AUDIT")
    print("=" * 84)

    scanner = TechMoatScanner()

    # 1. Audit CogniFlow AI
    print("\n>>> AUDITING STARTUP 1: CogniFlow AI (Enterprise Systems & SLM Moat)")
    scanner.company_name = "CogniFlow AI"
    rep1 = scanner.audit_manifests(
        requirements_txt=COGNIFLOW_REQUIREMENTS,
        code_snippets=COGNIFLOW_CODE_SAMPLE
    )
    print(f"Company:               {rep1.company_name}")
    print(f"Defensibility Score:   {rep1.defensibility_score} / 100 ({rep1.tier_classification})")
    print(f"Platform Extinction:   {rep1.extinction_risk}")
    print(f"Wrapper Vulnerability: {rep1.wrapper_index_pct}% | Systems Moat: {rep1.systems_moat_pct}%")
    print(f"Gross Margin Ceiling:  {rep1.gross_margin_ceiling_pct}% (Low third-party token COGS)")
    print(f"Deeptech Dependencies: {', '.join(rep1.deeptech_libraries_found)}")
    print(f"IC Recommendation:     {rep1.ic_recommendation}")
    print("-" * 84)

    # 2. Audit HyperBuzz AI
    print("\n>>> AUDITING STARTUP 2: HyperBuzz AI (Superficial LangChain / CrewAI Wrapper)")
    scanner.company_name = "HyperBuzz AI"
    rep2 = scanner.audit_manifests(
        requirements_txt=HYPERBUZZ_REQUIREMENTS,
        code_snippets=HYPERBUZZ_CODE_SAMPLE
    )
    print(f"Company:               {rep2.company_name}")
    print(f"Defensibility Score:   {rep2.defensibility_score} / 100 ({rep2.tier_classification})")
    print(f"Platform Extinction:   {rep2.extinction_risk}")
    print(f"Wrapper Vulnerability: {rep2.wrapper_index_pct}% | Systems Moat: {rep2.systems_moat_pct}%")
    print(f"Gross Margin Ceiling:  {rep2.gross_margin_ceiling_pct}% (Severe token pass-through drag)")
    print(f"Wrapper Dependencies:  {', '.join(rep2.wrapper_libraries_found)}")
    print(f"IC Recommendation:     {rep2.ic_recommendation}")
    print("=" * 84)


if __name__ == "__main__":
    run_tech_moat_demo()
