"""
ElenaCharacter — Komponen Karakter 2.5D Ringan (Shared Engine • Free-Rig)
Character : Elena (Warga & Pemandu Rumah Dugout Coober Pedy, 35 thn)
Prompt    : Pemilik rumah dugout Coober Pedy 35 tahun, wajah tirus tegas, mata ingin tahu, rambut cokelat ikal diikat bandana oranye tembaga, kaus katun krem, rompi utilitas hijau zaitun berkantong banyak, celana kargo cokelat pasir.
Requires  : character_engine_25d.py (simpan 1x di folder proyek yang sama)
"""

from __future__ import annotations

from typing import Any, Dict

from character_engine_25d import (
    BaseCharacter25D,
    Easing,
    StoryboardScene,
    Vec3,
    extract_lipsync_curve,
    interpolate,
    render_character_demo,
    run_character_cli,
    spring,
)

CHARACTER_CONFIG: Dict[str, Any] = {
    "name": "Elena",
    "prompt": "Pemandu rumah dugout Coober Pedy 35 tahun, wajah tirus tegas, rambut cokelat ikal diikat bandana oranye tembaga, kaus krem, rompi utilitas hijau zaitun berkantong banyak, celana kargo cokelat pasir",
    "headShape": "tall",
    "ears": True,
    "earPencil": False,
    "skinColor": "#E9BE9A",
    "blushColor": "#CE927B",
    "irisColor": "#5B3C22",
    "eyes": "honey_oval",
    "eyebrows": "raised",
    "nose": "upturned_tiny",
    "mouth": "smirk",
    "beard": "none",
    "faceAccessory": "none",
    "sweatDrop": False,
    "blush": False,
    "angerVein": False,
    "eyeGazeX": 0,
    "eyeGazeY": 0,
    "hat": "none",
    "hatPrimary": "#D66B2B",
    "hatAccent": "#F2C763",
    "hatTilt": 0,
    "hatLiftY": 0,
    "loupeOpen": False,
    "backHair": "curly",
    "hairColor": "#4A2D1F",
    "outfit": "tactical_vest",
    "robeColor": "#4F633E",
    "innerColor": "#EFE2C8",
    "sashColor": "#8C6C49",
    "trimColor": "#D66B2B",
    "beltStyle": "utility_belt",
    "cape": "none",
    "capeColor": "#4F633E",
    "emblem": "none",
    "pose": "heroic",
    "prop": "none",
    "limbColor": "#6B523B",
    "groundShadow": True,
    "outlineShadow": 1.35,
    "outlineLit": 1,
    "rimIntensity": 0.45,
    "shadowDepth": 1.5,
    "customLayers": [
        # Bandana motif geometris oranye tembaga (360° wrap jelas di bawah rambut ikal!)
        {"layer": "head", "type": "rect", "x": 36, "y": 105, "w": 138, "h": 11, "radius": 3, "fill": "#D66B2B", "stroke": "#1E1520", "lineWidth": 2.2},
        {"layer": "head", "type": "circle", "x": 58, "y": 110.5, "r": 2.6, "fill": "#F7CE70"},
        {"layer": "head", "type": "circle", "x": 76, "y": 110.5, "r": 2.6, "fill": "#F7CE70"},
        {"layer": "head", "type": "circle", "x": 94, "y": 110.5, "r": 2.6, "fill": "#F7CE70"},
        {"layer": "head", "type": "circle", "x": 112, "y": 110.5, "r": 2.6, "fill": "#F7CE70"},
        {"layer": "head", "type": "circle", "x": 130, "y": 110.5, "r": 2.6, "fill": "#F7CE70"},
        {"layer": "head", "type": "circle", "x": 148, "y": 110.5, "r": 2.6, "fill": "#F7CE70"},
    ],
}


class ElenaCharacter(BaseCharacter25D):
    """Karakter 2.5D Elena (Pemandu Dugout Coober Pedy) — Open Free-Rig, Layered IK, 360° Turntable."""

    DEFAULT_CONFIG: Dict[str, Any] = CHARACTER_CONFIG
    DEFAULT_ANIMATION = "free"
    DEFAULT_ANGLE: float = 0.0
    DEFAULT_FPS: int = 30
    DEFAULT_SCALE: float = 3.0
    DEFAULT_TIME_OFFSET: float = 3.12


def render_demo_scene(output_path: str = "demo_elena.mp4", width: int = 720, height: int = 1280, fps: int = 30, scale: float = 2.5, audio_path: str | None = None) -> str:
    return render_character_demo(ElenaCharacter, output_path=output_path, width=width, height=height, fps=fps, scale=scale, audio_path=audio_path)


if __name__ == "__main__":
    run_character_cli(ElenaCharacter)
