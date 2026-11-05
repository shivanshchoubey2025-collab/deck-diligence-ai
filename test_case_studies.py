"""
Unit tests for the real-world pitch deck case studies.
Verifies that:
  1. The 3 case study JSONs (Airbnb 2008, Front 2016, Brex 2018) load without error.
  2. Each case study executes cleanly through PitchDeckScreener.
  3. Each case study triggers the audit coverage refusal rule (audits_run_count < 3).
"""

import json
import os
import pytest
from deck_screener import PitchDeckScreener


CASES = [
    "airbnb_seed_2008.json",
    "front_series_a_2016.json",
    "brex_series_b_2018.json"
]


@pytest.mark.parametrize("filename", CASES)
def test_case_study_execution_and_refusal(filename):
    case_path = os.path.join(os.path.dirname(__file__), "case_studies", filename)
    assert os.path.exists(case_path), f"Missing case study JSON: {case_path}"

    with open(case_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    screener = PitchDeckScreener(data)
    screener.compute_derived_metrics()
    screener.run_sanity_audits()
    verdict, rationale = screener.get_verdict()

    assert screener.audits_run_count < 3
    assert verdict == "INSUFFICIENT DATA / REFUSE VERDICT"
    assert "Fewer than 3 of 6 sanity audits could be evaluated" in rationale
