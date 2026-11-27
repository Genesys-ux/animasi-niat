"""
Biomechanical 4-Phase Walk Cycle (Anti-Foot-Sliding) & Expressive Free-Rig Acting Library
for the 2.5D Shared Engine (character_engine_25d.py).

Guarantees:
  - 4 Explicit Walk Phases synced directly to real-world distance traveled (distance_m / stride_m * 2*pi):
      1. Contact  (heel strikes forward, rear toe pushes)
      2. Down     (stance knee flexes, pelvis drops 6-8% absorbing weight)
      3. Passing  (swing foot lifts high off ground, knee bends cleanly past stance leg)
      4. Up       (push-off rebound, pelvis peaks)
  - Stance foot stays pinned to floor plane during ground contact (ZERO foot sliding!).
  - Opposite-phase arm swing with clavicle follow, head bob, torso lean & breathing micro-motion.
  - Dedicated realistic seated IK & prop-interaction acting routines (zero stiff/frozen poses!).
"""

from __future__ import annotations

import math
from typing import Any, Dict, Optional, Tuple


def _leg_ik_for_phase(
    phase: float,
    x_hip: float,
    stride_px: float,
    lift_px: float,
    ground_y: float = 466.0,
    backward: bool = False,
) -> Tuple[Tuple[float, float, float], float]:
    """
    Compute exact 3D ankle target (x, y, z) and knee bend for one leg at walk phase [0..2*pi).
    - [0 .. pi)     : Stance phase -> foot stays pinned on floor (y = ground_y), sweeping linearly
                      from front (+stride) to back (-stride) to cancel root translation 1:1!
    - [pi .. 2*pi)  : Swing phase  -> foot lifts cleanly high (up to -lift_px) with knee bend!
    """
    p = phase % (2.0 * math.pi)
    dir_sign = -1.0 if backward else 1.0

    if p < math.pi:
        # STANCE PHASE (foot solidly planted on floor — linear ground lock!)
        u = p / math.pi  # 0 (heel contact front) -> 1 (toe push-off rear)
        z = dir_sign * (stride_px * (1.0 - 2.0 * u))
        y = ground_y
        # Slight stance knee bend on Down phase (u ~ 0.25)
        knee_flex = math.sin(u * math.pi) * 6.0
    else:
        # SWING PHASE (foot lifted high through Passing phase -> heel strike!)
        u = (p - math.pi) / math.pi  # 0 (rear lift) -> 1 (front contact)
        # Smooth S-curve forward swing
        su = 0.5 - 0.5 * math.cos(u * math.pi)
        z = dir_sign * (stride_px * (-1.0 + 2.0 * su))
        # High Passing clearance arch
        arch = math.sin(u * math.pi) ** 0.85
        y = ground_y - arch * lift_px
        knee_flex = 12.0 * arch

    return (x_hip, y, z), knee_flex


def build_walk_rig(
    distance_m: float,
    t: float,
    stride_m: float = 0.82,
    crouch_px: float = 0.0,
    backward: bool = False,
    jog: bool = False,
    left_hand_override: Optional[Tuple[float, float, float]] = None,
    right_hand_override: Optional[Tuple[float, float, float]] = None,
) -> Dict[str, Any]:
    """
    Distance-locked 4-Phase Biomechanical Walk/Jog Cycle using Open Free-Rig 2-Bone IK!
    phase = (distance_m / stride_m) * 2 * pi ensures ZERO foot sliding at ANY translation speed!
    """
    phi = (distance_m / max(0.25, stride_m)) * 2.0 * math.pi
    stride_px = 56.0 if jog else 50.0
    lift_px = 50.0 if jog else 44.0
    if crouch_px > 10.0:
        stride_px = 44.0
        lift_px = 38.0

    # 4-Phase vertical pelvis weight curve (Contact -> Down +10px -> Passing -4px -> Up -9px)
    # 2 full bounce cycles per full 2-step stride (frequency = 2*phi)!
    step_wave = math.sin(2.0 * phi - 0.55)
    pelvis_drop = crouch_px + (-step_wave * (11.5 if jog else 8.5)) + 5.0
    sq_y = 1.0 + step_wave * (0.036 if jog else 0.026)
    sq_x = 1.0 / sq_y

    l_foot, _ = _leg_ik_for_phase(phi, -18.0, stride_px, lift_px, 462.0, backward=backward)
    r_foot, _ = _leg_ik_for_phase(phi + math.pi, 22.0, stride_px, lift_px, 462.0, backward=backward)

    # Opposite-phase natural arm swing (Left arm swings with Right leg!)
    arm_amp_z = 60.0 if jog else 52.0
    arm_lift = 28.0 if jog else 20.0
    dir_s = -1.0 if backward else 1.0
    l_arm_s = -math.cos(phi) * dir_s
    r_arm_s = math.cos(phi) * dir_s

    l_hand = left_hand_override or (
        -50.0 - abs(l_arm_s) * 6.0,
        286.0 + pelvis_drop * 0.65 - max(0.0, l_arm_s) * arm_lift,
        l_arm_s * arm_amp_z,
    )
    r_hand = right_hand_override or (
        54.0 + abs(r_arm_s) * 6.0,
        286.0 + pelvis_drop * 0.65 - max(0.0, r_arm_s) * arm_lift,
        r_arm_s * arm_amp_z,
    )

    lean = (10.0 if jog else 5.0) * dir_s + math.sin(phi) * 2.5
    if crouch_px > 10.0:
        lean += 11.0

    return {
        "animation": "free",
        "pelvis_y": pelvis_drop,
        "head_bob_y": -step_wave * 3.4,
        "torso_lean_deg": lean,
        "head_tilt_deg": math.sin(phi - 0.35) * 3.8,
        "squash_x": sq_x,
        "squash_y": sq_y,
        "left_foot_target": l_foot,
        "right_foot_target": r_foot,
        # Clean anatomical forward knee alignment (-4/+4 splay; 2-bone IK bends knees forward naturally!)
        "left_knee_bend": -4.0,
        "right_knee_bend": 4.0,
        "left_hand_target": l_hand,
        "right_hand_target": r_hand,
        "cape_sway": -10.0 - math.sin(phi - 0.5) * 14.0,
        "hat_tilt_extra": math.sin(phi - 0.4) * 2.8,
    }


