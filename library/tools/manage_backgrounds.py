#!/usr/bin/env python3
"""
CLI interface for Background Registry Management in @meowndr 2D Papercraft Explainer.

Commands:
  list        List all registered backgrounds with filtering and status
  info        Show full details and episode references for a background
  validate    Validate background registry and cross-check episode references
  discover    Scan disk for unregistered assets, missing files, and duplicate IDs
  add         Register a new background environment
  disable     Disable a background so it cannot be selected for new episodes
  archive     Archive a background
  enable      Re-enable a disabled or archived background
  remove      Remove a background (checks active episode references first)
  sync        Synchronize active backgrounds to library.json, index.json, and AssetLoader.ts
"""

import sys
import os
import argparse
import json

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from background_registry import BackgroundRegistry, get_registry


def format_table(rows: list, headers: list) -> str:
    """Formats rows as an ASCII table with column padding."""
    if not rows:
        return "No entries found."
    widths = [len(h) for h in headers]
    for row in rows:
        for idx, col in enumerate(row):
            widths[idx] = max(widths[idx], len(str(col)))

    sep = "+-" + "-+-".join("-" * w for w in widths) + "-+"
    header_line = "| " + " | ".join(h.ljust(widths[i]) for i, h in enumerate(headers)) + " |"

    lines = [sep, header_line, sep]
    for row in rows:
        r_line = "| " + " | ".join(str(c).ljust(widths[i]) for i, c in enumerate(row)) + " |"
        lines.append(r_line)
    lines.append(sep)
    return "\n".join(lines)


def cmd_list(args):
    reg = BackgroundRegistry()
    bgs = reg.list_backgrounds(
        category=args.category,
        status=args.status,
        query=args.query,
        tag=args.tag,
        check_exists=True,
    )

    if args.json:
        print(json.dumps(bgs, indent=2))
        return

    print("=" * 80)
    print(f">> Background Registry ({len(bgs)} of {len(reg.data.get('backgrounds', []))} matching)")
    print("=" * 80)

    rows = []
    headers = ["ID", "Name", "Category", "Status", "Exists", "Asset Path"]
    for b in bgs:
        st = b.get("status", "active")
        status_disp = f"[{st.upper()}]"
        exists_disp = "YES" if b.get("exists_on_disk") else "MISSING!"
        rows.append([
            b.get("id"),
            b.get("name")[:24],
            b.get("category", "")[:18],
            status_disp,
            exists_disp,
            b.get("assetPath", "")[:35],
        ])

    print(format_table(rows, headers))


def cmd_info(args):
    reg = BackgroundRegistry()
    bg = reg.get_background(args.id)
    if not bg:
        print(f"[ERROR] Background '{args.id}' not found in registry.", file=sys.stderr)
        sys.exit(1)

    refs = reg.find_active_references(args.id).get(args.id, [])

    if args.json:
        bg["references"] = refs
        print(json.dumps(bg, indent=2))
        return

    print("=" * 70)
    print(f">> Background Details: {bg.get('id')}")
    print("=" * 70)
    print(f"• Name:          {bg.get('name')}")
    print(f"• Category:      {bg.get('category')}")
    print(f"• Status:        {bg.get('status', 'active').upper()}")
    if bg.get("statusReason"):
        print(f"• Status Reason: {bg.get('statusReason')}")
    print(f"• Description:   {bg.get('description')}")
    print(f"• Asset Path:    {bg.get('assetPath')}")
    print(f"• Thumbnail:     {bg.get('thumbnailPath') or 'Not available'}")
    print(f"• Dimensions:    {bg.get('dimensions', {}).get('width')}x{bg.get('dimensions', {}).get('height')} ({bg.get('aspectRatio')})")
    print(f"• Floor Y:       {bg.get('floorY')}")
    print(f"• Mood:          {bg.get('mood')}")
    print(f"• Tags:          {', '.join(bg.get('tags', []))}")
    print(f"• Created At:    {bg.get('createdAt')}")
    print(f"• Updated At:    {bg.get('updatedAt')}")

    print("\n[Active Episode References]")
    if refs:
        for r in refs:
            print(f"  • Episode: {r['episode']} ({r['file']}) - {r['context']}")
    else:
        print("  (None - safe to disable or remove)")
    print("=" * 70)


