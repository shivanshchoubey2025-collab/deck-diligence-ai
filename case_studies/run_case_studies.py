"""
Empirical Refusal-Rate Case Study Script for DeckDiligence.ai.

Executes PitchDeckScreener against verified, slide-extracted JSONs of real-world pitch decks:
  1. Airbnb Seed Pitch Deck (2009, 14 slides)
  2. Buffer Seed Pitch Deck (2011, 13 slides)
  3. Front Series A Pitch Deck (2016, 21 slides)

All figures in the source JSONs were extracted and checked by hand against public slides
on 2026-11-05 with verbatim slide citations and URLs.

Outputs markdown screening memos and terminal scorecards into `case_studies/outputs/`
and writes a consolidated results JSON documenting the refusal rate across real decks.
"""

import json
import os
import sys

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from deck_screener import PitchDeckScreener


def run_all_cases():
    cases_dir = os.path.dirname(os.path.abspath(__file__))
    outputs_dir = os.path.join(cases_dir, "outputs")
    os.makedirs(outputs_dir, exist_ok=True)

    case_files = [
        ("Airbnb Seed (2009)", "airbnb_seed_2009.json"),
        ("Buffer Seed (2011)", "buffer_seed_2011.json"),
        ("Front Series A (2016)", "front_series_a_2016.json"),
    ]

    results_summary = []

    print("=" * 85)
    print(" DECKDILIGENCE.AI — REFUSAL-RATE STUDY ON 3 PUBLIC PITCH DECKS")
    print(" Extractions checked by hand against source slides on 2026-11-05")
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

        score_disp = f"{screener.effective_health_score}" if screener.effective_health_score is not None else "N/A"
        print(f"{display_name:<25} | {screener.audits_run_count}/6      | {score_disp:<6} | {verdict:<35}")

        results_summary.append({
            "company": display_name,
            "filename": filename,
            "deck_url": deck_data.get("deck_url"),
            "slide_count": deck_data.get("slide_count"),
            "sector": deck_data.get("sector"),
            "stage": deck_data.get("stage"),
            "audits_run_count": screener.audits_run_count,
            "audits_run_names": screener.audits_run_names,
            "audits_skipped_names": screener.audits_skipped_names,
            "health_score": screener.effective_health_score,
            "raw_score_before_refusal": screener.health_score,
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
