import json
import os
import subprocess
from pathlib import Path
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_ROOT / ".env"
CLIPS_DIR = PROJECT_ROOT / "audio" / "clips"
AUDIO_DIR = PROJECT_ROOT / "audio"
CLIPS_DIR.mkdir(parents=True, exist_ok=True)


def load_env(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Missing .env file at {path}")
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ[k.strip()] = v.strip().strip('"').strip("'")


# Premade voices (supported on ElevenLabs Free API) selected for cleanest Indonesian articulation with language_code="id"
VOICES = {
    "Fajar": {
        "voice_id": "bIHbv24MWmeRgasZH58o",  # Will - Clear, Energetic Young Male
        "voice_name": "Will",
        "settings": VoiceSettings(
            stability=0.58,
            similarity_boost=0.82,
            style=0.30,
            use_speaker_boost=True,
            speed=1.18,
        ),
    },
    "Pak Arthur": {
        "voice_id": "pqHfZKP75CvOlQylNhV4",  # Bill - Wise, Mature Male
        "voice_name": "Bill",
        "settings": VoiceSettings(
            stability=0.65,
            similarity_boost=0.80,
            style=0.20,
            use_speaker_boost=True,
            speed=1.12,
        ),
    },
    "Maya": {
        "voice_id": "cgSgspJ2msm6clMCkdW9",  # Jessica - Bright, Young Female
        "voice_name": "Jessica",
        "settings": VoiceSettings(
            stability=0.55,
            similarity_boost=0.82,
            style=0.35,
            use_speaker_boost=True,
            speed=1.16,
        ),
    },
    "Jack": {
        "voice_id": "nPczCjzI2devNBz1zQrb",  # Brian - Deep, Relaxed Male
        "voice_name": "Brian",
        "settings": VoiceSettings(
            stability=0.62,
            similarity_boost=0.80,
            style=0.22,
            use_speaker_boost=True,
            speed=1.14,
        ),
    },
    "Elena": {
        "voice_id": "EXAVITQu4vr4xnSDxMaL",  # Sarah - Clear, Confident Female
        "voice_name": "Sarah",
        "settings": VoiceSettings(
            stability=0.58,
            similarity_boost=0.82,
            style=0.30,
            use_speaker_boost=True,
            speed=1.16,
        ),
    },
    "Mateo": {
        "voice_id": "cjVigY5qzO86Huf0OWal",  # Eric - Smooth, Warm Male
        "voice_name": "Eric",
        "settings": VoiceSettings(
            stability=0.60,
            similarity_boost=0.80,
            style=0.28,
            use_speaker_boost=True,
            speed=1.14,
        ),
    },
}

SCRIPT_LINES = [
    {
        "id": "01_fajar_hook",
        "scene": "hook_whittier_ext",
        "character": "Fajar",
        "min_gap_after": 0.28,
        "text": "Bayangin satu kota penuh, isinya cuma satu gedung apartemen ini doang!",
    },
    {
        "id": "02_fajar_whittier_intro",
        "scene": "whittier_lobby",
        "character": "Fajar",
        "min_gap_after": 0.20,
        "text": "Selamat datang di Whittier, Alaska! Hampir semua warganya tinggal bareng di gedung empat belas lantai ini! Kantor pos, minimarket, klinik, kantor polisi, sampai gereja, semuanya menyatu di dalam sini!",
    },
    {
        "id": "03_arthur_dialog",
        "scene": "whittier_lobby",
        "character": "Pak Arthur",
        "min_gap_after": 0.28,
        "text": "Enak, Nak. Telat bangun lima menit pun tidak bakal kena macet!",
    },
    {
        "id": "04_fajar_tunnel",
        "scene": "whittier_tunnel",
        "character": "Fajar",
        "min_gap_after": 0.18,
        "text": "Saking ekstremnya badai salju di luar, anak sekolah pun dikasih terowongan bawah tanah khusus biar bisa berangkat tanpa jaket tebal!",
    },
    {
        "id": "05_maya_dialog",
        "scene": "whittier_tunnel",
        "character": "Maya",
        "min_gap_after": 0.50,
        "text": "Bisa berangkat sekolah pakai kaus pas di luar minus dua puluh derajat!",
    },
    {
        "id": "06_fajar_coober_intro",
        "scene": "coober_desert",
        "character": "Fajar",
        "min_gap_after": 0.22,
        "text": "Kalau dingin bikin orang mengumpet di satu gedung, panas ekstrem bikin satu kota di Australia pindah ke bawah tanah! Ini Coober Pedy, tempat suhu luarnya sering tembus lima puluh derajat!",
    },
    {
        "id": "07_fajar_dugout",
        "scene": "coober_dugout",
        "character": "Fajar",
        "min_gap_after": 0.18,
        "text": "Solusinya? Mereka gali rumah, hotel, sampai gereja langsung di dalam batu! Di bawah sini adem stabil dua puluh empat derajat tanpa AC! Dan serunya lagi...",
    },
    {
        "id": "08_jack_dialog",
        "scene": "coober_dugout",
        "character": "Jack",
        "min_gap_after": 0.18,
        "text": "Mau nambah kamar? Gampang, tinggal bor tembok!",
    },
    {
        "id": "09_elena_dialog",
        "scene": "coober_dugout",
        "character": "Elena",
        "min_gap_after": 0.50,
        "text": "Siapa tahu pas mengebor, malah ketemu batu opal harga miliaran!",
    },
    {
        "id": "10_fajar_setenil_intro",
        "scene": "setenil_street",
        "character": "Fajar",
        "min_gap_after": 0.20,
        "text": "Terakhir, kota yang bikin merinding tiap kali lihat ke atas: Setenil de las Bodegas, Spanyol! Warga di sini tidak ribet beli genteng, soalnya atap rumah mereka ya tebing batu jutaan tahun ini!",
    },
    {
        "id": "11_mateo_dialog",
        "scene": "setenil_street",
        "character": "Mateo",
        "min_gap_after": 0.25,
        "text": "Tenang, sudah berdiri ratusan tahun, anti bocor, anti panas!",
    },
    {
        "id": "12_fajar_insulator",
        "scene": "setenil_balcony",
        "character": "Fajar",
        "min_gap_after": 0.28,
        "text": "Batu tebing setebal puluhan meter ini jadi insulator alami, bikin rumah tetap dingin pas musim panas dan hangat pas musim dingin!",
    },
    {
        "id": "13_fajar_outro",
        "scene": "setenil_outro",
        "character": "Fajar",
        "min_gap_after": 0.40,
        "text": "Manusia memang jago banget adaptasi di tempat paling tidak masuk akal! Dari tiga kota unik ini, kamu paling betah tinggal di mana?",
    },
]


def get_duration(path: Path) -> float:
    out = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        text=True,
    ).strip()
    return float(out)


