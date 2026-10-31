#!/usr/bin/env python
"""Render an episode's shots to PNG sequences.

Run with the bpy venv:
    .venv-bpy/bin/python pipeline/render_episode.py content/episodes/ep001.json

Shot timing comes from the narration audio (timings.json, written by
tools/tts.py). If that file is missing the renderer falls back to the
estimated durations in the episode file, so the pipeline is runnable before
any ElevenLabs key exists.
"""
import bpy, json, sys, os, time, math, glob, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bpl import world, sets, human, kit, style, subjects

D = math.radians


def build_shot(shot, fps, nframes, seed=0):
    sc = world.new_scene(res=shot.get("res", "1080"), fps=fps,
                         samples=shot.get("samples", 4),
                         shading=shot.get("shading", "soft"),
                         sky=None,
                         theme=shot.get("theme", "pastel"),
                         fill=shot.get("fill", False))
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
        t = p["type"]
        loc = tuple(p.get("loc", (0, 0, 0)))
        if t == "suitcase":
            kit.suitcase(loc=loc, scale=p.get("scale", 1.0),
                         color=p.get("color", "hoodie"))
        elif t == "box":
            kit.box(loc, tuple(p["scale"]), p.get("color", "accent"))
        elif t == "cloud":
            subjects.cloud(loc=loc, scale=p.get("scale", 1.0),
                           seed=p.get("seed", 0),
                           grumpy=p.get("grumpy", True))
        elif t == "rain":
            subjects.rain(under=loc, w=p.get("w", 3.0), d=p.get("d", 2.0),
                          drop=p.get("drop", 3.0), n=p.get("n", 90))
        elif t == "car":
            subjects.car(loc=loc, yaw=p.get("yaw", 0),
                         color=p.get("color", "wall_d"))
        elif t == "mic":
            subjects.microphone(loc=loc, yaw=p.get("yaw", 0))
        elif t == "press":
            subjects.press_pack(target=tuple(p.get("target", (0, 0, 1.2))),
                                radius=p.get("radius", 1.5),
                                n=p.get("n", 5))
        elif t == "briefcase":
            subjects.briefcase(loc=loc, yaw=p.get("yaw", 0))
        elif t == "document":
            subjects.document(loc=loc, yaw=p.get("yaw", 0))
        elif t == "wheel":
            subjects.wheel(loc=loc, radius=p.get("radius", 0.9),
                           yaw=p.get("yaw", 0))
        elif t == "kerb":
            subjects.kerb(loc=loc, length=p.get("length", 18.0),
                          yaw=p.get("yaw", 0))
        elif t == "crowd":
            subjects.crowd(n=p.get("n", 5), centre=loc,
                           spread=tuple(p.get("spread", (5.0, 2.4))),
                           yaw=p.get("yaw", 0), seed=p.get("seed", 0))
        elif t == "luggage":
            subjects.luggage_pile(loc=loc, n=p.get("n", 4),
                                  seed=p.get("seed", 0))
        elif t == "case_file":
            subjects.case_file(loc=loc, number=str(p.get("number", "704")),
                               defendant=p.get("defendant", "CLOUD"),
                               yaw=p.get("yaw", 0))
        elif t == "sign":
            subjects.sign(p.get("text", ""), loc=loc,
                          size=p.get("size", 0.45),
                          color=p.get("color", "accent"),
                          yaw=p.get("yaw", 0), post=p.get("post", True))
        elif t == "text":
            subjects.text3d(p.get("text", ""), loc=loc,
                            size=p.get("size", 0.4),
                            color=p.get("color", "accent"),
                            yaw=p.get("yaw", 0))
        elif t == "tree":
            kit.tree(loc, h=p.get("h", 2.6), seed=p.get("seed", 0))
        else:
            raise KeyError(f"unknown prop type {t!r}")

    cam = shot.get("camera")
    if cam:
        # Explicit placement. The named rigs are sized around a 1.8-unit
        # figure; sets like a car park or a courthouse need their own framing.
        a = tuple(cam["loc"])
        b = tuple(cam.get("loc_end", cam["loc"]))
        obj, _ = world.camera(a, tuple(cam.get("look", (0, 0, 1.5))),
                              cam.get("lens", 38))
        obj.location = a
        obj.keyframe_insert("location", frame=1)
        obj.location = b
        obj.keyframe_insert("location", frame=nframes)
    else:
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

    # A previous run's manifest and frames must not survive into this one.
    # Leaving them lets a failed or still-running render be assembled from
    # stale frames, which looks like success and produces a wrong cut.
    stale = os.path.join(outdir, "render_manifest.json")
    if os.path.exists(stale):
        os.remove(stale)

    manifest = []
    t0 = time.time()
    for i, shot in enumerate(ep["shots"]):
        dur = (timings[i]["duration"] if timings and i < len(timings)
               else shot.get("dur", 3.0))
        nframes = max(1, int(round(dur * fps)))
        sdir = os.path.join(outdir, f"shot_{i:03d}")
        if os.path.isdir(sdir):
            shutil.rmtree(sdir)       # frame counts change with the audio
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
