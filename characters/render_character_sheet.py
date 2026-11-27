"""Render high-resolution preview portraits & full-cast lineup/turnaround sheets for all 6 characters."""

from __future__ import annotations

import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

CHAR_DIR = Path(__file__).resolve().parent
PREV_DIR = CHAR_DIR / "previews"
PREV_DIR.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(CHAR_DIR))

from fajar_character import FajarCharacter
from pak_arthur_character import PakArthurCharacter
from maya_character import MayaCharacter
from jack_character import JackCharacter
from elena_character import ElenaCharacter
from mateo_character import MateoCharacter

CAST = [
    ("fajar", "Fajar (23)", "Host / Penjelajah • Semua Lokasi", FajarCharacter, (184, 68, 48)),
    ("pak_arthur", "Pak Arthur (60)", "Petugas Pos • Whittier, Alaska", PakArthurCharacter, (83, 146, 199)),
    ("maya", "Maya (17)", "Pelajar Terowongan • Whittier", MayaCharacter, (75, 192, 181)),
    ("jack", "Jack (44)", "Penambang Opal • Coober Pedy", JackCharacter, (186, 150, 102)),
    ("elena", "Elena (35)", "Pemandu Dugout • Coober Pedy", ElenaCharacter, (79, 99, 62)),
    ("mateo", "Mateo (48)", "Pemilik Kedai Tapas • Setenil", MateoCharacter, (31, 53, 92)),
]


def load_font(size: int, bold: bool = False):
    candidates = [
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
    ]
    for p in candidates:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def main() -> None:
    font_title = load_font(44, bold=True)
    font_sub = load_font(22, bold=False)
    font_name = load_font(28, bold=True)
    font_role = load_font(18, bold=False)
    font_tag = load_font(16, bold=True)

    # 1) Full Cast Lineup Sheet (6 characters side by side at 3/4 dynamic angle)
    card_w, card_h = 420, 760
    pad = 24
    header_h = 115
    lineup_w = pad + len(CAST) * (card_w + pad)
    lineup_h = header_h + card_h + pad
    lineup = Image.new("RGBA", (lineup_w, lineup_h), (242, 238, 231, 255))
    draw = ImageDraw.Draw(lineup)

    # Subtle studio header band
    draw.rectangle([0, 0, lineup_w, header_h - 10], fill=(24, 21, 34, 255))
    draw.text((34, 18), "CAST LINEUP — 6 KARAKTER 2.5D (Shared Engine & Free-Rig)", fill=(248, 245, 252, 255), font=font_title)
    draw.text((34, 72), "Whittier (Alaska)  •  Coober Pedy (Australia)  •  Setenil de las Bodegas (Spanyol)", fill=(176, 188, 210, 255), font=font_sub)

    # 2) Turnaround Sheet (2 cols x 3 rows, each showing Front 0° + 3/4 38° + Back 180°)
    cell_w, cell_h = 1040, 560
    t_pad = 22
    t_w = t_pad + 2 * (cell_w + t_pad)
    t_h = header_h + 3 * (cell_h + t_pad)
    turnaround = Image.new("RGBA", (t_w, t_h), (240, 236, 229, 255))
    tdraw = ImageDraw.Draw(turnaround)
    tdraw.rectangle([0, 0, t_w, header_h - 10], fill=(24, 21, 34, 255))
    tdraw.text((34, 18), "360° TURNAROUND SHEET — DEPAN (0°)  •  3/4 (38°)  •  BELAKANG (180°)", fill=(248, 245, 252, 255), font=font_title)
    tdraw.text((34, 72), "Seluruh karakter menggunakan Shared Engine (character_engine_25d.py) & Open Free-Rig 2-Bone IK", fill=(176, 188, 210, 255), font=font_sub)

    for idx, (slug, name, role, cls, accent) in enumerate(CAST):
        print(f"Rendering {name}...")
        char = cls(scale=2.5, fps=30)

        img_front = char.render_pil(frame=0, angle=0, animation="free")
        img_34 = char.render_pil(frame=8, angle=38, animation="free")
        img_back = char.render_pil(frame=0, angle=180, animation="free")

        img_front.save(PREV_DIR / f"{slug}_front.png")
        img_34.save(PREV_DIR / f"{slug}_34.png")
        img_back.save(PREV_DIR / f"{slug}_back.png")

        # Paste onto Lineup Card
        cx0 = pad + idx * (card_w + pad)
        cy0 = header_h
        draw.rounded_rectangle([cx0, cy0, cx0 + card_w, cy0 + card_h], radius=22, fill=(252, 250, 246, 255), outline=(212, 205, 194, 255), width=2)
        draw.rounded_rectangle([cx0, cy0, cx0 + card_w, cy0 + 12], radius=6, fill=(*accent, 255))

        # Fit 3/4 sprite into card
        sprite = img_34.copy()
        sprite.thumbnail((card_w - 30, card_h - 125), Image.Resampling.LANCZOS)
        sx = cx0 + (card_w - sprite.width) // 2
        sy = cy0 + 20 + (card_h - 135 - sprite.height) // 2
        lineup.alpha_composite(sprite, (sx, sy))

        # Label footer
        draw.line([cx0 + 20, cy0 + card_h - 92, cx0 + card_w - 20, cy0 + card_h - 92], fill=(224, 218, 208, 255), width=2)
        draw.text((cx0 + 22, cy0 + card_h - 82), name, fill=(28, 24, 34, 255), font=font_name)
        draw.text((cx0 + 22, cy0 + card_h - 46), role, fill=(100, 94, 110, 255), font=font_role)

        # Paste onto Turnaround Cell
        col = idx % 2
        row = idx // 2
        tx0 = t_pad + col * (cell_w + t_pad)
        ty0 = header_h + row * (cell_h + t_pad)
        tdraw.rounded_rectangle([tx0, ty0, tx0 + cell_w, ty0 + cell_h], radius=20, fill=(252, 250, 246, 255), outline=(212, 205, 194, 255), width=2)
        tdraw.rounded_rectangle([tx0, ty0, tx0 + 14, ty0 + cell_h], radius=6, fill=(*accent, 255))
        tdraw.text((tx0 + 30, ty0 + 16), f"{name}  —  {role}", fill=(28, 24, 34, 255), font=font_name)

        views = [("Depan 0°", img_front), ("3/4 38°", img_34), ("Belakang 180°", img_back)]
        slot_w = (cell_w - 50) // 3
        for v_i, (v_label, v_img) in enumerate(views):
            sp = v_img.copy()
            sp.thumbnail((slot_w - 14, cell_h - 105), Image.Resampling.LANCZOS)
            vx = tx0 + 26 + v_i * slot_w + (slot_w - sp.width) // 2
            vy = ty0 + 58 + (cell_h - 105 - sp.height) // 2
            turnaround.alpha_composite(sp, (vx, vy))
            tdraw.text((tx0 + 26 + v_i * slot_w + slot_w // 2 - 42, ty0 + cell_h - 34), v_label, fill=(110, 104, 120, 255), font=font_tag)

    lineup_path = CHAR_DIR / "cast_lineup_sheet.png"
    turnaround_path = CHAR_DIR / "cast_turnaround_sheet.png"
    lineup.convert("RGB").save(lineup_path, quality=95)
    turnaround.convert("RGB").save(turnaround_path, quality=95)
    print(f"Saved: {lineup_path}")
    print(f"Saved: {turnaround_path}")


if __name__ == "__main__":
    main()
