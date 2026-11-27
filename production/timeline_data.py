"""
Master Choreography, 9:16 VERTICAL Wide-Angle Camera Script (32 Moves + Heavy Cliff Drop Shake!),
Distance-Synced 4-Phase Biomechanical Character Trajectories, Dynamic Build-Up Timings,
and Strict Complete-Sentence Preview Segments for "3 Kota Paling Unik di Dunia" (76.1s @ 30fps = 2283 frames).

100% Narrative-Synced to audio/vo_manifest.json.
Strict 3-Collection World Isolation:
  - LOC_01_Whittier   : Frames    0 ..  835  (Begich Towers Ext, Lobby, Post Office, Kozy Korner, School Tunnel)
  - LOC_02_CooberPedy : Frames  836 .. 1518  (Red Outback Desert, Mullock Heaps, Vent Pipes, Sandstone Dugout & Opal)
  - LOC_03_Setenil    : Frames 1519 .. 2282  (Calle Cuevas del Sol, Colossal Rock Overhang, Bar La Roca & Balconies)
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Tuple

from biomechanics import build_acting_rig, build_seated_rig, build_walk_rig

FPS = 30
TOTAL_FRAMES = 2283  # Exact 76.096s match to audio/vo_manifest.json

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

# Active Location Collection boundaries (STRICT isolation — zero cross-bleed!)
LOCATION_RANGES = {
    "LOC_01_Whittier":   (0, 835),
    "LOC_02_CooberPedy": (836, 1518),
    "LOC_03_Setenil":    (1519, 2282),
}

SCENE_RANGES = {
    "whittier_ext":    (0, 99),
    "whittier_lobby":  (100, 554),
    "whittier_tunnel": (555, 835),
    "coober_desert":   (836, 1092),
    "coober_dugout":   (1093, 1518),
    "setenil_street":  (1519, 1912),
    "setenil_balcony": (1913, 2094),
    "setenil_outro":   (2095, 2282),
}


def clamp01(t: float) -> float:
    return 0.0 if t <= 0.0 else (1.0 if t >= 1.0 else t)


def ease_in_out_expo(t: float) -> float:
    t = clamp01(t)
    if t == 0.0 or t == 1.0:
        return t
    return (2.0 ** (20.0 * t - 10.0)) * 0.5 if t < 0.5 else (2.0 - (2.0 ** (-20.0 * t + 10.0))) * 0.5


def ease_in_out_cubic(t: float) -> float:
    t = clamp01(t)
    return 4.0 * t * t * t if t < 0.5 else 1.0 - ((-2.0 * t + 2.0) ** 3) * 0.5


def ease_out_expo(t: float) -> float:
    t = clamp01(t)
    return 1.0 if t >= 1.0 else 1.0 - (2.0 ** (-10.0 * t))


def ease_out_back(t: float, s: float = 1.1) -> float:
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
# 32 CONTINUOUS 9:16 VERTICAL CAMERA MOVEMENTS (sensor_fit='VERTICAL', 24-28mm!)
# Carefully vertically centered so NO character or hero prop is ever cropped at L/R edges!
# ============================================================================
CAMERA_KEYS: List[Tuple[int, Tuple[float, float, float], Tuple[float, float, float], float, str, bool]] = [
    # --- ACT 0: HOOK — WHITTIER EXTERIOR (0..99) ---
    # M01: Dramatic vertical 9:16 establishing shot showing ALL 14 vertical stories of Begich Towers + Chugach peaks!
    (0,    (-1.4, -18.5, 2.2),  (0.0,  11.0, 12.5), 24.0, "out_expo",     False),
    # M02: Fast dolly-in tilting smoothly down onto shivering Fajar centered below snowy Begich canopy
    (42,   (-0.6,  -3.6, 1.50), (0.0,   4.8,  2.60), 25.0, "in_out_cubic", False),
    # M03: Crisp vertical hero framing on Fajar before pushing glass doors
    (64,   (-0.3,  -1.2, 1.45), (0.1,   4.2,  1.85), 26.0, "out_back",     False),
    # M04: Dynamic push right behind Fajar as both hands push glass lobby doors open!
    (86,   (0.1,    5.2, 1.48), (0.1,  11.4,  1.45), 25.0, "in_out_expo",  False),
    # M05: Smooth pass-through glass threshold into warm 3400K Begich Towers lobby!
    (102,  (0.0,   10.6, 1.50), (0.0,  16.8,  1.42), 25.0, "out_back",     False),

    # --- ACT 1A: BEGICH TOWERS LOBBY, KOZY KORNER & PAK ARTHUR (100..554) ---
    # M06: Vertical glide past 14-Floor Building Directory Board (left)
    (165,  (-0.5,  13.4, 1.55), (-3.0, 17.2,  1.58), 25.0, "in_out_cubic", False),
    # M07: Arc gently right showcasing colorful Kozy Korner minimarket storefront!
    (240,  (0.6,   16.8, 1.55), (3.4,  20.6,  1.48), 25.0, "in_out_cubic", False),
    # M08: Center corridor tracking following Fajar & strolling residents
    (320,  (0.2,   19.6, 1.50), (-1.2, 24.8,  1.40), 25.0, "in_out_cubic", False),
    # M09: Vertical two-shot framing Elevator opening & Pak Arthur stepping out in plaid pajamas!
    (378,  (0.9,   19.6, 1.45), (-2.0, 25.0,  1.30), 25.0, "out_back",     False),
    # M10: Tracking Pak Arthur stepping cleanly to wooden Post Office counter (BOTH Fajar & Arthur centered!)
    (435,  (0.35,  19.4, 1.42), (-1.55, 25.5, 1.28), 24.0, "in_out_cubic", False),
    # M11: Comedic vertical focus on Pak Arthur's sky-blue postal shirt + red-white plaid pajamas + U.S. Post Office!
    (492,  (-0.15, 20.6, 1.32), (-2.25, 26.2, 1.26), 26.0, "out_back",     False),
    # M12: Pull back gently showing Fajar laughing at Pak Arthur's punchline
    (544,  (0.65,  19.8, 1.46), (-1.35, 25.4, 1.34), 24.0, "in_out_cubic", False),

    # --- ACT 1B: WHIP-PAN INTO UNDERGROUND SCHOOL TUNNEL (555..835) ---
    # M13: Snappy whip-pan RIGHT following Maya toward "SCHOOL TUNNEL ->" stairwell!
    (570,  (1.8,   23.4, 1.55), (8.2,  24.0,  0.80), 24.0, "in_out_expo",  False),
    # M14: Diving down concrete stairwell behind jogging Maya
    (618,  (8.8,   23.8, 0.35), (16.5, 24.0, -1.25), 24.0, "in_out_cubic", False),
    # M15: Wide vertical tunnel tracking showcasing yellow-blue concrete vault, pipes & caged neons
    (688,  (17.2,  23.8, -1.00), (25.5, 24.0, -1.05), 24.0, "in_out_cubic", False),
    # M16: Centered 9:16 framing on Maya turning & waving happily in her teal sweater!
    (748,  (24.2,  23.6, -1.05), (29.8, 24.1, -1.08), 26.0, "out_back",     False),
    # M17: Dynamic close tracking of Maya stepping backward toward steel fire-door
    (800,  (29.2,  23.7, -1.10), (34.8, 24.0, -1.12), 25.0, "in_out_cubic", False),
    # M18: Speed-ramp dive through open steel bulkhead door -> match-cut!
    (835,  (40.2,  24.0, -1.15), (44.5, 24.0, -1.15), 20.0, "in_cubic",     False),

    # --- ACT 2A: COOBER PEDY SCORCHING RED OUTBACK DESERT (836..1092) ---
    # M19: Match-cut erupting vertically UP out of white desert ventilation shaft!
    (836,  (100.0,  2.0, 0.90), (100.0,  2.0, 6.80), 22.0, "out_expo",     True),
    # M20: High vertical crane pull-back revealing endless red Outback desert, Nishita sky, mullock heaps & pipes!
    (898,  (95.5,  -8.5, 6.20), (100.2,  8.5, 1.40), 24.0, "out_expo",     False),
    # M21: Sweeping desert tracking past staggered vent pipes & huge rusted "DANGER: OPEN SHAFTS" sign!
    (968,  (98.2,   1.8, 1.95), (100.4, 12.2, 1.50), 25.0, "in_out_cubic", False),
    # M22: Centered 9:16 framing on sweating Fajar fanning his face beside wooden cave door!
    (1032, (99.1,   6.8, 1.48), (100.0, 14.5, 1.45), 26.0, "out_back",     False),
    # M23: Push-in right behind Fajar pushing open heavy timber cave door into cool sandstone dugout!
    (1092, (100.0, 17.6, 1.48), (100.0, 24.5, 1.38), 24.0, "in_out_expo",  False),

    # --- ACT 2B: COOBER PEDY CARVED SANDSTONE DUGOUT & OPAL VEIN (1093..1518) ---
    # M24: Wide reveal glide inside carved sandstone vault as furniture pops in!
    (1168, (98.5,  20.6, 1.55), (100.2, 28.0, 1.35), 24.0, "in_out_cubic", False),
    # M25: Smooth orbit revealing recessed rock bookshelf, copper lamps, vintage fan & tribal rug!
    (1268, (103.6, 23.2, 1.52), (99.4,  28.4, 1.25), 25.0, "in_out_cubic", False),
    # M26: Centered 9:16 portrait on Jack seated relaxed on leather sofa lifting iced tea glass!
    (1372, (99.8,  23.4, 1.38), (98.4,  28.4, 1.10), 26.0, "out_back",     False),
    # M27: Unobstructed vertical hero shot centering Elena aiming LED flashlight & sparkling Opal Vein!
    (1445, (101.4, 24.8, 1.42), (103.6, 29.8, 1.38), 25.0, "in_out_expo",  False),
    # M28: Dramatic push-in straight into shimmering rainbow Opal Crystal flash -> match-cut!
    (1518, (103.4, 29.3, 1.42), (104.8, 30.8, 1.42), 20.0, "in_cubic",     False),

    # --- ACT 3: SETENIL DE LAS BODEGAS — CALLE CUEVAS DEL SOL (1519..2282) ---
    # M29: Match-cut emerging into Spanish Golden Hour alley as cobblestone & white houses build up!
    (1519, (199.2, -3.2, 1.28), (200.4, 10.0, 3.20), 24.0, "out_expo",     True),
    # M30: Low vertical tilt-up capturing the COLOSSAL rock cliff dropping & locking onto white roofs!
    (1585, (199.0,  2.2, 1.15), (200.8, 14.5, 4.40), 24.0, "in_out_cubic", False),
    # M31: Tracking Fajar stepping comically ducked (real 4-phase crouch steps!) beneath 4.5m cliff!
    (1725, (198.4, 10.4, 1.32), (200.6, 18.2, 2.05), 25.0, "in_out_cubic", False),
    # M32: Centered 9:16 two-shot on Bar La Roca terrace: Mateo knocks rock ceiling & serves Fajar!
    (1836, (198.2, 13.4, 1.48), (200.8, 19.2, 1.75), 25.0, "out_back",     False),
    # M33: Smooth vertical crane rise showcasing Pueblos Blancos, green shutters, geranium pots & laundry!
    (1965, (197.2, 18.2, 4.15), (201.8, 23.6, 4.30), 24.0, "in_out_cubic", False),
    # M34: Descending glide onto Mateo offering tapas bread to amazed Fajar
    (2072, (198.4, 14.6, 1.48), (200.8, 19.2, 1.55), 26.0, "out_back",     False),
    # M35: Majestic Golden Hour 9:16 pull-back framing Fajar centered under colossal rock silhouette -> snap loop!
    (2175, (199.5, 11.4, 1.58), (200.2, 19.0, 2.25), 25.0, "in_out_cubic", False),
    (2282, (199.2,  3.8, 2.15), (200.2, 19.0, 3.10), 24.0, "in_out_expo",  False),
]


def get_camera_state(frame: int) -> Tuple[Tuple[float, float, float], Tuple[float, float, float], float]:
    """Evaluate continuous 9:16 vertical camera (location, target, lens_mm) + cliff-drop micro shake!"""
    if frame <= CAMERA_KEYS[0][0]:
        k = CAMERA_KEYS[0]
        pos, tgt, lens = k[1], k[2], k[3]
    elif frame >= CAMERA_KEYS[-1][0]:
        k = CAMERA_KEYS[-1]
        pos, tgt, lens = k[1], k[2], k[3]
    else:
        pos, tgt, lens = CAMERA_KEYS[-1][1], CAMERA_KEYS[-1][2], CAMERA_KEYS[-1][3]
        for i in range(len(CAMERA_KEYS) - 1):
            f0, p0, t0, l0, _, _ = CAMERA_KEYS[i]
            f1, p1, t1, l1, ease_name, hard_cut = CAMERA_KEYS[i + 1]
            if f0 <= frame <= f1:
                if hard_cut:
                    pos, tgt, lens = (p1, t1, l1) if frame >= f1 else (p0, t0, l0)
                else:
                    u = (frame - f0) / max(1.0, float(f1 - f0))
                    if ease_name == "out_expo":
                        e = ease_out_expo(u)
                    elif ease_name == "in_out_expo":
                        e = ease_in_out_expo(u)
                    elif ease_name == "out_back":
                        e = ease_out_back(u, s=0.75)
                    elif ease_name == "in_cubic":
                        e = ease_in_cubic(u)
                    else:
                        e = ease_in_out_cubic(u)
                    pos = lerp3(p0, p1, e)
                    tgt = lerp3(t0, t1, e)
                    lens = lerp(l0, l1, clamp01(e))
                break

    # Subtle organic handheld camera breathing micro-motion
    t_sec = frame / float(FPS)
    bx = math.sin(t_sec * 1.15) * 0.02
    bz = math.cos(t_sec * 1.65) * 0.015

    # Crisp 4-frame micro camera shake right as Setenil's 100-ton rock cliff locks onto roofs (f=1570..1575)!
    if 1570 <= frame <= 1575:
        decay = 1.0 - (frame - 1570) / 6.0
        bx += math.sin(frame * 4.7) * 0.14 * decay
        bz += math.cos(frame * 5.9) * 0.18 * decay

    return (pos[0] + bx, pos[1], pos[2] + bz), tgt, lens


def get_scene_id(frame: int) -> str:
    for sid, (f0, f1) in SCENE_RANGES.items():
        if f0 <= frame <= f1:
            return sid
    return "setenil_outro"


def get_active_location(frame: int) -> str:
    for loc_name, (f0, f1) in LOCATION_RANGES.items():
        if f0 <= frame <= f1:
            return loc_name
    return "LOC_03_Setenil"


def compute_view_angle_deg(
    char_pos: Tuple[float, float, float],
    char_facing_yaw_deg: float,
    cam_pos: Tuple[float, float, float],
) -> float:
    dx = cam_pos[0] - char_pos[0]
    dy = cam_pos[1] - char_pos[1]
    cam_yaw = math.degrees(math.atan2(dx, -dy))
    return (cam_yaw - char_facing_yaw_deg) % 360.0


def _active_speaking(char_name: str, frame: int) -> bool:
    for c in VO_CLIPS:
        if c["char"] == char_name and c["f0"] <= frame <= c["f1"]:
            return True
    return False


# ============================================================================
# DISTANCE-SYNCED CHARACTER CHOREOGRAPHY (ZERO FOOT SLIDING, FULL ACTING!)
# ============================================================================
def get_character_states(frame: int, lipsync_vals: Dict[str, float] | None = None) -> Dict[str, Dict[str, Any]]:
    t = frame / float(FPS)
    cam_pos, _, _ = get_camera_state(frame)
    ls = lipsync_vals or {}
    states: Dict[str, Dict[str, Any]] = {}

    # ------------------------------------------------------------------
    # 1. FAJAR (Host & Narrator across ALL 3 locations!)
    # ------------------------------------------------------------------
    f_mv = ls.get("Fajar", 0.0)
    f_spk = _active_speaking("Fajar", frame)

    if frame <= 99:
        if frame < 58:
            # Shivering visibly in Arctic snowstorm, gesturing excitedly at 14-story Begich Towers!
            fajar_pos = (0.15, 2.4, 0.0)
            fajar_yaw = -8.0
            fajar_rig = build_acting_rig(
                t, mode="shiver_cold", speaking=f_spk, mouth_val=f_mv,
                extra={"eyes": "shocked" if frame < 32 else "honey_oval", "eyebrows": "worried"},
            )
        else:
            # Walking forward with true distance-locked 4-phase steps + reaching hands forward to push glass door!
            u = ease_in_out_cubic((frame - 58) / 41.0)
            dist = u * 9.0  # 2.4m -> 11.4m = 9.0m exact distance!
            fajar_pos = (lerp(0.15, 0.30, u), lerp(2.4, 11.4, u), 0.0)
            fajar_yaw = 180.0
            push_active = 64 <= frame <= 86
            fajar_rig = build_walk_rig(
                distance_m=dist, t=t, stride_m=0.88,
                left_hand_override=(-32.0, 210.0, 58.0) if push_active else None,
                right_hand_override=(44.0, 206.0, 62.0) if push_active else None,
            )
            fajar_rig.update({"eyes": "honey_oval", "eyebrows": "happy"})
    elif frame <= 554:
        if frame < 348:
            u = ease_in_out_cubic((frame - 100) / 248.0)
            dist = u * 12.2
            fajar_pos = (lerp(0.30, 0.35, u), lerp(11.6, 23.8, u), 0.0)
            fajar_yaw = lerp(165.0, -35.0, clamp01((frame - 150) / 198.0))
            fajar_rig = build_walk_rig(distance_m=dist, t=t, stride_m=0.90)
            fajar_rig.update({"eyes": "honey_oval", "eyebrows": "raised" if frame < 260 else "happy"})
        else:
            # Standing cleanly on right-center of vertical frame reacting with comedic surprise to Pak Arthur's pajamas!
            fajar_pos = (-0.65, 24.6, 0.0)
            fajar_yaw = -52.0
            fajar_rig = build_acting_rig(
                t, mode="talk_expressive", speaking=f_spk, mouth_val=f_mv,
                extra={
                    "eyes": "asymmetric" if 435 <= frame <= 515 else "happy",
                    "eyebrows": "skeptical" if 435 <= frame <= 515 else "happy",
                    "mouth": "small_o" if 435 <= frame <= 490 else "happy_open",
                    "eye_gaze_x": -0.45,
                },
            )
    elif frame <= 835:
        if frame < 610:
            u = ease_in_out_cubic((frame - 555) / 55.0)
            dist = u * 5.8
            fajar_pos = (lerp(0.35, 6.2, u), lerp(24.4, 24.4, u), lerp(0.0, -0.4, clamp01((frame - 585) / 25.0)))
            fajar_yaw = 90.0
            fajar_rig = build_walk_rig(distance_m=dist, t=t, stride_m=0.84)
            fajar_rig.update({"eyes": "honey_oval"})
        elif frame < 735:
            u = ease_in_out_cubic((frame - 610) / 125.0)
            dist = 5.8 + u * 15.8
            z_fl = lerp(-0.4, -2.4, clamp01((frame - 610) / 38.0))
            fajar_pos = (lerp(6.2, 22.0, u), 24.4, z_fl)
            fajar_yaw = 84.0
            fajar_rig = build_walk_rig(distance_m=dist, t=t, stride_m=0.86)
            fajar_rig.update({"eyes": "honey_oval", "eyebrows": "happy"})
        else:
            fajar_pos = (22.0, 24.4, -2.4)
            fajar_yaw = 75.0
            fajar_rig = build_acting_rig(t, mode="talk_expressive", speaking=f_spk, mouth_val=f_mv, extra={"eyes": "happy"})
    elif frame <= 1092:
        if frame < 1035:
            # Actively fanning sweaty face in scorching 50°C Coober Pedy desert!
            fajar_pos = (99.6, 12.2, 0.0)
            fajar_yaw = 10.0
            fajar_rig = build_acting_rig(
                t, mode="fan_heat", speaking=f_spk, mouth_val=f_mv,
                extra={"eyes": "panic" if frame < 960 else "focused", "eyebrows": "worried"},
            )
        else:
            # Distance-synced steps + hands reaching forward pushing open heavy wooden cave door!
            u = ease_in_out_cubic((frame - 1035) / 57.0)
            dist = u * 8.4
            fajar_pos = (lerp(99.6, 100.0, u), lerp(12.2, 20.6, u), 0.0)
            fajar_yaw = 180.0
            push_c = 1044 <= frame <= 1074
            fajar_rig = build_walk_rig(
                distance_m=dist, t=t, stride_m=0.86,
                left_hand_override=(-32.0, 212.0, 56.0) if push_c else None,
                right_hand_override=(44.0, 208.0, 62.0) if push_c else None,
            )
            fajar_rig.update({"sweat_drop": frame < 1072, "eyes": "focused"})
    elif frame <= 1518:
        if frame < 1230:
            u = ease_in_out_cubic((frame - 1093) / 137.0)
            dist = u * 5.6
            fajar_pos = (lerp(100.0, 101.2, u), lerp(20.8, 26.2, u), 0.0)
            fajar_yaw = lerp(175.0, -25.0, clamp01((frame - 1140) / 90.0))
            fajar_rig = build_walk_rig(distance_m=dist, t=t, stride_m=0.86)
            fajar_rig.update({"eyes": "happy"})
        else:
            # Step clear to the left during Elena's Opal close-up so Fajar NEVER blocks Elena or the Opal Vein!
            fajar_pos = (99.4, 26.6, 0.0) if frame >= 1415 else (101.0, 26.4, 0.0)
            fajar_yaw = 115.0 if frame > 1420 else -42.0
            is_opal = frame >= 1438
            fajar_rig = build_acting_rig(
                t, mode="talk_expressive", speaking=f_spk, mouth_val=f_mv,
                extra={
                    "eyes": "shocked" if is_opal else "happy",
                    "eyebrows": "raised",
                    "mouth": "small_o" if is_opal else "confident_gap",
                    "eye_gaze_x": 0.55 if is_opal else -0.35,
                },
            )
    elif frame <= 2094:
        if frame < 1815:
            # TRUE 4-PHASE CROUCH WALK (knees lifting & stepping naturally while comically ducked under giant cliff!)
            u = ease_in_out_cubic((frame - 1519) / 296.0)
            dist = u * 13.4
            fajar_pos = (lerp(199.4, 199.5, u), lerp(5.6, 19.0, u), 0.0)
            fajar_yaw = lerp(168.0, 48.0, clamp01((frame - 1710) / 105.0))
            fajar_rig = build_walk_rig(
                distance_m=dist, t=t, stride_m=0.80, crouch_px=18.0,
                left_hand_override=(-48.0, 188.0, 32.0) if frame < 1740 else None,
                right_hand_override=(52.0, 184.0, 34.0) if frame < 1740 else None,
            )
            fajar_rig.update({
                "eyes": "panic" if frame < 1720 else "shocked",
                "eyebrows": "worried",
                "sweat_drop": frame < 1795,
                "eye_gaze_y": -0.85,  # Glancing nervously UP at overhanging rock!
            })
        else:
            # At Bar La Roca terrace tasting tapas & nodding in amazement!
            fajar_pos = (199.5, 19.0, 0.0)
            fajar_yaw = 52.0 if frame < 2015 else 12.0
            fajar_rig = build_acting_rig(
                t, mode="talk_expressive", speaking=f_spk, mouth_val=f_mv,
                extra={
                    "eyes": "starry" if frame >= 2035 else "happy",
                    "eyebrows": "happy",
                    "eye_gaze_y": -0.65 if (2015 <= frame <= 2060) else 0.0,
                },
            )
    else:
        # Outro (2095..2282): Centered in Golden Hour alley -> 3 fingers -> point camera -> shrug & snap!
        fajar_pos = (200.0, 17.5, 0.0)
        fajar_yaw = 0.0
        snap_on = frame >= 2245
        fajar_rig = build_acting_rig(
            t,
            mode="fajar_shrug_snap" if snap_on else "talk_expressive",
            speaking=f_spk, mouth_val=f_mv,
            extra={
                "eyes": "happy" if snap_on else "honey_oval",
                "eyebrows": "raised" if frame >= 2215 else "happy",
                "mouth": "happy_open" if snap_on else "confident_gap",
            },
        )

    states["Fajar"] = {
        "visible": True, "pos": fajar_pos, "yaw": fajar_yaw, "height_m": 1.72,
        "angle": compute_view_angle_deg(fajar_pos, fajar_yaw, cam_pos),
        "rig": fajar_rig,
    }

    # ------------------------------------------------------------------
    # 2. PAK ARTHUR (Whittier Lobby: 4-Phase Walk out of Elevator -> Expressive Postal Acting!)
    # ------------------------------------------------------------------
    arthur_vis = 100 <= frame <= 565
    a_mv = ls.get("Pak Arthur", 0.0)
    a_spk = _active_speaking("Pak Arthur", frame)
    if frame < 368:
        arthur_pos = (-4.5, 25.0, 0.0)
        arthur_yaw = 90.0
        arthur_rig = build_acting_rig(t, mode="arthur_postal", speaking=False, mouth_val=0.0, extra={"eyes": "chill"})
    elif frame < 426:
        # True 4-Phase distance-synced steps exiting elevator while carrying coffee mug & letters!
        u = ease_in_out_cubic((frame - 368) / 58.0)
        arthur_pos = (lerp(-4.5, -2.5, u), lerp(25.0, 26.1, u), 0.0)
        dist = u * math.hypot(2.0, 1.1)  # 2.28m -> ~3 clean relaxed steps!
        arthur_yaw = lerp(90.0, 22.0, u)
        arthur_rig = build_walk_rig(
            distance_m=dist, t=t, stride_m=0.76,
            right_hand_override=(60.0, 224.0, 36.0),  # Carrying steaming WHITTIER mug steadily!
        )
        arthur_rig.update({"eyes": "chill", "eyebrows": "happy", "mouth": "smirk", "prop": "coffee_mug"})
    else:
        arthur_pos = (-2.5, 26.1, 0.0)
        arthur_yaw = 22.0
        arthur_rig = build_acting_rig(
            t, mode="arthur_postal", speaking=a_spk, mouth_val=a_mv,
            extra={"eyes": "happy" if frame >= 480 else "chill", "eyebrows": "happy", "mouth": "smirk"},
        )
    states["Pak Arthur"] = {
        "visible": arthur_vis, "pos": arthur_pos, "yaw": arthur_yaw, "height_m": 1.68,
        "angle": compute_view_angle_deg(arthur_pos, arthur_yaw, cam_pos),
        "rig": arthur_rig,
    }

    # ------------------------------------------------------------------
    # 3. MAYA (Whittier Tunnel: Energetic Jog -> Fluid Backward Steps + Multi-Joint Wave!)
    # ------------------------------------------------------------------
    maya_vis = 530 <= frame <= 835
    m_mv = ls.get("Maya", 0.0)
    m_spk = _active_speaking("Maya", frame)
    if frame < 605:
        u = ease_in_out_cubic(clamp01((frame - 548) / 57.0))
        maya_pos = (lerp(3.2, 11.2, u), 24.0, lerp(0.0, -1.6, clamp01((frame - 575) / 30.0)))
        maya_yaw = 90.0
        maya_rig = build_walk_rig(distance_m=u * 8.2, t=t, stride_m=0.92, jog=True)
        maya_rig.update({"eyes": "happy", "eyebrows": "happy", "mouth": "happy_open"})
    elif frame < 735:
        u = ease_in_out_cubic((frame - 605) / 130.0)
        maya_pos = (lerp(11.2, 28.2, u), 24.1, lerp(-1.6, -2.4, clamp01((frame - 605) / 25.0)))
        maya_yaw = 90.0 if frame < 712 else lerp(90.0, -72.0, (frame - 712) / 23.0)
        maya_rig = build_walk_rig(distance_m=8.2 + u * 17.0, t=t, stride_m=0.84)
        maya_rig.update({"eyes": "happy", "eyebrows": "happy"})
    else:
        # Walking briskly BACKWARD with distance-synced reverse steps while waving joyfully with shoulder & head tilt!
        u = ease_in_out_cubic(clamp01((frame - 735) / 92.0))
        maya_pos = (lerp(28.2, 34.4, u), 24.1, -2.4)
        maya_yaw = -76.0
        w = math.sin(t * 10.5)
        wc = math.cos(t * 10.5)
        maya_rig = build_walk_rig(
            distance_m=u * 6.2, t=t, stride_m=0.76, backward=True,
            right_hand_override=(86.0 + w * 24.0, 128.0 + wc * 14.0, 36.0),
            left_hand_override=(-36.0, 246.0, 30.0),
        )
        maya_rig.update({
            "eyes": "happy", "eyebrows": "happy", "mouth": "happy_open",
            "head_tilt_deg": -9.0 + w * 5.5,
            "torso_lean_deg": -4.0 + w * 3.5,
        })
    states["Maya"] = {
        "visible": maya_vis, "pos": maya_pos, "yaw": maya_yaw, "height_m": 1.56,
        "angle": compute_view_angle_deg(maya_pos, maya_yaw, cam_pos),
        "rig": maya_rig,
    }

    # ------------------------------------------------------------------
    # 4. JACK (Coober Pedy Dugout: True Biomechanical Seated Pose on Leather Sofa!)
    # ------------------------------------------------------------------
    jack_vis = 1090 <= frame <= 1518
    j_mv = ls.get("Jack", 0.0)
    j_spk = _active_speaking("Jack", frame)
    jack_pos = (98.4, 28.12, 0.0)  # Positioned cleanly on front edge of sofa seat so bent knees & boots sit unobstructed on floor!
    jack_yaw = 24.0
    lift_g = clamp01((frame - 1365) / 14.0) * (1.0 - clamp01((frame - 1428) / 12.0)) if 1365 <= frame <= 1440 else 0.0
    jack_rig = build_seated_rig(t, speaking=j_spk, mouth_val=j_mv, lift_glass=lift_g)
    jack_rig.update({
        "eyes": "happy" if j_spk else "chill",
        "eyebrows": "raised" if j_spk else "flat",
        "mouth": "grin_teeth" if j_spk else "smirk",
    })
    states["Jack"] = {
        "visible": jack_vis, "pos": jack_pos, "yaw": jack_yaw, "height_m": 1.72,
        "angle": compute_view_angle_deg(jack_pos, jack_yaw, cam_pos),
        "rig": jack_rig,
    }

    # ------------------------------------------------------------------
    # 5. ELENA (Coober Pedy Dugout: Active LED Flashlight Sweep + Geology Hammer Tap!)
    # ------------------------------------------------------------------
    elena_vis = 1090 <= frame <= 1518
    e_mv = ls.get("Elena", 0.0)
    e_spk = _active_speaking("Elena", frame)
    elena_pos = (103.0, 29.4, 0.0)
    elena_yaw = -34.0 if frame < 1435 else -14.0
    elena_rig = build_acting_rig(
        t, mode="elena_opal", speaking=e_spk, mouth_val=e_mv,
        extra={
            "eyes": "smug" if e_spk else "honey_oval",
            "eyebrows": "raised",
            "mouth": "grin_teeth" if e_spk else "smirk",
        },
    )
    states["Elena"] = {
        "visible": elena_vis, "pos": elena_pos, "yaw": elena_yaw, "height_m": 1.66,
        "angle": compute_view_angle_deg(elena_pos, elena_yaw, cam_pos),
        "rig": elena_rig,
    }

    # ------------------------------------------------------------------
    # 6. MATEO (Setenil Terrace: Serving Tapas -> Knocking Rock Ceiling -> Warm Outro Wave!)
    # ------------------------------------------------------------------
    mateo_vis = 1519 <= frame <= 2282
    ma_mv = ls.get("Mateo", 0.0)
    ma_spk = _active_speaking("Mateo", frame)
    mateo_pos = (201.6, 19.2, 0.0)
    mateo_yaw = -32.0 if frame < 2095 else -16.0
    if 1832 <= frame <= 1878:
        mateo_mode = "mateo_knock"
    elif frame >= 2095:
        mateo_mode = "maya_wave"  # Warm cheerful farewell wave from Bar La Roca terrace!
    else:
        mateo_mode = "mateo_serve"
    mateo_rig = build_acting_rig(
        t, mode=mateo_mode, speaking=ma_spk, mouth_val=ma_mv,
        extra={"eyes": "happy", "eyebrows": "happy", "mouth": "happy_open"},
    )
    states["Mateo"] = {
        "visible": mateo_vis, "pos": mateo_pos, "yaw": mateo_yaw, "height_m": 1.74,
        "angle": compute_view_angle_deg(mateo_pos, mateo_yaw, cam_pos),
        "rig": mateo_rig,
    }

    # ------------------------------------------------------------------
    # LIVING ANIMATED NPCs (100% Distance-Synced 4-Phase Walk & Seated Cafe Acting!)
    # ------------------------------------------------------------------
    if 100 <= frame <= 560:
        u1 = (frame - 100) / 460.0
        p_npc1 = (1.85, lerp(28.5, 13.5, u1), 0.0)
        states["NPC_Whittier_1"] = {
            "visible": True, "pos": p_npc1, "yaw": 0.0, "height_m": 1.66,
            "angle": compute_view_angle_deg(p_npc1, 0.0, cam_pos),
            "rig": {**build_walk_rig(distance_m=u1 * 15.0, t=t, stride_m=0.84), "eyes": "chill"},
        }
        u2 = clamp01(u1 * 1.25)
        p_npc2 = (-1.85, lerp(14.0, 22.0, u2), 0.0)
        npc2_rig = build_walk_rig(distance_m=u2 * 8.0, t=t, stride_m=0.84) if u2 < 0.98 else build_acting_rig(t, mode="talk_expressive")
        states["NPC_Whittier_2"] = {
            "visible": True, "pos": p_npc2, "yaw": 180.0, "height_m": 1.70,
            "angle": compute_view_angle_deg(p_npc2, 180.0, cam_pos),
            "rig": {**npc2_rig, "eyes": "happy"},
        }
    else:
        for nm in ("NPC_Whittier_1", "NPC_Whittier_2"):
            states[nm] = {"visible": False, "pos": (0.0, 20.0, 0.0), "yaw": 0.0, "height_m": 1.66, "angle": 0.0, "rig": {"animation": "free"}}

    if 1519 <= frame <= 2282:
        p_s1 = (201.9, 13.3, 0.0)
        p_s2 = (201.9, 14.7, 0.0)
        cafe_ready = frame >= 1580  # Appear ONLY once wicker café chairs have popped in & locked!
        u3 = (frame - 1519) / 763.0
        p_s3 = (197.4, lerp(26.5, 9.5, u3), 0.0)
        states["NPC_Setenil_1"] = {
            "visible": cafe_ready, "pos": p_s1, "yaw": 165.0, "height_m": 1.64,
            "angle": compute_view_angle_deg(p_s1, 165.0, cam_pos),
            "rig": {**build_seated_rig(t, speaking=True, mouth_val=abs(math.sin(t * 4.8)) * 0.4), "eyes": "happy"},
        }
        states["NPC_Setenil_2"] = {
            "visible": cafe_ready, "pos": p_s2, "yaw": -15.0, "height_m": 1.68,
            "angle": compute_view_angle_deg(p_s2, -15.0, cam_pos),
            "rig": {**build_seated_rig(t + 1.4, speaking=False), "eyes": "happy"},
        }
        # Strolling Setenil pedestrian using TRUE distance-synced 4-phase walk cycle (ZERO sliding!)
        states["NPC_Setenil_3"] = {
            "visible": True, "pos": p_s3, "yaw": 0.0, "height_m": 1.66,
            "angle": compute_view_angle_deg(p_s3, 0.0, cam_pos),
            "rig": {**build_walk_rig(distance_m=u3 * 17.0, t=t, stride_m=0.84), "eyes": "chill"},
        }
    else:
        for nm in ("NPC_Setenil_1", "NPC_Setenil_2", "NPC_Setenil_3"):
            states[nm] = {"visible": False, "pos": (200.0, 15.0, 0.0), "yaw": 0.0, "height_m": 1.66, "angle": 0.0, "rig": {"animation": "free"}}

    return states


# ============================================================================
# DYNAMIC BUILD-UP / ASSEMBLY REVEAL TIMING AT EVERY NEW LOCATION!
# Fast Exponential Ease-Out with Overshoot (8-12 frames per element, 2-3f stagger, Hard Lock!)
# ============================================================================
DYNAMIC_REVEALS = {
    # LOC 1 — Whittier (00:00 - 00:01.8): Mountains pop -> Begich 14 floors -> Canopy, signs, cars, pines!
    "whittier_mtns_popup":   {"start": 0,    "dur": 12, "stagger": 2},
    "begich_tower_arch":     {"start": 6,    "dur": 10, "stagger": 2},
    "whittier_props_snap":   {"start": 24,   "dur": 10, "stagger": 3},
    "lobby_post_assembly":   {"start": 104,  "dur": 12, "stagger": 3},
    "lobby_mart_assembly":   {"start": 122,  "dur": 12, "stagger": 3},
    "tunnel_sign_popup":     {"start": 562,  "dur": 12},
    # LOC 2 — Coober Pedy (00:27.8 - 00:30.0) & Dugout Interior (00:36.5 - 00:38.2)!
    "coober_hill_popup":     {"start": 838,  "dur": 12, "stagger": 3},
    "desert_pipes_wave":     {"start": 846,  "dur": 10, "stagger": 2},
    "danger_sign_popup":     {"start": 874,  "dur": 12},
    "dugout_furniture_asm":  {"start": 1094, "dur": 12, "stagger": 3},
    # LOC 3 — Setenil (00:50.6 - 00:53.2): Cobblestone -> White Houses -> HEAVY CLIFF DROP + SHAKE -> Cafe!
    "setenil_street_build":  {"start": 1520, "dur": 12},
    "setenil_houses_arch":   {"start": 1528, "dur": 12, "stagger": 3},
    "setenil_cliff_drop":    {"start": 1554, "dur": 16, "stagger": 2},  # Locks hard at f=1570 -> 4f camera shake!
    "setenil_cafe_wave":     {"start": 1572, "dur": 10, "stagger": 2},
    "bar_sign_popup":        {"start": 1574, "dur": 12},
}


# ============================================================================
# COMPLETE-SENTENCE PREVIEW REEL SEGMENTS (ZERO TRUNCATED WORDS OR CUT VO!)
# Every single segment starts cleanly before a sentence and ends cleanly after it finishes!
# ============================================================================
PREVIEW_SEGMENTS = [
    ("01_whittier_hook_buildup",  0,    99),  # 3.3s: Complete 01_fajar_hook (6..92) + Begich 14-floor build-up + pushing glass door!
    ("02_arthur_pajama_post",   422,   552),  # 4.3s: Pak Arthur at Post Office counter + complete 03_arthur_dialog (428..547)!
    ("03_maya_tunnel_matchcut", 740,   835),  # 3.2s: Maya reverse-step wave + complete 05_maya_dialog (743..827) + speed-ramp dive!
    ("04_coober_desert_buildup",836,  1092),  # 8.6s: Match-cut pipe burst + complete 06_fajar_coober_intro (841..1087) + desert build-up!
    ("05_dugout_jack_elena",   1363,  1518),  # 5.2s: Complete 08_jack_dialog (1367..1433) + complete 09_elena_dialog (1439..1510) + Opal flash!
    ("06_setenil_cliff_mateo", 1519,  1912),  # 13.1s: Match-cut sunbeam + Setenil build-up + Cliff Drop Shake + complete 10 & 11!
    ("07_setenil_outro_loop",  2092,  2282),  # 6.3s: Complete 13_fajar_outro (2096..2271) + Golden Hour pull-back + snap seamless loop!
]

# Focused Fast-Turnaround QA Review Reel (~31s / 937 frames -> ~5 min on 18 GitHub Actions runners!)
# Showcases ALL 3 evaluation targets: (1) Assembly Animations, (2) 4-Phase Character Walks, (3) Prop Interactions!
QA_SHOWCASE_SEGMENTS = [
    ("01_whittier_buildup_walk_door",  0,    99, "1/9 | ASSEMBLY + WALK + PUSH GLASS DOOR (Whittier)"),
    ("02_arthur_elevator_walk_mug",  368,   548, "2/9 | 4-PHASE WALK + MUG & POST PROPS (Pak Arthur)"),
    ("03_maya_tunnel_reverse_walk",  740,   829, "3/9 | BACKWARD WALK + WAVE (School Tunnel Maya)"),
    ("04_coober_desert_assembly",    838,   892, "4/9 | DESERT ASSEMBLY WAVE (Coober Pedy Pipes)"),
    ("05_fajar_fan_door_dugout_asm",1020,  1142, "5/9 | FAN HEAT + PUSH CAVE DOOR + DUGOUT ASSEMBLY"),
    ("06_jack_seated_elena_opal",   1364,  1512, "6/9 | SEATED MUG LIFT (Jack) + PICKAXE & OPAL (Elena)"),
    ("07_setenil_cliff_drop_asm",   1520,  1602, "7/9 | SETENIL ASSEMBLY + CLIFF DROP LOCK & SHAKE"),
    ("08_setenil_crouch_walk_npc",  1665,  1735, "8/9 | 4-PHASE CROUCH WALK (Fajar) + STROLLING NPC"),
    ("09_mateo_knock_rock_tapas",   1825,  1909, "9/9 | KNOCK ROCK CEILING + TAPAS SERVE (Mateo)"),
]
