#!/usr/bin/env python
"""Render an episode's shots to PNG sequences.

Run with the bpy venv:
    .venv-bpy/bin/python pipeline/render_episode.py content/episodes/ep001.json

Shot timing comes from the narration audio (timings.json, written by
tools/tts.py). If that file is missing the renderer falls back to the
estimated durations in the episode file, so the pipeline is runnable before
any ElevenLabs key exists.
"""
import bpy, json, sys, os, time, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bpl import world, sets, human, kit, style

D = math.radians


def build_shot(shot, fps, nframes, seed=0):
    sc = world.new_scene(res=shot.get("res", "1080"), fps=fps,
                         samples=shot.get("samples", 4),
                         shading=shot.get("shading", "soft"),
                         sky=None,
                         theme=shot.get("theme", "pastel"))
    sc.frame_start = 1
    sc.frame_end = nframes

    sets.build_set(shot.get("set", "street"), seed=seed)

    subject = (0.0, 0.0, 1.0)
    actor = shot.get("actor")
    if actor:
        root, joints = human.build(
            "hero",
            loc=tuple(actor.get("loc", (0, 0, 0))),
            hoodie=actor.get("hoodie", "hoodie"),
            trouser=actor.get("trouser", "trouser"),
        )
        root.rotation_euler = (0, 0, D(actor.get("yaw", 180)))
        act = actor.get("action", "idle")
        if act == "walk":
            human.walk(joints, root, 1, nframes,
                       step_frames=max(4, int(fps / 2.4)),
                       distance=actor.get("distance", 3.0),
                       direction=tuple(actor.get("direction", (0, 1))))
        else:
            human.pose(joints, getattr(human, act.upper(), human.IDLE), frame=1)
        subject = (root.location.x, root.location.y, 1.0)

    for p in shot.get("props", []):
        if p["type"] == "suitcase":
            kit.suitcase(loc=tuple(p.get("loc", (1, 0, 0))),
                         scale=p.get("scale", 1.0),
                         color=p.get("color", "hoodie"))
        elif p["type"] == "box":
            kit.box(tuple(p["loc"]), tuple(p["scale"]), p.get("color", "accent"))

    sets.rig(shot.get("cam", "medium"), subject=subject,
             frame_start=1, frame_end=nframes, seed=seed)
    return sc


def main(ep_path):
    ep = json.load(open(ep_path))
    root = os.path.dirname(os.path.dirname(os.path.abspath(ep_path)))
    outdir = os.path.join(os.path.dirname(os.path.abspath(ep_path)),
                          "..", "..", "output", ep["id"])
    outdir = os.path.normpath(outdir)
    os.makedirs(outdir, exist_ok=True)

    fps = ep.get("fps", 24)
    timing_path = os.path.join(outdir, "timings.json")
    timings = json.load(open(timing_path)) if os.path.exists(timing_path) else None
    if timings:
        print(f"[render] using narration timings from {timing_path}")
    else:
        print("[render] no timings.json -- using estimated durations")

    manifest = []
    t0 = time.time()
    for i, shot in enumerate(ep["shots"]):
        dur = (timings[i]["duration"] if timings and i < len(timings)
               else shot.get("dur", 3.0))
        nframes = max(1, int(round(dur * fps)))
        sdir = os.path.join(outdir, f"shot_{i:03d}")
        os.makedirs(sdir, exist_ok=True)
        sc = build_shot(shot, fps, nframes, seed=ep.get("seed", 0) + i)
        sc.render.filepath = os.path.join(sdir, "f_")
        st = time.time()
        bpy.ops.render.render(animation=True)
        el = time.time() - st
        print(f"[render] shot {i:03d}  {nframes:4d}f  {dur:5.2f}s  "
              f"{el:6.1f}s render  ({el/nframes:.2f}s/frame)", flush=True)
        manifest.append({"index": i, "dir": sdir, "frames": nframes,
                         "duration": dur, "line": shot.get("line", "")})

    json.dump({"id": ep["id"], "fps": fps, "shots": manifest},
              open(os.path.join(outdir, "render_manifest.json"), "w"), indent=2)
    total = time.time() - t0
    frames = sum(m["frames"] for m in manifest)
    print(f"[render] DONE {frames} frames in {total/60:.1f} min "
          f"({total/max(1,frames):.2f}s/frame avg) -> {outdir}")


if __name__ == "__main__":
    main(sys.argv[1])
