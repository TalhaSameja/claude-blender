#!/usr/bin/env python3
"""Split one episode-long narration file into per-line clips.

Generating a whole episode as a single take in the ElevenLabs UI is far less
tedious than exporting ten clips by hand -- and it keeps the delivery
consistent across lines, which matters for a recurring narrator. This splits
that take back into line_000, line_001, ... on the silences between lines.

    python3 tools/split_audio.py content/episodes/ep002.json take.mp3

If the detected count does not match the script it says so and changes
nothing, rather than silently misaligning every caption in the episode.
Tune with --min-silence (seconds) and --threshold (dBFS).
"""
import json, os, sys, subprocess, re, argparse


def detect_silences(path, min_sil, thresh):
    r = subprocess.run(
        ["ffmpeg", "-i", path, "-af",
         f"silencedetect=noise={thresh}dB:d={min_sil}", "-f", "null", "-"],
        capture_output=True, text=True)
    starts = [float(m) for m in re.findall(r"silence_start: ([0-9.]+)", r.stderr)]
    ends = [float(m) for m in re.findall(r"silence_end: ([0-9.]+)", r.stderr)]
    return starts, ends


def total_duration(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                        "format=duration", "-of", "csv=p=0", path],
                       capture_output=True, text=True)
    return float(r.stdout.strip())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("episode")
    ap.add_argument("take")
    ap.add_argument("--min-silence", type=float, default=0.45)
    ap.add_argument("--threshold", type=float, default=-38.0)
    a = ap.parse_args()

    ep = json.load(open(a.episode))
    lines = [i for i, s in enumerate(ep["shots"]) if s.get("line", "").strip()]
    outdir = os.path.normpath(os.path.join(
        os.path.dirname(os.path.abspath(a.episode)), "..", "..",
        "output", ep["id"]))
    adir = os.path.join(outdir, "audio")
    os.makedirs(adir, exist_ok=True)

    starts, ends = detect_silences(a.take, a.min_silence, a.threshold)
    dur = total_duration(a.take)

    # Build speech spans from the gaps between detected silences.
    cuts = [0.0]
    for st, en in zip(starts, ends + [dur]):
        cuts.append((st + en) / 2.0)
    cuts.append(dur)
    cuts = sorted(set(round(c, 3) for c in cuts if 0 <= c <= dur))
    spans = [(cuts[i], cuts[i + 1]) for i in range(len(cuts) - 1)
             if cuts[i + 1] - cuts[i] > 0.35]

    if len(spans) != len(lines):
        print(f"[split] detected {len(spans)} segments but the script has "
              f"{len(lines)} lines -- NOT writing anything.")
        print("[split] adjust --min-silence / --threshold and retry. "
              "Current: "
              f"--min-silence {a.min_silence} --threshold {a.threshold}")
        for i, (s, e) in enumerate(spans):
            print(f"         seg {i:02d}  {s:7.2f} -> {e:7.2f}  ({e-s:.2f}s)")
        sys.exit(1)

    for idx, (shot_i, (s, e)) in enumerate(zip(lines, spans)):
        dest = os.path.join(adir, f"line_{shot_i:03d}.mp3")
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", a.take,
                        "-ss", f"{s:.3f}", "-to", f"{e:.3f}",
                        "-c:a", "libmp3lame", "-q:a", "3", dest], check=True)
        print(f"[split] line_{shot_i:03d}.mp3  {e-s:5.2f}s")

    print(f"[split] {len(spans)} lines -> {adir}")
    print("[split] next: tools/import_audio.py, then re-render, then assemble.")


if __name__ == "__main__":
    main()
