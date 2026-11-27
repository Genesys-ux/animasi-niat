import json
import os
import subprocess
from pathlib import Path
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_ROOT / ".env"
AUDIO_DIR = PROJECT_ROOT / "audio"
CLIPS_DIR = AUDIO_DIR / "clips"
MANIFEST_PATH = AUDIO_DIR / "vo_manifest.json"


def load_env(path: Path) -> None:
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ[k.strip()] = v.strip().strip('"').strip("'")


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
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    # Regenerate ONLY 03_arthur_dialog with clearer articulation, higher stability, slower crisp speed
    cid = "03_arthur_dialog"
    new_text = "Enak, Nak... Telat bangun lima menit pun, tidak akan kena macet!"
    raw_mp3 = CLIPS_DIR / f"{cid}_raw.mp3"
    final_wav = CLIPS_DIR / f"{cid}.wav"

    print(f"Regenerating {cid} for crystal-clear articulation...")
    audio_stream = client.text_to_speech.convert(
        voice_id="pqHfZKP75CvOlQylNhV4",  # Bill
        model_id="eleven_turbo_v2_5",
        language_code="id",
        text=new_text,
        output_format="mp3_44100_128",
        voice_settings=VoiceSettings(
            stability=0.75,
            similarity_boost=0.85,
            style=0.12,
            use_speaker_boost=True,
            speed=1.02,
        ),
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
            "silenceremove=start_periods=1:start_silence=0.03:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_silence=0.05:start_threshold=-45dB,areverse,highpass=f=85,equalizer=f=3200:t=q:w=1.2:g=2.5,loudnorm=I=-16:TP=-1.5:LRA=11",
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

    # Rebuild timeline cleanly using existing clips + updated clip 03
    gaps = {
        "01_fajar_hook": 0.28,
        "02_fajar_whittier_intro": 0.28,
        "03_arthur_dialog": 0.28,
        "04_fajar_tunnel": 0.18,
        "05_maya_dialog": 0.48,
        "06_fajar_coober_intro": 0.22,
        "07_fajar_dugout": 0.18,
        "08_jack_dialog": 0.18,
        "09_elena_dialog": 0.48,
        "10_fajar_setenil_intro": 0.20,
        "11_mateo_dialog": 0.25,
        "12_fajar_insulator": 0.28,
        "13_fajar_outro": 0.40,
    }

    cursor = 0.20
    for clip in manifest["clips"]:
        if clip["id"] == cid:
            clip["text"] = new_text
        wav_path = PROJECT_ROOT / clip["file"]
        dur = get_duration(wav_path)
        start_sec = cursor
        end_sec = start_sec + dur
        cursor = end_sec + gaps.get(clip["id"], 0.22)
        clip["start_sec"] = round(start_sec, 3)
        clip["end_sec"] = round(end_sec, 3)
        clip["duration_sec"] = round(dur, 3)
        clip["start_frame_30fps"] = round(start_sec * 30)
        clip["end_frame_30fps"] = round(end_sec * 30)
        print(f"  -> {clip['id']}: {start_sec:05.2f}s - {end_sec:05.2f}s (dur {dur:.2f}s)")

    total_duration = round(cursor, 3)
    manifest["total_duration_sec"] = total_duration
    manifest["total_frames_30fps"] = int(round(total_duration * 30))

    # Mix master WAV & MP3
    inputs = []
    filter_parts = []
    mix_labels = []
    for idx, m in enumerate(manifest["clips"]):
        inputs.extend(["-i", str(PROJECT_ROOT / m["file"])])
        delay_ms = int(round(m["start_sec"] * 1000))
        filter_parts.append(f"[{idx}:a]adelay={delay_ms}|{delay_ms}[a{idx}]")
        mix_labels.append(f"[a{idx}]")

    filter_complex = (
        ";".join(filter_parts)
        + f";{''.join(mix_labels)}amix=inputs={len(manifest['clips'])}:duration=longest:dropout_transition=0:normalize=0,apad=whole_dur={total_duration}[out]"
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

    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nUpdated master VO complete: {total_duration:.2f}s ({manifest['total_frames_30fps']} frames @ 30fps)")


if __name__ == "__main__":
    main()
