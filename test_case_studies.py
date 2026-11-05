"""
Unit tests for the refusal-rate pitch deck case studies.
Verifies that:
  1. The 3 real-world case study JSONs (Airbnb 2009, Buffer 2011, Front 2016) load without error.
  2. Each case study executes cleanly through PitchDeckScreener.
  3. Each case study triggers the audit coverage refusal rule (audits_run_count < 3).
  4. Provenance Enforcement: Every non-null metric MUST have an explicit slide citation in verbatim_citations.
"""

import json
import os
import pytest
from deck_screener import PitchDeckScreener


CASES = [
    "airbnb_seed_2009.json",
    "buffer_seed_2011.json",
    "front_series_a_2016.json"
]

METRIC_TO_CITATION_KEY = {
    "arr_usd": "arr",
    "net_new_arr_last_12m_usd": "net_new_arr",
    "monthly_net_burn_usd": "burn",
    "cash_in_bank_usd": "cash",
    "claimed_gross_margin_pct": "gross_margin",
    "claimed_monthly_churn_pct": "churn",
    "claimed_cac_usd": "cac",
    "claimed_arpu_monthly_usd": "arpu",
    "claimed_tam_usd": "tam"
}


@pytest.mark.parametrize("filename", CASES)
def test_case_study_execution_and_refusal(filename):
    case_path = os.path.join(os.path.dirname(__file__), "case_studies", filename)
    assert os.path.exists(case_path), f"Missing case study JSON: {case_path}"

    with open(case_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Verify provenance metadata
    assert "deck_url" in data, f"Missing deck_url in {filename}"
    assert "verbatim_citations" in data, f"Missing verbatim_citations in {filename}"
    assert data["deck_url"].startswith("https://"), f"Invalid deck_url in {filename}"

    screener = PitchDeckScreener(data)
    screener.compute_derived_metrics()
    screener.run_sanity_audits()
    verdict, rationale = screener.get_verdict()

    assert screener.audits_run_count < 3
    assert verdict == "INSUFFICIENT DATA / REFUSE VERDICT"
    assert "Fewer than 3 of 6 sanity audits could be evaluated" in rationale


@pytest.mark.parametrize("filename", CASES)
def test_provenance_enforcement_non_null_metrics_must_cite_slides(filename):
    """
    Provenance Enforcement Test:
    Every quantitative figure passed to the screener must cite its exact source slide
    in verbatim_citations. Fails if a number is present without verified provenance.
    """
    case_path = os.path.join(os.path.dirname(__file__), "case_studies", filename)
    with open(case_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    citations = data.get("verbatim_citations", {})
    metrics = data.get("claimed_metrics", {})

    for metric_name, value in metrics.items():
        if value is not None and metric_name in METRIC_TO_CITATION_KEY:
            citation_key = METRIC_TO_CITATION_KEY[metric_name]
            assert citation_key in citations, (
                f"{filename}: '{metric_name}' is non-null ({value}) but lacks a citation key '{citation_key}' in verbatim_citations."
            )
            citation_text = citations[citation_key]
            assert isinstance(citation_text, str) and len(citation_text) > 5, (
                f"{filename}: Citation for '{citation_key}' is empty or invalid."
            )
            assert "Slide" in citation_text or "Deck" in citation_text, (
                f"{filename}: Citation for '{citation_key}' does not reference a Slide or Deck ('{citation_text}')."
            )

    # Check funding ask provenance
    if data.get("funding_ask_usd") is not None:
        assert "funding_ask" in citations, f"{filename}: funding_ask_usd is present but missing 'funding_ask' citation."
        assert "Slide" in citations["funding_ask"] or "Deck" in citations["funding_ask"]

    # Check valuation provenance
    if data.get("claimed_post_money_valuation_usd") is not None:
        assert "valuation" in citations, f"{filename}: claimed_post_money_valuation_usd is present but missing 'valuation' citation."


BANNED_EXTERNAL_SOURCES = [
    "retrospective",
    "interview",
    "podcast",
    "blog",
    "article",
    "wikipedia",
    "techcrunch",
    "outside knowledge",
    "founder stated",
    "subsequent round"
]


@pytest.mark.parametrize("filename", CASES)
def test_provenance_citations_ban_external_commentary(filename):
    """
    Provenance Hygiene Test:
    Citations must derive exclusively from the slide deck itself.
    Citations referencing external post-hoc commentary (retrospectives, interviews, podcasts, articles)
    are strictly rejected.
    """
    case_path = os.path.join(os.path.dirname(__file__), "case_studies", filename)
    with open(case_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    citations = data.get("verbatim_citations", {})
    assert len(citations) > 0, f"{filename}: verbatim_citations is empty"

    for key, citation_text in citations.items():
        assert isinstance(citation_text, str), f"{filename}: Citation '{key}' is not a string"
        
        # Every citation must reference a Slide, Deck, or explicit absence on slides
        has_slide_or_deck_anchor = (
            "Slide" in citation_text or 
            "Deck" in citation_text or 
            "Not stated on any slide" in citation_text
        )
        assert has_slide_or_deck_anchor, (
            f"{filename}: Citation '{key}' lacks a Slide/Deck anchor: '{citation_text}'"
        )

        # Ban external retrospective sources
        lower_text = citation_text.lower()
        for banned in BANNED_EXTERNAL_SOURCES:
            assert banned not in lower_text, (
                f"{filename}: Citation '{key}' contains banned external source '{banned}': '{citation_text}'"
            )
