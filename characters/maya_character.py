"""
MayaCharacter — Komponen Karakter 2.5D Ringan (Shared Engine • Free-Rig)
Character : Maya (Pelajar Terowongan Whittier, 17 thn)
Prompt    : Pelajar remaja cerah 17 tahun, pipi merona alami, mata berbinar energik, rambut cokelat gelap panjang/kepang, sweater rajut toska muda, celana jin biru terang, ransel sekolah penuh pin enamel, sepatu kets putih-merah.
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
    "name": "Maya",
    "prompt": "Pelajar remaja 17 tahun Whittier, wajah cerah merona, mata berbinar, rambut cokelat gelap kepang, sweater toska muda, denim biru terang, ransel sekolah penuh pin",
    "headShape": "round",
    "ears": True,
    "earPencil": False,
    "skinColor": "#FCE9DC",
    "blushColor": "#F0A8AD",
    "irisColor": "#5C3820",
    "eyes": "honey_oval",
    "eyebrows": "happy",
    "nose": "upturned_tiny",
    "mouth": "happy_open",
    "beard": "none",
    "faceAccessory": "none",
    "sweatDrop": False,
    "blush": True,
    "angerVein": False,
    "eyeGazeX": 0,
    "eyeGazeY": 0,
    "hat": "none",
    "hatPrimary": "#4BC0B5",
    "hatAccent": "#E04E4E",
    "hatTilt": 0,
    "hatLiftY": 0,
    "loupeOpen": False,
    "backHair": "long_flow",
    "hairColor": "#3B231A",
    "outfit": "hoodie",
    "robeColor": "#4BC0B5",
    "innerColor": "#F6F8FA",
    "sashColor": "#3B6EA8",
    "trimColor": "#E04E4E",
    "beltStyle": "plain",
    "cape": "backpack",
    "capeColor": "#C84B45",
    "emblem": "star",
    "pose": "wave",
    "prop": "none",
    "limbColor": "#3B6EA8",
    "groundShadow": True,
    "outlineShadow": 1.35,
    "outlineLit": 1,
    "rimIntensity": 0.45,
    "shadowDepth": 1.5,
    "customLayers": [
        # Poni remaja bervolume & lembut di dahi + pelipis (clipped ke kepala 360°)
        {"layer": "head", "type": "ellipse", "x": 104, "y": 89, "rx": 74, "ry": 31, "fill": "#3B231A", "stroke": "#1B1218", "lineWidth": 2.5},
        {"layer": "head", "type": "ellipse", "x": 62, "y": 110, "rx": 28, "ry": 17, "rot": -0.28, "fill": "#3B231A", "stroke": "#1B1218", "lineWidth": 2.0},
        {"layer": "head", "type": "ellipse", "x": 144, "y": 109, "rx": 28, "ry": 17, "rot": 0.25, "fill": "#3B231A", "stroke": "#1B1218", "lineWidth": 2.0},
        {"layer": "head", "type": "ellipse", "x": 94, "y": 104, "rx": 24, "ry": 12, "rot": -0.10, "fill": "#3B231A"},
        {"layer": "head", "type": "ellipse", "x": 118, "y": 86, "rx": 28, "ry": 6.5, "rot": 0.08, "fill": "#6E4636", "opacity": 0.56},
        {"layer": "head", "type": "rect", "x": 52, "y": 106, "w": 12, "h": 4.5, "radius": 2, "fill": "#E04E4E", "stroke": "#1B1218", "lineWidth": 1.3},
    ],
}


class MayaCharacter(BaseCharacter25D):
    """Karakter 2.5D Maya (Pelajar Whittier) — Open Free-Rig, Layered IK, 360° Turntable."""

    DEFAULT_CONFIG: Dict[str, Any] = CHARACTER_CONFIG
    DEFAULT_ANIMATION = "free"
    DEFAULT_ANGLE: float = 0.0
    DEFAULT_FPS: int = 30
    DEFAULT_SCALE: float = 3.0
    DEFAULT_TIME_OFFSET: float = 1.94


def render_demo_scene(output_path: str = "demo_maya.mp4", width: int = 720, height: int = 1280, fps: int = 30, scale: float = 2.5, audio_path: str | None = None) -> str:
    return render_character_demo(MayaCharacter, output_path=output_path, width=width, height=height, fps=fps, scale=scale, audio_path=audio_path)


if __name__ == "__main__":
    run_character_cli(MayaCharacter)
