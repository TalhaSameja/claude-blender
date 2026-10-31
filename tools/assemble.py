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
MAX_CHARS = 18            # 540px of usable width / ~30px per bold
                          # glyph at this size. 24 overflowed the frame.
CAPS_UPPERCASE = False    # that reference uses sentence case, not caps

# Instagram/TikTok overlay their own UI on the bottom ~20% and the right-hand
# ~18% of a Reel. Captions sat at 82% of height, directly under the like,
# comment and share buttons. Everything below is keyed off these.
CAP_BASELINE = 0.33       # caption MarginV as a fraction of height (from foot)
SIDE_MARGIN = 0.125       # left/right margin as a fraction of width


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(f"{' '.join(cmd[:6])}... failed:\n{r.stderr[-1500:]}")
    return r


def make_bed(seconds, dest, tone="institutional"):
    """Generate an original ambient bed with ffmpeg's synth sources.

    Deadpan needs something under it: with pure narration the gaps between
    lines read as broken audio on a phone rather than as comic timing. These
    are generated sine and noise sources, so the bed is original by
    construction and carries no licence risk -- unlike trending audio, which
    is the most common cause of demonetisation on otherwise-original work.
    """
    recipes = {
        # low fifth + filtered rumble: reads as a room with air in it
        "institutional":
            "sine=frequency=55:duration={d}[a];"
            "sine=frequency=82.5:duration={d}[b];"
            "anoisesrc=d={d}:c=brown:a=0.30[n];"
            "[a][b]amix=inputs=2[t];"
            "[n]lowpass=f=220,volume=0.5[nn];"
            "[t][nn]amix=inputs=2:weights=1 0.8,"
            "tremolo=f=0.18:d=0.25,highpass=f=35,volume=-12dB[out]",
        "bright":
            "sine=frequency=110:duration={d}[a];"
            "anoisesrc=d={d}:c=pink:a=0.25[n];"
            "[n]lowpass=f=900,volume=0.4[nn];"
            "[a][nn]amix=inputs=2:weights=1 0.9,"
            "volume=-14dB[out]",
    }
    graph = recipes.get(tone, recipes["institutional"]).format(d=f"{seconds:.2f}")
    run(["ffmpeg", "-loglevel", "error", "-y", "-filter_complex", graph,
         "-map", "[out]", "-ac", "1", "-ar", "44100",
         "-c:a", "aac", "-b:a", "96k", dest])
    return dest


def ts(t):
    h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h:d}:{m:02d}:{s:05.2f}"


def chunks(line, max_chars=MAX_CHARS):
    """Split a line into caption cards.

    Splits at sentence boundaries first, so a punchline clause stays whole,
    then packs words. A trailing card of one or two words is pulled back into
    the previous card where it fits -- stranding the payoff noun on its own
    card ("hundred and four.") kills the joke.
    """
    sentences = [x.strip() for x in re.split(r"(?<=[.!?])\s+", line) if x.strip()]
    out = []
    for sent in sentences:
        cur = ""
        part = []
        for w in sent.split():
            if cur and len(cur) + 1 + len(w) > max_chars:
                part.append(cur); cur = w
            else:
                cur = f"{cur} {w}".strip()
        if cur:
            part.append(cur)
        # A card must not end on a word that leans on the next one, and a
        # final card of one or two words strands the payoff.
        WEAK = {"a", "an", "the", "to", "of", "in", "on", "at", "for", "and",
                "but", "or", "is", "was", "it", "he", "she", "they", "this",
                "that", "has", "have", "had", "by", "with", "from", "as"}
        i = 0
        while i < len(part) - 1:
            words = part[i].split()
            while len(words) > 1 and words[-1].lower().strip(".,!?") in WEAK:
                part[i + 1] = f"{words.pop()} {part[i + 1]}"
                part[i] = " ".join(words)
            i += 1
        if len(part) > 1 and len(part[-1].split()) <= 2:
            if len(part[-2]) + 1 + len(part[-1]) <= max_chars + 10:
                part[-2] = f"{part[-2]} {part[-1]}"
                part.pop()
        out.extend(part)
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
WrapStyle: 0

[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Cap,{FONT},{int(height*0.042)},{WHITE},&H00000000,&H88000000,-1,0,0,0,100,100,0,0,1,{max(3,int(height*0.0050))},2,2,{int(width*SIDE_MARGIN)},{int(width*SIDE_MARGIN)},{int(height*CAP_BASELINE)},1
Style: Band,{FONT},{int(height*0.027)},{WHITE},&H00000000,&H00101010,-1,0,0,0,100,100,0,0,3,{int(height*0.009)},0,7,0,0,0,1
Style: Live,{FONT},{int(height*0.021)},{WHITE},{RED},{RED},-1,0,0,0,100,100,0,0,3,{int(height*0.008)},0,7,0,0,0,1

[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
"""
    lines = []
    for t, shot in zip(timings, shots):
        # news-style lower third, held for the whole shot
        ov = shot.get("overlay")
        if ov:
            x = int(width * 0.055)
            y = int(height * 0.070)
            start, end = ts(t["start"]), ts(t["start"] + t["duration"])
            if ov.get("live", True):
                lines.append(
                    f"Dialogue: 1,{start},{end},Live,,0,0,0,"
                    f",{{\\an7\\pos({x},{y})}}\u00a0LIVE\u00a0")
                y += int(height * 0.040)
            headline = ov.get("headline", "").upper()
            lines.append(
                f"Dialogue: 1,{start},{end},Band,,0,0,0,"
                f",{{\\an7\\pos({x},{y})}}\u00a0{headline}\u00a0")

        if shot.get("caption") is False:
            continue          # the shot's own 3D type carries the line
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

    # Guard against assembling a stale render: if the manifest's shot lengths
    # no longer match timings.json, the frames on disk belong to a different
    # (or unfinished) run.
    if len(man["shots"]) != len(timings):
        sys.exit(f"[assemble] manifest has {len(man['shots'])} shots but "
                 f"timings has {len(timings)} -- re-render first")
    for m, t in zip(man["shots"], timings):
        if abs(m["duration"] - t["duration"]) > 0.01:
            sys.exit(f"[assemble] shot {m['index']} was rendered for "
                     f"{m['duration']:.2f}s but the narration is "
                     f"{t['duration']:.2f}s -- re-render first")
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

    # 2b. mix the bed under the narration
    bed_tone = ep.get("bed", "institutional")
    if bed_tone:
        vdur = float(subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "csv=p=0", voice], capture_output=True,
            text=True).stdout.strip())
        bed = make_bed(vdur + 0.5, os.path.join(work, "bed.m4a"), bed_tone)
        mixed = os.path.join(work, "mix.m4a")
        run(["ffmpeg", "-loglevel", "error", "-y", "-i", voice, "-i", bed,
             "-filter_complex",
             "[0:a]volume=1.0[v];[1:a]volume=1.0[b];"
             "[v][b]amix=inputs=2:duration=first:dropout_transition=0:"
             "normalize=0[out]",
             "-map", "[out]", "-c:a", "aac", "-b:a", "160k", mixed])
        voice = mixed

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
