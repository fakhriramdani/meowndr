#!/usr/bin/env python3
"""
test_text_safe_layout.py: Automated QA test suite for collision-free text placement,
leader lines, obstacle avoidance, and safe-zone constraints.
"""

from typing import List, Dict, Any, Optional

CANVAS_BOUNDS = {"x": 40, "y": 40, "width": 1000, "height": 1840}
TOP_BANNER_ZONE = {"x": 0, "y": 0, "width": 1080, "height": 380}
BOTTOM_CAPTION_ZONE = {"x": 0, "y": 1410, "width": 1080, "height": 510}


def rects_overlap(r1: Dict[str, float], r2: Dict[str, float], padding: float = 12.0) -> bool:
    return not (
        r1["x"] + r1["width"] + padding <= r2["x"] or
        r2["x"] + r2["width"] + padding <= r1["x"] or
        r1["y"] + r1["height"] + padding <= r2["y"] or
        r2["y"] + r2["height"] + padding <= r1["y"]
    )


def estimate_dims(text: str, font_size: float, t_type: str = "badge", max_w: float = 420.0) -> Dict[str, float]:
    char_w = font_size * 0.62
    pad_x = 36.0 if t_type == "badge" else 40.0
    pad_y = 20.0 if t_type == "badge" else 32.0
    line_h = font_size * 1.35

    raw_w = len(text) * char_w + pad_x
    if raw_w <= max_w:
        return {"width": raw_w, "height": line_h + pad_y, "fontSize": font_size}

    # Multi-line
    words = text.split(" ")
    lines = []
    cur = ""
    for w in words:
        test = f"{cur} {w}" if cur else w
        if len(test) * char_w + pad_x > max_w:
            if cur:
                lines.append(cur)
            cur = w
        else:
            cur = test
    if cur:
        lines.append(cur)

    num_lines = max(1, len(lines))
    return {"width": max_w, "height": num_lines * line_h + pad_y, "fontSize": font_size}


