# HANDOFF — read this first

You are picking up a working project mid-flight. This file is the complete
context: what it is, what exists, what has been tried, what is broken, and
what to do next. Read it before touching anything.

**Repo:** https://github.com/TalhaSameja/claude-blender
**Owner:** Talha Sameja — backend/full-stack engineer (MERN, NestJS,
PostgreSQL), currently interning. Comfortable in code; this is his project,
not a client's.
**Status as of handoff:** pipeline works end to end, two episodes finished
with real narration, quality raised through two external review passes.

---

## 1. What this project is

An automated pipeline that produces vertical (9:16) short-form videos for a
new Instagram + YouTube Shorts channel.

**Channel handle: `@ayeyoowhatsthisshit`** — the owner chose this and
confirmed it after I argued against it. Do not relitigate. (My objection, for
the record: it is hard to spell from hearing it, and its excited-reaction
energy pulls against the deadpan the content depends on. He decided. Move on.)

**The content:** absurd, out-of-context, deliberately nonsensical comedy that
*feels* informational. A straight-faced institutional frame — a news
bulletin, a court case, a product recall — wrapped around a subject that
cannot possibly participate in it. The narrator must never seem amused.

**Posting target:** 2 videos/day — 1/day on YouTube, 2/day on Instagram.

**Hard requirement: copyright-free.** Every visual is generated from
primitives in code. No stock footage, no downloaded models, no third-party
textures, no trending audio. The owner wants a brand he can monetise and
build on, so nothing in a frame may need a licence.

---

## 2. Current state

| | |
|---|---|
| Pipeline | Working end to end |
| Episodes finished | 2, with real ElevenLabs narration |
| `ep001` | "Why Do Suitcases Have Wheels?" — 42.8s, 10 shots |
| `ep002` | "A Cloud Has Been Charged With Loitering" — 31.8s, 8 shots |
| Review passes | 2 (external critic agent); findings in `docs/REVIEWS.md` |
| Render cost | ~1.0 s/frame at 720×1280 on 4 CPU cores, no GPU |

Finished videos: `deliverables/videos/`. Contact sheets of both:
`deliverables/stills/current/`.

**`ep002` is the stronger of the two** and is the template to follow. `ep001`
is structurally weaker — its gag does not arrive until ~16s.

---

## 3. How the pipeline works

An episode is a **JSON file**. Nothing is modelled by hand; sets, props and
the character are generated from primitives, which is what keeps the output
licence-clean and makes a new episode a *writing* job rather than a 3D job.

```
content/episodes/epNNN.json   ← the episode: shots, sets, cameras, props, lines
        │
        ├── tools/tts.py            narration → output/<id>/audio/line_NNN.mp3
        │                           + timings.json  (ElevenLabs; see §7)
        ├── pipeline/render_episode.py   shots → PNG sequences
        └── tools/assemble.py       frames + audio + ASS captions → final .mp4
```

**Shot length comes from the narration audio**, never the other way round.
That is why the order matters: audio first, then render, then assemble. The
assembler refuses to run if the rendered shot lengths disagree with
`timings.json`.

### The one tool you should use constantly

```bash
.venv-bpy/bin/python pipeline/preview_episode.py content/episodes/ep001.json
```

Renders **one frame per shot** at low resolution and tiles them into a contact
sheet — about a minute for a ten-shot episode, against ~17 minutes for a real
render. It exists because framing errors are invisible in the JSON. On its
first run it immediately caught a shot rendering **completely black** (camera
placed inside a building) and the central gag of ep001 with **both props
outside the camera frustum**. Always preview before rendering.

### Module map

```
pipeline/
  bpl/style.py      palette + material library. Two themes: "pastel", "retro".
  bpl/world.py      scene bootstrap, render settings, lighting, camera
  bpl/kit.py        generic props: buildings, trees, roads, suitcase
  bpl/human.py      low-poly character: joints, poses, walk cycle
  bpl/subjects.py   story props: cloud, courtroom, car park, courthouse,
                    press mics, rain, wheel, kerb, crowd, 3D text, case file
  bpl/sets.py       named sets + camera rigs
  render_episode.py renders an episode
  preview_episode.py contact sheet (use this)
tools/
  tts.py            ElevenLabs narration → per-line audio + timings.json
  split_audio.py    one long take → per-line clips (see §7)
  import_audio.py   externally-made audio → timings.json
  assemble.py       frames + audio + captions → final MP4
  make.sh           runs tts → render → assemble
content/episodes/   episode scripts (JSON)
content/scripts/    narration text, incl. Eleven v4 tagged versions
deliverables/       finished videos + reference stills (tracked on purpose)
docs/               this file, STRATEGY, IDEAS, DECISIONS, REVIEWS
```

### Setup from scratch

```bash
python3 -m venv .venv-bpy && .venv-bpy/bin/pip install bpy
```

```bash
sudo apt-get install -y libegl1 libgl1 libglx-mesa0 libgles2 libxkbcommon0 libsm6 libxrender1 libxi6 libxxf86vm1 libxfixes3
```

