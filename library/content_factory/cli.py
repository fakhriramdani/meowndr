#!/usr/bin/env python3
"""
CLI interface for Papercraft Content Factory.

Commands:
  init      Initialize or load an episode workflow state
  status    Print current workflow stage, status, gates, and artifacts
  approve   Record user approval at Gate 1, 2, or 3
  reject    Record user rejection at Gate 1, 2, or 3
  validate  Validate all produced artifacts in an episode against schemas
  niches    List supported content niches and their configurations
"""

import sys
import os
import argparse
import json

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(HERE))
TOOLS_DIR = os.path.join(os.path.dirname(HERE), "tools")
sys.path.insert(0, HERE)
sys.path.insert(0, TOOLS_DIR)

from workflow_engine import WorkflowEngine, STAGE_NAMES
from niche_manager import NICHES, list_supported_niches
from schema_validator import validate_artifact_file
from narration_standard import NarrationValidator, IndonesianNumberConverter


def cmd_init(args):
    engine = WorkflowEngine(args.slug, niche=args.niche, title=args.title or "", on_demand_trends=args.trends)
    st = engine.get_status()
    print("=" * 65)
    print(f">> Initialized Papercraft Content Factory Episode: {st['episode_id']}")
    print("=" * 65)
    print(f"• Niche:         {st['niche']}")
    print(f"• Current Stage: {st['current_stage']} ({st['stage_name']})")
    print(f"• Status:        {st['status']}")
    print(f"• Location:      episodes/{args.slug}/content_factory/workflow_state.json")
    print("=" * 65)


def cmd_status(args):
    engine = WorkflowEngine(args.slug)
    st = engine.get_status()
    print("=" * 65)
    print(f"  Content Factory Status: {st['episode_id']}")
    print("=" * 65)
    print(f"• Niche:             {st['niche']}")
    print(f"• Current Stage:     Stage {st['current_stage']}: {st['stage_name']}")
    print(f"• Pipeline Status:   {st['status']}")
    print(f"• Completed Stages:  {st['completed_stages']}")
    print("\n[Approval Gates]")
    for gname, ginfo in st['approval_gates'].items():
        icon = "[v]" if ginfo["status"] == "APPROVED" else ("[x]" if ginfo["status"] == "REJECTED" else "[?]")
        print(f"  {icon} {gname}: {ginfo['status']} (Notes: {ginfo.get('notes') or 'None'})")

    if st['artifacts']:
        print("\n[Artifacts]")
        for k, v in st['artifacts'].items():
            print(f"  • {k}: {v}")
    print("=" * 65)


def cmd_approve(args):
    engine = WorkflowEngine(args.slug)
    gate_num = int(args.gate)
    notes = args.notes or "Approved via CLI"
    user = args.user or "User"

    if gate_num == 1:
        hook_id = args.hook or "v1"
        res = engine.run_stage_4_gate_1_approval(approved_by=user, selected_hook_id=hook_id, notes=notes)
    elif gate_num == 2:
        res = engine.run_stage_6_gate_2_approval(approved_by=user, notes=notes)
    elif gate_num == 3:
        res = engine.run_stage_12_gate_3_approval(approved_by=user, notes=notes)
    else:
        print(f"[ERROR] Invalid gate number: {gate_num}. Choose 1, 2, or 3.")
        sys.exit(1)

    print(f">> Gate {gate_num} APPROVED successfully!")
    print(f"• Next Stage: {engine.state['current_stage']} ({STAGE_NAMES.get(engine.state['current_stage'])})")
    print(f"• Status:     {engine.state['status']}")
    if gate_num == 3 and res.get("gdrive_destination"):
        print(f"• Google Drive: {res['gdrive_destination']}")


def cmd_reject(args):
    engine = WorkflowEngine(args.slug)
    gate_num = int(args.gate)
    notes = args.notes or "Rejected via CLI for revision"
    gate_map = {1: "gate_1_topic_hook", 2: "gate_2_script", 3: "gate_3_final_video"}

    if gate_num not in gate_map:
        print(f"[ERROR] Invalid gate number: {gate_num}. Choose 1, 2, or 3.")
        sys.exit(1)

    gname = gate_map[gate_num]
    engine.state["approval_gates"][gname]["status"] = "REJECTED"
    engine.state["approval_gates"][gname]["notes"] = notes
    engine.state["status"] = "HALTED"
    engine._save_state()

    print(f">> Gate {gate_num} marked REJECTED. Pipeline HALTED.")
    print(f"• Notes: {notes}")


