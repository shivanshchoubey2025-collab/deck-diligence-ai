"""
Unit tests for Dependency & AST Architecture Auditor
Validates:
  1. AST parser extracts imports and ignores comments containing library names
  2. Pure wrapper manifests trigger critical red flag and low defensibility score
  3. Native systems manifests trigger top-tier score and high margin ceiling
"""

import pytest
from tech_moat_scanner import TechMoatScanner, PythonASTImportVisitor


def test_ast_ignores_comments():
    scanner = TechMoatScanner()
    # Code with ebpf and torch only in comments/strings!
    code_with_comments_only = '''
    # We should consider using bcc or torch in the future
    """This system does not yet use triton or vllm."""
    import requests
    import json
    '''
    imports = scanner.parse_python_ast(code_with_comments_only)
    assert "bcc" not in imports
    assert "torch" not in imports
    assert "triton" not in imports
    assert "requests" in imports
    assert "json" in imports


def test_ast_genuine_imports():
    scanner = TechMoatScanner()
    code = '''
    import torch
    from vllm import LLM
    import openai
    '''
    imports = scanner.parse_python_ast(code)
    assert "torch" in imports
    assert "vllm" in imports
    assert "openai" in imports


def test_pure_wrapper_detection():
    scanner = TechMoatScanner("Wrapper Co")
    reqs = "openai==1.0.0\nlangchain==0.1.0\ncrewai==0.2.0"
    report = scanner.audit_manifests(requirements_txt=reqs)
    
    assert report.defensibility_score <= 40
    assert report.gross_margin_ceiling_pct <= 65.0
    assert len(report.wrapper_libraries_found) >= 2
    assert len(report.deeptech_libraries_found) == 0


def test_deeptech_systems_detection():
    scanner = TechMoatScanner("Systems Co")
    reqs = "torch==2.0.0\ntriton==2.1.0\nvllm==0.4.0\nfastapi==0.100.0"
    report = scanner.audit_manifests(requirements_txt=reqs)
    
    assert report.defensibility_score >= 75
    assert report.gross_margin_ceiling_pct >= 80.0
    assert len(report.deeptech_libraries_found) >= 3
    assert len(report.wrapper_libraries_found) == 0
