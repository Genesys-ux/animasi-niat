"""
PakArthurCharacter — Komponen Karakter 2.5D Ringan (Shared Engine • Free-Rig)
Character : Pak Arthur (Petugas Pos Whittier, 60 thn)
Prompt    : Petugas pos Whittier ramah 60 tahun berperut buncit hangat, rambut abu-abu menipis di atas, kumis putih rapi, kacamata baca bulat kawat emas, kemeja dinas pos biru langit berpatch bahu, aksen piyama kotak-kotak merah-putih, sandal cokelat hangat.
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
    "name": "Pak Arthur",
    "prompt": "Petugas pos Whittier 60 tahun, wajah bulat ramah, kumis putih rapi, rambut abu-abu menipis, kacamata bulat emas, seragam pos biru langit dengan patch bahu dan aksen piyama merah-putih",
    "headShape": "pear",
    "ears": True,
    "earPencil": False,
    "skinColor": "#F5DDCB",
    "blushColor": "#E3B2A4",
    "irisColor": "#4A5A6A",
    "eyes": "chill",
    "eyebrows": "happy",
    "nose": "upturned_tiny",
    "mouth": "smirk",
    "beard": "mustache",
    "faceAccessory": "round_glasses",
    "sweatDrop": False,
    "blush": True,
    "angerVein": False,
    "eyeGazeX": 0,
    "eyeGazeY": 0,
    "hat": "none",
    "hatPrimary": "#4C8CC4",
    "hatAccent": "#E5B84B",
    "hatTilt": 0,
    "hatLiftY": 0,
    "loupeOpen": False,
    "backHair": "short",
    "hairColor": "#C4CAD2",
    "outfit": "royal_uniform",
    "robeColor": "#5392C7",
    "innerColor": "#F5EFE6",
    "sashColor": "#3A4B63",
    "trimColor": "#E6BD54",
    "beltStyle": "buckle",
    "cape": "none",
    "capeColor": "#5392C7",
    "emblem": "none",
    "pose": "akimbo",
    "prop": "none",
    "limbColor": "#A63232",
    "groundShadow": True,
    "outlineShadow": 1.35,
    "outlineLit": 1,
    "rimIntensity": 0.45,
    "shadowDepth": 1.5,
    "customLayers": [
        # Celana piyama flanel kotak-kotak merah-putih (360° wrap di bagian bawah pinggang!)
        {"layer": "torso", "type": "rect", "x": 42, "y": 282, "w": 136, "h": 54, "radius": 0, "fill": "#C93838", "stroke": "#1E1520", "lineWidth": 2.2},
        {"layer": "torso", "type": "rect", "x": 42, "y": 294, "w": 136, "h": 5, "radius": 0, "fill": "#F7F1E8", "opacity": 0.88},
        {"layer": "torso", "type": "rect", "x": 42, "y": 310, "w": 136, "h": 5, "radius": 0, "fill": "#F7F1E8", "opacity": 0.88},
        {"layer": "torso", "type": "rect", "x": 42, "y": 324, "w": 136, "h": 4, "radius": 0, "fill": "#7A1D22", "opacity": 0.55},
        {"layer": "torso", "type": "rect", "x": 62, "y": 282, "w": 5, "h": 54, "radius": 0, "fill": "#F7F1E8", "opacity": 0.82},
        {"layer": "torso", "type": "rect", "x": 86, "y": 282, "w": 5, "h": 54, "radius": 0, "fill": "#F7F1E8", "opacity": 0.82},
        {"layer": "torso", "type": "rect", "x": 110, "y": 282, "w": 5, "h": 54, "radius": 0, "fill": "#F7F1E8", "opacity": 0.82},
        {"layer": "torso", "type": "rect", "x": 134, "y": 282, "w": 5, "h": 54, "radius": 0, "fill": "#F7F1E8", "opacity": 0.82},
        {"layer": "torso", "type": "rect", "x": 156, "y": 282, "w": 5, "h": 54, "radius": 0, "fill": "#F7F1E8", "opacity": 0.82},
        {"layer": "torso", "type": "rect", "x": 74, "y": 282, "w": 4, "h": 54, "radius": 0, "fill": "#6B1A20", "opacity": 0.42},
        {"layer": "torso", "type": "rect", "x": 98, "y": 282, "w": 4, "h": 54, "radius": 0, "fill": "#6B1A20", "opacity": 0.42},
        {"layer": "torso", "type": "rect", "x": 122, "y": 282, "w": 4, "h": 54, "radius": 0, "fill": "#6B1A20", "opacity": 0.42},
        {"layer": "torso", "type": "rect", "x": 146, "y": 282, "w": 4, "h": 54, "radius": 0, "fill": "#6B1A20", "opacity": 0.42},
    ],
}


class PakArthurCharacter(BaseCharacter25D):
    """Karakter 2.5D Pak Arthur (Petugas Pos Whittier) — Open Free-Rig, Layered IK, 360° Turntable."""

    DEFAULT_CONFIG: Dict[str, Any] = CHARACTER_CONFIG
    DEFAULT_ANIMATION = "free"
    DEFAULT_ANGLE: float = 0.0
    DEFAULT_FPS: int = 30
    DEFAULT_SCALE: float = 3.0
    DEFAULT_TIME_OFFSET: float = 1.18


def render_demo_scene(output_path: str = "demo_pak_arthur.mp4", width: int = 720, height: int = 1280, fps: int = 30, scale: float = 2.5, audio_path: str | None = None) -> str:
    return render_character_demo(PakArthurCharacter, output_path=output_path, width=width, height=height, fps=fps, scale=scale, audio_path=audio_path)


if __name__ == "__main__":
    run_character_cli(PakArthurCharacter)
