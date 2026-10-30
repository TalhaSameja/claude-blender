#!/usr/bin/env python3
"""Narration via ElevenLabs, one audio file per shot line.

Writes output/<ep>/audio/line_NNN.mp3 plus timings.json, which the Blender
renderer reads so shot length always matches the voice-over exactly. Without
ELEVENLABS_API_KEY it produces silent placeholders of an estimated length, so
the whole pipeline stays runnable offline.

Usage:  python3 tools/tts.py content/episodes/ep001.json
"""
import json, os, sys, subprocess, urllib.request, urllib.error, shutil

API = "https://api.elevenlabs.io/v1/text-to-speech/{voice}"
# Deadpan narrator. Override per-episode with "voice_id".
DEFAULT_VOICE = "pNInz6obpgDQGcFmaJgB"
WORDS_PER_MIN = 165          # measured against the reference clips


def est_seconds(text):
    return max(1.2, len(text.split()) / WORDS_PER_MIN * 60.0 + 0.45)


def probe_duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", path], capture_output=True, text=True)
    try:
        return float(out.stdout.strip())
    except ValueError:
        return None


def synth(text, dest, key, voice, model="eleven_multilingual_v2"):
    body = json.dumps({
        "text": text,
        "model_id": model,
        "voice_settings": {"stability": 0.45, "similarity_boost": 0.75,
                           "style": 0.35, "use_speaker_boost": True},
    }).encode()
    req = urllib.request.Request(
        API.format(voice=voice), data=body,
        headers={"xi-api-key": key, "Content-Type": "application/json",
                 "Accept": "audio/mpeg"})
    with urllib.request.urlopen(req, timeout=120) as r, open(dest, "wb") as f:
        shutil.copyfileobj(r, f)


def silence(seconds, dest):
    subprocess.run(
        ["ffmpeg", "-loglevel", "error", "-f", "lavfi", "-i",
         "anullsrc=r=44100:cl=mono", "-t", f"{seconds:.3f}",
         "-q:a", "9", "-y", dest], check=True)


def main(ep_path):
    ep = json.load(open(ep_path))
    outdir = os.path.normpath(os.path.join(
        os.path.dirname(os.path.abspath(ep_path)), "..", "..",
        "output", ep["id"]))
    adir = os.path.join(outdir, "audio")
    os.makedirs(adir, exist_ok=True)

    key = os.environ.get("ELEVENLABS_API_KEY")
    voice = ep.get("voice_id", DEFAULT_VOICE)
    if not key:
        print("[tts] ELEVENLABS_API_KEY not set -> writing silent placeholders")

    timings, cursor = [], 0.0
    degraded = False
    for i, shot in enumerate(ep["shots"]):
        line = shot.get("line", "").strip()
        dest = os.path.join(adir, f"line_{i:03d}.mp3")
        if key and line and not degraded:
            try:
                synth(line, dest, key, voice)
                dur = probe_duration(dest) or est_seconds(line)
            except (urllib.error.URLError, OSError) as e:
                # Unreachable API (blocked host, offline, outage) must not
                # abort a render that is otherwise ready to go.
                print(f"[tts] ERROR reaching ElevenLabs: {e}")
                print("[tts] falling back to silent placeholders for all lines")
                degraded = True
                dur = shot.get("dur") or est_seconds(line)
                silence(dur, dest)
        else:
            dur = shot.get("dur") or est_seconds(line or "...")
            silence(dur, dest)
        pad = shot.get("pad", 0.25)        # breathing room between lines
        dur = dur + pad
        timings.append({"index": i, "line": line, "audio": dest,
                        "duration": round(dur, 3),
                        "start": round(cursor, 3)})
        cursor += dur
        print(f"[tts] {i:03d} {dur:5.2f}s  {line[:58]}")

    json.dump(timings, open(os.path.join(outdir, "timings.json"), "w"), indent=2)
    print(f"[tts] total {cursor:.1f}s -> {outdir}/timings.json")
    if degraded or not key:
        print("[tts] NOTE: audio is silent placeholder. Re-run this step once "
              "ElevenLabs is reachable, THEN re-render -- shot lengths come "
              "from the real audio.")


if __name__ == "__main__":
    main(sys.argv[1])