def main() -> None:
    load_env(ENV_FILE)
    client = ElevenLabs(api_key=os.environ["ELEVENLABS_API_KEY"])

    raw_durs = []
    for item in SCRIPT_LINES:
        cid = item["id"]
        char = item["character"]
        vinfo = VOICES[char]
        raw_mp3 = CLIPS_DIR / f"{cid}_raw.mp3"
        clean_wav = CLIPS_DIR / f"{cid}_clean.wav"

        print(f"Generating {cid} ({char} / {vinfo['voice_name']})...")
        audio_stream = client.text_to_speech.convert(
            voice_id=vinfo["voice_id"],
            model_id="eleven_turbo_v2_5",
            language_code="id",
            text=item["text"],
            output_format="mp3_44100_128",
            voice_settings=vinfo["settings"],
        )
        with open(raw_mp3, "wb") as f:
            for chunk in audio_stream:
                if chunk:
                    f.write(chunk)

        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(raw_mp3),
                "-af",
                "silenceremove=start_periods=1:start_silence=0.03:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_silence=0.05:start_threshold=-45dB,areverse,loudnorm=I=-16:TP=-1.5:LRA=11",
                "-ar",
                "44100",
                "-ac",
                "1",
                str(clean_wav),
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        raw_durs.append(get_duration(clean_wav))

    total_gaps = 0.20 + sum(item["min_gap_after"] for item in SCRIPT_LINES)
    total_speech = sum(raw_durs)
    est_total = total_speech + total_gaps
    target_total = 75.0

    # Gentle pitch-preserving tempo fit so final master lands cleanly around ~75s
    tempo = 1.0
    if est_total > 76.0:
        tempo = min(1.15, total_speech / (target_total - total_gaps))
        print(f"Applying gentle pitch-preserving tempo fit: {tempo:.3f}x (est {est_total:.2f}s -> ~{target_total:.1f}s)")

    manifest_items = []
    cursor = 0.20
    for item in SCRIPT_LINES:
        cid = item["id"]
        char = item["character"]
        vinfo = VOICES[char]
        clean_wav = CLIPS_DIR / f"{cid}_clean.wav"
        final_wav = CLIPS_DIR / f"{cid}.wav"

        if tempo > 1.005:
            subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-i",
                    str(clean_wav),
                    "-af",
                    f"atempo={tempo:.4f}",
                    "-ar",
                    "44100",
                    "-ac",
                    "1",
                    str(final_wav),
                ],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        else:
            final_wav.write_bytes(clean_wav.read_bytes())

        dur = get_duration(final_wav)
        start_sec = cursor
        end_sec = start_sec + dur
        cursor = end_sec + item["min_gap_after"]

        manifest_items.append(
            {
                "id": cid,
                "scene": item["scene"],
                "character": char,
                "voice_name": vinfo["voice_name"],
                "voice_id": vinfo["voice_id"],
                "text": item["text"],
                "file": str(final_wav.relative_to(PROJECT_ROOT)).replace("\\", "/"),
                "start_sec": round(start_sec, 3),
                "end_sec": round(end_sec, 3),
                "duration_sec": round(dur, 3),
                "start_frame_30fps": round(start_sec * 30),
                "end_frame_30fps": round(end_sec * 30),
            }
        )
        print(f"  -> {cid}: {start_sec:05.2f}s - {end_sec:05.2f}s (dur {dur:.2f}s)")

    total_duration = round(cursor, 3)

    inputs = []
    filter_parts = []
    mix_labels = []
    for idx, m in enumerate(manifest_items):
        inputs.extend(["-i", str(PROJECT_ROOT / m["file"])])
        delay_ms = int(round(m["start_sec"] * 1000))
        filter_parts.append(f"[{idx}:a]adelay={delay_ms}|{delay_ms}[a{idx}]")
        mix_labels.append(f"[a{idx}]")

    filter_complex = (
        ";".join(filter_parts)
        + f";{''.join(mix_labels)}amix=inputs={len(manifest_items)}:duration=longest:dropout_transition=0:normalize=0,apad=whole_dur={total_duration}[out]"
    )

    master_wav = AUDIO_DIR / "master_vo.wav"
    master_mp3 = AUDIO_DIR / "master_vo.mp3"

    subprocess.run(
        [
            "ffmpeg",
            "-y",
            *inputs,
            "-filter_complex",
            filter_complex,
            "-map",
            "[out]",
            "-ar",
            "44100",
            "-ac",
            "2",
            str(master_wav),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(master_wav),
            "-c:a",
            "libmp3lame",
            "-b:a",
            "192k",
            str(master_mp3),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    manifest = {
        "model_id": "eleven_turbo_v2_5",
        "language_code": "id",
        "tempo_fit": round(tempo, 4),
        "fps": 30,
        "total_duration_sec": total_duration,
        "total_frames_30fps": int(round(total_duration * 30)),
        "master_wav": "audio/master_vo.wav",
        "master_mp3": "audio/master_vo.mp3",
        "clips": manifest_items,
    }
    manifest_path = AUDIO_DIR / "vo_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    print("\n=== MASTER VOICEOVER (ID-LOCKED ~75s) COMPLETE ===")
    print(f"Master MP3: {master_mp3}")
    print(f"Master WAV: {master_wav}")
    print(f"Manifest:   {manifest_path}")
    print(f"Total Dur:  {total_duration:.2f}s ({manifest['total_frames_30fps']} frames @ 30fps)")


if __name__ == "__main__":
    main()
