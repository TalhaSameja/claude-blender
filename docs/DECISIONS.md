# Technical decisions and measurements

Everything here was measured on the build machine: **4 CPU cores, 15 GB RAM,
no GPU** (`/dev/dri` absent). Re-measure before changing any of it.

## Why Blender as a Python module

`pip install bpy` (Blender 5.2.3) rather than a desktop install. Runs fully
headless, needs no display server, and installs in a venv like any other
dependency. `download.blender.org` is blocked by the container's network
policy anyway, so PyPI was also the only route in.

Needs the GL runtime present or Cycles will not initialise:

```bash
sudo apt-get install -y libegl1 libgl1 libglx-mesa0 libgles2 libxkbcommon0 libsm6 libxrender1 libxi6 libxxf86vm1 libxfixes3
```

## Render engine: Cycles, not EEVEE

| Engine | s/frame @1080×1920 | Notes |
|---|---|---|
| Workbench | 1.3 | Fast but no real materials |
| **Cycles** | **1.14** | 4 samples, denoiser off |
| EEVEE | 60.2 | Software rasteriser; also renders broken-dark |

EEVEE is GPU-first. With no GPU it falls through to llvmpipe and is **five
times slower than Cycles** while looking worse. Do not switch to EEVEE as an
"optimisation".

## The denoiser was the bottleneck

| Settings (1080×1920) | s/frame |
|---|---|
| 16 samples + denoise | 12.18 |
| 8 samples + denoise | 14.2 (measured on a lit scene) |
| **4 samples, denoise off** | **1.14** |
| 1 sample, denoise off | 0.57 |

OpenImageDenoise on CPU cost roughly 10× the sampling it was cleaning, and
flat/toon shading produces almost no noise to clean. Turning it off and
dropping to 4 samples is the single biggest win in the pipeline.

**`sun.data.angle = 0`** removed what noise remained — soft shadows were the
only remaining stochastic source. A hard sun lets 4 samples render clean.

**`max_bounces = 0`** (direct light only). Consequence: the world sky is not a
light source, so interiors render black on surfaces facing away from the key.
Interior shots set `"fill": true`, which adds an opposing fill sun for the
cost of one extra shadow ray.

## Real-episode cost

Synthetic benchmarks use one object and are optimistic. Measured on real
episodes with dressed sets (~100 objects/scene):

| Episode | Frames | Time | s/frame |
|---|---|---|---|
| ep001 (10 shots, 4 sets) | 1026 | 16.9 min | 0.99 |
| ep002 (8 shots, 5 sets) | 762 | 13.6 min | 1.07 |

**Scene complexity dominates, not sample count** — a dressed set costs ~3× a
bare one. Budget **~1.0 s/frame at 720×1280** and **~3 s/frame at 1080×1920**.

A 60s 1080p episode is therefore a little over an hour, unattended. At the
owner's 2/day target that is comfortably within a day's slack, so **rendering
is not the bottleneck — writing is.**

## Why the output is 720×1280, not 1080×1920

Both are supported (`"res"` per shot). 720 renders ~3× faster and is well
within what Reels and Shorts accept. Switch to 1080 for the final cut of a
video that is performing; draft at 720.

## Audio

**Shot length derives from narration**, never the reverse. `timings.json` is
the contract between the audio stage and the renderer; the assembler refuses
to run if the rendered manifest disagrees with it.

**Per-shot `pad`** adds a beat of silence after a line. The rendered shot is
clip + pad, so the audio concat must interleave silence of the same length or
`-shortest` truncates the episode.

**The ambient bed** is generated from ffmpeg's `sine` and `anoisesrc` — so it
is original by construction and carries no licence risk. Trending audio is the
most common way an otherwise-original channel loses monetisation.

Levels, after two passes:

| | mean |
|---|---|
| Narration | −23.6 dB |
| Bed | −42.5 dB |
| Gaps between lines | −38 dB → **−31.6 dB** |

At the first attempt the bed sat 34 dB under the voice and was inaudible, and
`amix`'s default normalisation pulled the narration down 6 dB on top. Fixed
with `normalize=0` and the bed at −12 dB.

## Captions

Composited as **ASS subtitles**, not rendered in Blender and not drawn with
`drawtext`. ASS gives the heavy outline the reference clips use and allows
per-word colour inline. It also means caption and chyron changes need only a
re-assemble (seconds) rather than a re-render (minutes).

Geometry, derived from where the platforms put their own UI:

| | value | why |
|---|---|---|
| Caption baseline | 67% of height | 82% sat under IG's like/comment/share buttons |
| Side margins | 12.5% of width | keeps text clear of the right-hand action column |
| Max chars/card | 18 | 24 bold glyphs at this size ≈ the full 720px width |
| WrapStyle | 0 | 2 (no wrap) let long cards run off frame |

The chunker splits at sentence boundaries first, pushes a trailing weak word
(article/preposition/conjunction) onto the next card, and merges a one- or
two-word final card back — stranding the payoff noun kills the joke.

`"caption": false` on a shot suppresses its caption where the shot's own 3D
type carries the line.

## 3D text

Blender text objects render real lettering. Needed wherever the gag *is* the
words — a case number read aloud has to be legible on screen or the beat is
wasted. See `subjects.case_file`, `subjects.sign`, `subjects.text3d`.

## Palette

Two themes in `bpl/style.py`:

- **`pastel`** — bright toy-city, matches the suitcase reference
- **`retro`** — muted sage/teal/cream with rust accents, matches the
  `@ro14z_3f` reference. **This is the house look.**

At this shading level, similar values merge into one flat mass. The courtroom
was an unreadable brown hole until floor, walls, panelling and bench were
given four distinct values.
