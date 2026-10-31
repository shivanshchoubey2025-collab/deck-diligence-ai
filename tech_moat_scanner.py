"""
========================================================================================
DEPENDENCY & AST ARCHITECTURE AUDITOR — AI TECHNICAL DUE DILIGENCE
----------------------------------------------------------------------------------------
Purpose: Audits repository dependency manifests and Python ASTs to evaluate whether
         an early-stage AI startup has proprietary systems/model depth vs. thin API pass-through.
Methodology:
  1. AST Inspection: Parses real Python ASTs (ast.Import, ast.ImportFrom) to verify
     that imported modules are functional code imports, NOT comments or string mentions.
  2. Declared vs. Used Reconciliation: If source code is provided, declared dependencies
     must actually be imported in code to receive technical credit.
  3. Canonical Import Mapping: Normalizes PyPI package names to Python import names
     (e.g., scikit-learn -> sklearn, langchain-core -> langchain_core, flash-attn -> flash_attn).
  4. Non-Moat Utilities Removed: General utilities (numpy, redis, docker) are excluded from
     deeptech moat scoring.
========================================================================================
"""

import os
import ast
import re
import json
import textwrap
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Set


# -----------------------------------------------------------------------------
# CANONICAL PYPI PACKAGE TO PYTHON IMPORT NAME MAPPING
# -----------------------------------------------------------------------------
PACKAGE_TO_IMPORT_MAP = {
    # Wrapper frameworks
    "openai": "openai",
    "anthropic": "anthropic",
    "langchain": "langchain",
    "langchain-core": "langchain_core",
    "langchain-community": "langchain_community",
    "langchain-experimental": "langchain_experimental",
    "crewai": "crewai",
    "autogen": "autogen",
    "embedchain": "embedchain",
    "cohere": "cohere",
    "groq": "groq",
    "replicate": "replicate",
    
    # Native Deeptech & Specialized Systems
    "torch": "torch",
    "torchvision": "torchvision",
    "torchaudio": "torchaudio",
    "vllm": "vllm",
    "triton": "triton",
    "onnx": "onnx",
    "onnxruntime": "onnxruntime",
    "tensorrt": "tensorrt",
    "bitsandbytes": "bitsandbytes",
    "accelerate": "accelerate",
    "deepspeed": "deepspeed",
    "transformers": "transformers",
    "peft": "peft",
    "bcc": "bcc",
    "aya": "aya",
    "scikit-learn": "sklearn",
    "flash-attn": "flash_attn",
    "cupy": "cupy",
    "faiss-gpu": "faiss",
    
    # Distributed Infrastructure
    "ray": "ray",
    "grpcio": "grpc",
    "celery": "celery",
    "confluent-kafka": "confluent_kafka",
}

IMPORT_TO_PACKAGE_MAP = {v: k for k, v in PACKAGE_TO_IMPORT_MAP.items()}

WRAPPER_PACKAGES = {
    "openai", "anthropic", "langchain", "langchain-core", "langchain-community",
    "langchain-experimental", "crewai", "autogen", "embedchain", "cohere", "groq", "replicate"
}

DEEPTECH_PACKAGES = {
    "torch", "torchvision", "torchaudio", "vllm", "triton", "onnx", "onnxruntime",
    "tensorrt", "bitsandbytes", "accelerate", "deepspeed", "transformers", "peft",
    "bcc", "aya", "scikit-learn", "flash-attn", "cupy", "faiss-gpu"
}

INFRASTRUCTURE_PACKAGES = {
    "ray", "grpcio", "celery", "confluent-kafka"
}


class PythonASTImportVisitor(ast.NodeVisitor):
    """
    Genuine Abstract Syntax Tree (AST) visitor that extracts actual imports and call sites.
    Prevents false positives from comments or documentation containing library names.
    """
    def __init__(self):
        self.imported_modules: Set[str] = set()

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            base_mod = alias.name.split(".")[0].lower()
            self.imported_modules.add(base_mod)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        if node.module:
            base_mod = node.module.split(".")[0].lower()
            self.imported_modules.add(base_mod)
        self.generic_visit(node)


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
    unused_declared_libraries: List[str]
    audit_findings: List[Dict[str, str]]
    ic_recommendation: str
    limitations_disclaimer: str = (
        "Technical audit measures dependency reliance and token pass-through architecture. "
        "It does not verify commercial moats (data contracts, customer switching costs, workflow lock-in)."
    )


