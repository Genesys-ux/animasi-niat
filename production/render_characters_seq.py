"""
Frame-Accurate 2.5D Open Free-Rig & Lip-Sync Character Sprite Sequence Renderer.
Uses the Shared Engine (characters/character_engine_25d.py) + all 6 Hero Characters
+ 5 Living Background NPCs, synced 100% to production/timeline_data.py and audio/clips/*.wav.

Usage:
  python production/render_characters_seq.py --start 0 --end 115
  python production/render_characters_seq.py --frames 25,220,445,765,975,1395,1465,1760,1855,2180
"""

from __future__ import annotations

import argparse
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Dict, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CHAR_DIR = PROJECT_ROOT / "characters"
OUT_ROOT = PROJECT_ROOT / "production" / "char_sprites"

sys.path.insert(0, str(CHAR_DIR))
sys.path.insert(0, str(PROJECT_ROOT / "production"))

from character_engine_25d import Character25D, extract_lipsync_curve
from fajar_character import FajarCharacter
from pak_arthur_character import PakArthurCharacter
from maya_character import MayaCharacter
from jack_character import JackCharacter
from elena_character import ElenaCharacter
from mateo_character import MateoCharacter

from timeline_data import FPS, VO_CLIPS, get_character_states

# Clean filesystem slug for every actor
ACTOR_SLUGS = {
    "Fajar": "fajar",
    "Pak Arthur": "pak_arthur",
    "Maya": "maya",
    "Jack": "jack",
    "Elena": "elena",
    "Mateo": "mateo",
    "NPC_Whittier_1": "npc_whittier_1",
    "NPC_Whittier_2": "npc_whittier_2",
    "NPC_Setenil_1": "npc_setenil_1",
    "NPC_Setenil_2": "npc_setenil_2",
    "NPC_Setenil_3": "npc_setenil_3",
}


def build_actor_instances(scale: float = 2.0) -> Dict[str, Any]:
    """Instantiate all 6 hero characters + 5 living background NPCs on Shared Engine."""
    actors: Dict[str, Any] = {
        "Fajar": FajarCharacter(scale=scale, fps=FPS),
        "Pak Arthur": PakArthurCharacter(scale=scale, fps=FPS),
        "Maya": MayaCharacter(scale=scale, fps=FPS),
        "Jack": JackCharacter(scale=scale, fps=FPS),
        "Elena": ElenaCharacter(scale=scale, fps=FPS),
        "Mateo": MateoCharacter(scale=scale, fps=FPS),
    }

    # 5 Consistent Living NPCs (same 2.5D Shared Engine style, unique silhouettes & palettes!)
    npc_configs = {
        "NPC_Whittier_1": {
            "name": "Warga Whittier 1",
            "headShape": "round", "ears": True, "skinColor": "#F4D9C4", "eyes": "chill",
            "eyebrows": "happy", "nose": "upturned_tiny", "mouth": "smirk", "beard": "none",
            "hat": "beanie", "hatPrimary": "#355C7D", "hatAccent": "#F2B644", "backHair": "short",
            "hairColor": "#4A3428", "outfit": "hoodie", "robeColor": "#456990", "innerColor": "#EFECE6",
            "sashColor": "#2C3E50", "trimColor": "#F2B644", "beltStyle": "plain", "cape": "backpack",
            "capeColor": "#2B3D52", "limbColor": "#2C3E50", "pose": "ready", "prop": "none",
        },
        "NPC_Whittier_2": {
            "name": "Warga Whittier 2",
            "headShape": "potato", "ears": True, "skinColor": "#E8BFA0", "eyes": "happy",
            "eyebrows": "happy", "nose": "upturned_tiny", "mouth": "smirk", "beard": "stubble",
            "hat": "cap", "hatPrimary": "#2F5D46", "hatAccent": "#E5B44A", "backHair": "short",
            "hairColor": "#2E2420", "outfit": "plaid_suspenders", "robeColor": "#8F3D38",
            "innerColor": "#3C2D24", "sashColor": "#2C221E", "trimColor": "#E5B44A",
            "beltStyle": "buckle", "cape": "none", "limbColor": "#333A46", "pose": "ready", "prop": "none",
        },
        "NPC_Setenil_1": {
            "name": "Pengunjung Kafe 1",
            "headShape": "chubby_oval", "ears": True, "skinColor": "#E8BA96", "eyes": "happy",
            "eyebrows": "happy", "nose": "upturned_tiny", "mouth": "happy_open", "beard": "none",
            "hat": "beret", "hatPrimary": "#B83B4A", "hatAccent": "#241E28", "backHair": "curly",
            "hairColor": "#3A221A", "outfit": "haori_stripe", "robeColor": "#F5EFE6",
            "innerColor": "#C94452", "sashColor": "#2B2530", "trimColor": "#E5B44A",
            "beltStyle": "plain", "cape": "none", "limbColor": "#38313D", "pose": "ready", "prop": "none",
        },
        "NPC_Setenil_2": {
            "name": "Pengunjung Kafe 2",
            "headShape": "wide", "ears": True, "skinColor": "#DBA47C", "eyes": "chill",
            "eyebrows": "happy", "nose": "upturned_tiny", "mouth": "smirk", "beard": "mustache",
            "hat": "fedora", "hatPrimary": "#C9B08A", "hatAccent": "#6E3B2B", "backHair": "short",
            "hairColor": "#2C221E", "outfit": "suit_tie", "robeColor": "#4A6078",
            "innerColor": "#FAF6EE", "sashColor": "#C44536", "trimColor": "#D9A84A",
            "beltStyle": "buckle", "cape": "none", "limbColor": "#2C3542", "pose": "ready", "prop": "none",
        },
        "NPC_Setenil_3": {
            "name": "Pejalan Setenil",
            "headShape": "tall", "ears": True, "skinColor": "#ECC3A2", "eyes": "honey_oval",
            "eyebrows": "happy", "nose": "upturned_tiny", "mouth": "smirk", "beard": "none",
            "hat": "none", "backHair": "side_part", "hairColor": "#2B1D19", "outfit": "street_varsity",
            "robeColor": "#D97D38", "innerColor": "#FAF4E8", "sashColor": "#2C3E50",
            "trimColor": "#F2C65A", "beltStyle": "plain", "cape": "backpack",
            "capeColor": "#45586C", "limbColor": "#34465C", "pose": "ready", "prop": "none",
        },
    }
    offsets = [0.71, 1.49, 2.15, 2.88, 3.31]
    for idx, (nm, cfg) in enumerate(npc_configs.items()):
        actors[nm] = Character25D(cfg, scale=scale, fps=FPS, default_animation="free", time_offset=offsets[idx])
    return actors