def cmd_validate(args):
    reg = BackgroundRegistry()
    val = reg.validate_registry(check_episodes=not args.no_episodes)

    if args.json:
        print(json.dumps(val, indent=2))
        sys.exit(0 if val["is_valid"] else 1)

    print("=" * 70)
    print(">> Background Registry Validation Report")
    print("=" * 70)
    print(f"• Total Backgrounds: {val['stats']['total_backgrounds']}")
    print(f"• Active:            {val['stats']['active_count']}")
    print(f"• Disabled:          {val['stats']['disabled_count']}")
    print(f"• Archived:          {val['stats']['archived_count']}")
    print(f"• Overall Status:    {'[PASS]' if val['is_valid'] else '[FAIL]'}")

    if val["errors"]:
        print("\n[Validation Errors]")
        for e in val["errors"]:
            print(f"  [X] {e}")

    if val["warnings"]:
        print("\n[Validation Warnings]")
        for w in val["warnings"]:
            print(f"  [!] {w}")

    print("=" * 70)
    if args.strict and not val["is_valid"]:
        sys.exit(1)
    sys.exit(0 if val["is_valid"] else 1)


def cmd_discover(args):
    reg = BackgroundRegistry()
    res = reg.discover_backgrounds()

    if args.json:
        print(json.dumps(res, indent=2))
        return

    print("=" * 70)
    print(">> Background Asset Discovery Report")
    print("=" * 70)
    print(f"• Registered in registry: {res['total_registered']}")
    print(f"• Unregistered on disk:   {len(res['unregistered'])}")
    print(f"• Missing from disk:      {len(res['missing_on_disk'])}")
    print(f"• Duplicate IDs:          {len(res['duplicate_ids'])}")

    if res["unregistered"]:
        print("\n[Unregistered Assets on Disk]")
        for u in res["unregistered"]:
            comp = "[Compliant 1080x1920]" if u["isCompliant"] else f"[Non-compliant: {u['dimensions']['width']}x{u['dimensions']['height']}]"
            print(f"  • ID candidate: '{u['id']}' | File: {u['diskPath']} {comp}")

    if res["missing_on_disk"]:
        print("\n[Missing Assets from Disk]")
        for m in res["missing_on_disk"]:
            print(f"  [X] ID: '{m['id']}' expected at {m['expectedPath']} (Status: {m['status']})")

    if res["duplicate_ids"]:
        print("\n[Duplicate IDs]")
        for d in res["duplicate_ids"]:
            print(f"  [X] ID: '{d}'")

    if not res["unregistered"] and not res["missing_on_disk"] and not res["duplicate_ids"]:
        print("\n[v] Registry is 100% synchronized with disk assets.")
    print("=" * 70)


def cmd_add(args):
    reg = BackgroundRegistry()
    tags = [t.strip() for t in args.tags.split(",")] if args.tags else None
    try:
        res = reg.add_background(
            image_path=args.image_path,
            bg_id=args.id,
            name=args.name,
            category=args.category or "Education / STEM",
            description=args.desc or "",
            tags=tags,
            status=args.status or "active",
            floor_y=args.floor_y or 1380,
            mood=args.mood or "cool / studious",
            allow_overwrite=args.overwrite,
            skip_preview=args.skip_preview,
            skip_sync=args.skip_sync,
        )
        print(f">> Successfully registered background '{res['id']}'!")
        print(f"• Status:           {res['entry']['status'].upper()}")
        print(f"• Asset Path:       {res['entry']['assetPath']}")
        print(f"• Preview created:  {'YES' if res['preview_generated'] else 'NO'}")
    except Exception as e:
        print(f"[ERROR] Failed to add background: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_disable(args):
    reg = BackgroundRegistry()
    try:
        res = reg.disable_background(args.id, reason=args.reason, skip_sync=args.skip_sync)
        print(f">> Background '{args.id}' is now DISABLED.")
        if args.reason:
            print(f"• Reason: {args.reason}")
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)


def cmd_archive(args):
    reg = BackgroundRegistry()
    try:
        res = reg.archive_background(args.id, reason=args.reason, skip_sync=args.skip_sync)
        print(f">> Background '{args.id}' is now ARCHIVED.")
        if args.reason:
            print(f"• Reason: {args.reason}")
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)


def cmd_enable(args):
    reg = BackgroundRegistry()
    try:
        res = reg.enable_background(args.id, skip_sync=args.skip_sync)
        print(f">> Background '{args.id}' is now ACTIVE.")
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)


def cmd_remove(args):
    reg = BackgroundRegistry()
    try:
        res = reg.remove_background(
            args.id,
            force=args.force,
            delete_asset=args.delete_asset,
            skip_sync=args.skip_sync,
        )
        print(f">> Successfully removed background '{args.id}' from registry.")
        if res.get("deleted_asset_files"):
            print("• Underlying image files deleted from disk.")
        else:
            print("• Underlying image files retained on disk (safe mode).")
        if res.get("warn_references"):
            print("[WARN] Background was removed despite active references (force=True).")
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)


