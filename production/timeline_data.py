"""
Master Choreography, 30-Move Continuous Camera Script, Dynamic Reveal Timings,
and Character 3D World Trajectories for "3 Kota Paling Unik di Dunia" (76.1s @ 30fps = 2283 frames).

100% Narrative-Synced to audio/vo_manifest.json.
Every coordinate is in Blender meters (X right, Y forward/depth, Z up).

7 Distinct 3D Shoot Zones arranged cleanly in world space (zero cross-bleeding):
  Zone 1 (X=  0, Y=  0.. 10, Z=0): Begich Towers Exterior Plaza & Snowy Mountains (Whittier, Alaska)
  Zone 2 (X=  0, Y= 12.. 32, Z=0): Begich Towers Warm Lobby, Post Office, Elevator & Kozy Korner
  Zone 3 (X= 10..42, Y=24, Z=-2.4): Whittier Underground School Tunnel (Yellow-Blue Arched Concrete)
  Zone 4 (X=100, Y=  0.. 18, Z=0): Coober Pedy Scorching Red Outback Desert, Mullock Heaps & Vent Pipes
  Zone 5 (X=100, Y= 20.. 38, Z=0): Coober Pedy Underground Sandstone Dugout Living Room & Opal Vein
  Zone 6 (X=200, Y=  0.. 36, Z=0): Setenil de las Bodegas — Calle Cuevas del Sol & Bar La Roca Terrace
  Zone 7 (X=200, Y= 18.. 36, Z=4.2): Setenil 2nd-Floor Balcony, Geraniums & Golden Hour Cliff Overlook
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Tuple

FPS = 30
TOTAL_FRAMES = 2283  # 76.096s exact match to vo_manifest.json

# ============================================================================
# EXACT VOICEOVER SEGMENTS (from audio/vo_manifest.json)
# ============================================================================
VO_CLIPS = [
    {"id": "01_fajar_hook",          "char": "Fajar",      "f0":    6, "f1":   92, "wav": "audio/clips/01_fajar_hook.wav"},
    {"id": "02_fajar_whittier_intro","char": "Fajar",      "f0":  101, "f1":  420, "wav": "audio/clips/02_fajar_whittier_intro.wav"},
    {"id": "03_arthur_dialog",       "char": "Pak Arthur", "f0":  428, "f1":  547, "wav": "audio/clips/03_arthur_dialog.wav"},
    {"id": "04_fajar_tunnel",        "char": "Fajar",      "f0":  555, "f1":  738, "wav": "audio/clips/04_fajar_tunnel.wav"},
    {"id": "05_maya_dialog",         "char": "Maya",       "f0":  743, "f1":  827, "wav": "audio/clips/05_maya_dialog.wav"},
    {"id": "06_fajar_coober_intro",  "char": "Fajar",      "f0":  841, "f1": 1087, "wav": "audio/clips/06_fajar_coober_intro.wav"},
    {"id": "07_fajar_dugout",        "char": "Fajar",      "f0": 1094, "f1": 1361, "wav": "audio/clips/07_fajar_dugout.wav"},
    {"id": "08_jack_dialog",         "char": "Jack",       "f0": 1367, "f1": 1433, "wav": "audio/clips/08_jack_dialog.wav"},
    {"id": "09_elena_dialog",        "char": "Elena",      "f0": 1439, "f1": 1510, "wav": "audio/clips/09_elena_dialog.wav"},
    {"id": "10_fajar_setenil_intro", "char": "Fajar",      "f0": 1524, "f1": 1822, "wav": "audio/clips/10_fajar_setenil_intro.wav"},
    {"id": "11_mateo_dialog",        "char": "Mateo",      "f0": 1828, "f1": 1907, "wav": "audio/clips/11_mateo_dialog.wav"},
    {"id": "12_fajar_insulator",     "char": "Fajar",      "f0": 1914, "f1": 2087, "wav": "audio/clips/12_fajar_insulator.wav"},
    {"id": "13_fajar_outro",         "char": "Fajar",      "f0": 2096, "f1": 2271, "wav": "audio/clips/13_fajar_outro.wav"},
]

# Scene boundaries (continuous camera transitions)
SCENE_RANGES = {
    "whittier_ext":    (0, 99),      # 00:00.0 - 00:03.3  (2s Hook + pushes glass door)
    "whittier_lobby":  (100, 554),   # 00:03.3 - 00:18.5  (Lobby, directory, Pak Arthur PO, Kozy Korner)
    "whittier_tunnel": (555, 835),   # 00:18.5 - 00:27.8  (Whip-pan stairs -> yellow-blue tunnel + Maya + speed dive)
    "coober_desert":   (836, 1092),  # 00:27.8 - 00:36.4  (Pipe erupt -> crane pull-back desert -> cave door)
    "coober_dugout":   (1093, 1518), # 00:36.4 - 00:50.6  (Dugout interior orbit, Jack, Elena opal flash)
    "setenil_street":  (1519, 1912), # 00:50.6 - 01:03.7  (Low-angle tracking Calle Cuevas del Sol, Fajar ducks, Mateo)
    "setenil_balcony": (1913, 2094), # 01:03.7 - 01:09.8  (Crane arc past white houses & geranium balcony, tapas bite)
    "setenil_outro":   (2095, 2282), # 01:09.8 - 01:16.1  (Golden hour pull-back, 3 fingers, snap loop hook)
}

# ============================================================================
# EASING HELPERS (Non-Linear Organic Curves + Subtle Overshoot)
# ============================================================================
def clamp01(t: float) -> float:
    return 0.0 if t <= 0.0 else (1.0 if t >= 1.0 else t)


def ease_in_out_expo(t: float) -> float:
    t = clamp01(t)
    if t == 0.0 or t == 1.0:
        return t
    if t < 0.5:
        return (2.0 ** (20.0 * t - 10.0)) * 0.5
    return (2.0 - (2.0 ** (-20.0 * t + 10.0))) * 0.5


def ease_in_out_cubic(t: float) -> float:
    t = clamp01(t)
    return 4.0 * t * t * t if t < 0.5 else 1.0 - ((-2.0 * t + 2.0) ** 3) * 0.5


def ease_out_expo(t: float) -> float:
    t = clamp01(t)
    return 1.0 if t >= 1.0 else 1.0 - (2.0 ** (-10.0 * t))


def ease_out_back(t: float, s: float = 1.25) -> float:
    t = clamp01(t)
    u = t - 1.0
    return 1.0 + (s + 1.0) * (u ** 3) + s * (u ** 2)


def ease_in_cubic(t: float) -> float:
    t = clamp01(t)
    return t * t * t


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def lerp3(a: Tuple[float, float, float], b: Tuple[float, float, float], t: float) -> Tuple[float, float, float]:
    return (lerp(a[0], b[0], t), lerp(a[1], b[1], t), lerp(a[2], b[2], t))


# ============================================================================
# 30 CONTINUOUS WIDE-ANGLE CAMERA MOVEMENTS (Exceeds >25 rule!)
# Format: (frame, cam_pos(x,y,z), target_pos(x,y,z), focal_mm, easing_name, hard_cut)
# Hard cuts ONLY on the 2 deliberate match-cut transitions (f=836 pipe burst, f=1519 sunbeam flash)
# ============================================================================
CAMERA_KEYS: List[Tuple[int, Tuple[float, float, float], Tuple[float, float, float], float, str, bool]] = [
    # --- ACT 0: HOOK — WHITTIER EXTERIOR (0..99) ---
    # M01: Wide establishing snowstorm push-in showing towering 14-story Begich + Chugach mountains!
    (0,    (-2.2, -16.5, 2.4),  (0.0,  9.5, 9.5),  17.0, "out_expo",    False),
    # M02: Fast dolly-in tilting down to shivering Fajar in front of 14-story tower
    (36,   (-1.0,  -4.2, 1.50), (0.0,  4.5, 2.40), 19.0, "in_out_cubic", False),
    # M03: Emphasis zoom-in on Fajar shivering + pointing back at massive tower
    (62,   (-0.5,  -0.4, 1.48), (0.1,  3.8, 1.65), 24.0, "out_back",    False),
    # M04: Dynamic follow-through as Fajar pushes open glass lobby door at t=2.2s
    (86,   (0.0,    5.6, 1.45), (0.0, 11.2, 1.35), 22.0, "in_out_expo", False),
    # M05: Smooth pass-through threshold into warm Begich lobby!
    (102,  (0.0,   10.8, 1.45), (0.0, 16.5, 1.35), 22.0, "out_back",    False),

    # --- ACT 1A: BEGICH TOWERS LOBBY & POST OFFICE (100..554) ---
    # M06: Continuous tracking shot sweeping past building directory board (left)
    (165,  (-1.3,  14.2, 1.55), (-2.6, 17.8, 1.50), 23.0, "in_out_cubic", False),
    # M07: Arc right past Fajar revealing 14-floor interior hub & Kozy Korner minimart
    (240,  (1.2,   17.4, 1.58), (2.8,  21.5, 1.40), 22.0, "in_out_cubic", False),
    # M08: Dolly forward along warm corridor as NPCs stroll past
    (315,  (0.6,   20.2, 1.50), (-1.4, 24.5, 1.38), 22.0, "in_out_cubic", False),
    # M09: Emphasis zoom onto elevator doors sliding open & Pak Arthur stepping out in pajamas!
    (375,  (1.4,   21.8, 1.42), (-2.6, 25.2, 1.25), 28.0, "out_back",    False),
    # M10: Tracking Pak Arthur 5 steps to wooden Post Office counter
    (430,  (0.4,   22.6, 1.35), (-3.1, 26.2, 1.25), 28.0, "in_out_cubic", False),
    # M11: Comedic low tilt emphasis on Pak Arthur's red-white plaid pajamas & mug!
    (490,  (-0.5,  23.4, 1.05), (-2.9, 26.3, 0.95), 32.0, "out_back",    False),
    # M12: Pull back slightly catching Fajar reacting to Pak Arthur's joke
    (542,  (0.8,   22.2, 1.45), (-1.4, 25.6, 1.30), 24.0, "in_out_cubic", False),

    # --- ACT 1B: WHIP-PAN INTO UNDERGROUND SCHOOL TUNNEL (555..835) ---
    # M13: Snappy whip-pan RIGHT following Maya toward "TO SCHOOL TUNNEL ->" doorway!
    (568,  (2.2,   23.2, 1.55), (8.2,  24.0, 0.85), 20.0, "in_out_expo", False),
    # M14: Diving smoothly down concrete staircase behind Maya
    (615,  (9.2,   23.6, 0.45), (16.5, 24.0, -1.25), 20.0, "in_out_cubic", False),
    # M15: Low wide tracking inside arched yellow-blue concrete tunnel
    (685,  (17.5,  23.6, -1.05), (25.0, 24.0, -1.15), 20.0, "in_out_cubic", False),
    # M16: Pull alongside Maya as she looks back smiling & waves in her teal sweater!
    (745,  (25.2,  22.9, -1.00), (28.5, 24.2, -1.12), 26.0, "out_back",    False),
    # M17: Dynamic close emphasis on Maya & clean sneakers before steel tunnel exit
    (798,  (29.8,  23.1, -1.10), (33.5, 24.0, -1.20), 24.0, "in_out_cubic", False),
    # M18: Speed-ramp dive straight into dark tunnel exit portal -> match-cut!
    (835,  (39.8,  24.0, -1.15), (44.0, 24.0, -1.15), 16.0, "in_cubic",    False),

    # --- ACT 2A: COOBER PEDY SCORCHING RED DESERT (836..1092) ---
    # M19: Match-cut erupting UP out of white desert ventilation pipe!
    (836,  (100.0,  2.0, 0.85), (100.0, 2.0,  6.50), 16.0, "out_expo",    True),
    # M20: Fast high-angle crane pull-back revealing vast red ochre desert & mullock heaps!
    (895,  (94.5,  -7.5, 7.20), (100.5, 6.5,  1.20), 19.0, "out_expo",    False),
    # M21: Sweeping desert arc past white vent pipes & rusted "DANGER: OPEN SHAFTS" sign
    (965,  (97.2,   1.5, 2.15), (100.4, 12.2, 1.45), 21.0, "in_out_cubic", False),
    # M22: Emphasis dolly onto Fajar fanning his face next to red hill wooden cave door
    (1030, (98.4,   7.8, 1.48), (100.0, 14.5, 1.42), 24.0, "out_back",    False),
    # M23: Push-in following Fajar opening heavy timber dugout door into cool cave sanctuary!
    (1092, (100.0, 17.6, 1.45), (100.0, 24.0, 1.35), 22.0, "in_out_expo", False),

    # --- ACT 2B: COOBER PEDY SANDSTONE DUGOUT & OPAL REVEAL (1093..1518) ---
    # M24: Wide reveal glide inside carved sandstone dugout living room
    (1165, (97.2,  21.4, 1.55), (100.5, 28.0, 1.25), 21.0, "in_out_cubic", False),
    # M25: Smooth 180° orbit around leather sofa, recessed rock bookshelf & terracotta floor
    (1265, (104.4, 24.5, 1.52), (99.8,  28.2, 1.18), 22.0, "in_out_cubic", False),
    # M26: Orbit continuing onto Jack relaxing on leather sofa with iced tea (deadpan off-fan nearby!)
    (1370, (102.6, 25.0, 1.38), (98.5,  28.4, 1.15), 28.0, "out_back",    False),
    # M27: Whip-arc right to Elena shining LED flashlight beam onto shimmering Opal Vein!
    (1442, (99.8,  25.8, 1.45), (103.5, 29.8, 1.38), 28.0, "in_out_expo", False),
    # M28: Extreme emphasis push-in directly into glowing blue-green-magenta opal crystal flash!
    (1518, (103.0, 29.3, 1.42), (104.6, 30.8, 1.42), 18.0, "in_cubic",    False),

    # --- ACT 3: SETENIL DE LAS BODEGAS — CALLE CUEVAS DEL SOL (1519..2282) ---
    # M29: Match-cut emerging from Golden Hour sunbeam slicing under giant overhanging cliff!
    (1519, (198.2, -3.5, 1.15), (200.0,  8.0, 2.90), 19.0, "out_expo",    True),
    # M30: Low-angle speed-tracking tilting UP to showcase hundred-ton rock overhang!
    (1610, (198.8,  4.8, 1.05), (200.5, 15.0, 3.80), 19.0, "in_out_cubic", False),
    # M31: Tracking Fajar walking reflexively ducked under 4.5m cliff rock ceiling!
    (1715, (197.8, 10.6, 1.35), (200.6, 18.0, 2.10), 21.0, "in_out_cubic", False),
    # M32: Dolly onto Bar La Roca terrace as Mateo confidently sets tapas & knocks cliff ceiling!
    (1830, (197.8, 14.2, 1.45), (201.4, 19.6, 1.85), 23.0, "out_back",    False),
    # M33: Smooth crane arc rising sideways past white stucco houses & geranium balconies!
    (1955, (196.4, 19.8, 4.20), (201.8, 23.5, 4.40), 22.0, "in_out_cubic", False),
    # M34: Descending crane glide back to Mateo offering tapas bread to amazed Fajar!
    (2075, (198.5, 16.5, 1.50), (201.4, 20.4, 1.38), 25.0, "out_back",    False),
    # M35: Majestic Golden Hour pull-back down cobblestone alley — Fajar 3 fingers -> snap loop!
    (2175, (199.2, 11.2, 1.65), (200.5, 20.5, 1.85), 21.0, "in_out_cubic", False),
    (2282, (198.6,  1.8, 2.35), (200.5, 19.5, 2.65), 18.0, "in_out_expo", False),
]


def get_camera_state(frame: int) -> Tuple[Tuple[float, float, float], Tuple[float, float, float], float]:
    """Evaluate continuous camera (location, look_at_target, lens_mm) at exact frame."""
    if frame <= CAMERA_KEYS[0][0]:
        k = CAMERA_KEYS[0]
        return k[1], k[2], k[3]
    if frame >= CAMERA_KEYS[-1][0]:
        k = CAMERA_KEYS[-1]
        return k[1], k[2], k[3]

    for i in range(len(CAMERA_KEYS) - 1):
        f0, p0, t0, l0, _, _ = CAMERA_KEYS[i]
        f1, p1, t1, l1, ease_name, hard_cut = CAMERA_KEYS[i + 1]
        if f0 <= frame <= f1:
            if hard_cut:
                return (p1, t1, l1) if frame >= f1 else (p0, t0, l0)
            u = (frame - f0) / max(1.0, float(f1 - f0))
            if ease_name == "out_expo":
                e = ease_out_expo(u)
            elif ease_name == "in_out_expo":
                e = ease_in_out_expo(u)
            elif ease_name == "out_back":
                e = ease_out_back(u, s=0.85)
            elif ease_name == "in_cubic":
                e = ease_in_cubic(u)
            else:
                e = ease_in_out_cubic(u)
            pos = lerp3(p0, p1, e)
            tgt = lerp3(t0, t1, e)
            lens = lerp(l0, l1, clamp01(e))
            # Subtle organic handheld camera breathing micro-motion (never static!)
            t_sec = frame / float(FPS)
            bx = math.sin(t_sec * 1.15) * 0.025
            bz = math.cos(t_sec * 1.65) * 0.018
            return (pos[0] + bx, pos[1], pos[2] + bz), tgt, lens
    k = CAMERA_KEYS[-1]
    return k[1], k[2], k[3]


def get_scene_id(frame: int) -> str:
    for sid, (f0, f1) in SCENE_RANGES.items():
        if f0 <= frame <= f1:
            return sid
    return "setenil_outro"


def compute_view_angle_deg(
    char_pos: Tuple[float, float, float],
    char_facing_yaw_deg: float,
    cam_pos: Tuple[float, float, float],
) -> float:
    """
    Compute 2.5D character turntable angle (0..360 deg) relative to Blender 3D camera!
    char_facing_yaw_deg: 0 = facing -Y (toward default camera), 90 = +X, 180 = +Y, 270 = -X.
    """
    dx = cam_pos[0] - char_pos[0]
    dy = cam_pos[1] - char_pos[1]
    cam_yaw = math.degrees(math.atan2(dx, -dy))
    rel = (cam_yaw - char_facing_yaw_deg) % 360.0
    return rel


# ============================================================================
# CHARACTER 3D WORLD POSITIONS, FACING, & OPEN FREE-RIG ACTING STATES
# Strict Ground Contact: Z is ALWAYS exact floor height (0.0 or tunnel -2.4)
# ============================================================================
def _active_speaking(char_name: str, frame: int) -> bool:
    for c in VO_CLIPS:
        if c["char"] == char_name and c["f0"] <= frame <= c["f1"]:
            return True
    return False


def get_character_states(frame: int) -> Dict[str, Dict[str, Any]]:
    """
    Returns world transform + Free-Rig kwargs for all 6 hero characters + animated NPCs.
    Every character's feet sit strictly at ground Z (zero floating, zero wall clipping!).
    """
    t = frame / float(FPS)
    cam_pos, _, _ = get_camera_state(frame)
    states: Dict[str, Dict[str, Any]] = {}

    # ------------------------------------------------------------------
    # 1. FAJAR (Present across all 3 cities!)
    # ------------------------------------------------------------------
    fajar_vis = True
    fajar_pos = (0.0, 2.2, 0.0)
    fajar_yaw = 0.0
    fajar_rig: Dict[str, Any] = {"animation": "free", "eyes": "honey_oval", "eyebrows": "thick_arch", "mouth": "confident_gap"}

    if frame <= 99:
        # Whittier Exterior: shivering in blizzard, then pushing glass door at f=60..98!
        if frame < 58:
            shiver = math.sin(t * 26.0) * 3.5
            fajar_pos = (0.15, 2.4, 0.0)
            fajar_yaw = -10.0
            fajar_rig.update({
                "animation": "talk",
                "pose": "crossed",
                "eyes": "shocked" if frame < 32 else "honey_oval",
                "eyebrows": "worried",
                "head_tilt_deg": shiver,
                "torso_lean_deg": 4.0 + math.sin(t * 18.0) * 1.5,
                "pelvis_y": 5.0 + abs(math.sin(t * 14.0)) * 3.0,
                "gesture_energy": 0.9,
            })
        else:
            u = ease_in_out_cubic((frame - 58) / 41.0)
            fajar_pos = (lerp(0.15, 0.35, u), lerp(2.4, 11.4, u), 0.0)
            fajar_yaw = 180.0  # Walking forward into lobby
            fajar_rig.update({
                "animation": "walk",
                "arm_pose": "point" if frame < 84 else "ready",
                "right_hand_target": (84.0, 178.0, 42.0) if 66 <= frame <= 86 else None,
                "torso_lean_deg": 6.0,
            })
    elif frame <= 554:
        # Begich Towers Warm Lobby: strolling through hub -> reacting to Pak Arthur
        if frame < 355:
            u = ease_in_out_cubic((frame - 100) / 255.0)
            fajar_pos = (lerp(0.35, 0.45, u), lerp(11.6, 23.8, u), 0.0)
            fajar_yaw = lerp(165.0, -35.0, clamp01((frame - 140) / 215.0))
            fajar_rig.update({
                "animation": "walk" if frame < 335 else "talk",
                "arm_pose": "point" if (180 <= frame <= 260) else "wave",
                "eyes": "honey_oval",
                "eyebrows": "raised" if (150 <= frame <= 250) else "happy",
                "gesture_energy": 0.85,
            })
        else:
            # Watching Pak Arthur emerge in plaid pajamas!
            fajar_pos = (0.45, 23.8, 0.0)
            fajar_yaw = -62.0  # Looking left toward Pak Arthur at Post Office counter
            fajar_rig.update({
                "animation": "free",
                "pose": "akimbo" if frame > 480 else "ready",
                "eyes": "asymmetric" if 435 <= frame <= 515 else "happy",
                "eyebrows": "skeptical" if 435 <= frame <= 515 else "happy",
                "mouth": "small_o" if 435 <= frame <= 490 else "happy_open",
                "head_tilt_deg": math.sin(t * 2.5) * 4.5,
                "eye_gaze_x": -0.4,
            })
    elif frame <= 835:
        # Following Maya into school tunnel!
        if frame < 610:
            u = ease_in_out_cubic((frame - 555) / 55.0)
            fajar_pos = (lerp(0.5, 6.2, u), lerp(23.8, 24.4, u), lerp(0.0, -0.4, clamp01((frame - 585) / 25.0)))
            fajar_yaw = 90.0
            fajar_rig.update({"animation": "walk", "eyes": "honey_oval", "gesture_energy": 0.7})
        else:
            u = ease_in_out_cubic((frame - 610) / 185.0)
            z_floor = lerp(-0.4, -2.4, clamp01((frame - 610) / 40.0))
            fajar_pos = (lerp(6.2, 23.5, u), 24.6, z_floor)
            fajar_yaw = 82.0 if frame < 735 else 65.0
            fajar_rig.update({
                "animation": "walk" if frame < 735 else "talk",
                "arm_pose": "wave" if frame >= 740 else "point",
                "eyes": "happy" if frame >= 740 else "honey_oval",
                "gesture_energy": 0.8,
            })
    elif frame <= 1092:
        # Coober Pedy Desert: fanning face in scorching 50C heat -> pushing open cave door!
        if frame < 1035:
            fajar_pos = (99.4, 12.2, 0.0)
            fajar_yaw = 18.0
            fan_y = 148.0 + math.sin(t * 14.0) * 16.0
            fan_x = 80.0 + math.cos(t * 14.0) * 10.0
            fajar_rig.update({
                "animation": "talk",
                "eyes": "panic" if frame < 960 else "focused",
                "eyebrows": "worried",
                "sweat_drop": True,
                "right_hand_target": (fan_x, fan_y, 34.0),
                "head_tilt_deg": -5.0 + math.sin(t * 6.0) * 3.0,
                "gesture_energy": 0.9,
            })
        else:
            u = ease_in_out_cubic((frame - 1035) / 57.0)
            fajar_pos = (lerp(99.4, 100.0, u), lerp(12.2, 20.6, u), 0.0)
            fajar_yaw = 180.0
            fajar_rig.update({
                "animation": "walk",
                "right_hand_target": (84.0, 176.0, 40.0) if frame < 1072 else None,
                "sweat_drop": frame < 1070,
            })
    elif frame <= 1518:
        # Coober Pedy Dugout Interior: cool relief -> awestruck by glowing Opal vein!
        if frame < 1360:
            u = ease_in_out_cubic((frame - 1093) / 140.0)
            fajar_pos = (lerp(100.0, 101.2, u), lerp(20.8, 26.2, u), 0.0)
            fajar_yaw = lerp(175.0, -25.0, clamp01((frame - 1140) / 160.0))
            fajar_rig.update({
                "animation": "walk" if frame < 1230 else "talk",
                "eyes": "happy",
                "eyebrows": "happy",
                "arm_pose": "heroic" if frame >= 1230 else "ready",
                "gesture_energy": 0.8,
            })
        else:
            # Turns toward Elena's glowing opal wall -> eyes wide shocked/starry!
            fajar_pos = (101.4, 26.8, 0.0)
            fajar_yaw = 125.0 if frame > 1425 else -45.0
            is_opal = frame >= 1435
            fajar_rig.update({
                "animation": "free",
                "eyes": "shocked" if is_opal else "happy",
                "eyebrows": "raised",
                "mouth": "small_o" if is_opal else "confident_gap",
                "torso_lean_deg": 9.0 if is_opal else 2.0,
                "pelvis_y": -6.0 if (1440 <= frame <= 1455) else 0.0,
                "eye_gaze_x": 0.55 if is_opal else -0.35,
            })
    elif frame <= 2094:
        # Setenil Calle Cuevas del Sol: walking comically ducked under giant hanging rock -> tasting tapas!
        if frame < 1815:
            u = ease_in_out_cubic((frame - 1519) / 296.0)
            fajar_pos = (lerp(199.4, 200.4, u), lerp(5.5, 19.2, u), 0.0)
            fajar_yaw = lerp(170.0, 45.0, clamp01((frame - 1700) / 115.0))
            duck_bob = 22.0 + math.sin(t * 7.0) * 5.0
            fajar_rig.update({
                "animation": "walk",
                "arm_pose": "panic" if frame < 1710 else "think",
                "eyes": "panic" if frame < 1710 else "shocked",
                "eyebrows": "worried",
                "sweat_drop": frame < 1790,
                "pelvis_y": duck_bob,
                "torso_lean_deg": 14.0,
                "head_tilt_deg": -10.0,
                "eye_gaze_y": -0.85,  # Staring tensely UP at overhanging rock!
            })
        else:
            # At Mateo's terrace: tasting tapas, looking up in awe, nodding!
            fajar_pos = (199.5, 18.8, 0.0)
            fajar_yaw = 55.0 if frame < 2010 else 10.0
            nod = math.sin(t * 6.5) * 7.0 if frame >= 2030 else 0.0
            fajar_rig.update({
                "animation": "talk" if _active_speaking("Fajar", frame) else "free",
                "pose": "think" if frame < 2015 else "heroic",
                "eyes": "starry" if frame >= 2035 else "happy",
                "eyebrows": "happy",
                "head_tilt_deg": nod,
                "eye_gaze_y": -0.65 if (2015 <= frame <= 2060) else 0.0,
                "gesture_energy": 0.78,
            })
    else:
        # Outro (2095..2282): Center of sunlit cobblestone street -> 3 fingers -> point camera -> shrug & snap!
        fajar_pos = (200.0, 17.5, 0.0)
        fajar_yaw = 0.0
        snap_active = frame >= 2248
        shrug_active = 2215 <= frame < 2248
        fajar_rig.update({
            "animation": "talk" if _active_speaking("Fajar", frame) else "free",
            "pose": "point" if (2165 <= frame < 2215) else ("wave" if snap_active else "heroic"),
            "eyes": "happy" if snap_active else "honey_oval",
            "eyebrows": "raised" if shrug_active else "happy",
            "mouth": "happy_open" if snap_active else "confident_gap",
            "right_hand_target": (88.0, 155.0, 38.0) if snap_active else None,
            "pelvis_y": -8.0 if snap_active else (4.0 if shrug_active else 0.0),
            "gesture_energy": 0.95,
        })

    states["Fajar"] = {
        "visible": fajar_vis,
        "pos": fajar_pos,
        "yaw": fajar_yaw,
        "height_m": 1.72,
        "angle": compute_view_angle_deg(fajar_pos, fajar_yaw, cam_pos),
        "rig": {k: v for k, v in fajar_rig.items() if v is not None},
    }

    # ------------------------------------------------------------------
    # 2. PAK ARTHUR (Whittier Begich Lobby: Elevator -> Post Office Counter)
    # ------------------------------------------------------------------
    arthur_vis = 100 <= frame <= 565
    if frame < 370:
        arthur_pos = (-4.6, 25.0, 0.0)  # Inside elevator bay waiting for doors
        arthur_yaw = 90.0
        arthur_rig = {"animation": "idle", "pose": "ready", "eyes": "chill"}
    elif frame < 426:
        # Strolling 5 relaxed steps from elevator to Post Office counter!
        u = ease_in_out_cubic((frame - 370) / 56.0)
        arthur_pos = (lerp(-4.6, -2.8, u), lerp(25.0, 26.2, u), 0.0)
        arthur_yaw = lerp(90.0, 18.0, u)
        arthur_rig = {
            "animation": "walk",
            "arm_pose": "ready",
            "right_hand_target": (74.0, 210.0, 28.0),  # Holding steaming WHITTIER coffee mug!
            "eyes": "chill",
        }
    else:
        # Behind/beside Post Office window casually sorting letters & delivering punchline!
        arthur_pos = (-2.8, 26.2, 0.0)
        arthur_yaw = 22.0
        arthur_rig = {
            "animation": "talk" if _active_speaking("Pak Arthur", frame) else "idle",
            "pose": "akimbo",
            "eyes": "happy" if frame >= 480 else "chill",
            "eyebrows": "happy",
            "mouth": "smirk",
            "gesture_energy": 0.7,
        }
    states["Pak Arthur"] = {
        "visible": arthur_vis,
        "pos": arthur_pos,
        "yaw": arthur_yaw,
        "height_m": 1.68,
        "angle": compute_view_angle_deg(arthur_pos, arthur_yaw, cam_pos),
        "rig": arthur_rig,
    }

    # ------------------------------------------------------------------
    # 3. MAYA (Whittier Lobby -> Stairs -> School Tunnel)
    # ------------------------------------------------------------------
    maya_vis = 530 <= frame <= 835
    if frame < 605:
        u = ease_in_out_cubic(clamp01((frame - 548) / 57.0))
        maya_pos = (lerp(3.2, 11.2, u), 24.0, lerp(0.0, -1.6, clamp01((frame - 575) / 30.0)))
        maya_yaw = 90.0
        maya_rig = {"animation": "run", "eyes": "happy", "eyebrows": "happy", "mouth": "happy_open"}
    elif frame < 735:
        u = ease_in_out_cubic((frame - 605) / 130.0)
        maya_pos = (lerp(11.2, 28.2, u), 24.2, lerp(-1.6, -2.4, clamp01((frame - 605) / 25.0)))
        maya_yaw = 90.0 if frame < 710 else lerp(90.0, -65.0, (frame - 710) / 25.0)
        maya_rig = {"animation": "walk", "arm_pose": "wave" if frame > 700 else "ready", "eyes": "happy"}
    else:
        # Turning & walking backwards joyfully waving at Fajar while speaking!
        u = ease_in_out_cubic(clamp01((frame - 735) / 90.0))
        maya_pos = (lerp(28.2, 34.8, u), 24.2, -2.4)
        maya_yaw = -72.0  # Facing back toward Fajar & camera!
        maya_rig = {
            "animation": "talk" if _active_speaking("Maya", frame) else "wave",
            "pose": "wave",
            "eyes": "happy",
            "eyebrows": "happy",
            "mouth": "happy_open",
            "gesture_energy": 0.95,
        }
    states["Maya"] = {
        "visible": maya_vis,
        "pos": maya_pos,
        "yaw": maya_yaw,
        "height_m": 1.56,
        "angle": compute_view_angle_deg(maya_pos, maya_yaw, cam_pos),
        "rig": maya_rig,
    }

    # ------------------------------------------------------------------
    # 4. JACK (Coober Pedy Dugout: Seated relaxed on leather sofa with iced tea!)
    # ------------------------------------------------------------------
    jack_vis = 1090 <= frame <= 1518
    jack_pos = (98.4, 28.4, 0.22)  # Seated height aligned cleanly to leather sofa cushion!
    jack_yaw = 32.0
    jack_speaking = _active_speaking("Jack", frame)
    jack_lift = 1.0 if jack_speaking else 0.0
    jack_rig: Dict[str, Any] = {
        "animation": "talk" if jack_speaking else "free",
        "pose": "ready",
        "pelvis_y": 24.0,  # Seated relaxed posture
        "torso_lean_deg": -4.0,
        "eyes": "happy" if jack_speaking else "chill",
        "eyebrows": "raised" if jack_speaking else "flat",
        "mouth": "grin_teeth" if jack_speaking else "smirk",
        "right_hand_target": (82.0, 175.0 - jack_lift * 26.0, 34.0),  # Raising iced tea glass!
        "gesture_energy": 0.75,
    }
    states["Jack"] = {
        "visible": jack_vis,
        "pos": jack_pos,
        "yaw": jack_yaw,
        "height_m": 1.72,
        "angle": compute_view_angle_deg(jack_pos, jack_yaw, cam_pos),
        "rig": jack_rig,
    }

    # ------------------------------------------------------------------
    # 5. ELENA (Coober Pedy Dugout: Shining LED flashlight on Opal Vein!)
    # ------------------------------------------------------------------
    elena_vis = 1090 <= frame <= 1518
    elena_pos = (103.0, 29.4, 0.0)
    elena_yaw = -38.0 if frame < 1435 else -12.0
    elena_speaking = _active_speaking("Elena", frame)
    elena_rig: Dict[str, Any] = {
        "animation": "talk" if elena_speaking else "free",
        "pose": "point",
        "eyes": "smug" if elena_speaking else "honey_oval",
        "eyebrows": "raised",
        "mouth": "grin_teeth" if elena_speaking else "smirk",
        "right_hand_target": (88.0, 172.0 + math.sin(t * 2.2) * 5.0, 38.0),  # Aiming flashlight at opal wall!
        "gesture_energy": 0.85,
    }
    states["Elena"] = {
        "visible": elena_vis,
        "pos": elena_pos,
        "yaw": elena_yaw,
        "height_m": 1.66,
        "angle": compute_view_angle_deg(elena_pos, elena_yaw, cam_pos),
        "rig": elena_rig,
    }

    # ------------------------------------------------------------------
    # 6. MATEO (Setenil Bar La Roca Terrace: Sets Tapas -> Knocks Rock -> Waves Outro!)
    # ------------------------------------------------------------------
    mateo_vis = 1519 <= frame <= 2282
    mateo_pos = (201.8, 19.2, 0.0)
    mateo_yaw = -35.0 if frame < 2095 else -18.0
    mateo_speaking = _active_speaking("Mateo", frame)
    if 1835 <= frame <= 1875:
        # Reaching UP to knock firmly on overhanging cliff ceiling (tink-tok!)
        knock_y = 112.0 + abs(math.sin((frame - 1835) * 0.55)) * 18.0
        mateo_rig = {
            "animation": "talk",
            "eyes": "happy",
            "eyebrows": "happy",
            "mouth": "happy_open",
            "right_hand_target": (82.0, knock_y, 30.0),
            "head_tilt_deg": -8.0,
            "gesture_energy": 0.9,
        }
    elif frame >= 2095:
        # Warm farewell wave from tapas cafe terrace!
        mateo_rig = {
            "animation": "wave",
            "eyes": "happy",
            "eyebrows": "happy",
            "mouth": "happy_open",
        }
    else:
        mateo_rig = {
            "animation": "talk" if mateo_speaking else "idle",
            "pose": "wave" if frame >= 2020 else "ready",
            "eyes": "happy",
            "eyebrows": "happy",
            "mouth": "happy_open",
            "gesture_energy": 0.85,
        }
    states["Mateo"] = {
        "visible": mateo_vis,
        "pos": mateo_pos,
        "yaw": mateo_yaw,
        "height_m": 1.74,
        "angle": compute_view_angle_deg(mateo_pos, mateo_yaw, cam_pos),
        "rig": mateo_rig,
    }

    # ------------------------------------------------------------------
    # LIVING ANIMATED BACKGROUND NPCs (Lobby Residents + Setenil Cafe Patrons!)
    # ------------------------------------------------------------------
    # NPC 1: Begich Towers Lobby resident walking along hallway with groceries
    if 100 <= frame <= 560:
        u1 = ((frame - 100) / 460.0)
        p_npc1 = (1.9, lerp(28.5, 13.5, u1), 0.0)
        states["NPC_Whittier_1"] = {
            "visible": True, "pos": p_npc1, "yaw": 0.0, "height_m": 1.66,
            "angle": compute_view_angle_deg(p_npc1, 0.0, cam_pos),
            "rig": {"animation": "walk", "eyes": "chill"},
        }
        p_npc2 = (-1.8, lerp(14.0, 22.0, clamp01(u1 * 1.3)), 0.0)
        states["NPC_Whittier_2"] = {
            "visible": True, "pos": p_npc2, "yaw": 180.0, "height_m": 1.70,
            "angle": compute_view_angle_deg(p_npc2, 180.0, cam_pos),
            "rig": {"animation": "walk" if u1 < 0.75 else "idle", "eyes": "happy"},
        }
    else:
        states["NPC_Whittier_1"] = {"visible": False, "pos": (1.9, 28.0, 0.0), "yaw": 0.0, "height_m": 1.66, "angle": 0.0, "rig": {"animation": "idle"}}
        states["NPC_Whittier_2"] = {"visible": False, "pos": (-1.8, 14.0, 0.0), "yaw": 180.0, "height_m": 1.70, "angle": 0.0, "rig": {"animation": "idle"}}

    # NPC 3 & 4: Setenil Cafe Patrons chatting happily at bistro tables under the rock!
    if 1519 <= frame <= 2282:
        p_s1 = (202.4, 13.2, 0.16)
        p_s2 = (202.4, 14.8, 0.16)
        p_s3 = (197.8, 22.8, 0.0)
        u3 = ((frame - 1519) / 763.0)
        p_s3 = (197.8, lerp(26.5, 10.5, u3), 0.0)
        states["NPC_Setenil_1"] = {
            "visible": True, "pos": p_s1, "yaw": 165.0, "height_m": 1.64,
            "angle": compute_view_angle_deg(p_s1, 165.0, cam_pos),
            "rig": {"animation": "talk", "pelvis_y": 22.0, "eyes": "happy", "mouth_open": abs(math.sin(t * 5.2)) * 0.45},
        }
        states["NPC_Setenil_2"] = {
            "visible": True, "pos": p_s2, "yaw": -15.0, "height_m": 1.68,
            "angle": compute_view_angle_deg(p_s2, -15.0, cam_pos),
            "rig": {"animation": "idle", "pelvis_y": 22.0, "eyes": "happy", "head_tilt_deg": math.sin(t * 2.4) * 5.0},
        }
        states["NPC_Setenil_3"] = {
            "visible": True, "pos": p_s3, "yaw": 0.0, "height_m": 1.66,
            "angle": compute_view_angle_deg(p_s3, 0.0, cam_pos),
            "rig": {"animation": "walk", "eyes": "chill"},
        }
    else:
        for nm in ("NPC_Setenil_1", "NPC_Setenil_2", "NPC_Setenil_3"):
            states[nm] = {"visible": False, "pos": (200.0, 15.0, 0.0), "yaw": 0.0, "height_m": 1.66, "angle": 0.0, "rig": {"animation": "idle"}}

    return states


# ============================================================================
# DYNAMIC REVEAL TIMING TABLE (Strictly 1 dominant effect per hero prop/zone!)
# Synced 0.2s ahead of VO keywords -> hard-locked after end_frame!
# ============================================================================
DYNAMIC_REVEALS = {
    # 1. Architectural Build-up: Begich Towers 14-story floors & windows (f=10..56)
    "begich_tower_arch":    {"type": "architectural", "start": 4,    "dur": 46},
    # 2. Assembly Build-up: Lobby Directory + Post Office Counter + PO Boxes (f=210..275)
    "lobby_post_assembly":  {"type": "assembly",      "start": 205,  "dur": 36},
    "lobby_mart_assembly":  {"type": "assembly",      "start": 255,  "dur": 34},
    # 3. Pop-up Diorama: School Tunnel sign & glowing ceiling frames (f=565..600)
    "tunnel_sign_popup":    {"type": "popup",         "start": 562,  "dur": 22},
    # 4. Procedural Staggered Wave: Coober Pedy white ventilation pipes across desert (f=855..945)
    "desert_pipes_wave":    {"type": "procedural",    "start": 850,  "stagger": 3, "dur": 20},
    # 5. Pop-up Diorama: "DANGER: OPEN SHAFTS" rusted yellow triangle sign (f=950..974)
    "danger_sign_popup":    {"type": "popup",         "start": 948,  "dur": 22},
    # 6. Assembly Build-up: Dugout carved bookshelf, leather sofa & opal display (f=1120..1185)
    "dugout_furniture_asm": {"type": "assembly",      "start": 1118, "dur": 36},
    # 7. Architectural Build-up: Setenil whitewashed Andalusian houses under cliff (f=1565..1645)
    "setenil_houses_arch":  {"type": "architectural", "start": 1560, "dur": 52},
    # 8. Procedural Staggered Wave: Geranium pots & bistro tables along Calle Cuevas del Sol (f=1690..1775)
    "setenil_cafe_wave":    {"type": "procedural",    "start": 1688, "stagger": 4, "dur": 18},
    # 9. Pop-up Diorama: "BAR LA ROCA — TAPAS" wooden menu board (f=1790..1814)
    "bar_sign_popup":       {"type": "popup",         "start": 1788, "dur": 22},
}


# ============================================================================
# PREVIEW REEL SEGMENTS (For fast multi-location GitHub review clip!)
# Covers EVERY city, character, dynamic reveal, transition, and comedy beat!
# ============================================================================
PREVIEW_SEGMENTS = [
    ("01_whittier_hook_door",     0,   115),  # 3.8s: 2s Snowstorm Hook + Begich Architectural reveal + Fajar pushes glass door
    ("02_arthur_pajama_post",   365,   525),  # 5.3s: Elevator opens + Pak Arthur in red-white plaid pajamas + VO punchline
    ("03_maya_tunnel_dive",     715,   865),  # 5.0s: Maya waves in school tunnel + speed-ramp dive -> Coober Pedy vent pipe match-cut!
    ("04_coober_desert_pipes",  890,  1040),  # 5.0s: Red desert crane pull-back + Vent pipe procedural wave + Danger sign + Fajar fanning
    ("05_dugout_jack_elena",   1355,  1545),  # 6.3s: Dugout orbit, Jack iced tea, Elena opal flashlight -> Setenil sunbeam match-cut!
    ("06_setenil_cliff_mateo", 1745,  1920),  # 5.8s: Fajar ducking under giant rock + Mateo knocks ceiling + Bar La Roca
    ("07_setenil_outro_loop",  2135,  2282),  # 4.9s: Golden hour pull-back, Fajar 3 fingers -> finger snap loop!
]
