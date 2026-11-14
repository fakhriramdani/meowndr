#!/usr/bin/env python3
"""
Launcher CLI for @meowndr Asset Studio.

Visual Asset Management Interface for 2D Papercraft Explainer.
Usage:
  python3 library/tools/asset_studio.py [--port 4000] [--host 127.0.0.1] [--open]
"""

import os
import sys
import argparse
import webbrowser

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from asset_studio_server import run_asset_studio_server
from background_registry import find_repo_root


def main():
    parser = argparse.ArgumentParser(description="@meowndr Asset Studio — Visual Asset Management UI")
    parser.add_argument("--port", type=int, default=4000, help="Port to bind server (default: 4000)")
    parser.add_argument("--host", default="127.0.0.1", help="Host address to bind (default: 127.0.0.1)")
    parser.add_argument("--open", dest="open_browser", action="store_true", default=False, help="Automatically open browser")
    parser.add_argument("--repo-root", help="Custom repository root directory")

    args = parser.parse_args()
    root = args.repo_root or find_repo_root()

    url = f"http://{args.host}:{args.port}/"

    if args.open_browser:
        try:
            webbrowser.open(url)
        except Exception:
            pass

    run_asset_studio_server(host=args.host, port=args.port, repo_root=root)


if __name__ == "__main__":
    main()