def cmd_niches(args):
    print("=" * 65)
    print("  Supported Multi-Niche Profiles")
    print("=" * 65)
    for nid, prof in NICHES.items():
        print(f"• {nid.upper()} ({prof['name']})")
        print(f"  - Default Env:     {prof['default_environment']}")
        print(f"  - Presenter Title: {prof['presenter']['role_title']}")
        print(f"  - Description:     {prof['description']}")
    print("=" * 65)


def cmd_trends(args):
    from trend_intelligence import run_trend_research_pipeline
    print("=" * 65)
    print(">> Running Trend Research & Content Intelligence for @meowndr...")
    print("=" * 65)
    res = run_trend_research_pipeline(date_str=args.date, niche=args.niche)
    print(f"\n[OK] Trend discovery and scoring complete for date: {res['date']}")
    print("Generated Artifacts:")
    for k, v in res["files"].items():
        print(f"  • {k}: {v}")


def cmd_validate(args):
    engine = WorkflowEngine(args.slug)
    artifacts = engine.state.get("artifacts", {})
    print("=" * 65)
    print(f"  Validating Artifacts for: {args.slug}")
    print("=" * 65)
    if not artifacts:
        print("No artifacts recorded in workflow state.")
        return

    failed = 0
    type_map = {
        "dossier": "dossier",
        "hook_matrix": "hook_matrix",
        "script": "script",
        "storyboard": "storyboard",
        "asset_plan": "asset_plan",
        "audio_plan": "audio_plan",
        "qa_report": "qa_report"
    }

    for key, rel_path in artifacts.items():
        art_type = type_map.get(key)
        if not art_type:
            continue
        full_path = os.path.join(REPO_ROOT, rel_path)
        valid, errs = validate_artifact_file(art_type, full_path)
        if valid:
            print(f"  [PASS] {key} -> {rel_path}")
        else:
            print(f"  [FAIL] {key} -> {rel_path}")
            for e in errs:
                print(f"    - {e}")
            failed += 1

    print("-" * 65)
    if failed == 0:
        print(">> All recorded artifacts valid according to schema!")
    else:
        print(f">> {failed} artifact(s) failed schema validation.")
        sys.exit(1)


