#!/usr/bin/env python
"""Render ONE frame per shot at low resolution and tile them into a contact
sheet, so framing can be checked in well under a minute.

Framing mistakes -- a prop outside the frustum, a subject cropped, a close-up
too tight to read -- are invisible in the episode JSON and cost a full render
to discover. At 360px a ten-shot episode previews in roughly 20 seconds
against ~18 minutes for the real thing.

    .venv-bpy/bin/python pipeline/preview_episode.py content/episodes/ep001.json
"""
import bpy, json, sys, os, subprocess, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_episode as R

TILE_W = 360


def main(ep_path, at=0.5):
    ep = json.load(open(ep_path))
    outdir = os.path.normpath(os.path.join(
        os.path.dirname(os.path.abspath(ep_path)), "..", "..",
        "output", ep["id"], "_preview"))
    os.makedirs(outdir, exist_ok=True)
    fps = ep.get("fps", 24)

    shots = []
    for i, shot in enumerate(ep["shots"]):
        s = dict(shot)
        s["res"] = "540"
        # sample mid-shot so camera drift is represented
        n = max(2, int(round(s.get("dur", 2.0) * fps)))
        sc = R.build_shot(s, fps, n, seed=ep.get("seed", 0) + i)
        sc.frame_set(max(1, int(n * at)))
        path = os.path.join(outdir, f"s{i:02d}.png")
        sc.render.filepath = path
        bpy.ops.render.render(write_still=True)
        shots.append(path)
        print(f"[preview] shot {i:02d}  {s.get('set','?'):10s} "
              f"{s.get('line','')[:44]}", flush=True)

    sheet = os.path.join(outdir, "contact_sheet.png")
    cols = min(5, len(shots))
    cmd = ["montage", *shots, "-tile", f"{cols}x", "-geometry",
           f"{TILE_W}x+4+4", "-background", "#222", "-label", "%f", sheet]
    try:
        subprocess.run(cmd, check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        subprocess.run(["convert", *shots, "-resize", f"{TILE_W}x",
                        "+append", sheet], check=True)
    print(f"[preview] contact sheet -> {sheet}")


if __name__ == "__main__":
    main(sys.argv[1], at=float(sys.argv[2]) if len(sys.argv) > 2 else 0.5)
