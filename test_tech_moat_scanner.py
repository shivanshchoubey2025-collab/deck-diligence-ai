"""
Unit tests for Dependency & AST Architecture Auditor
Validates:
  1. AST parser extracts imports and ignores comments containing library names
  2. Declared vs Used Reconciliation: torch declared in requirements without code import is NOT credited
  3. Canonical Package-to-Import Name Mapping: scikit-learn -> sklearn, flash-attn -> flash_attn
  4. General utilities (numpy, redis, docker) are excluded from deeptech moat
  5. Unparseable syntax code is rejected rather than fallen back to regex
"""

import pytest
from tech_moat_scanner import TechMoatScanner


def test_ast_ignores_comments():
    scanner = TechMoatScanner()
    code_with_comments_only = '''
    # We should consider using bcc or torch in the future
    """This system does not yet use triton or vllm."""
    import requests
    import json
    '''
    imports, err = scanner.parse_python_ast(code_with_comments_only)
    assert err is None
    assert "bcc" not in imports
    assert "torch" not in imports
    assert "triton" not in imports
    assert "requests" in imports
    assert "json" in imports


def test_declared_vs_used_reconciliation():
    """Declaring torch/vllm in requirements while only importing openai in code must NOT score high!"""
    scanner = TechMoatScanner("Cheater AI")
    reqs = "torch==2.4.0\nvllm==0.5.0\nopenai==1.30.0"
    code = '''
    import openai
    def run():
        return openai.chat.completions.create(model="gpt-4o", messages=[])
    '''
    report = scanner.audit_manifests(requirements_txt=reqs, code_snippets=code)
    
    # torch and vllm should be flagged as unused
    assert "torch" in report.unused_declared_libraries
    assert "vllm" in report.unused_declared_libraries
    # Only openai should be active
    assert "openai" in report.wrapper_libraries_found
    assert len(report.deeptech_libraries_found) == 0
    assert report.defensibility_score <= 40


def test_canonical_import_name_mapping():
    """Verifies that pip names (scikit-learn, flash-attn) map to import names (sklearn, flash_attn)."""
    scanner = TechMoatScanner("ML Co")
    reqs = "scikit-learn==1.5.0\nflash-attn==2.6.0\nlangchain-core==0.2.0"
    code = '''
    import sklearn
    import flash_attn
    import langchain_core
    '''
    report = scanner.audit_manifests(requirements_txt=reqs, code_snippets=code)
    assert "scikit-learn" in report.deeptech_libraries_found
    assert "flash-attn" in report.deeptech_libraries_found
    assert "langchain-core" in report.wrapper_libraries_found


def test_general_utilities_excluded_from_moat():
    """numpy, redis, and docker are standard utilities and must NOT score as deeptech moats."""
    scanner = TechMoatScanner("Utility Co")
    reqs = "numpy==1.26.0\nredis==5.0.0\ndocker==7.0.0"
    report = scanner.audit_manifests(requirements_txt=reqs)
    
    assert len(report.deeptech_libraries_found) == 0
    assert report.defensibility_score <= 40


def test_unparseable_code_rejected_cleanly():
    """Code with syntax errors is rejected with an explicit error instead of falling back to regex."""
    scanner = TechMoatScanner("Broken Co")
    broken_code = '''
    def broken_func(
        # unclosed parenthesis
        import torch
    '''
    report = scanner.audit_manifests(code_snippets=broken_code)
    syntax_findings = [f for f in report.audit_findings if f["severity"] == "SYNTAX ERROR"]
    assert len(syntax_findings) > 0
    # Must not credit torch
    assert len(report.deeptech_libraries_found) == 0
