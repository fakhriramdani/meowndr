#!/usr/bin/env python3
"""
test_dynamic_character.py: Automated QA test suite for Dynamic Cat Scientist kinematics,
movement interpolation, reaction dynamics, and visual interaction.
"""

import math
import sys
from typing import Dict, Any, Optional

def calculate_kinematics(
    frame: int,
    base_x: float,
    base_y: float,
    size: float = 240,
    base_face: int = 1,
    base_state: str = "idle",
    base_point_angle: float = -30,
    movement: Optional[Dict[str, Any]] = None,
    interaction: Optional[Dict[str, Any]] = None,
    interactive_action: Optional[Dict[str, Any]] = None,
    gaze: Optional[str] = None
) -> Dict[str, Any]:
    """Python mirror of calculateCatKinematics from DynamicCatScientist.tsx."""
    cur_x = base_x
    cur_y = base_y
    walk_bob = 0.0
    is_moving = False
    auto_face = base_face
    active_state = base_state
    active_point_angle = base_point_angle

    # 1. Movement interpolation
    if movement and movement.get("type") and movement["type"] != "static":
        start_f = movement.get("startFrame", 0)
        dur_f = max(1, movement.get("duration", 30))
        end_f = start_f + dur_f

        s_x = movement.get("startX", base_x)
        e_x = movement.get("endX", base_x)
        s_y = movement.get("startY", base_y)
        e_y = movement.get("endY", base_y)

        m_type = movement["type"]
        if m_type == "enter_left":
            s_x = -180
            e_x = movement.get("endX", base_x)
        elif m_type == "enter_right":
            s_x = 1260
            e_x = movement.get("endX", base_x)
        elif m_type == "exit_left":
            s_x = base_x
            e_x = -180
        elif m_type == "exit_right":
            s_x = base_x
            e_x = 1260
        elif m_type == "step_back":
            s_x = base_x
            e_x = base_x - base_face * 80

        if frame <= start_f:
            cur_x = s_x
            cur_y = s_y
        elif frame >= end_f:
            cur_x = e_x
            cur_y = e_y
        else:
            is_moving = True
            progress = (frame - start_f) / dur_f
            progress = max(0.0, min(1.0, progress))

            # Easing
            easing = movement.get("easing", "linear")
            if easing == "easeInOut":
                t = 2 * progress * progress if progress < 0.5 else -1 + (4 - 2 * progress) * progress
            elif easing == "easeOut":
                t = math.sin((progress * math.pi) / 2)
            else:
                t = progress

            cur_x = s_x + (e_x - s_x) * t
            cur_y = s_y + (e_y - s_y) * t

            if m_type in ("walk", "enter_left", "enter_right", "exit_left", "exit_right"):
                step_cycle = (frame - start_f) * 0.45
                walk_bob = abs(math.sin(step_cycle)) * 9.0

        if e_x > s_x + 10:
            auto_face = 1
        elif e_x < s_x - 10:
            auto_face = -1

    active_face = auto_face
    active_gaze = gaze

    # 2. Interaction
    if interaction:
        i_start = interaction.get("startFrame", 0)
        i_dur = interaction.get("duration", 60)
        is_active = i_start <= frame < (i_start + i_dur)

        if is_active:
            target = interaction.get("target")
            if target:
                tx = target["x"]
                ty = target["y"]

                if not is_moving:
                    active_face = 1 if tx >= cur_x else -1

                i_type = interaction.get("type")
                if i_type in ("point_at", "explain_with_gesture"):
                    active_state = "explaining"
                    arm_y = cur_y - size * 0.45
                    dx = tx - cur_x
                    dy = ty - arm_y
                    raw_deg = math.degrees(math.atan2(dy, dx if active_face == 1 else -dx))
                    active_point_angle = max(-80.0, min(45.0, round(raw_deg, 1)))

                if i_type in ("look_at", "point_at", "reach_for"):
                    eye_y = cur_y - size * 0.7
                    if ty < eye_y - size * 0.25:
                        active_gaze = "up"
                    elif ty > eye_y + size * 0.2:
                        active_gaze = "down"
                    else:
                        active_gaze = "right" if ((active_face == 1 and tx > cur_x) or (active_face == -1 and tx < cur_x)) else "left"

            if interaction.get("type") == "celebrate":
                active_state = "celebrating"
            elif interaction.get("type") == "surprised_reaction":
                active_state = "surprised"

    # 3. Interactive Action Choreography & Gadget Engagement
    body_offset = {"x": 0.0, "y": -walk_bob, "rotate": 0.0}
    squash_stretch = {"scaleX": 1.0, "scaleY": 1.0}
    active_gadget = None

    if interactive_action and interactive_action.get("type"):
        a_start = interactive_action.get("startFrame", 30)
        a_dur = max(24, interactive_action.get("duration", 75))
        rf = frame - a_start
        if 0 <= rf <= a_dur:
            progress = rf / float(a_dur)
            intensity = interactive_action.get("intensity", 1.0)
            tx = interactive_action.get("target", {}).get("x", cur_x + 340 * active_face)
            ty = interactive_action.get("target", {}).get("y", 680)
            active_face = 1 if tx >= cur_x else -1
            a_type = interactive_action["type"]

            if a_type == "operate_lever":
                step_in = math.sin(progress * math.pi) * 52.0 * intensity
                pull_cycle = math.sin(progress * math.pi * 2.0)
                body_offset["x"] += active_face * step_in
                body_offset["rotate"] = active_face * (pull_cycle * 9.0 * intensity)
                squash_stretch["scaleY"] = 1.0 - abs(pull_cycle) * 0.08
                squash_stretch["scaleX"] = 1.0 + abs(pull_cycle) * 0.06
                active_state = "pointing" if progress < 0.5 else "explaining"
            elif a_type == "launch_experiment":
                if progress < 0.35:
                    press = progress / 0.35
                    body_offset["y"] += press * 22.0 * intensity
                    squash_stretch["scaleY"] = 1.0 - press * 0.16
                    squash_stretch["scaleX"] = 1.0 + press * 0.12
                    active_state = "pointing"
                else:
                    hop = abs(math.sin(((progress - 0.35) / 0.65) * math.pi * 2.0))
                    body_offset["y"] -= hop * 46.0 * intensity
                    active_state = "excited"

            active_gadget = {"type": a_type, "progress": progress, "targetX": tx, "targetY": ty}

    return {
        "x": cur_x,
        "y": cur_y,
        "face": active_face,
        "state": active_state,
        "pointAngle": active_point_angle,
        "gaze": active_gaze,
        "bodyOffset": body_offset,
        "squashStretch": squash_stretch,
        "activeGadget": active_gadget,
    }


