"""
Case Study Execution Script for DeckDiligence.ai.

Executes PitchDeckScreener against verified, slide-extracted JSONs of real-world pitch decks:
  1. Airbnb Seed Pitch Deck (2008)
  2. Front Series A Pitch Deck (2016)
  3. Brex Series B Pitch Deck (2018)

Outputs markdown screening memos and terminal scorecards into `case_studies/outputs/`
and writes a consolidated results JSON to prove transparent execution without hindsight.
"""

import json
import os
import sys

# Ensure parent directory is in path to import deck_screener
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from deck_screener import PitchDeckScreener


def run_all_cases():
    cases_dir = os.path.dirname(os.path.abspath(__file__))
    outputs_dir = os.path.join(cases_dir, "outputs")
    os.makedirs(outputs_dir, exist_ok=True)

    case_files = [
        ("Airbnb Seed (2008)", "airbnb_seed_2008.json"),
        ("Front Series A (2016)", "front_series_a_2016.json"),
        ("Brex Series B (2018)", "brex_series_b_2018.json"),
    ]

    results_summary = []

    print("=" * 85)
    print(" DECKDILIGENCE.AI — REAL-WORLD CASE STUDY VERIFICATION RUN")
    print("=" * 85)
    print(f"{'Company':<25} | {'Audits':<8} | {'Score':<6} | {'Verdict':<35}")
    print("-" * 85)

    for display_name, filename in case_files:
        filepath = os.path.join(cases_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            deck_data = json.load(f)

        screener = PitchDeckScreener(deck_data)
        screener.compute_derived_metrics()
        screener.run_sanity_audits()
        verdict, rationale = screener.get_verdict()

        # Generate outputs
        base_name = filename.replace(".json", "")
        memo_path = os.path.join(outputs_dir, f"IC_Memo_{base_name}.md")
        scorecard_path = os.path.join(outputs_dir, f"Scorecard_{base_name}.txt")

        screener.generate_markdown_memo(memo_path)
        with open(scorecard_path, "w", encoding="utf-8") as sf:
            sf.write(screener.generate_scorecard())

        print(f"{display_name:<25} | {screener.audits_run_count}/6      | {screener.health_score:<6} | {verdict:<35}")

        results_summary.append({
            "company": display_name,
            "filename": filename,
            "sector": deck_data.get("sector"),
            "stage": deck_data.get("stage"),
            "audits_run_count": screener.audits_run_count,
            "audits_run_names": screener.audits_run_names,
            "audits_skipped_names": screener.audits_skipped_names,
            "health_score": screener.health_score,
            "verdict": verdict,
            "rationale": rationale,
            "missing_metrics": screener.missing_metrics
        })

    print("=" * 85)

    # Save consolidated results JSON
    summary_path = os.path.join(outputs_dir, "case_study_results.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(results_summary, f, indent=2)

    print(f"\n[OK] Memos, scorecards, and case_study_results.json saved to: {outputs_dir}\n")


if __name__ == "__main__":
    run_all_cases()
