"""
Procedural Cinematic SFX, Ambient Beds & Foley Mixer for "3 Kota Paling Unik di Dunia".
Synthesizes crisp, clean SFX synced to audio/vo_manifest.json and mixes them with
ElevenLabs audio/master_vo.wav -> audio/master_mix.wav & audio/master_mix.mp3.
"""

from __future__ import annotations

import json
import math
import subprocess
import wave
from pathlib import Path
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
AUDIO_DIR = PROJECT_ROOT / "audio"
VO_WAV = AUDIO_DIR / "master_vo.wav"
MANIFEST_PATH = AUDIO_DIR / "vo_manifest.json"
SFX_WAV = AUDIO_DIR / "sfx_bed.wav"
MASTER_MIX_WAV = AUDIO_DIR / "master_mix.wav"
MASTER_MIX_MP3 = AUDIO_DIR / "master_mix.mp3"

SR = 44100


def lowpass(sig: np.ndarray, cutoff_hz: float) -> np.ndarray:
    rc = 1.0 / (2.0 * math.pi * max(20.0, cutoff_hz))
    dt = 1.0 / SR
    a = dt / (rc + dt)
    out = np.empty_like(sig)
    y = 0.0
    for i in range(len(sig)):
        y += a * (sig[i] - y)
        out[i] = y
    return out


def add_at(buf: np.ndarray, sec: float, clip: np.ndarray, gain: float = 1.0) -> None:
    i0 = int(round(sec * SR))
    if i0 < 0:
        clip = clip[-i0:]
        i0 = 0
    i1 = min(len(buf), i0 + len(clip))
    if i1 > i0:
        buf[i0:i1] += clip[: i1 - i0] * gain


def make_noise(dur: float, seed: int = 1) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return rng.standard_normal(int(round(dur * SR))).astype(np.float64)


def make_envelope(n: int, attack_s: float = 0.05, release_s: float = 0.1) -> np.ndarray:
    env = np.ones(n, dtype=np.float64)
    na = min(n, max(1, int(attack_s * SR)))
    nr = min(n, max(1, int(release_s * SR)))
    env[:na] = np.linspace(0.0, 1.0, na)
    env[-nr:] *= np.linspace(1.0, 0.0, nr)
    return env


def synth_wind(dur: float, base_cut: float, mod_hz: float, seed: int) -> np.ndarray:
    n = int(round(dur * SR))
    t = np.arange(n) / SR
    raw = make_noise(dur, seed)
    # Fast vectorized smoothing via convolution (blizzard / desert wind texture)
    k = max(5, int(SR / max(80.0, base_cut)))
    kernel = np.hanning(k)
    kernel /= kernel.sum()
    smooth = np.convolve(raw, kernel, mode="same")
    # Add howling whistle harmonic
    whistle = np.sin(2.0 * np.pi * (base_cut * 0.55 + np.sin(2.0 * np.pi * mod_hz * t) * 45.0) * t) * 0.14
    mod = 0.65 + 0.35 * np.sin(2.0 * np.pi * mod_hz * t)
    return (smooth * 2.8 + whistle) * mod * make_envelope(n, 0.12, 0.18)


def synth_ding(freq: float = 1174.66, dur: float = 1.1) -> np.ndarray:
    """Crisp metallic elevator DING!"""
    n = int(round(dur * SR))
    t = np.arange(n) / SR
    sig = (
        np.sin(2 * np.pi * freq * t) * np.exp(-3.5 * t)
        + 0.45 * np.sin(2 * np.pi * (freq * 2.01) * t) * np.exp(-6.0 * t)
        + 0.20 * np.sin(2 * np.pi * (freq * 3.03) * t) * np.exp(-10.0 * t)
    )
    return sig * make_envelope(n, 0.003, 0.1)


def synth_door_thud(freq: float = 110.0, dur: float = 0.25) -> np.ndarray:
    n = int(round(dur * SR))
    t = np.arange(n) / SR
    thump = np.sin(2 * np.pi * freq * np.exp(-8 * t) * t) * np.exp(-16 * t)
    click = make_noise(dur, 42) * np.exp(-45 * t) * 0.35
    return (thump + click) * make_envelope(n, 0.002, 0.05)