def test_character_movement_continuity():
    """Verify position interpolation has smooth continuity without teleportation."""
    movement = {
        "type": "walk",
        "startX": 200,
        "endX": 600,
        "startFrame": 10,
        "duration": 40,
        "easing": "easeInOut",
    }

    # Before movement starts
    k_pre = calculate_kinematics(5, base_x=200, base_y=1380, movement=movement)
    assert k_pre["x"] == 200, f"Expected 200 at frame 5, got {k_pre['x']}"
    assert k_pre["bodyOffset"]["y"] == 0, "No walk bob before movement"

    # Mid movement (frame 30 = halfway)
    k_mid = calculate_kinematics(30, base_x=200, base_y=1380, movement=movement)
    assert 350 < k_mid["x"] < 450, f"Expected mid around 400, got {k_mid['x']}"
    assert k_mid["face"] == 1, "Should face right during rightward walk"

    # After movement completes (frame 55)
    k_post = calculate_kinematics(55, base_x=200, base_y=1380, movement=movement)
    assert k_post["x"] == 600, f"Expected 600 at frame 55, got {k_post['x']}"

    # Smoothness check: delta between consecutive frames must never exceed 25px
    prev_x = 200.0
    for f in range(10, 51):
        k = calculate_kinematics(f, base_x=200, base_y=1380, movement=movement)
        dx = abs(k["x"] - prev_x)
        assert dx < 25.0, f"Teleportation detected at frame {f}: dx = {dx}px"
        prev_x = k["x"]

    print("  [PASS] test_character_movement_continuity passed.")


