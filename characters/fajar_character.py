"""
FajarCharacter — Komponen Karakter 2.5D Ringan (Shared Engine • Free-Rig)
Character : Fajar (Host & Penjelajah, 23 thn)
Prompt    : Host penjelajah muda kulit sawo matang cerah, rambut acak rapi, parka modular merah bata berkantong dengan kaus dalam kuning mustard, celana kargo abu arang, tas punggung/gear petualang, ekspresi antusias mata besar.
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
    "name": "Fajar",
    "prompt": "Host penjelajah muda 23 tahun, kulit sawo matang cerah, rambut acak rapi, parka merah bata dengan kaus kuning mustard, celana kargo abu arang, ekspresi antusias",
    "headShape": "chubby_oval",
    "ears": True,
    "earPencil": False,
    "skinColor": "#DFA97E",
    "blushColor": "#C48466",
    "irisColor": "#5E381E",
    "eyes": "honey_oval",
    "eyebrows": "thick_arch",
    "nose": "upturned_tiny",
    "mouth": "confident_gap",
    "beard": "none",
    "faceAccessory": "none",
    "sweatDrop": False,
    "blush": True,
    "angerVein": False,
    "eyeGazeX": 0,
    "eyeGazeY": 0,
    "hat": "none",
    "hatPrimary": "#363A42",
    "hatAccent": "#E5B238",
    "hatTilt": 0,
    "hatLiftY": 0,
    "loupeOpen": False,
    "backHair": "windswept_bolt",
    "hairColor": "#231B1E",
    "outfit": "safari_explorer",
    "robeColor": "#B84430",
    "innerColor": "#363A42",
    "sashColor": "#D99F2B",
    "trimColor": "#F0E2C8",
    "beltStyle": "utility_belt",
    "cape": "backpack",
    "capeColor": "#363A42",
    "emblem": "none",
    "pose": "point",
    "prop": "none",
    "limbColor": "#363A42",
    "groundShadow": True,
    "outlineShadow": 1.35,
    "outlineLit": 1,
    "rimIntensity": 0.45,
    "shadowDepth": 1.5,
    "customLayers": [],
}


class FajarCharacter(BaseCharacter25D):
    """Karakter 2.5D Fajar (Host & Penjelajah) — Open Free-Rig, Layered IK, 360° Turntable."""

    DEFAULT_CONFIG: Dict[str, Any] = CHARACTER_CONFIG
    DEFAULT_ANIMATION = "free"
    DEFAULT_ANGLE: float = 0.0
    DEFAULT_FPS: int = 30
    DEFAULT_SCALE: float = 3.0
    DEFAULT_TIME_OFFSET: float = 0.42


def render_demo_scene(output_path: str = "demo_fajar.mp4", width: int = 720, height: int = 1280, fps: int = 30, scale: float = 2.5, audio_path: str | None = None) -> str:
    return render_character_demo(FajarCharacter, output_path=output_path, width=width, height=height, fps=fps, scale=scale, audio_path=audio_path)


if __name__ == "__main__":
    run_character_cli(FajarCharacter)
