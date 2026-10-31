#!/usr/bin/env python3
"""Adopt narration generated elsewhere.

Drop files named line_000.mp3, line_001.mp3 ... into output/<id>/audio/ and
run this. It probes each file's real duration and writes timings.json, which
is what the renderer reads for shot lengths. Use this when ElevenLabs is
generated on another machine.

    python3 tools/import_audio.py content/episodes/ep002.json

Then re-render and assemble -- shot lengths come from these durations, so the
render must follow the audio, not precede it.
"""
import json, os, sys, subprocess, glob


def probe(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                        "format=duration", "-of", "csv=p=0", path],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return None


def main(ep_path):
    ep = json.load(open(ep_path))
    outdir = os.path.normpath(os.path.join(
        os.path.dirname(os.path.abspath(ep_path)), "..", "..", "output", ep["id"]))
    adir = os.path.join(outdir, "audio")
    if not os.path.isdir(adir):
        sys.exit(f"no audio dir at {adir} -- create it and add line_NNN.mp3 files")

    timings, cursor, missing = [], 0.0, []
    for i, shot in enumerate(ep["shots"]):
        hits = sorted(glob.glob(os.path.join(adir, f"line_{i:03d}.*")))
        hits = [h for h in hits if not h.endswith(".json")]
        if not hits:
            missing.append(i)
            continue
        path = hits[0]
        dur = probe(path)
        if dur is None:
            sys.exit(f"ffprobe could not read {path}")
        dur += shot.get("pad", 0.25)
        timings.append({"index": i, "line": shot.get("line", ""), "audio": path,
                        "duration": round(dur, 3), "start": round(cursor, 3)})
        cursor += dur
        print(f"[import] {i:03d} {dur:5.2f}s  {os.path.basename(path)}")

    if missing:
        sys.exit(f"missing audio for shot(s): {missing}. Expected "
                 f"line_NNN.<ext> in {adir}")

    json.dump(timings, open(os.path.join(outdir, "timings.json"), "w"), indent=2)
    print(f"[import] {len(timings)} lines, {cursor:.1f}s total -> "
          f"{outdir}/timings.json")
    print("[import] now re-render, then assemble.")


if __name__ == "__main__":
    main(sys.argv[1])