def synth_whoosh(dur: float = 0.9, up: bool = True) -> np.ndarray:
    n = int(round(dur * SR))
    t = np.arange(n) / SR
    raw = make_noise(dur, 77)
    k = 65
    ker = np.hanning(k)
    ker /= ker.sum()
    band = np.convolve(raw, ker, mode="same") * 3.0
    sweep = np.sin(2 * np.pi * (np.linspace(160, 740, n) if up else np.linspace(680, 140, n)) * t) * 0.18
    env = np.sin(np.pi * (t / dur)) ** 1.4
    return (band + sweep) * env


def synth_tink_sparkle() -> np.ndarray:
    """Geology hammer tink! + crystal opal chime shimmer!"""
    dur = 1.6
    n = int(round(dur * SR))
    t = np.arange(n) / SR
    out = np.zeros(n, dtype=np.float64)
    # Metallic hammer tink
    out += (np.sin(2 * np.pi * 2480 * t) * np.exp(-18 * t) + 0.5 * np.sin(2 * np.pi * 3920 * t) * np.exp(-26 * t)) * 0.55
    # Crystal opal shimmer cascade
    notes = [1567.98, 1975.53, 2349.32, 2637.02, 3135.96]
    for idx, f in enumerate(notes):
        delay = 0.14 + idx * 0.09
        mask = t >= delay
        dt = np.where(mask, t - delay, 0.0)
        chime = np.where(mask, np.sin(2 * np.pi * f * dt) * np.exp(-4.2 * dt), 0.0)
        out += chime * 0.22
    return out * make_envelope(n, 0.002, 0.2)


def synth_guitar_chord(freqs: list[float], dur: float = 1.4, strum_gap: float = 0.028) -> np.ndarray:
    """Warm Spanish acoustic nylon guitar strum!"""
    n = int(round(dur * SR))
    t = np.arange(n) / SR
    out = np.zeros(n, dtype=np.float64)
    for i, f in enumerate(freqs):
        d = i * strum_gap
        mask = t >= d
        dt = np.where(mask, t - d, 0.0)
        # Warm plucked nylon string harmonic profile
        s = (
            1.00 * np.sin(2 * np.pi * f * dt) * np.exp(-2.2 * dt)
            + 0.42 * np.sin(2 * np.pi * 2 * f * dt) * np.exp(-3.6 * dt)
            + 0.18 * np.sin(2 * np.pi * 3 * f * dt) * np.exp(-5.4 * dt)
            + 0.07 * np.sin(2 * np.pi * 4 * f * dt) * np.exp(-8.0 * dt)
        )
        out += np.where(mask, s, 0.0) * 0.22
    return out * make_envelope(n, 0.004, 0.15)


def synth_snap() -> np.ndarray:
    dur = 0.14
    n = int(round(dur * SR))
    t = np.arange(n) / SR
    raw = make_noise(dur, 99)
    sig = raw * np.exp(-65 * t) * 0.9 + np.sin(2 * np.pi * 1850 * t) * np.exp(-55 * t) * 0.55
    return sig * make_envelope(n, 0.001, 0.04)


