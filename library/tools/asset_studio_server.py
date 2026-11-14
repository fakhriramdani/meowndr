#!/usr/bin/env python3
"""
HTTP Backend Server for @meowndr Asset Studio.

Provides RESTful endpoints for:
- Asset Overview & Metrics
- Backgrounds Management (CRUD, status, previews, references)
- Characters & Variant Management
- Props Management
- Foregrounds & Brand Identity Assets
- Collections Management
- Cross-Asset Validation Center
- Downstream Synchronization
- Static Asset Serving & Security Enforcement
"""

import os
import sys
import json
import mimetypes
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Any, Dict, Optional

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from asset_studio_service import AssetStudioService

SERVICE = AssetStudioService()
UI_DIR = os.path.join(HERE, "asset_studio_ui")


class AssetStudioHandler(BaseHTTPRequestHandler):
    """Request handler for Asset Studio API and UI."""

    def log_message(self, format, *args):
        # Override to keep terminal output clean unless error occurs
        if args and str(args[1]) in ("400", "403", "404", "500"):
            super().log_message(format, *args)

    def send_json(self, data: Any, status: int = 200):
        body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def send_error_json(self, message: str, status: int = 400):
        self.send_json({"status": "error", "message": message}, status=status)

    def read_json_body(self) -> Dict[str, Any]:
        content_len = int(self.headers.get("Content-Length", 0))
        if content_len == 0:
            return {}
        body = self.rfile.read(content_len).decode("utf-8")
        return json.loads(body) if body else {}

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    # -------------------------------------------------------------------------
    # GET Routing
    # -------------------------------------------------------------------------

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        try:
            # 1. API Endpoints
            if path == "/api/overview":
                return self.send_json(SERVICE.get_overview())

            elif path == "/api/backgrounds":
                cat = query.get("category", [None])[0]
                status = query.get("status", [None])[0]
                q = query.get("query", [None])[0]
                tag = query.get("tag", [None])[0]
                return self.send_json(SERVICE.list_backgrounds(category=cat, status=status, query=q, tag=tag))

            elif path.startswith("/api/backgrounds/"):
                bg_id = path.replace("/api/backgrounds/", "").strip()
                bg = SERVICE.get_background(bg_id)
                if not bg:
                    return self.send_error_json(f"Background '{bg_id}' not found.", status=404)
                return self.send_json(bg)

            elif path == "/api/characters":
                return self.send_json(SERVICE.list_characters())

            elif path.startswith("/api/characters/"):
                c_id = path.replace("/api/characters/", "").strip()
                char = SERVICE.get_character(c_id)
                if not char:
                    return self.send_error_json(f"Character '{c_id}' not found.", status=404)
                return self.send_json(char)

            elif path == "/api/props":
                return self.send_json(SERVICE.list_props())

            elif path.startswith("/api/props/"):
                p_id = path.replace("/api/props/", "").strip()
                prop = SERVICE.get_prop(p_id)
                if not prop:
                    return self.send_error_json(f"Prop '{p_id}' not found.", status=404)
                return self.send_json(prop)

            elif path == "/api/other-assets":
                return self.send_json(SERVICE.list_other_assets())

            elif path == "/api/collections":
                return self.send_json(SERVICE.list_collections())

            elif path == "/api/validation":
                return self.send_json(SERVICE.validate_all())

            # 2. Static Asset Serving (/assets/...)
            elif path.startswith("/assets/"):
                rel_path = path.lstrip("/")
                try:
                    full_path = SERVICE.resolve_safe_path(rel_path)
                except Exception as pe:
                    return self.send_error_json(str(pe), status=403)

                if not os.path.isfile(full_path):
                    return self.send_error_json(f"File not found: {rel_path}", status=404)

                mime, _ = mimetypes.guess_type(full_path)
                mime = mime or "application/octet-stream"

                with open(full_path, "rb") as f:
                    content = f.read()

                self.send_response(200)
                self.send_header("Content-Type", mime)
                self.send_header("Content-Length", str(len(content)))
                self.send_header("Cache-Control", "no-cache")
                self.end_headers()
                self.wfile.write(content)
                return

            # 3. UI Static Files
            elif path in ("/", "/index.html"):
                return self.serve_ui_file("index.html", "text/html")
            elif path == "/app.css":
                return self.serve_ui_file("app.css", "text/css")
            elif path == "/app.js":
                return self.serve_ui_file("app.js", "application/javascript")

            else:
                return self.send_error_json(f"Endpoint not found: {path}", status=404)

        except Exception as e:
            self.send_error_json(f"Internal error: {e}", status=500)

    # -------------------------------------------------------------------------
    # POST Routing
    # -------------------------------------------------------------------------

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        try:
            # Add Background
            if path == "/api/backgrounds":
                payload = self.read_json_body()
                res = SERVICE.add_background(
                    image_path=payload["imagePath"],
                    bg_id=payload["id"],
                    name=payload["name"],
                    category=payload.get("category", "Education / STEM"),
                    description=payload.get("description", ""),
                    tags=payload.get("tags"),
                    status=payload.get("status", "active"),
                    floor_y=payload.get("floorY", 1380),
                    mood=payload.get("mood", "cool / studious"),
                    allow_overwrite=payload.get("allowOverwrite", False),
                    skip_preview=payload.get("skipPreview", False),
                )
                return self.send_json(res, status=201)

            # Background Status Change (enable/disable/archive)
            elif "/status" in path and path.startswith("/api/backgrounds/"):
                bg_id = path.replace("/api/backgrounds/", "").replace("/status", "").strip()
                payload = self.read_json_body()
                status = payload.get("status")
                reason = payload.get("reason")
                res = SERVICE.set_background_status(bg_id, status=status, reason=reason)
                return self.send_json(res)

            # Add Prop
            elif path == "/api/props":
                payload = self.read_json_body()
                res = SERVICE.add_prop(
                    prop_id=payload["id"],
                    name=payload["name"],
                    description=payload.get("description", ""),
                    width=payload.get("width", 120),
                    height=payload.get("height", 180),
                    anchor=payload.get("anchor", "bottom-center"),
                    supports_floor=payload.get("supportsFloor", True),
                    supports_hand=payload.get("supportsHand", True),
                    image_path=payload.get("imagePath"),
                )
                return self.send_json(res, status=201)

            # Add Character Variant
            elif "/variants" in path and path.startswith("/api/characters/"):
                c_id = path.replace("/api/characters/", "").replace("/variants", "").strip()
                payload = self.read_json_body()
                res = SERVICE.add_character_variant(
                    char_id=c_id,
                    variant_id=payload["variantId"],
                    image_source_path=payload["imageSourcePath"],
                )
                return self.send_json(res, status=201)

            # Collections CRUD
            elif path == "/api/collections":
                payload = self.read_json_body()
                res = SERVICE.create_collection(
                    coll_id=payload["id"],
                    name=payload["name"],
                    description=payload.get("description", ""),
                    category=payload.get("category", "Curated"),
                    asset_ids=payload.get("assetIds", []),
                )
                return self.send_json(res, status=201)

            # Downstream Synchronization
            elif path == "/api/sync":
                res = SERVICE.sync_all()
                return self.send_json(res)

            # Upload / Temporary File Staging
            elif path == "/api/upload":
                content_type = self.headers.get("Content-Type", "")
                if "application/json" in content_type:
                    payload = self.read_json_body()
                    # Expects { "filename": str, "contentBase64": str }
                    import base64
                    fname = os.path.basename(payload["filename"])
                    b64 = payload["contentBase64"].split(",")[-1]
                    raw = base64.b64decode(b64)
                    tmp_dir = os.path.join(self.server.repo_root, ".tmp_uploads")
                    os.makedirs(tmp_dir, exist_ok=True)
                    tmp_file = os.path.join(tmp_dir, fname)
                    with open(tmp_file, "wb") as f:
                        f.write(raw)
                    return self.send_json({
                        "status": "success",
                        "stagedPath": os.path.relpath(tmp_file, self.server.repo_root),
                        "filename": fname,
                    })
                else:
                    return self.send_error_json("Unsupported upload format. Use JSON base64 upload.")

            else:
                return self.send_error_json(f"POST endpoint not found: {path}", status=404)

        except Exception as e:
            self.send_error_json(str(e), status=400)

    # -------------------------------------------------------------------------
    # PUT Routing
    # -------------------------------------------------------------------------

    def do_PUT(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        try:
            if path.startswith("/api/backgrounds/"):
                bg_id = path.replace("/api/backgrounds/", "").strip()
                payload = self.read_json_body()
                res = SERVICE.update_background(bg_id, payload)
                return self.send_json(res)

            elif path.startswith("/api/characters/"):
                c_id = path.replace("/api/characters/", "").strip()
                payload = self.read_json_body()
                res = SERVICE.update_character(c_id, payload)
                return self.send_json(res)

            elif path.startswith("/api/collections/"):
                coll_id = path.replace("/api/collections/", "").strip()
                payload = self.read_json_body()
                res = SERVICE.update_collection(coll_id, payload)
                return self.send_json(res)

            else:
                return self.send_error_json(f"PUT endpoint not found: {path}", status=404)

        except Exception as e:
            self.send_error_json(str(e), status=400)

    # -------------------------------------------------------------------------
    # DELETE Routing
    # -------------------------------------------------------------------------

    def do_DELETE(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        force = query.get("force", ["false"])[0].lower() in ("true", "1")
        delete_asset = query.get("delete_asset", ["false"])[0].lower() in ("true", "1")

        try:
            # Delete Background
            if path.startswith("/api/backgrounds/"):
                bg_id = path.replace("/api/backgrounds/", "").strip()
                res = SERVICE.remove_background(bg_id, force=force, delete_asset=delete_asset)
                return self.send_json(res)

            # Delete Prop
            elif path.startswith("/api/props/"):
                p_id = path.replace("/api/props/", "").strip()
                res = SERVICE.remove_prop(p_id, force=force, delete_asset=delete_asset)
                return self.send_json(res)

            # Delete Character Variant
            elif "/variants/" in path and path.startswith("/api/characters/"):
                parts = path.replace("/api/characters/", "").split("/variants/")
                c_id, var_id = parts[0], parts[1]
                res = SERVICE.remove_character_variant(c_id, var_id)
                return self.send_json(res)

            # Delete Collection
            elif path.startswith("/api/collections/"):
                coll_id = path.replace("/api/collections/", "").strip()
                res = SERVICE.delete_collection(coll_id)
                return self.send_json(res)

            else:
                return self.send_error_json(f"DELETE endpoint not found: {path}", status=404)

        except Exception as e:
            self.send_error_json(str(e), status=400)

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------

    def serve_ui_file(self, filename: str, mime: str):
        full_path = os.path.join(UI_DIR, filename)
        if not os.path.isfile(full_path):
            return self.send_error_json(f"UI asset '{filename}' not found.", status=404)

        with open(full_path, "rb") as f:
            content = f.read()

        self.send_response(200)
        self.send_header("Content-Type", f"{mime}; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(content)


def run_asset_studio_server(host: str = "127.0.0.1", port: int = 4000, repo_root: Optional[str] = None):
    root = repo_root or find_repo_root()
    server = HTTPServer((host, port), AssetStudioHandler)
    server.repo_root = root
    print("=" * 70)
    print(">> @meowndr Asset Studio — Visual Asset Management UI")
    print("=" * 70)
    print(f"• Studio URL:       http://{host}:{port}/")
    print(f"• API Base:         http://{host}:{port}/api/overview")
    print(f"• Repository Root:  {root}")
    print("• Press Ctrl+C to stop.")
    print("=" * 70)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Asset Studio server...")
        server.server_close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="@meowndr Asset Studio Server")
    parser.add_argument("--host", default="127.0.0.1", help="Host address (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=4000, help="Port (default: 4000)")
    args = parser.parse_args()
    run_asset_studio_server(host=args.host, port=args.port)