def cmd_sync(args):
    reg = BackgroundRegistry()
    reg.sync_downstream()
    print(">> Successfully synchronized Background Registry downstream:")
    print("• assets/backgrounds/index.json")
    print("• assets/library.json")
    print("• library/papercut/kit/assets/AssetLoader.ts")
    print("• Public Remotion asset directories")


def main():
    parser = argparse.ArgumentParser(description="Background Registry CLI (@meowndr Content Factory)")
    sub = parser.add_subparsers(dest="cmd", required=True)

    # list
    p_list = sub.add_parser("list", help="List registered backgrounds")
    p_list.add_argument("--category", help="Filter by category")
    p_list.add_argument("--status", choices=["active", "disabled", "archived"], help="Filter by status")
    p_list.add_argument("--query", "-q", help="Search query (ID, name, description, tags)")
    p_list.add_argument("--tag", help="Filter by tag")
    p_list.add_argument("--json", action="store_true", help="Output JSON")

    # info
    p_info = sub.add_parser("info", help="Get detailed information about a background")
    p_info.add_argument("id", help="Background ID")
    p_info.add_argument("--json", action="store_true", help="Output JSON")

    # validate
    p_val = sub.add_parser("validate", help="Validate registry consistency and episode references")
    p_val.add_argument("--strict", action="store_true", help="Exit with code 1 if invalid")
    p_val.add_argument("--no-episodes", action="store_true", help="Skip checking episode references")
    p_val.add_argument("--json", action="store_true", help="Output JSON")

    # discover
    p_disc = sub.add_parser("discover", help="Scan disk for unregistered assets, missing files, or duplicates")
    p_disc.add_argument("--json", action="store_true", help="Output JSON")

    # add
    p_add = sub.add_parser("add", help="Add a new background to the registry")
    p_add.add_argument("image_path", help="Path to 1080x1920 image file")
    p_add.add_argument("--id", required=True, help="Unique background ID (kebab-case)")
    p_add.add_argument("--name", required=True, help="Human-readable name")
    p_add.add_argument("--category", default="Education / STEM", help="Category")
    p_add.add_argument("--desc", default="", help="Description")
    p_add.add_argument("--tags", help="Comma-separated searchable tags")
    p_add.add_argument("--status", default="active", choices=["active", "disabled", "archived"], help="Initial status")
    p_add.add_argument("--floor-y", type=int, default=1380, help="Floor Y level (default 1380)")
    p_add.add_argument("--mood", default="cool / studious", help="Mood description")
    p_add.add_argument("--overwrite", action="store_true", help="Allow overwriting existing ID")
    p_add.add_argument("--skip-preview", action="store_true", help="Skip preview rendering")
    p_add.add_argument("--skip-sync", action="store_true", help="Skip downstream synchronization")

    # disable
    p_dis = sub.add_parser("disable", help="Disable a background")
    p_dis.add_argument("id", help="Background ID")
    p_dis.add_argument("--reason", help="Reason for disabling")
    p_dis.add_argument("--skip-sync", action="store_true", help="Skip downstream sync")

    # archive
    p_arc = sub.add_parser("archive", help="Archive a background")
    p_arc.add_argument("id", help="Background ID")
    p_arc.add_argument("--reason", help="Reason for archiving")
    p_arc.add_argument("--skip-sync", action="store_true", help="Skip downstream sync")

    # enable
    p_en = sub.add_parser("enable", help="Re-enable a background")
    p_en.add_argument("id", help="Background ID")
    p_en.add_argument("--skip-sync", action="store_true", help="Skip downstream sync")

    # remove
    p_rem = sub.add_parser("remove", help="Remove a background from the registry")
    p_rem.add_argument("id", help="Background ID")
    p_rem.add_argument("--force", action="store_true", help="Force removal even if referenced by episodes")
    p_rem.add_argument("--delete-asset", action="store_true", help="Delete physical image files from disk")
    p_rem.add_argument("--skip-sync", action="store_true", help="Skip downstream sync")

    # sync
    sub.add_parser("sync", help="Synchronize active backgrounds downstream")

    args = parser.parse_args()
    if args.cmd == "list":
        cmd_list(args)
    elif args.cmd == "info":
        cmd_info(args)
    elif args.cmd == "validate":
        cmd_validate(args)
    elif args.cmd == "discover":
        cmd_discover(args)
    elif args.cmd == "add":
        cmd_add(args)
    elif args.cmd == "disable":
        cmd_disable(args)
    elif args.cmd == "archive":
        cmd_archive(args)
    elif args.cmd == "enable":
        cmd_enable(args)
    elif args.cmd == "remove":
        cmd_remove(args)
    elif args.cmd == "sync":
        cmd_sync(args)


if __name__ == "__main__":
    main()
