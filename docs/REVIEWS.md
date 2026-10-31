# Review history

Two review passes were run by an independent critic agent briefed to be harsh
and specific, and to judge against the reference accounts rather than against
"is this impressive for a procedural renderer". Both reports are summarised
here with what was done about each finding.

Contact sheets of the current cuts: `deliverables/stills/current/`.

---

## Pass 1 — first complete cut of ep002

### Verdict on the opening
> "Shot 0 is a cloud sitting in a brown wooden box with a tiny faceless figure
> and an orange disc behind it. At phone size it does not read as a courtroom
> — it reads as a cloud in a crate. The joke dies because the institution
> isn't visible."

### Findings and outcomes

| Finding | Outcome |
|---|---|
| Captions at 82% height sit under Instagram's like/comment/share buttons | **Fixed** — moved to 67%, side margins 12.5% |
| Caption text clipped both frame edges | **Fixed** — 18 chars/card, `WrapStyle 0` |
| Caption splits strand punchlines ("hundred and four.") | **Fixed** — sentence-boundary splits, tails merged |
| Chyron grey-on-grey, illegible at phone size | **Fixed** — solid black bar, red LIVE pill |
| Case-number shot showed a blank card with grey bars while the narration read out a number | **Fixed** — real 3D type, `CASE No. 704 / DEFENDANT: CLOUD` |
| Gerald shot: cloud cropped out of the strongest line in the script | **Partially fixed** — both now in frame, but see Pass 2 |
| Lawyer is "a blank-faced black blob at the frame edge" | **Fixed** — centred, briefcase in shot |
| Courthouse shot: cloud is a speck in the corner | **Fixed** — moved over the building |
| No pauses before punchlines; zero music | **Fixed** — pads added, ambient bed generated |
| Opening is effectively a still; 2.2s for 5 words | **Not fixed** — still one shot per line |
| No end card, no loop | **Not fixed** |

---

## Pass 2 — both episodes, after the above

The critic was asked to **verify each claimed fix** rather than take it on
trust. Three had not landed.

### Did not land

1. **ep002's courtroom opening.** Verdict: still "a cloud in a brown crate on
   a loading dock. The judge is a ~20px black speck under an orange disc;
   there is no gallery, no rail, no flag, no second figure. Bottom 40% of
   frame is empty brown steps." Widening the lens from 30mm to 26mm was not
   enough — the set itself needs more furniture and the judge needs scale.
   **This is the highest-value open item.**

2. **Gerald's shot reads as split-screen.** "Cloud over green field, Gerald on
   grey asphalt, with a hard horizon between them. Reads as a split-screen,
   not a shared space." They are both in frame but not in the same place.

3. **ep001's opening is a scroll-past.** "A static untextured navy box holds
   the frame for 3.7 seconds. The copy is a question, not an image. Nothing
   moves, nothing is funny, nothing is legible as a suitcase." The suitcase
   prop has since been rebuilt, but the 3.7s static hold remains.

### Landed, then improved further

| Verified | Follow-up |
|---|---|
| Chyron — "solid black bar, red LIVE pill, fully legible at thumbnail size" | — |
| Case-number 3D type | Caption was colliding with the word DEFENDANT → caption suppressed for that shot |
| Beats — but **overdone**: 11.5s of silence in 31.8s (36%), with no music under it. "On a phone that reads as broken audio, not deadpan." | Ambient bed added; gaps lifted from −38 dB to −31.6 dB |
| Caption position verified at 66.1% | Chunker still broke on function words ("A man looked at a", "You pick it up and") → weak-word rule added |
| ep001 rebuild — no black frames, gag props all in frustum | — |

### First three seconds

- **ep002: a scroller stops.** "Angry cloud face, LIVE chyron, 'A cloud has
  been charged.' Absurd premise visible in frame 1. This is the right kind of
  hook."
- **ep001: no. Scroll-past.**

### Stronger video
**ep002, decisively.** "Visual premise in the first frame, an expressive
character, news-format furniture that sells the deadpan. ep001 is a history
lecture with props; its gag only arrives at ~16s and you have no reason to be
there."

### Recommended cuts (not yet done — each needs a script edit)

- **ep002:** the courthouse colonnade shot. "Generic stock-render, cloud
  shrunk to a dot, no joke."
- **ep001:** the crowd shot. "Three identical figures standing still; the line
  does all the work and the image adds nothing."

### Remaining ranked fixes from Pass 2

1. Ambient bed under everything — **done**
2. Texture the suitcase — **done**
3. Cut ep001's opening hold to ~1.2s and lead with the gag — **open**
4. Move ep002's caption off the case card — **done**
5. Harden the chunker's split rule — **done**

---

## How to run another review

Spawn a general-purpose agent, point it at the `.mp4` and a contact sheet,
give it the concept and the reference accounts, and tell it to be merciless
and to **verify each claimed fix rather than trust the summary**. That last
instruction is what caught the three that had not landed.