def resolve_safe_placements(
    items: List[Dict[str, Any]],
    obstacles: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Python mirror of resolveSafeTextPlacements from TextCollisionEngine.ts."""
    sorted_items = sorted(items, key=lambda x: x.get("priority", 3))
    placed = []
    results = []

    active_obs = [o["rect"] for o in obstacles] + [TOP_BANNER_ZONE, BOTTOM_CAPTION_ZONE]

    for item in sorted_items:
        base_fs = item.get("fontSize", 28.0)
        min_fs = item.get("minFontSize", 20.0)
        t_type = item.get("type", "badge")
        max_w = item.get("width", 400.0)

        dims = estimate_dims(item["text"], base_fs, t_type, max_w)
        cand_x = item["preferredX"] - dims["width"] / 2.0
        cand_y = item["preferredY"] - dims["height"] / 2.0

        def test_rect(x: float, y: float, w: float, h: float) -> bool:
            if x < CANVAS_BOUNDS["x"] or x + w > CANVAS_BOUNDS["x"] + CANVAS_BOUNDS["width"]:
                return False
            if y < CANVAS_BOUNDS["y"] or y + h > CANVAS_BOUNDS["y"] + CANVAS_BOUNDS["height"]:
                return False
            r = {"x": x, "y": y, "width": w, "height": h}
            for obs in active_obs:
                if rects_overlap(r, obs, 14.0):
                    return False
            for p in placed:
                if rects_overlap(r, p["rect"], 14.0):
                    return False
            return True

        final_x = cand_x
        final_y = cand_y
        final_w = dims["width"]
        final_h = dims["height"]
        final_fs = base_fs
        is_placed = False

        if test_rect(cand_x, cand_y, dims["width"], dims["height"]):
            is_placed = True
        else:
            candidates = [
                {"x": cand_x, "y": cand_y - dims["height"] - 30},
                {"x": cand_x + 180, "y": cand_y},
                {"x": cand_x - 180, "y": cand_y},
                {"x": 620, "y": max(400.0, cand_y)},
                {"x": 620, "y": 720},
                {"x": 80, "y": max(400.0, cand_y)},
                {"x": 80, "y": 720},
            ]
            for c in candidates:
                cx = max(CANVAS_BOUNDS["x"], min(CANVAS_BOUNDS["x"] + CANVAS_BOUNDS["width"] - dims["width"], c["x"]))
                cy = max(400.0, min(1380.0 - dims["height"], c["y"]))
                if test_rect(cx, cy, dims["width"], dims["height"]):
                    final_x = cx
                    final_y = cy
                    is_placed = True
                    break

            if not is_placed and base_fs > min_fs:
                final_fs = min_fs
                compact = estimate_dims(item["text"], final_fs, t_type, min(320.0, max_w))
                final_w = compact["width"]
                final_h = compact["height"]
                for c in candidates:
                    cx = max(CANVAS_BOUNDS["x"], min(CANVAS_BOUNDS["x"] + CANVAS_BOUNDS["width"] - final_w, c["x"]))
                    cy = max(400.0, min(1380.0 - final_h, c["y"]))
                    if test_rect(cx, cy, final_w, final_h):
                        final_x = cx
                        final_y = cy
                        is_placed = True
                        break

        resolved_rect = {"x": final_x, "y": final_y, "width": final_w, "height": final_h}
        placed.append({"id": item["id"], "rect": resolved_rect, "priority": item.get("priority", 3)})

        leader_line = None
        if item.get("targetPoint"):
            tp = item["targetPoint"]
            leader_line = {
                "startX": final_x + final_w / 2.0,
                "startY": final_y + final_h / 2.0,
                "endX": tp["x"],
                "endY": tp["y"],
            }

        results.append({
            "id": item["id"],
            "rect": resolved_rect,
            "fontSize": final_fs,
            "hasCollision": not is_placed,
            "leaderLine": leader_line,
        })

    return results


def test_avoid_cat_and_visualization_collision():
    """Verify text automatically avoids colliding with Cat Scientist and molecular visualization."""
    # Cat Scientist standing at x=360, y=1380
    cat_rect = {"x": 252, "y": 1128, "width": 216, "height": 252}
    # Molecular visualization at x=460, y=600, w=560, h=580
    vis_rect = {"x": 460, "y": 600, "width": 560, "height": 580}

    obstacles = [
        {"name": "cat_scientist", "rect": cat_rect},
        {"name": "visualization", "rect": vis_rect},
    ]

    # Test item: Badge whose preferred position is directly on the visualization (x=700, y=750)
    items = [
        {
            "id": "label_hydrogen",
            "text": "IKATAN HIDROGEN",
            "preferredX": 700,
            "preferredY": 750, # Inside the visualization!
            "fontSize": 26,
            "priority": 2,
            "targetPoint": {"x": 680, "y": 700},
        }
    ]

    res = resolve_safe_placements(items, obstacles)
    item_res = res[0]
    r = item_res["rect"]

    # Must NOT overlap with visualization
    assert not rects_overlap(r, vis_rect), "Resolved text collided with molecular visualization!"
    # Must NOT overlap with Cat Scientist
    assert not rects_overlap(r, cat_rect), "Resolved text collided with Cat Scientist!"
    # Must NOT overlap with Top Banner Zone (y < 380)
    assert not rects_overlap(r, TOP_BANNER_ZONE), "Resolved text collided with top banner zone!"
    # Must NOT overlap with Bottom Caption Zone (y > 1410)
    assert not rects_overlap(r, BOTTOM_CAPTION_ZONE), "Resolved text collided with bottom caption zone!"
    # Must have leader line pointing to target
    assert item_res["leaderLine"] is not None, "Leader line must exist"
    assert item_res["leaderLine"]["endX"] == 680, "Leader line must point to target x=680"

    print("  [PASS] test_avoid_cat_and_visualization_collision passed.")


def test_multiple_text_elements_no_overlap():
    """Verify multiple concurrent text elements do not overlap with each other."""
    obstacles = [
        {"name": "cat_scientist", "rect": {"x": 260, "y": 1130, "width": 200, "height": 250}},
    ]

    items = [
        {"id": "t1", "text": "ANOMALI AIR 4°C", "preferredX": 750, "preferredY": 650, "priority": 1},
        {"id": "t2", "text": "KEPADATAN MAKSIMUM", "preferredX": 750, "preferredY": 660, "priority": 2}, # Collision candidate
        {"id": "t3", "text": "VOLUME MEMUAI", "preferredX": 750, "preferredY": 670, "priority": 3},    # Collision candidate
    ]

    res = resolve_safe_placements(items, obstacles)
    rects = [r["rect"] for r in res]

    for i in range(len(rects)):
        for j in range(i + 1, len(rects)):
            assert not rects_overlap(rects[i], rects[j]), f"Collision detected between item {i} and {j}!"

    print("  [PASS] test_multiple_text_elements_no_overlap passed.")


def test_font_size_safety():
    """Verify font size is never shrunk below readable threshold (minFontSize >= 20px)."""
    obstacles = [
        {"name": "full_crowd", "rect": {"x": 100, "y": 400, "width": 800, "height": 900}},
    ]
    items = [
        {
            "id": "long_text",
            "text": "Struktur kristal es memiliki rongga heksagonal yang terbuka lebar.",
            "preferredX": 540,
            "preferredY": 600,
            "fontSize": 28,
            "minFontSize": 20,
            "priority": 2,
        }
    ]
    res = resolve_safe_placements(items, obstacles)
    assert res[0]["fontSize"] >= 20, f"Font size fell below 20px threshold: {res[0]['fontSize']}"
    print("  [PASS] test_font_size_safety passed.")


def main():
    print("=================================================================")
    print("  Running Text Safe Layout & Collision Prevention Test Suite")
    print("=================================================================")
    test_avoid_cat_and_visualization_collision()
    test_multiple_text_elements_no_overlap()
    test_font_size_safety()
    print(">> All 3 Text Safe Layout tests PASSED successfully!")
    print("=================================================================")


if __name__ == "__main__":
    main()
