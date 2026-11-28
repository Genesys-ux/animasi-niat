"""
Assemble rendered Blender frames + synchronized audio/master_mix.wav into a crisp H.264 MP4!
Supports both:
  - --mode preview_reel : Stitches the 7 PREVIEW_SEGMENTS clips (~36s across all 3 cities & 6 characters)
                          with exact time-aligned audio slices + 0.15s smooth audio crossfades!
  - --mode full_video   : Stitches all frames 0..2282 with full 76.1s audio/master_mix.wav!
Also generates a high-res visual contact sheet PNG for GitHub Actions Summary preview.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path
from PIL import Image, ImageDraw

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROD_DIR = PROJECT_ROOT / "production"
AUDIO_MIX = PROJECT_ROOT / "audio" / "master_mix.wav"
sys.path.insert(0, str(PROD_DIR))

from timeline_data import FPS, PREVIEW_SEGMENTS, QA_SHOWCASE_SEGMENTS, TOTAL_FRAMES


def build_contact_sheet(frame_paths: list[Path], out_png: Path) -> None:
    if not frame_paths:
        return
    step = max(1, len(frame_paths) // 9)
    picks = frame_paths[::step][:9]
    imgs = [Image.open(p).convert("RGB") for p in picks]
    # Auto-detect vertical 9:16 vs horizontal 16:9 aspect ratio so tiles are never stretched
    w0, h0 = imgs[0].size
    if h0 > w0:
        tw, th = 270, 480
        cols = 3
    else:
        tw, th = 426, 240
        cols = 3
    rows = (len(imgs) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tw, rows * th), (18, 16, 24))
    for i, im in enumerate(imgs):
        im_r = im.resize((tw, th), Image.Resampling.LANCZOS)
        r, c = divmod(i, cols)
        sheet.paste(im_r, (c * tw, r * th))
    sheet.save(out_png, quality=92)
    print(f"Saved contact sheet ({tw}x{th} tiles): {out_png}")


def assemble_full(frames_dir: Path, out_mp4: Path, crf: int = 16, audio_bitrate: str = "256k") -> None:
    import tempfile
    out_mp4.parent.mkdir(parents=True, exist_ok=True)
    # Build sequential symlink folder on local fast SSD temp dir (works even when frames_dir is on Google Drive FUSE!)
    seq_dir = Path(tempfile.mkdtemp(prefix="seq_full_3kota_"))
    try:
        collected: list[Path] = []
        idx = 0
        for f in range(TOTAL_FRAMES):
            src = frames_dir / f"frame_{f:04d}.png"
            if src.exists():
                dst = seq_dir / f"seq_{idx:05d}.png"
                try:
                    dst.symlink_to(src.resolve())
                except Exception:
                    shutil.copy2(src, dst)
                collected.append(src)
                idx += 1
        if not collected:
            raise RuntimeError(f"No rendered frames found in {frames_dir}")

        cmd = [
            "ffmpeg", "-y",
            "-framerate", str(FPS),
            "-i", str(seq_dir / "seq_%05d.png"),
            "-i", str(AUDIO_MIX),
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", str(crf), "-preset", "slow",
            "-profile:v", "high", "-level", "4.2",
            "-c:a", "aac", "-b:a", audio_bitrate, "-shortest",
            "-movflags", "+faststart",
            str(out_mp4),
        ]
        subprocess.run(cmd, check=True)
        build_contact_sheet(collected, out_mp4.with_suffix(".contact_sheet.png"))
        print(f"Assembled FULL CINEMA video ({len(collected)} frames, CRF {crf}): {out_mp4}")
    finally:
        shutil.rmtree(seq_dir, ignore_errors=True)


def _stamp_qa_badge(src_png: Path, dst_png: Path, label: str, frame_num: int) -> None:
    """Stamp a crisp non-intrusive top-left QA chapter pill badge + frame counter onto a QA clip frame."""
    im = Image.open(src_png).convert("RGBA")
    w, _ = im.size
    overlay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    dr = ImageDraw.Draw(overlay)
    bar_h = max(28, int(w * 0.058))
    dr.rectangle([0, 0, w, bar_h], fill=(12, 16, 26, 185))
    dr.text((10, max(6, (bar_h - 12) // 2)), f"{label}  [f{frame_num:04d}]", fill=(255, 245, 210, 255))
    out = Image.alpha_composite(im, overlay).convert("RGB")
    out.save(dst_png)


def assemble_segments_reel(
    frames_dir: Path,
    out_mp4: Path,
    segments: list,
    stamp_labels: bool = False,
    tag: str = "PREVIEW REEL",
) -> None:
    out_mp4.parent.mkdir(parents=True, exist_ok=True)
    seg_dir = frames_dir / "_preview_segs"
    seg_dir.mkdir(exist_ok=True)

    seg_mp4s: list[Path] = []
    all_frames: list[Path] = []

    for seg in segments:
        slug, f0, f1 = seg[0], seg[1], seg[2]
        label = seg[3] if len(seg) > 3 else slug
        sub_dir = seg_dir / slug
        sub_dir.mkdir(exist_ok=True)
        n = 0
        for f in range(f0, f1 + 1):
            src = frames_dir / f"frame_{f:04d}.png"
            if src.exists():
                dst = sub_dir / f"f_{n:04d}.png"
                if stamp_labels:
                    _stamp_qa_badge(src, dst, label, f)
                else:
                    shutil.copy2(src, dst)
                all_frames.append(dst if stamp_labels else src)
                n += 1
        if n == 0:
            print(f"Skipping missing segment {slug} ({f0}..{f1})")
            continue

        start_sec = f0 / float(FPS)
        dur_sec = n / float(FPS)
        seg_out = seg_dir / f"{slug}.mp4"
        subprocess.run(
            [
                "ffmpeg", "-y",
                "-framerate", str(FPS),
                "-i", str(sub_dir / "f_%04d.png"),
                "-ss", f"{start_sec:.3f}", "-t", f"{dur_sec:.3f}",
                "-i", str(AUDIO_MIX),
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "19", "-preset", "medium",
                "-c:a", "aac", "-b:a", "192k",
                "-af", f"afade=t=in:st=0:d=0.06,afade=t=out:st={max(0.0, dur_sec - 0.08):.3f}:d=0.08",
                "-shortest",
                str(seg_out),
            ],
            check=True,
        )
        seg_mp4s.append(seg_out)

    if not seg_mp4s:
        raise RuntimeError(f"No segments could be assembled from {frames_dir}")

    concat_txt = seg_dir / "concat.txt"
    concat_txt.write_text("\n".join(f"file '{p.resolve().as_posix()}'" for p in seg_mp4s), encoding="utf-8")

    subprocess.run(
        [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", str(concat_txt),
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "19", "-preset", "medium",
            "-c:a", "aac", "-b:a", "192k",
            "-movflags", "+faststart",
            str(out_mp4),
        ],
        check=True,
    )
    build_contact_sheet(all_frames, out_mp4.with_suffix(".contact_sheet.png"))
    print(f"Assembled {tag} ({len(all_frames)} frames across {len(seg_mp4s)} clips): {out_mp4}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Assemble Blender frames + audio into MP4")
    parser.add_argument("--mode", choices=["qa_showcase", "preview_reel", "full_video"], default="qa_showcase")
    parser.add_argument("--frames-dir", default=str(PROD_DIR / "rendered_frames"))
    parser.add_argument("--out", default=str(PROD_DIR / "output" / "preview_3_kota_unik.mp4"))
    parser.add_argument("--crf", type=int, default=16, help="H.264 CRF quality (14-16 = cinema Full HD, 19 = draft)")
    args = parser.parse_args()

    frames_dir = Path(args.frames_dir)
    out_mp4 = Path(args.out)
    if args.mode == "full_video":
        assemble_full(frames_dir, out_mp4, crf=args.crf)
    elif args.mode == "qa_showcase":
        assemble_segments_reel(frames_dir, out_mp4, QA_SHOWCASE_SEGMENTS, stamp_labels=True, tag="QA SHOWCASE")
    else:
        assemble_segments_reel(frames_dir, out_mp4, PREVIEW_SEGMENTS, stamp_labels=False, tag="PREVIEW REEL")


if __name__ == "__main__":
    main()