def test_interaction_aiming_and_gaze():
    """Verify arm pointing angle and gaze vector aim accurately at target coordinates."""
    # Target high and to the right
    interaction_high = {
        "type": "point_at",
        "target": {"x": 750, "y": 600},
        "startFrame": 0,
        "duration": 60,
    }
    k_high = calculate_kinematics(10, base_x=300, base_y=1380, size=240, interaction=interaction_high)
    assert k_high["face"] == 1, "Should auto-face towards target on right"
    assert k_high["state"] == "explaining", "Pointing should trigger explaining state"
    assert k_high["pointAngle"] < 0, f"Pointing upwards should be negative angle, got {k_high['pointAngle']}"
    assert k_high["gaze"] == "up", f"Target at y=600 should cause gaze up, got {k_high['gaze']}"

    # Target low (e.g. pond / lake below floor)
    interaction_low = {
        "type": "look_at",
        "target": {"x": 300, "y": 1600},
        "startFrame": 0,
        "duration": 60,
    }
    k_low = calculate_kinematics(10, base_x=300, base_y=1380, size=240, interaction=interaction_low)
    assert k_low["gaze"] == "down", f"Target at y=1600 should cause gaze down, got {k_low['gaze']}"

    print("  [PASS] test_interaction_aiming_and_gaze passed.")


def test_interactive_action_choreography():
    """Verify interactiveAction (operate_lever & launch_experiment) engages gadget and steps/hops."""
    act = {
        "type": "operate_lever",
        "target": {"x": 700, "y": 680},
        "startFrame": 40,
        "duration": 60,
        "intensity": 1.0,
    }

    # Frame 39: Before interactiveAction
    k_pre = calculate_kinematics(39, base_x=260, base_y=1380, interactive_action=act)
    assert k_pre["state"] == "idle"
    assert k_pre["activeGadget"] is None

    # Frame 55: Stepping in & pulling lever (rf = 15, progress = 0.25)
    k_pull = calculate_kinematics(55, base_x=260, base_y=1380, interactive_action=act)
    assert k_pull["state"] == "pointing"
    assert k_pull["bodyOffset"]["x"] > 20, f"Expected forward step toward lever, got {k_pull['bodyOffset']['x']}"
    assert k_pull["squashStretch"]["scaleY"] < 1.0
    assert k_pull["activeGadget"] is not None and k_pull["activeGadget"]["type"] == "operate_lever"

    # Frame 85: Explaining phase (rf = 45, progress = 0.75)
    k_exp = calculate_kinematics(85, base_x=260, base_y=1380, interactive_action=act)
    assert k_exp["state"] == "explaining"

    print("  [PASS] test_interactive_action_choreography passed.")


def test_entrance_and_exit_trajectories():
    """Verify enter_left and exit_right bounds and motion."""
    enter_mov = {
        "type": "enter_left",
        "endX": 360,
        "startFrame": 0,
        "duration": 30,
    }
    k_enter_start = calculate_kinematics(0, base_x=360, base_y=1380, movement=enter_mov)
    assert k_enter_start["x"] == -180, f"enter_left should start off-screen left (-180), got {k_enter_start['x']}"

    k_enter_end = calculate_kinematics(30, base_x=360, base_y=1380, movement=enter_mov)
    assert k_enter_end["x"] == 360, f"enter_left should finish at 360, got {k_enter_end['x']}"

    exit_mov = {
        "type": "exit_right",
        "startFrame": 50,
        "duration": 30,
    }
    k_exit_end = calculate_kinematics(80, base_x=360, base_y=1380, movement=exit_mov)
    assert k_exit_end["x"] == 1260, f"exit_right should end off-screen right (1260), got {k_exit_end['x']}"

    print("  [PASS] test_entrance_and_exit_trajectories passed.")


def main():
    print("=================================================================")
    print("  Running Dynamic Cat Scientist Kinematics & Reaction Test Suite")
    print("=================================================================")
    test_character_movement_continuity()
    test_interaction_aiming_and_gaze()
    test_interactive_action_choreography()
    test_entrance_and_exit_trajectories()
    print(">> All 4 Dynamic Cat Scientist tests PASSED successfully!")
    print("=================================================================")


if __name__ == "__main__":
    main()
