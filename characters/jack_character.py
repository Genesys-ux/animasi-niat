"""
JackCharacter — Komponen Karakter 2.5D Ringan (Shared Engine • Free-Rig)
Character : Jack (Penambang Opal Coober Pedy, 44 thn)
Prompt    : Penambang opal Outback Australia 44 tahun, kulit kecokelatan terpanggang matahari, rahang kokoh berjanggut pendek, topi kulit lebar Akubra, kemeja kerja khaki gurun, sabuk kulit pelat kuningan, celana kerja denim pudar.
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
    "name": "Jack",
    "prompt": "Penambang opal Coober Pedy Australia 44 tahun, kulit kecokelatan gurun, rahang kokoh janggut pendek, topi kulit lebar Akubra, kemeja khaki gurun, ikat pinggang kulit kuningan, celana denim pudar",
    "headShape": "wide",
    "ears": True,
    "earPencil": False,
    "skinColor": "#D5996D",
    "blushColor": "#B57452",
    "irisColor": "#463529",
    "eyes": "chill",
    "eyebrows": "flat",
    "nose": "upturned_tiny",
    "mouth": "smirk",
    "beard": "stubble",
    "faceAccessory": "none",
    "sweatDrop": False,
    "blush": False,
    "angerVein": False,
    "eyeGazeX": 0,
    "eyeGazeY": 0,
    "hat": "cowboy",
    "hatPrimary": "#6E4226",
    "hatAccent": "#C99442",
    "hatTilt": -4,
    "hatLiftY": 0,
    "loupeOpen": False,
    "backHair": "short",
    "hairColor": "#3A271C",
    "outfit": "vest_western",
    "robeColor": "#BA9666",
    "innerColor": "#EADAC0",
    "sashColor": "#8C3D2B",
    "trimColor": "#D9A844",
    "beltStyle": "buckle",
    "cape": "none",
    "capeColor": "#6E4226",
    "emblem": "none",
    "pose": "ready",
    "prop": "none",
    "limbColor": "#2C4563",
    "groundShadow": True,
    "outlineShadow": 1.35,
    "outlineLit": 1,
    "rimIntensity": 0.45,
    "shadowDepth": 1.5,
    "customLayers": [],
}


class JackCharacter(BaseCharacter25D):
    """Karakter 2.5D Jack (Penambang Opal Coober Pedy) — Open Free-Rig, Layered IK, 360° Turntable."""

    DEFAULT_CONFIG: Dict[str, Any] = CHARACTER_CONFIG
    DEFAULT_ANIMATION = "free"
    DEFAULT_ANGLE: float = 0.0
    DEFAULT_FPS: int = 30
    DEFAULT_SCALE: float = 3.0
    DEFAULT_TIME_OFFSET: float = 2.63


def render_demo_scene(output_path: str = "demo_jack.mp4", width: int = 720, height: int = 1280, fps: int = 30, scale: float = 2.5, audio_path: str | None = None) -> str:
    return render_character_demo(JackCharacter, output_path=output_path, width=width, height=height, fps=fps, scale=scale, audio_path=audio_path)


if __name__ == "__main__":
    run_character_cli(JackCharacter)