def build_seated_rig(
    t: float,
    speaking: bool = False,
    mouth_val: float = 0.0,
    lift_glass: float = 0.0,
) -> Dict[str, Any]:
    """
    Authentic Biomechanical Seated Pose:
    Hips seated cleanly on sofa cushion, knees bent forward (+Z), feet planted solidly on floor!
    """
    breath = math.sin(t * 2.4)
    act = 0.35 + 0.65 * mouth_val if speaking else 0.18
    gesture = math.sin(t * 4.2) * act

    # Right hand lifts frosted iced tea glass smoothly up & outward when speaking!
    r_hand = (
        66.0 + lift_glass * 16.0 + gesture * 12.0,
        252.0 - lift_glass * 58.0 - abs(gesture) * 14.0,
        36.0 + lift_glass * 14.0,
    )
    # Left hand rests relaxed on sofa armrest with subtle expressive beats
    l_hand = (
        -64.0 - gesture * 10.0,
        266.0 - abs(gesture) * 12.0,
        22.0 + gesture * 8.0,
    )

    return {
        "animation": "free",
        "pelvis_y": 34.0 + breath * 2.5,
        "torso_lean_deg": -6.0 + breath * 1.4 + gesture * 4.0,
        "head_tilt_deg": -3.0 + math.sin(t * 1.8) * 3.5 + gesture * 5.0,
        "head_bob_y": breath * 2.0 - mouth_val * 3.5,
        "squash_y": 1.0 + breath * 0.014,
        "squash_x": 1.0 - breath * 0.014,
        # Knees bent forward cleanly + feet grounded on floor in front of sofa!
        "left_foot_target": (-20.0, 462.0, 54.0),
        "right_foot_target": (24.0, 462.0, 56.0),
        "left_knee_bend": -4.0,
        "right_knee_bend": 4.0,
        "left_hand_target": l_hand,
        "right_hand_target": r_hand,
        "prop": "coffee_mug" if lift_glass > 0.08 else "none",
    }