def main() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    total_sec = float(manifest["total_duration_sec"])
    n_total = int(round(total_sec * SR))
    sfx = np.zeros(n_total, dtype=np.float64)

    # 1. Act 0: Arctic blizzard roar (0.0s .. 3.15s) -> abrupt door shut + elevator DING!
    add_at(sfx, 0.00, synth_wind(3.15, 580.0, 0.9, seed=11), gain=0.22)
    add_at(sfx, 3.05, synth_door_thud(95.0, 0.22), gain=0.35)
    add_at(sfx, 3.25, synth_ding(1174.66, 1.0), gain=0.26)

    # 2. Act 1A: Warm cozy lobby subtle hum (3.3s .. 18.5s) + elevator door ding at Pak Arthur entrance (12.3s)
    add_at(sfx, 3.30, synth_wind(15.2, 180.0, 0.25, seed=12), gain=0.04)
    add_at(sfx, 12.25, synth_ding(1318.5, 0.9), gain=0.22)

    # 3. Act 1B: School tunnel light echoes + Maya brisk footsteps (18.6s .. 27.6s) + Speed-ramp dive whoosh!
    for step_t in np.arange(18.8, 26.8, 0.36):
        add_at(sfx, float(step_t), synth_door_thud(180.0, 0.09), gain=0.10)
    add_at(sfx, 27.25, synth_whoosh(0.95, up=True), gain=0.30)

    # 4. Act 2A: Coober Pedy scorching dry desert wind + heat sizzle (28.0s .. 36.2s) + heavy wood cave door!
    add_at(sfx, 27.90, synth_wind(8.3, 420.0, 0.45, seed=21), gain=0.16)
    add_at(sfx, 35.95, synth_door_thud(78.0, 0.30), gain=0.40)

    # 5. Act 2B: Cool subterranean dugout calm room tone (36.3s .. 50.4s) + Hammer tink & Opal crystal shimmer!
    add_at(sfx, 36.30, synth_wind(14.0, 140.0, 0.15, seed=22), gain=0.03)
    add_at(sfx, 47.65, synth_tink_sparkle(), gain=0.30)
    add_at(sfx, 49.95, synth_whoosh(0.85, up=True), gain=0.28)

    # 6. Act 3: Setenil de las Bodegas — Warm Andalusian acoustic Spanish guitar progression! (50.7s .. 75.5s)
    # Classic Andalusian cadence: Am -> G -> F -> E7!
    chords = [
        [220.00, 261.63, 329.63, 440.00],  # Am
        [196.00, 246.94, 293.66, 392.00],  # G
        [174.61, 220.00, 261.63, 349.23],  # F
        [164.81, 207.65, 246.94, 329.63],  # E
    ]
    beat_t = 50.75
    ci = 0
    while beat_t < 73.5:
        add_at(sfx, beat_t, synth_guitar_chord(chords[ci % 4], dur=1.9, strum_gap=0.025), gain=0.16)
        beat_t += 2.2
        ci += 1
    # Final crisp Spanish guitar resolution chord + Mateo ceiling knock (61.2s, 61.5s) + Finger snap loop hook (74.95s)!
    add_at(sfx, 61.20, synth_door_thud(145.0, 0.14), gain=0.34)
    add_at(sfx, 61.48, synth_door_thud(155.0, 0.14), gain=0.34)
    add_at(sfx, 74.10, synth_guitar_chord([220.00, 277.18, 329.63, 440.00], dur=1.6, strum_gap=0.022), gain=0.22)
    add_at(sfx, 74.95, synth_snap(), gain=0.38)
    add_at(sfx, 75.15, synth_wind(0.95, 520.0, 1.1, seed=11), gain=0.16)  # Seamless loop swell back to 00:00 blizzard!

    # Normalize & write stereo SFX bed WAV
    peak = max(1e-6, float(np.max(np.abs(sfx))))
    sfx = np.clip(sfx / max(peak, 1.0) * 0.72, -0.95, 0.95)
    pcm = (sfx * 32767.0).astype(np.int16)
    stereo = np.column_stack([pcm, pcm]).ravel()

    with wave.open(str(SFX_WAV), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(stereo.tobytes())

    # Mix master VO (dominant, crisp) + SFX bed (warm cinematic support, zero voice masking)
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", str(VO_WAV),
            "-i", str(SFX_WAV),
            "-filter_complex",
            "[0:a]volume=1.05[vo];[1:a]volume=0.58[fx];[vo][fx]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,alimiter=limit=0.95[out]",
            "-map", "[out]",
            "-ar", "44100", "-ac", "2",
            str(MASTER_MIX_WAV),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(MASTER_MIX_WAV), "-c:a", "libmp3lame", "-b:a", "192k", str(MASTER_MIX_MP3)],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    print(f"SFX bed + Master Audio Mix complete: {MASTER_MIX_WAV} ({total_sec:.2f}s)")


if __name__ == "__main__":
    main()
