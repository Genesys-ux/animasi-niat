"""
MateoCharacter — Komponen Karakter 2.5D Ringan (Shared Engine • Free-Rig)
Character : Mateo (Pemilik Kedai Tapas Setenil, 48 thn)
Prompt    : Pemilik kedai tapas Andalusia 48 tahun, bahu lebar, kulit hangat kecokelatan, kumis hitam tebal melengkung, rambut hitam bergelombang disisir rapi, kemeja linen putih bersih, celemek twill biru dongker panjang, aksen merah anggur.
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
    "name": "Mateo",
    "prompt": "Pemilik kedai tapas Setenil Spanyol 48 tahun, bahu lebar, kulit hangat Andalusia, kumis hitam tebal melengkung, rambut hitam disisir rapi, kemeja linen putih bersih, celemek biru dongker panjang",
    "headShape": "wide",
    "ears": True,
    "earPencil": False,
    "skinColor": "#DDA67D",
    "blushColor": "#C47E68",
    "irisColor": "#33221A",
    "eyes": "happy",
    "eyebrows": "happy",
    "nose": "upturned_tiny",
    "mouth": "happy_open",
    "beard": "handlebar",
    "faceAccessory": "none",
    "sweatDrop": False,
    "blush": True,
    "angerVein": False,
    "eyeGazeX": 0,
    "eyeGazeY": 0,
    "hat": "none",
    "hatPrimary": "#1F355C",
    "hatAccent": "#7D2434",
    "hatTilt": 0,
    "hatLiftY": 0,
    "loupeOpen": False,
    "backHair": "side_part",
    "hairColor": "#1C181F",
    "outfit": "chef_apron",
    "robeColor": "#F6F5F0",
    "innerColor": "#1F355C",
    "sashColor": "#7D2434",
    "trimColor": "#D9A84A",
    "beltStyle": "knot",
    "cape": "none",
    "capeColor": "#7D2434",
    "emblem": "none",
    "pose": "wave",
    "prop": "none",
    "limbColor": "#2C2420",
    "groundShadow": True,
    "outlineShadow": 1.35,
    "outlineLit": 1,
    "rimIntensity": 0.45,
    "shadowDepth": 1.5,
    "customLayers": [],
}


class MateoCharacter(BaseCharacter25D):
    """Karakter 2.5D Mateo (Pemilik Kedai Tapas Setenil) — Open Free-Rig, Layered IK, 360° Turntable."""

    DEFAULT_CONFIG: Dict[str, Any] = CHARACTER_CONFIG
    DEFAULT_ANIMATION = "free"
    DEFAULT_ANGLE: float = 0.0
    DEFAULT_FPS: int = 30
    DEFAULT_SCALE: float = 3.0
    DEFAULT_TIME_OFFSET: float = 3.55


def render_demo_scene(output_path: str = "demo_mateo.mp4", width: int = 720, height: int = 1280, fps: int = 30, scale: float = 2.5, audio_path: str | None = None) -> str:
    return render_character_demo(MateoCharacter, output_path=output_path, width=width, height=height, fps=fps, scale=scale, audio_path=audio_path)


if __name__ == "__main__":
    run_character_cli(MateoCharacter)