def build_lipsync_tables() -> Dict[str, Dict[int, float]]:
    """Extract frame-accurate lip-sync mouth_open values (0..1) from actual ElevenLabs WAVs."""
    tables: Dict[str, Dict[int, float]] = {}
    for clip in VO_CLIPS:
        wav_path = PROJECT_ROOT / clip["wav"]
        if not wav_path.exists():
            continue
        curve = extract_lipsync_curve(str(wav_path), fps=FPS, smooth=0.30, gain=2.6)
        char = clip["char"]
        f0 = int(clip["f0"])
        tbl = tables.setdefault(char, {})
        for i, val in enumerate(curve):
            tbl[f0 + i] = float(val)
    return tables


def render_frames(frames: List[int], scale: float = 2.0, workers: int = 4) -> None:
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    for slug in ACTOR_SLUGS.values():
        (OUT_ROOT / slug).mkdir(parents=True, exist_ok=True)

    actors = build_actor_instances(scale=scale)
    lipsync = build_lipsync_tables()

    tasks = []
    for f in frames:
        ls_frame = {nm: tbl[f] for nm, tbl in lipsync.items() if f in tbl}
        st_map = get_character_states(f, lipsync_vals=ls_frame)
        for name, st in st_map.items():
            if not st["visible"]:
                continue
            slug = ACTOR_SLUGS[name]
            out_png = OUT_ROOT / slug / f"frame_{f:04d}.png"
            rig = dict(st["rig"])
            if name in ls_frame:
                rig["mouth_open"] = ls_frame[name]
            rig["ground_shadow"] = False
            tasks.append((name, f, float(st["angle"]), rig, out_png))

    print(f"Rendering {len(tasks)} character sprites across {len(frames)} frames (scale={scale}, workers={workers})...")

    def _run_one(item):
        name, f, angle, rig, out_png = item
        actors[name].save_frame(str(out_png), frame=f, fps=FPS, angle=angle, **rig)
        return out_png

    if workers > 1 and len(tasks) > 1:
        with ThreadPoolExecutor(max_workers=workers) as pool:
            done = 0
            for _ in pool.map(_run_one, tasks):
                done += 1
                if done % 150 == 0 or done == len(tasks):
                    print(f"  [Sprites] {done}/{len(tasks)}", flush=True)
    else:
        for i, t_item in enumerate(tasks, 1):
            _run_one(t_item)
            if i % 50 == 0 or i == len(tasks):
                print(f"  [Sprites] {i}/{len(tasks)}", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Render 2.5D Free-Rig character sprites for Blender 3D hybrid pipeline")
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--end", type=int, default=0)
    parser.add_argument("--frames", type=str, default="", help="Comma-separated exact frame list (overrides --start/--end)")
    parser.add_argument("--scale", type=float, default=2.0, help="2.0 = 480x1040 crisp HD sprites")
    parser.add_argument("--workers", type=int, default=min(6, os.cpu_count() or 4))
    args = parser.parse_args()

    if args.frames.strip():
        frame_list = [int(x.strip()) for x in args.frames.split(",") if x.strip()]
    else:
        frame_list = list(range(args.start, args.end + 1))

    render_frames(frame_list, scale=args.scale, workers=args.workers)


if __name__ == "__main__":
    main()