Blender runs as a **Python module** (`bpy`), not a desktop install — fully
headless. The apt packages are the GL runtime Cycles needs.

---

## 4. Non-obvious technical decisions

These were all measured, not guessed. Changing them without re-measuring will
make things worse. Full detail in `docs/DECISIONS.md`.

**Cycles at 4 samples with the denoiser OFF.** The OpenImageDenoise pass cost
~10× more than the sampling it was cleaning, and flat cartoon shading has
almost no noise to clean. 1080×1920 went from **12.18 s/frame → 1.14 s/frame**.

**Sun angular diameter = 0.** Soft shadows were the only remaining noise
source. Hard sun lets 4 samples render clean.

**EEVEE is unusable here.** With no GPU it falls back to a software
rasteriser and renders at **60 s/frame** — five times slower than Cycles, and
the output is broken-dark. Do not "optimise" by switching to EEVEE.

**`max_bounces = 0`** (direct light only). Consequence: the world sky is *not*
a light source, so interiors go black on every surface facing away from the
key. Interior shots must set `"fill": true`.

**Scene complexity dominates, not sample count.** A dressed set costs roughly
3× a bare one. Budget ~1.0 s/frame at 720×1280 and ~3 s/frame at 1080×1920.

**Captions are composited, not rendered.** Caption and chyron changes need
only a re-assemble (seconds), not a re-render (minutes).

---

## 5. Bugs already found and fixed — do not reintroduce

Each of these cost real time. They are fixed; this is so you recognise them.

1. **`matrix_parent_inverse` on a stale `matrix_world`.** Building a figure
   and reading `parent.matrix_world` before the depsgraph has evaluated gives
   garbage — the character rendered as a featureless box. Children now carry
   plain local offsets and no inverse is set.
2. **Blender 5.x removed `action.fcurves`** (slotted actions). Setting
   `preferences.edit.keyframe_new_interpolation_type` up front is both
   version-proof and cheaper than walking curves.
3. **Lateral limb poses used `rx`.** Limbs hang along −Z, so `rx` swings them
   forward/up, not out. Lateral motion needs `ry`.
4. **Variable shadowing broke every caption file.** A local named `head` (the
   headline text) clobbered the `head` holding the ASS header, so the file
   began with a headline instead of `[Script Info]` and ffmpeg rejected it.
5. **`BorderStyle 3` takes its box colour from `OutlineColour`, not
   `BackColour`.** White-on-white made the LIVE pill invisible.
6. **Captions sat under the platform UI.** At 82% of frame height they were
   beneath Instagram's like/comment/share buttons. Now 67%, side margins
   12.5%.
7. **Caption cards overflowed the frame.** 24 bold glyphs at this size ≈ the
   full 720px width. Capped at 18 with real wrapping (`WrapStyle 0`).
8. **The narration track was short by `sum(pad)`.** Shots render for clip +
   pad but the audio concat used clips alone, so `-shortest` truncated the end
   of every episode (ep002 lost 2.4s). Silence of the same pad is now
   interleaved.
9. **`amix` normalises by default**, pulling the narration down 6 dB when the
   music bed was mixed in. Use `normalize=0`.
10. **Stale `render_manifest.json` let a half-finished render be assembled**
    as if complete — a silently wrong cut. The renderer now deletes the
    manifest and wipes shot directories at start, and the assembler refuses a
    manifest that disagrees with `timings.json`.
11. **`pgrep -f "<pattern>"` matches the waiting process itself** when the
    pattern appears in its own command line. Two wait-loops deadlocked against
    each other. Poll for a file marker instead.

---

## 6. What the reviews said (two passes, external critic)

Full reports in `docs/REVIEWS.md`. The short version:

**Fixed:** captions under the platform UI; captions clipping frame edges;
punchline words stranded on their own card; invisible LIVE pill; low-contrast
chyron; a case-number shot that showed no number; 11.5s of literal silence in
a 31.8s video; the suitcase reading as "a filing cabinet".

**Still open — these are your next jobs:**

1. **`ep002`'s opening still does not read as a courtroom.** Flagged in both
   reviews. "A cloud in a brown crate on a loading dock." The judge is a
   ~20px speck; there is no gallery, no rail, no second figure. The whole joke
   depends on the institution being unmistakable in frame one.
2. **`ep001` has no hook.** A static shot holds for 3.7s before the first cut,
   and the gag does not arrive until ~16s. Verdict: "a history lecture with
   props." This is a *script* problem, not a rendering one.
3. **Two shots should be cut entirely** — ep002's courthouse colonnade
   ("cloud shrunk to a dot, no joke") and ep001's crowd shot ("three identical
   figures standing still"). Both need the narration line rehomed, so it is a
   script edit.
4. **Gerald's shot reads as split-screen** — cloud over green field, Gerald on
   grey asphalt, hard horizon between them. In frame together but not in the
   same *space*.
5. **No SFX.** The music bed is in; discrete effects (gavel, camera shutters,
   rain) are not. They must be original or properly licensed.

---

## 7. Environment constraints that will bite you

