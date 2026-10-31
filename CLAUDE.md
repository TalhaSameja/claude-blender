# claude-blender

Automated vertical-video pipeline for the Instagram/YouTube channel
**`@ayeyoowhatsthisshit`** — deadpan absurdist comedy that *feels*
informational.

## Read `docs/HANDOFF.md` first

It is the complete project context: architecture, measured benchmarks, the
bugs already fixed, two rounds of review findings, environment constraints,
and what to do next. Do not start work without it.

## Rules that matter

**Every narrated line must be SHOWN on screen.** The first cut of ep002
narrated a cloud's arrest and trial over footage of a man in an empty street.
That is the failure mode to avoid. `pipeline/bpl/subjects.py` is the library
of things-an-episode-is-about; when a script mentions something, build it.

**Preview before rendering.** `pipeline/preview_episode.py` renders one frame
per shot in about a minute. A full render is ~17 minutes. Framing errors are
invisible in the episode JSON — a camera inside a building, props outside the
frustum — and the preview catches them.

**Audio first, then render, then assemble.** Shot lengths derive from the
narration, never the reverse.

**Nothing in a frame may need a licence.** Every visual is generated from
primitives. No stock footage, no downloaded models, no trending audio. This
is a hard requirement, not a preference.

**Do not switch to EEVEE.** There is no GPU; EEVEE falls back to a software
rasteriser at 60s/frame, five times slower than Cycles, and looks worse.

**Do not re-enable the Cycles denoiser.** It cost ~10× the sampling it was
cleaning. See `docs/DECISIONS.md`.

## Commands

```bash
.venv-bpy/bin/python pipeline/preview_episode.py content/episodes/epNNN.json
```

```bash
.venv-bpy/bin/python tools/tts.py content/episodes/epNNN.json
```

```bash
.venv-bpy/bin/python pipeline/render_episode.py content/episodes/epNNN.json
```

```bash
.venv-bpy/bin/python tools/assemble.py content/episodes/epNNN.json
```

## Docs

| File | Contents |
|---|---|
| `docs/HANDOFF.md` | **Start here** — full project context |
| `docs/DECISIONS.md` | Benchmarks and why the settings are what they are |
| `docs/REVIEWS.md` | Two critic passes; what landed and what is still open |
| `docs/STRATEGY.md` | Positioning, monetisation, policy risk |
| `docs/IDEAS.md` | Channel concept and 60 ready episode titles |
| `deliverables/` | Finished videos and reference stills |