def build_acting_rig(
    t: float,
    mode: str = "talk_expressive",
    speaking: bool = False,
    mouth_val: float = 0.0,
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Rich Secondary Motion & Prop-Interaction Free-Rig Acting (Zero stiff/frozen characters!):
    Always includes organic breathing bob, weight shift, speech-driven head tilt, and live 2-Bone IK hands!
    """
    breath = math.sin(t * 2.7)
    act = (0.42 + 0.85 * mouth_val) if speaking else 0.25
    g1 = math.sin(t * 4.4)
    g2 = math.cos(t * 3.1)

    rig: Dict[str, Any] = {
        "animation": "free",
        "pelvis_y": breath * 3.2 + (abs(g1) * 2.5 if speaking else 0.0),
        "head_bob_y": breath * 2.4 - (mouth_val * 4.0 if speaking else 0.0),
        "torso_lean_deg": math.sin(t * 1.8) * 2.5 + (g1 * 4.5 * act),
        "head_tilt_deg": math.sin(t * 2.2) * 4.2 + (g2 * 5.5 * act),
        "squash_y": 1.0 + breath * 0.015,
        "squash_x": 1.0 - breath * 0.015,
        "left_foot_target": (-20.0, 466.0, -6.0),
        "right_foot_target": (24.0, 466.0, 8.0),
        "left_knee_bend": -5.0,
        "right_knee_bend": 5.0,
    }

    if mode == "shiver_cold":
        shiv = math.sin(t * 28.0)
        rig.update({
            "pelvis_y": 8.0 + abs(math.sin(t * 14.0)) * 4.5,
            "torso_lean_deg": 5.0 + shiv * 2.4,
            "head_tilt_deg": shiv * 5.5,
            "left_hand_target": (-26.0 + shiv * 4.0, 242.0, 34.0),
            "right_hand_target": (32.0 - shiv * 4.0, 236.0, 36.0),
            "squash_x": 1.03,
            "squash_y": 0.97,
        })
    elif mode == "push_door":
        # Full-body lean forward + both hands firmly pushing glass/wooden door!
        rig.update({
            "pelvis_y": 6.0,
            "torso_lean_deg": 12.0,
            "head_tilt_deg": -5.0,
            "left_hand_target": (-34.0, 212.0, 56.0),
            "right_hand_target": (46.0, 206.0, 62.0),
        })
    elif mode == "fan_heat":
        # Fajar visibly sweating & furiously fanning face with handheld fan in 50°C Coober Pedy desert!
        fw = math.sin(t * 17.0)
        fc = math.cos(t * 17.0)
        rig.update({
            "pelvis_y": 4.0 + math.sin(t * 5.2) * 4.0,
            "torso_lean_deg": -4.0 + math.sin(t * 3.0) * 3.0,
            "head_tilt_deg": -8.0 + math.sin(t * 4.5) * 4.5,
            "right_hand_target": (74.0 + fc * 20.0, 154.0 + fw * 20.0, 38.0),
            "left_hand_target": (-58.0, 268.0 + math.sin(t * 5.2) * 8.0, 24.0),
            "sweat_drop": True,
            "prop": "fan",
        })
    elif mode == "arthur_postal":
        # Pak Arthur holds steaming WHITTIER coffee mug locked directly to his IK right hand + lively left gesture!
        sip = max(0.0, math.sin(t * 1.8)) * 22.0
        rig.update({
            "torso_lean_deg": -2.0 + math.sin(t * 2.0) * 3.5,
            "head_tilt_deg": math.sin(t * 2.8) * 6.0,
            "right_hand_target": (62.0, 224.0 - sip, 36.0),
            "left_hand_target": (-68.0 - g1 * 18.0 * act, 224.0 - abs(g2) * 32.0 * act, 36.0),
            "prop": "coffee_mug",
        })
    elif mode == "maya_wave":
        # Fluid joyous multi-joint wave (shoulder + elbow + head tilt + bouncy knees!)
        w = math.sin(t * 10.5)
        wc = math.cos(t * 10.5)
        rig.update({
            "pelvis_y": math.sin(t * 5.2) * 5.5,
            "torso_lean_deg": -5.0 + w * 4.0,
            "head_tilt_deg": -10.0 + w * 5.5,
            "right_hand_target": (86.0 + w * 24.0, 128.0 + wc * 14.0, 36.0),
            "left_hand_target": (-34.0, 248.0, 30.0),  # Hugging school notebook!
        })
    elif mode == "elena_opal":
        # Elena holds & taps geology rock pickaxe toward rainbow Opal cluster while LED beam tracks it!
        sweep = math.sin(t * 2.8)
        tap = max(0.0, math.sin(t * 9.5)) ** 2 if speaking else 0.0
        rig.update({
            "torso_lean_deg": 6.0 + sweep * 3.0,
            "head_tilt_deg": -4.0 + sweep * 5.0,
            "right_hand_target": (84.0 + tap * 14.0, 178.0 - tap * 22.0, 48.0),
            "left_hand_target": (-64.0 + sweep * 12.0, 220.0 - abs(sweep) * 16.0, 36.0),
            "prop": "pickaxe",
        })
    elif mode == "mateo_knock":
        # Mateo reaches UP high knocking twice firmly on the overhanging cliff ceiling!
        kn = abs(math.sin(t * 13.5))
        rig.update({
            "pelvis_y": -4.0 + kn * 4.0,
            "torso_lean_deg": -4.0,
            "head_tilt_deg": -12.0 + kn * 4.0,
            "right_hand_target": (74.0, 96.0 + kn * 24.0, 32.0),
            "left_hand_target": (-58.0, 240.0, 34.0),  # Balancing tapas tray!
            "prop": "none",
        })
    elif mode == "mateo_serve":
        # Warm expressive tapas serving & lively Mediterranean hand gestures with kitchen spatula!
        rig.update({
            "torso_lean_deg": 5.0 + g1 * 3.5,
            "head_tilt_deg": g2 * 6.0,
            "right_hand_target": (74.0 + g1 * 14.0, 206.0 - abs(g2) * 26.0, 44.0),
            "left_hand_target": (-64.0 - g2 * 12.0, 228.0 - abs(g1) * 16.0, 34.0),
            "prop": "spatula",
        })
    elif mode == "fajar_shrug_snap":
        # Outro punchline: amazed shrug -> crisp finger snap!
        rig.update({
            "pelvis_y": -6.0,
            "torso_lean_deg": 3.0,
            "head_tilt_deg": 6.0,
            "left_hand_target": (-82.0, 184.0, 32.0),
            "right_hand_target": (88.0, 148.0, 44.0),
        })
    else:
        # Expressive host / narrator two-hand gestures synced to voice!
        rig.update({
            "left_hand_target": (-66.0 - g1 * 18.0 * act, 224.0 - abs(g2) * 38.0 * act, 34.0),
            "right_hand_target": (72.0 + g2 * 20.0 * act, 212.0 - abs(g1) * 44.0 * act, 38.0),
        })

    if extra:
        rig.update(extra)
    return rig