**ElevenLabs is blocked from the container.** `api.elevenlabs.io` is denied by
the session's network policy (403 at the proxy). `tools/tts.py` degrades to
silent placeholders rather than crashing. The owner has a **paid commercial
ElevenLabs plan** and generates audio himself in the web UI.

To fix: add `api.elevenlabs.io` under Allowed domains in the environment's
network settings (cloud environment menu in the title bar → Edit).

**The owner-generated-audio workflow**, which currently works:

1. Hand him the tagged script from `content/scripts/epNNN_v4.txt`. He pastes
   the whole thing into Eleven v4 as **one** generation.
2. He returns one long take.
3. `tools/split_audio.py` splits it into per-line clips on the silences.
4. `tools/import_audio.py` probes real durations → `timings.json`.
5. Render, then assemble.

**Why `split_audio.py` has a word-count aligner:** Eleven v4 honours mid-line
tags like `[slight pause]` with gaps *the same length* as the gaps between
lines — measured 0.59–0.71s across all eleven gaps in a real take. No silence
threshold separates them. So when it finds more segments than lines, a
dynamic program groups them by each line's share of the word count. It
merged exactly the three lines carrying a mid-line pause. Too *few* segments
still fails loudly.

**Narration pace is ~95 wpm**, not the 165 wpm I first estimated from the
reference clips. Deadpan needs room. Real episodes run ~40% longer than
word-count estimates.

**Voice settings:** Eleven v4, Stability toward **Robust (~75%)**, Similarity
~75%. Consistency matters more than expressiveness for a recurring narrator.
Tags stay sparse — over-tagging makes v4 *perform*, and performing kills the
format.

---

## 8. The reference material

The owner supplied **14 reference clips**. Frame grids of the key ones are in
`deliverables/stills/reference/`.

| File | What it is |
|---|---|
| `ref-A_ro14z3f_news-court.png` | **The one he called "a good example."** Low-poly 3D, muted retro palette, a tsunami arrested, tried and sentenced. News chyrons. This is the north star. |
| `ref-B_suitcase-escalation.png` | Low-poly pastel city, deadpan escalation — the basis for ep001 |
| `ref-C_crane-explainer.png` | Mid-poly architecture explainer with keyword pills |
| `ref-D_dogfiguresitout-monologue.png` | Rounded 3D cartoon, ranting monologue, bold captions with highlight words |
| `ref-E_explaining-infographic.png` | Dark moody 3D, persistent title header, timeline infographic |
| `ref-F_dayzero-2d-hud.png` | 2D flat motion graphics with HUD overlays |
| `ref-G_2d-cartoon-dialogue.png` | 2D vector cartoon dialogue |
| `ref-H_samcotton-stock-doodle.png` | Stock wildlife + doodled props. **Avoid this approach** — it is the one reference with real licensing exposure. |

**The shared DNA across all 14** — this is the actual format:

- Vertical 9:16, **40–95 seconds** (median ~70s). Not 15-second loops.
- Deadpan voice-over drives everything; the visual illustrates, never carries
  the joke alone.
- Burned-in captions, bottom third, heavy outline, one or two words
  colour-highlighted.
- **An explainer frame wrapped around nonsense.** Documentary *structure*,
  absurd *content*.
- A persistent handle watermark.

---

## 9. The rule that matters most

**Every line must be shown.**

The first cut of ep002 narrated a cloud's arrest, trial and lawyer while
showing a man standing in an empty street — no cloud, no courtroom, no car
park anywhere in it. The owner's response was the most useful feedback in the
project:

> "this is not it ... the videos should show what it is saying the audiance
> will get bored and will have no idea what we are talking about if we do not
> show it atleat put some effort in it"

He is right, and it is the standard to hold. `pipeline/bpl/subjects.py`
exists because of this: it is the library of *things an episode is about*.
When a script mentions something, build it and put it on screen.

---

## 10. Where to start

1. Read `docs/STRATEGY.md` (positioning, monetisation, policy risk) and
   `docs/IDEAS.md` (the concept and 60 ready episode titles).
2. Watch both videos in `deliverables/videos/`.
3. Fix `ep002`'s courtroom opening — highest-value single change.
4. Rewrite `ep001` to lead with its gag.
5. Write ep003 from the `docs/IDEAS.md` bank, in the **ep002 shape**: absurd
   premise stated flatly in the first sentence, procedural detail, escalation,
   one oddly specific fact, deflating landing.

**Before any render, run `preview_episode.py`.**

---

## 11. One standing warning

The owner wants 2 videos/day. YouTube renamed its "repetitious content" rule
to **inauthentic content** on 2025-07-15, explicitly to cover mass-produced
and repetitive uploads. A templated pipeline posting twice daily is exactly
the shape that policy describes.

The mitigation is that **rendering is automatable and writing is not**. Every
episode needs a genuinely original script, varied sets and varied shot counts.
His 1-on-YouTube / 2-on-Instagram split is a good instinct — YouTube is where
the rule bites.

Policy details in `docs/STRATEGY.md` come from third-party reporting;
`support.google.com` was unreachable from this container, so the official
pages were never verified. Say so rather than stating them as fact.
