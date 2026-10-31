#!/usr/bin/env python3
"""Turn rendered PNG sequences + narration into the finished vertical video.

Captions are generated as ASS rather than drawn with drawtext: ASS gives the
heavy outline the reference clips use, and lets individual words be coloured
inline for the highlight-word look without a second filter pass.

Usage: python3 tools/assemble.py content/episodes/ep001.json
"""
import json, os, sys, subprocess, textwrap, re

FONT = "DejaVu Sans"
# ASS colours are &HBBGGRR.
HILITE = "&H003C62D8"     # rust orange -- the highlight colour the
                          # @ro14z_3f reference uses on key words
WHITE = "&H00F2F2F2"
RED = "&H003030CC"
MAX_CHARS = 28            # per caption line, tuned for 1080-wide vertical
CAPS_UPPERCASE = False    # that reference uses sentence case, not caps


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(f"{' '.join(cmd[:6])}... failed:\n{r.stderr[-1500:]}")
    return r


def ts(t):
    h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h:d}:{m:02d}:{s:05.2f}"


def chunks(line, max_chars=MAX_CHARS):
    """Split a line into caption-sized groups, preserving word order."""
    words, out, cur = line.split(), [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > max_chars:
            out.append(cur); cur = w
        else:
            cur = f"{cur} {w}".strip()
    if cur:
        out.append(cur)
    return out or [""]


def style_words(text, hilite):
    """Colour any word listed in `hilite` (case-insensitive)."""
    if not hilite:
        return text
    hset = {h.lower().strip(".,!?") for h in hilite}
    out = []
    for w in text.split():
        if w.lower().strip(".,!?") in hset:
            out.append(f"{{\\c{HILITE}}}{w}{{\\c{WHITE}}}")
        else:
            out.append(w)
    return " ".join(out)


def build_ass(timings, shots, path, width, height):
    ass_header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {width}
PlayResY: {height}
WrapStyle: 2

[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Cap,{FONT},{int(height*0.040)},{WHITE},&H00000000,&H88000000,-1,0,0,0,100,100,0,0,1,{max(3,int(height*0.0045))},2,2,60,60,{int(height*0.16)},1
Style: Band,{FONT},{int(height*0.026)},{WHITE},&H00000000,&H00151515,-1,0,0,0,100,100,0,0,3,0,0,7,{int(width*0.055)},60,60,1
Style: Live,{FONT},{int(height*0.020)},{WHITE},&H00000000,{RED},-1,0,0,0,100,100,0,0,3,0,0,7,{int(width*0.055)},60,60,1

[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
"""
    lines = []
    for t, shot in zip(timings, shots):
        # news-style lower third, held for the whole shot
        ov = shot.get("overlay")
        if ov:
            y = int(height * 0.075)
            start, end = ts(t["start"]), ts(t["start"] + t["duration"])
            if ov.get("live", True):
                lines.append(
                    f"Dialogue: 1,{start},{end},Live,,0,0,0,"
                    f",{{\\an7\\pos({int(width*0.065)},{y})}}  LIVE  ")
            headline = ov.get("headline", "").upper()
            lines.append(
                f"Dialogue: 1,{start},{end},Band,,0,0,0,"
                f",{{\\an7\\pos({int(width*0.065)},{y + int(height*0.034)})}}  {headline}  ")

        text = (t.get("line") or "").strip()
        if not text:
            continue
        parts = chunks(text.upper() if CAPS_UPPERCASE else text)
        # distribute the shot's audio length across its caption chunks by
        # word count, so long chunks hold longer
        weights = [max(1, len(p.split())) for p in parts]
        total_w = sum(weights)
        span = max(0.4, t["duration"] - shot.get("pad", 0.25))
        cur = t["start"]
        for p, w in zip(parts, weights):
            d = span * (w / total_w)
            body = style_words(p, shot.get("hilite"))
            lines.append(f"Dialogue: 0,{ts(cur)},{ts(cur+d)},Cap,,0,0,0,,{body}")
            cur += d
    open(path, "w").write(ass_header + "\n".join(lines) + "\n")
    return path


def main(ep_path):
    ep = json.load(open(ep_path))
    outdir = os.path.normpath(os.path.join(
        os.path.dirname(os.path.abspath(ep_path)), "..", "..", "output", ep["id"]))
    man = json.load(open(os.path.join(outdir, "render_manifest.json")))
    timings = json.load(open(os.path.join(outdir, "timings.json")))
    fps = man["fps"]
    work = os.path.join(outdir, "work"); os.makedirs(work, exist_ok=True)

    # 1. each shot's frames -> a clip
    clips = []
    for m in man["shots"]:
        clip = os.path.join(work, f"shot_{m['index']:03d}.mp4")
        run(["ffmpeg", "-loglevel", "error", "-y", "-framerate", str(fps),
             "-i", os.path.join(m["dir"], "f_%04d.png"),
             "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
             "-preset", "medium", clip])
        clips.append(clip)

    lst = os.path.join(work, "concat.txt")
    open(lst, "w").write("\n".join(f"file '{os.path.abspath(c)}'" for c in clips))
    silent = os.path.join(work, "video.mp4")
    run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0",
         "-i", lst, "-c", "copy", silent])

    # 2. narration -> one track.
    # Each shot is rendered for clip + pad, so the same pad has to exist in
    # the audio as silence. Without it the track is short by sum(pad) and
    # -shortest truncates the end of every episode.
    sil_dir = os.path.join(work, "sil"); os.makedirs(sil_dir, exist_ok=True)
    seq = []
    for i, (t, shot) in enumerate(zip(timings, ep["shots"])):
        seq.append(os.path.abspath(t["audio"]))
        pad = shot.get("pad", 0.25)
        if pad > 0:
            sp = os.path.join(sil_dir, f"pad_{i:03d}.mp3")
            run(["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i",
                 "anullsrc=r=44100:cl=mono", "-t", f"{pad:.3f}",
                 "-c:a", "libmp3lame", "-q:a", "9", sp])
            seq.append(os.path.abspath(sp))
    alst = os.path.join(work, "audio.txt")
    open(alst, "w").write("\n".join(f"file '{p}'" for p in seq))
    voice = os.path.join(work, "voice.m4a")
    run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0",
         "-i", alst, "-c:a", "aac", "-b:a", "160k", voice])

    # 3. captions
    probe = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v",
                            "-show_entries", "stream=width,height",
                            "-of", "csv=p=0:s=x", silent],
                           capture_output=True, text=True).stdout.strip()
    W, H = (int(x) for x in probe.split("x"))
    ass = build_ass(timings, ep["shots"], os.path.join(work, "caps.ass"), W, H)

    final = os.path.join(outdir, f"{ep['id']}.mp4")
    run(["ffmpeg", "-loglevel", "error", "-y", "-i", silent, "-i", voice,
         "-vf", f"subtitles={ass}:fontsdir=/usr/share/fonts",
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
         "-preset", "medium", "-c:a", "aac", "-b:a", "160k",
         "-shortest", "-movflags", "+faststart", final])
    dur = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                          "format=duration", "-of", "csv=p=0", final],
                         capture_output=True, text=True).stdout.strip()
    print(f"[assemble] {final}  {float(dur):.1f}s  {W}x{H}")


if __name__ == "__main__":
    main(sys.argv[1])
