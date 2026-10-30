# claude-blender

An automated vertical-video pipeline. Writes scenes in Blender from plain
JSON, narrates them with ElevenLabs, burns captions, and outputs a finished
9:16 MP4 — with **no third-party assets anywhere in the render path**, so
every frame is original work the channel owns.

- **Strategy, monetisation and policy risk:** [`docs/STRATEGY.md`](docs/STRATEGY.md)
- **Channel concept and 60 ready episode ideas:** [`docs/IDEAS.md`](docs/IDEAS.md)

## How it works

An episode is a JSON file. Each shot names a set, a camera, a pose, some
props and a line of narration:

```json
{"set":"suburb","cam":"closeup","res":"1080","theme":"retro",
 "actor":{"loc":[0,0,0],"yaw":8,"action":"shrug"},
 "props":[{"type":"suitcase","loc":[0.95,-0.35,0]}],
 "overlay":{"headline":"TSUNAMI ESCAPES FROM PRISON","live":true},
 "hilite":["escaped"],
 "line":"A tsunami has escaped."}
```

Nothing is modelled by hand. Sets, props and the character are all generated
from primitives in `pipeline/bpl/`, which is what keeps the output
licence-clean and makes a new episode a writing job rather than a 3D job.

Shot length is taken from the narration audio, so picture and voice can never
drift apart.

## Setup

Blender runs as a Python module — no desktop install, works headless:

```bash
python3 -m venv .venv-bpy && .venv-bpy/bin/pip install bpy
```

On a bare Linux box Cycles also needs the GL runtime:

```bash
sudo apt-get install -y libegl1 libgl1 libglx-mesa0 libgles2 libxkbcommon0 libsm6 libxrender1 libxi6 libxxf86vm1 libxfixes3
```

Set your voice key (any shell that will run the pipeline):

```bash
export ELEVENLABS_API_KEY=sk_...
```

Without the key the pipeline still runs end to end, substituting silent
placeholder audio of the estimated length.

## Making an episode

```bash
.venv-bpy/bin/python tools/tts.py             content/episodes/ep001.json
.venv-bpy/bin/python pipeline/render_episode.py content/episodes/ep001.json
.venv-bpy/bin/python tools/assemble.py        content/episodes/ep001.json
```

Output lands in `output/<id>/<id>.mp4`.

## Render performance

Measured on 4 CPU cores, no GPU.

Synthetic benchmark — one object, which is what isolates the settings:

| Settings (1080×1920) | s/frame |
|---|---|
| 16 samples + denoise | 12.18 |
| 4 samples, denoiser off | **1.14** |

Real episode — `ep001`, 10 shots across 3 sets, ~100 objects per scene:

| | |
|---|---|
| 720×1280, 4 samples | **1.13 s/frame** |
| 809 frames (31s of video) | **15.2 min** |

Scene complexity, not sample count, dominates once a set is dressed: a full
street costs roughly 3× a bare one. Budget **~1.1 s/frame at 720×1280** and
**~3 s/frame at 1080×1920** for real episodes, so a 60-second 1080p episode
is a little over an hour unattended.

The denoiser was costing ~10× more than the sampling it was cleaning up,
while flat-shaded cartoon geometry has almost no noise to clean. Turning it
off and dropping to 4 samples is the single biggest win in the pipeline.
The other half is `sun.data.angle = 0` — soft shadows were the only
remaining noise source.

EEVEE is **not** usable here: with no GPU it falls back to a software
rasteriser and renders at 60s/frame, five times slower than Cycles.

## Layout

```
pipeline/
  bpl/style.py     palette + material library (pastel and retro themes)
  bpl/world.py     scene bootstrap, render settings, lighting, camera
  bpl/kit.py       procedural props: buildings, trees, roads, suitcase
  bpl/human.py     low-poly character rig, poses, walk cycle
  bpl/sets.py      named sets + camera rigs
  render_episode.py
tools/
  tts.py           ElevenLabs narration -> per-shot audio + timings.json
  assemble.py      frames + audio + ASS captions -> final MP4
content/episodes/  episode scripts
output/            renders (gitignored)
```

## Licensing

Every visual is generated from primitives — there is no stock footage, no
downloaded model and no third-party texture in this repo. Two things still
need care: **music** (do not use trending audio) and **voice** (ElevenLabs'
free tier grants no commercial rights; the paid tier is required for
monetised video — verify the current terms yourself). See `docs/STRATEGY.md`.
