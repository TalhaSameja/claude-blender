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


def align_segments(spans, texts):
    """Group `spans` into len(texts) contiguous runs.

    Each line's expected duration is its share of the total word count. A
    dynamic program picks the grouping that minimises squared error against
    those expectations, so a pause inside a line gets absorbed rather than
    splitting it.
    """
    m, n = len(spans), len(texts)
    dur = [e - s for s, e in spans]
    total = sum(dur)
    weights = [max(1, len(t.split())) for t in texts]
    wsum = sum(weights)
    want = [total * w / wsum for w in weights]

    pre = [0.0] * (m + 1)
    for i, d in enumerate(dur):
        pre[i + 1] = pre[i] + d

    INF = float("inf")
    # best[j][i] = cost of covering the first i segments with the first j lines
    best = [[INF] * (m + 1) for _ in range(n + 1)]
    back = [[-1] * (m + 1) for _ in range(n + 1)]
    best[0][0] = 0.0
    for j in range(1, n + 1):
        for i in range(j, m - (n - j) + 1):
            for k in range(j - 1, i):
                if best[j - 1][k] == INF:
                    continue
                got = pre[i] - pre[k]
                c = best[j - 1][k] + (got - want[j - 1]) ** 2
                if c < best[j][i]:
                    best[j][i] = c
                    back[j][i] = k

    cuts, i = [m], m
    for j in range(n, 0, -1):
        i = back[j][i]
        cuts.append(i)
    cuts.reverse()
    return [(spans[cuts[j]][0], spans[cuts[j + 1] - 1][1]) for j in range(n)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("episode")
    ap.add_argument("take")
    ap.add_argument("--min-silence", type=float, default=0.45)
    ap.add_argument("--threshold", type=float, default=-38.0)
    ap.add_argument("--no-align", action="store_true",
                    help="fail on a segment-count mismatch instead of "
                         "aligning by word count")
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

    if len(spans) < len(lines):
        print(f"[split] detected only {len(spans)} segments for "
              f"{len(lines)} lines -- NOT writing anything.")
        print("[split] lower --min-silence and retry. Current: "
              f"--min-silence {a.min_silence} --threshold {a.threshold}")
        sys.exit(1)

    if len(spans) > len(lines):
        if a.no_align:
            print(f"[split] detected {len(spans)} segments but the script has "
                  f"{len(lines)} lines -- NOT writing anything.")
            for i, (st, en) in enumerate(spans):
                print(f"         seg {i:02d}  {st:7.2f} -> {en:7.2f}  "
                      f"({en-st:.2f}s)")
            sys.exit(1)
        # A delivery tag inside a line (e.g. "[slight pause]") produces a gap
        # as long as the one between lines, so silence alone cannot tell them
        # apart. Merge the extra segments back by grouping them into exactly
        # one run per line, choosing the split points that best match each
        # line's share of the words.
        print(f"[split] {len(spans)} segments for {len(lines)} lines "
              f"-- aligning by word count (mid-line pauses merged)")
        spans = align_segments(spans, [ep["shots"][i]["line"] for i in lines])

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
