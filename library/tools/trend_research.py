#!/usr/bin/env python3
"""
Trend Research & Content Intelligence CLI for @meowndr.

Commands:
    python3 library/tools/trend_research.py run [--date YYYY-MM-DD] [--niche <niche>] [--daily | --weekly | --on-demand]
    python3 library/tools/trend_research.py validate <trend_data_json_path>
    python3 library/tools/trend_research.py report <trend_data_json_path>
"""

import os
import sys
import json
import argparse
import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from library.content_factory.trend_intelligence import (
    run_trend_research_pipeline,
    TrendValidator,
    ArtifactExporter,
    OpportunityScorer
)


def main():
    parser = argparse.ArgumentParser(description="Trend Research & Content Intelligence CLI (@meowndr)")
    subparsers = parser.add_subparsers(dest="command", help="Subcommand to execute")

    # Run command
    run_p = subparsers.add_parser("run", help="Execute trend discovery and generate intelligence artifacts")
    run_p.add_argument("--date", type=str, default=None, help="Target research date (YYYY-MM-DD), defaults to today")
    run_p.add_argument("--niche", type=str, default=None, help="Filter discovery to specific niche (e.g. science, history, psychology)")
    run_p.add_argument("--daily", action="store_true", help="Run in daily trend monitoring mode")
    run_p.add_argument("--weekly", action="store_true", help="Run in weekly trend summary mode")
    run_p.add_argument("--on-demand", action="store_true", help="Run on-demand before starting a new episode (default)")

    # Validate command
    val_p = subparsers.add_parser("validate", help="Validate a trend-data.json artifact against schema and quality rules")
    val_p.add_argument("path", type=str, help="Path to trend-data.json file")

    # Report command
    rep_p = subparsers.add_parser("report", help="Display summary metrics from an existing trend-data.json file")
    rep_p.add_argument("path", type=str, help="Path to trend-data.json file")

    args = parser.parse_args()

    if not args.command or args.command == "run":
        target_date = getattr(args, "date", None)
        target_niche = getattr(args, "niche", None)
        mode = "on-demand"
        if getattr(args, "daily", False):
            mode = "daily"
        elif getattr(args, "weekly", False):
            mode = "weekly"

        print("=" * 70)
        print(f"  @meowndr Trend Research & Content Intelligence ({mode.upper()})")
        print("=" * 70)
        print(f"Target Date: {target_date or datetime.date.today().isoformat()}")
        if target_niche:
            print(f"Target Niche: {target_niche}")

        try:
            result = run_trend_research_pipeline(date_str=target_date, niche=target_niche)
            print("\n[SUCCESS] Trend discovery completed & verified.")
            print("Generated Deliverables:")
            for k, fpath in result["files"].items():
                print(f"  - {k}: {fpath}")

            print("\nPlatforms Monitored:")
            for p in result["payload"]["platforms_monitored"]:
                print(f"  * {p['platform']}: {p['status']} ({p['access_mode']})")

            print("\nTop Content Opportunities (Score >= 70):")
            for opp in result["payload"]["evaluated_opportunities"]:
                sc = opp["scoring"]
                print(f"  * [{sc['total_score']}/100] {opp['proposed_title']} ({opp['niche']}) -> {opp['status']}")

            print("\nDisqualified / Rejected Topics:")
            for rej in result["payload"]["rejected_topics"]:
                print(f"  * [REJECTED] {rej['topic']} -> {rej['disqualification_category']}")

            return 0
        except Exception as e:
            print(f"\n[ERROR] Pipeline execution failed: {e}")
            import traceback
            traceback.print_exc()
            return 1

    elif args.command == "validate":
        target_path = Path(args.path)
        if not target_path.exists():
            print(f"[FAIL] File not found: {target_path}")
            return 2

        with open(target_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        valid, errors = TrendValidator.validate(data)
        if valid:
            print(f"[PASS] {target_path} is valid.")
            print(f"  - Total raw trends: {len(data.get('raw_trends', []))}")
            print(f"  - Evaluated opportunities: {len(data.get('evaluated_opportunities', []))}")
            print(f"  - Rejected topics: {len(data.get('rejected_topics', []))}")
            print(f"  - Platforms monitored: {len(data.get('platforms_monitored', []))}")
            return 0
        else:
            print(f"[FAIL] {target_path} failed validation:")
            for err in errors:
                print(f"  - {err}")
            return 1

    elif args.command == "report":
        target_path = Path(args.path)
        if not target_path.exists():
            print(f"[FAIL] File not found: {target_path}")
            return 2
        with open(target_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        print("=" * 70)
        print(f"  Trend Intelligence Summary: {data.get('research_date')}")
        print("=" * 70)
        for opp in data.get("evaluated_opportunities", []):
            sc = opp["scoring"]
            vc = opp["video_concept"]
            print(f"\n[{sc['total_score']}/100] {opp['proposed_title']}")
            print(f"  Question: {vc['main_question']}")
            print(f"  Hook: \"{vc['opening_hook']}\"")
            print(f"  Platform: {vc['recommended_platform']} | Duration: {vc['estimated_duration_seconds']}s")
        return 0


if __name__ == "__main__":
    sys.exit(main())