class TechMoatScanner:
    def __init__(self, company_name: str = "Target Startup"):
        self.company_name = company_name

    def parse_python_ast(self, python_code: str) -> Tuple[Optional[Set[str]], Optional[str]]:
        """
        Parses raw Python code using Python's standard `ast` module.
        Extracts verified import statements. Rejects unparseable code with syntax errors.
        """
        try:
            tree = ast.parse(textwrap.dedent(python_code))
            visitor = PythonASTImportVisitor()
            visitor.visit(tree)
            return visitor.imported_modules, None
        except SyntaxError as e:
            return None, f"SyntaxError on line {e.lineno}: {e.msg}"

    def audit_manifests(
        self,
        requirements_txt: Optional[str] = None,
        package_json_str: Optional[str] = None,
        code_snippets: Optional[str] = None
    ) -> CodeAuditReport:
        """
        Audits Python requirements.txt, Node package.json, and verified AST code imports.
        Enforces declared vs. used reconciliation when source code is provided.
        """
        manifest_declared_pkgs = set()
        code_imports = set()
        syntax_error = None

        # 1. Parse requirements.txt
        if requirements_txt:
            for line in requirements_txt.splitlines():
                line = line.strip().split("==")[0].split(">=")[0].split("<=")[0].split("~=")[0].strip().lower()
                if not line or line.startswith("#"):
                    continue
                manifest_declared_pkgs.add(line)

        # 2. Parse package.json
        if package_json_str:
            try:
                pkg = json.loads(package_json_str)
                all_deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
                for dep in all_deps:
                    manifest_declared_pkgs.add(dep.lower())
            except Exception:
                pass

        # 3. Genuine AST Parsing of Source Code (No Regex Fallback)
        if code_snippets:
            imported_mods, err = self.parse_python_ast(code_snippets)
            if err:
                syntax_error = err
            elif imported_mods:
                code_imports = imported_mods

        # Reconcile packages:
        # If code is provided, packages only count if their canonical import name is found in code!
        active_packages = set()
        unused_packages = set()

        if code_snippets and not syntax_error and code_imports:
            # Code was provided: check which declared packages are actually imported
            for pkg in manifest_declared_pkgs:
                expected_import = PACKAGE_TO_IMPORT_MAP.get(pkg, pkg.replace("-", "_"))
                if expected_import in code_imports or pkg in code_imports:
                    active_packages.add(pkg)
                else:
                    unused_packages.add(pkg)
            
            # Also credit any imported packages that appear in code directly
            for imp in code_imports:
                pkg_name = IMPORT_TO_PACKAGE_MAP.get(imp, imp)
                active_packages.add(pkg_name)
        else:
            # No code provided; evaluate based on manifest declarations alone
            active_packages = set(manifest_declared_pkgs)

        # Classify into taxonomies
        wrapper_found = active_packages.intersection(WRAPPER_PACKAGES)
        deeptech_found = active_packages.intersection(DEEPTECH_PACKAGES)
        infra_found = active_packages.intersection(INFRASTRUCTURE_PACKAGES)

        # Track unused deeptech claims
        unused_deeptech = unused_packages.intersection(DEEPTECH_PACKAGES)

        # Calculate Dependency Metrics
        total_signals = len(wrapper_found) + len(deeptech_found) + len(infra_found)
        findings = []

        if syntax_error:
            findings.append({
                "severity": "SYNTAX ERROR",
                "title": "Unparseable Python Source Code",
                "finding": f"AST parser failed: {syntax_error}. Code was not credited to prevent comment spoofing.",
                "vc_impact": "Code cannot be verified automatically."
            })

        if unused_deeptech:
            findings.append({
                "severity": "WARNING",
                "title": "Unused Declared Deeptech Dependencies",
                "finding": f"Manifest declares ({', '.join(unused_deeptech)}), but AST found zero import references in code.",
                "vc_impact": "Declared dependencies do not reflect active production architecture."
            })

        if total_signals == 0:
            wrapper_index = 0.50
            systems_moat = 0.00
            score = 30
            margin_ceiling = 70.0
        else:
            wrapper_index = len(wrapper_found) / max(1.0, (len(wrapper_found) + len(deeptech_found) * 1.5))
            systems_moat = (len(deeptech_found) * 1.5 + len(infra_found) * 0.5) / max(1.0, total_signals * 1.2)
            wrapper_index = min(1.0, max(0.0, wrapper_index))
            systems_moat = min(1.0, max(0.0, systems_moat))
            score = int((systems_moat * 70) + ((1.0 - wrapper_index) * 30))

            if wrapper_index >= 0.70 and len(deeptech_found) == 0:
                margin_ceiling = 55.0  # Third-party variable API token COGS drag
            elif wrapper_index >= 0.40:
                margin_ceiling = 68.0  # Hybrid inference
            elif len(deeptech_found) >= 2:
                margin_ceiling = 80.0  # Self-hosted / local compiled kernels
            else:
                margin_ceiling = 75.0

        if len(wrapper_found) > 0 and len(deeptech_found) == 0:
            score = min(score, 35)
            findings.append({
                "severity": "CRITICAL RED FLAG",
                "title": "Third-Party API Pass-Through Architecture",
                "finding": f"Identified active wrapper dependencies ({', '.join(wrapper_found)}) with zero native local models or compiled compute runtimes.",
                "vc_impact": "High exposure to foundation model commoditization; gross margins capped at ~55% due to variable API token bills."
            })
        elif len(wrapper_found) > 0 and len(deeptech_found) > 0:
            findings.append({
                "severity": "POSITIVE SIGNAL",
                "title": "Hybrid Architecture with Native Inference",
                "finding": f"Uses external APIs ({', '.join(wrapper_found)}) combined with verified native systems libraries ({', '.join(deeptech_found)}).",
                "vc_impact": "Protects unit economics via local SLM routing while maintaining fast product velocity."
            })
        elif len(deeptech_found) >= 2:
            score = max(score, 82)
            findings.append({
                "severity": "TOP-TIER MOAT",
                "title": "Proprietary Systems & Infrastructure Depth",
                "finding": f"Strong verified systems-level AST imports ({', '.join(deeptech_found)}). Zero reliance on superficial wrapper frameworks.",
                "vc_impact": "Substantial technical barrier to entry. Independent from hyperscaler pricing changes."
            })

        if score >= 75:
            extinction_risk = "LOW // PROPRIETARY COMPUTE"
            tier = "Tier-1 Deep Tech Systems Moat"
            ic_rec = "TECHNICAL APPROVAL: Codebase demonstrates genuine systems depth and defensible inference infrastructure."
        elif score >= 50:
            extinction_risk = "MODERATE // HYBRID WORKFLOW"
            tier = "Tier-2 Workflow & Integration Architecture"
            ic_rec = "CONDITIONAL APPROVAL: Verify enterprise workflow switching costs and proprietary dataset defensibility."
        else:
            extinction_risk = "HIGH // COMMODITIZATION IMMINENT"
            tier = "Tier-3 Vulnerable API Wrapper"
            ic_rec = "PASS / REJECT: High risk of obsolescence on next major foundation model API update."

        score = max(10, min(95, score))

        return CodeAuditReport(
            company_name=self.company_name,
            target_source="Manifest & AST Codebase Audit",
            defensibility_score=score,
            tier_classification=tier,
            extinction_risk=extinction_risk,
            wrapper_index_pct=round(wrapper_index * 100, 1),
            systems_moat_pct=round(systems_moat * 100, 1),
            gross_margin_ceiling_pct=margin_ceiling,
            wrapper_libraries_found=list(wrapper_found),
            deeptech_libraries_found=list(deeptech_found),
            infrastructure_libraries_found=list(infra_found),
            unused_declared_libraries=list(unused_packages),
            audit_findings=findings,
            ic_recommendation=ic_rec
        )


COGNIFLOW_REQUIREMENTS = """
torch==2.4.0
vllm==0.5.4
transformers==4.42.0
bcc==0.29.0
triton==3.0.0
fastapi==0.111.0
grpcio==1.64.0
"""

COGNIFLOW_CODE_SAMPLE = '''
import torch
import vllm
import triton
from bcc import BPF

def run_inference_pipeline(prompt: str):
    llm = vllm.LLM(model="meta-llama/Meta-Llama-3-8B")
    return llm.generate(prompt)
'''

HYPERBUZZ_REQUIREMENTS = """
openai==1.35.0
langchain==0.2.6
langchain-core==0.2.10
crewai==0.36.0
flask==3.0.3
"""

HYPERBUZZ_CODE_SAMPLE = '''
import openai
from langchain.chains import LLMChain

def generate_social_buzz(prompt: str):
    client = openai.OpenAI()
    return client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": prompt}])
'''