def cmd_narration(args):
    script_path = os.path.join(REPO_ROOT, "episodes", args.slug, "narration", "script.json")
    if not os.path.exists(script_path):
        print(f"[ERROR] Script not found at {script_path}")
        sys.exit(1)

    with open(script_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if args.normalize:
        updated, summary = NarrationValidator.normalize_script(data, populate_tts_field=True)
        with open(script_path, "w", encoding="utf-8") as f:
            json.dump(updated, f, indent=2, ensure_ascii=False)
        print(f">> Successfully normalized narration script for '{args.slug}'!")
        print(f"• Transformed lines: {summary['transformed_lines']}")
        for t in summary["audit_details"]:
            print(f"  [{t['id']}]:")
            for item in t["transformations"]:
                print(f"    - {item['type']}: '{item['original']}' -> '{item['converted']}'")
        data = updated

    rep = NarrationValidator.validate_script(data)
    print("=" * 65)
    print(f"  Indonesian Narration Standard Audit: {args.slug}")
    print("=" * 65)
    print(f"• Total Lines: {rep['total_lines']}")
    print(f"• Total Words: {rep['total_words']} (Target: 130–155)")
    print(f"• Est Duration: {rep['estimated_duration_sec']:.1f}s (Target: 45–58s)")
    print(f"• Compliance:  {'[PASS]' if rep['is_valid'] else '[FAIL - BLOCKING ERRORS]'}")

    if rep["errors"]:
        print("\n[Blocking Errors]")
        for e in rep["errors"]:
            print(f"  • {e}")

    if rep["warnings"]:
        print("\n[Pacing & Rhythm Warnings]")
        for w in rep["warnings"]:
            print(f"  • {w}")

    print("=" * 65)
    if args.strict and not rep["is_valid"]:
        sys.exit(1)
    sys.exit(0 if rep["is_valid"] else 1)


def main():
    parser = argparse.ArgumentParser(description="Papercraft Content Factory CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    # init
    p_init = sub.add_parser("init", help="Initialize an episode workflow")
    p_init.add_argument("slug", help="Episode slug")
    p_init.add_argument("--niche", default="science", choices=list_supported_niches(), help="Target niche")
    p_init.add_argument("--title", help="Working title")
    p_init.add_argument("--trends", action="store_true", help="Trigger on-demand trend research (Stage 1)")

    # status
    p_status = sub.add_parser("status", help="View episode workflow state")
    p_status.add_argument("slug", help="Episode slug")

    # approve
    p_app = sub.add_parser("approve", help="Approve an approval gate")
    p_app.add_argument("slug", help="Episode slug")
    p_app.add_argument("--gate", type=int, required=True, choices=[1, 2, 3], help="Gate number (1, 2, or 3)")
    p_app.add_argument("--notes", help="Approval notes")
    p_app.add_argument("--user", default="User", help="Approver name")
    p_app.add_argument("--hook", default="v1", help="Selected hook id (for Gate 1)")

    # reject
    p_rej = sub.add_parser("reject", help="Reject an approval gate")
    p_rej.add_argument("slug", help="Episode slug")
    p_rej.add_argument("--gate", type=int, required=True, choices=[1, 2, 3], help="Gate number (1, 2, or 3)")
    p_rej.add_argument("--notes", help="Rejection reason")

    # niches
    sub.add_parser("niches", help="List supported niches")

    # trends
    p_trends = sub.add_parser("trends", help="Run trend research and content intelligence")
    p_trends.add_argument("--date", help="Target research date (YYYY-MM-DD)")
    p_trends.add_argument("--niche", choices=list_supported_niches(), help="Filter by niche")

    # validate
    p_val = sub.add_parser("validate", help="Validate recorded artifacts against schemas")
    p_val.add_argument("slug", help="Episode slug")

    # narration
    p_nar = sub.add_parser("narration", help="Audit or normalize narration script for Indonesian speech")
    p_nar.add_argument("slug", help="Episode slug")
    p_nar.add_argument("--normalize", action="store_true", help="Populate 'tts' with normalized speech words")
    p_nar.add_argument("--strict", action="store_true", help="Exit with error if validation fails")

    # backgrounds
    p_bg = sub.add_parser("backgrounds", help="Manage centralized background registry")
    p_bg.add_argument("bg_cmd", choices=["list", "info", "validate", "discover", "add", "disable", "archive", "enable", "remove", "sync"], help="Background command")
    p_bg.add_argument("bg_args", nargs=argparse.REMAINDER, help="Arguments passed to background command")

    # studio
    p_studio = sub.add_parser("studio", help="Launch @meowndr Asset Studio visual management UI")
    p_studio.add_argument("--port", type=int, default=4000, help="Server port (default: 4000)")
    p_studio.add_argument("--host", default="127.0.0.1", help="Server host (default: 127.0.0.1)")
    p_studio.add_argument("--open", dest="open_browser", action="store_true", help="Open browser on start")

    args = parser.parse_args()
    if args.cmd == "studio":
        from asset_studio_server import run_asset_studio_server
        if args.open_browser:
            import webbrowser
            try:
                webbrowser.open(f"http://{args.host}:{args.port}/")
            except Exception:
                pass
        run_asset_studio_server(host=args.host, port=args.port, repo_root=REPO_ROOT)
        return
    if args.cmd == "backgrounds":
        from manage_backgrounds import main as bg_main
        # Re-construct sys.argv for manage_backgrounds
        sys.argv = [sys.argv[0] + " backgrounds", args.bg_cmd] + (args.bg_args or [])
        bg_main()
        return
    if args.cmd == "init":
        cmd_init(args)
    elif args.cmd == "status":
        cmd_status(args)
    elif args.cmd == "approve":
        cmd_approve(args)
    elif args.cmd == "reject":
        cmd_reject(args)
    elif args.cmd == "niches":
        cmd_niches(args)
    elif args.cmd == "trends":
        cmd_trends(args)
    elif args.cmd == "validate":
        cmd_validate(args)
    elif args.cmd == "narration":
        cmd_narration(args)


if __name__ == "__main__":
    main()
