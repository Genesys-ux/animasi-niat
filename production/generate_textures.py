"""Generate crisp, real-world-referenced signage PNG textures using system Python + Pillow."""

from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

TEX_DIR = Path(__file__).resolve().parent / "textures"
TEX_DIR.mkdir(parents=True, exist_ok=True)


def _load_font(size: int, bold: bool = True):
    candidates = [
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]
    for p in candidates:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def main() -> None:
    def save_sign(slug: str, img: Image.Image) -> None:
        p = TEX_DIR / f"{slug}.png"
        img.save(p)
        print(f"Generated {p.name}")

    # 1. Begich Towers Exterior Plaque
    im = Image.new("RGB", (1024, 256), (38, 56, 82))
    d = ImageDraw.Draw(im)
    d.rectangle([10, 10, 1014, 246], outline=(218, 196, 146), width=8)
    d.text((70, 48), "BEGICH TOWERS CONDOMINIUM", fill=(244, 238, 224), font=_load_font(54, True))
    d.text((195, 138), "WHITTIER, ALASKA  •  EST. 1957  •  14 FLOORS", fill=(214, 194, 152), font=_load_font(30, False))
    save_sign("sign_begich_ext", im)

    # 2. Begich Towers 14-Floor Directory Board
    im = Image.new("RGB", (640, 880), (26, 30, 38))
    d = ImageDraw.Draw(im)
    d.rectangle([14, 14, 626, 866], outline=(196, 162, 92), width=10)
    d.rectangle([28, 28, 612, 128], fill=(46, 76, 112))
    d.text((54, 48), "BEGICH TOWERS", fill=(250, 245, 232), font=_load_font(44, True))
    d.text((130, 96), "CITY UNDER ONE ROOF", fill=(235, 206, 130), font=_load_font(22, True))
    rows = [
        ("FL 1",    "U.S. POST OFFICE & LOBBY"),
        ("FL 1",    "KOZY KORNER GROCERY"),
        ("FL 1",    "WHITTIER POLICE DEPT"),
        ("FL 1",    "MAYOR & CITY OFFICES"),
        ("FL 2",    "HEALTH CLINIC & LAUNDROMAT"),
        ("FL B1",   "SCHOOL TUNNEL ACCESS ->"),
        ("FL B1",   "COMMUNITY CHURCH"),
        ("FL 3-14", "196 RESIDENTIAL APTS"),
    ]
    y = 165
    for fl, desc in rows:
        d.rectangle([42, y, 162, y + 54], fill=(210, 174, 88))
        d.text((52, y + 12), fl, fill=(22, 24, 30), font=_load_font(24, True))
        d.text((180, y + 13), desc, fill=(242, 240, 234), font=_load_font(22, True))
        d.line([42, y + 66, 598, y + 66], fill=(64, 72, 88), width=2)
        y += 82
    save_sign("sign_directory", im)

    # 3. U.S. Post Office Whittier Counter Sign
    im = Image.new("RGB", (900, 220), (30, 62, 116))
    d = ImageDraw.Draw(im)
    d.rectangle([8, 8, 892, 212], outline=(232, 228, 216), width=6)
    d.rectangle([8, 176, 892, 212], fill=(198, 48, 44))
    d.text((76, 36), "U.S. POST OFFICE", fill=(252, 250, 244), font=_load_font(68, True))
    d.text((220, 118), "WHITTIER, ALASKA 99693", fill=(224, 214, 172), font=_load_font(34, True))
    save_sign("sign_post_office", im)

    # 4. Kozy Korner Minimarket Sign
    im = Image.new("RGB", (900, 240), (196, 54, 42))
    d = ImageDraw.Draw(im)
    d.rectangle([10, 10, 890, 230], outline=(248, 220, 116), width=10)
    d.text((88, 38), "KOZY KORNER", fill=(255, 248, 224), font=_load_font(78, True))
    d.text((190, 144), "GROCERY  •  COFFEE  •  SNACKS", fill=(252, 226, 134), font=_load_font(32, True))
    save_sign("sign_kozy_korner", im)

    # 5. School Tunnel Directional & Overhead Sign
    im = Image.new("RGB", (900, 240), (232, 186, 42))
    d = ImageDraw.Draw(im)
    d.rectangle([12, 12, 888, 228], outline=(24, 54, 104), width=14)
    d.rectangle([26, 26, 874, 90], fill=(28, 66, 128))
    d.text((120, 36), "WHITTIER COMMUNITY SCHOOL", fill=(250, 248, 240), font=_load_font(38, True))
    d.text((86, 118), "SCHOOL TUNNEL  ->", fill=(20, 28, 46), font=_load_font(72, True))
    save_sign("sign_school_tunnel", im)

    # 6. Coober Pedy DANGER: OPEN SHAFTS (Rusted Outback Yellow Warning Sign)
    im = Image.new("RGB", (640, 640), (222, 176, 36))
    d = ImageDraw.Draw(im)
    for rx, ry, rr in [(35, 40, 60), (595, 580, 75), (60, 590, 50), (585, 55, 55), (320, 610, 45)]:
        d.ellipse([rx - rr, ry - rr, rx + rr, ry + rr], fill=(138, 72, 34))
    d.rectangle([22, 22, 618, 618], outline=(28, 22, 18), width=18)
    d.polygon([(320, 65), (560, 480), (80, 480)], fill=(234, 188, 38), outline=(28, 22, 18))
    d.line([(320, 65), (560, 480), (80, 480), (320, 65)], fill=(28, 22, 18), width=18)
    d.text((290, 175), "!", fill=(26, 20, 16), font=_load_font(190, True))
    d.rectangle([38, 486, 602, 600], fill=(28, 22, 18))
    d.text((152, 496), "DANGER", fill=(238, 194, 44), font=_load_font(54, True))
    d.text((112, 552), "OPEN SHAFTS", fill=(250, 242, 222), font=_load_font(42, True))
    save_sign("sign_danger_shafts", im)

    # 7. Coober Pedy Dugout Opal Mining Map
    im = Image.new("RGB", (768, 512), (228, 204, 164))
    d = ImageDraw.Draw(im)
    d.rectangle([16, 16, 752, 496], outline=(98, 62, 38), width=12)
    d.text((120, 34), "COOBER PEDY OPAL FIELDS", fill=(74, 42, 24), font=_load_font(40, True))
    for i in range(6):
        d.line([(60 + i * 110, 100), (90 + i * 110, 450)], fill=(182, 142, 98), width=3)
        d.line([(50, 120 + i * 60), (710, 130 + i * 60)], fill=(182, 142, 98), width=3)
    for ox, oy in [(220, 210), (410, 280), (560, 190), (310, 360)]:
        d.ellipse([ox - 16, oy - 16, ox + 16, oy + 16], fill=(42, 196, 188), outline=(58, 34, 20), width=4)
    d.text((160, 440), "24°C NATURAL DUGOUT ZONE", fill=(142, 54, 30), font=_load_font(28, True))
    save_sign("sign_opal_map", im)

    # 8. Setenil BAR LA ROCA — TAPAS Carved Wood & Andalusian Tile Board
    im = Image.new("RGB", (640, 820), (88, 52, 32))
    d = ImageDraw.Draw(im)
    d.rectangle([16, 16, 624, 804], outline=(235, 224, 198), width=12)
    d.rectangle([34, 34, 606, 210], fill=(28, 56, 108))
    d.text((88, 58), "BAR LA ROCA", fill=(252, 246, 232), font=_load_font(64, True))
    d.text((146, 142), "SETENIL DE LAS BODEGAS", fill=(242, 198, 94), font=_load_font(26, True))
    d.text((186, 250), "~ TAPAS ~", fill=(246, 206, 104), font=_load_font(48, True))
    menu = [
        "Pan con Tomate ...... 3€",
        "Aceitunas Verdes .... 2€",
        "Jamón Ibérico ....... 6€",
        "Queso Manchego ...... 5€",
        "Zumo de Naranja ..... 3€",
    ]
    y = 335
    for line in menu:
        d.text((78, y), line, fill=(248, 240, 224), font=_load_font(34, False))
        y += 78
    save_sign("sign_bar_laroca", im)


if __name__ == "__main__":
    main()
