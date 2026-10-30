# Channel Strategy

## 1. What the 13 reference videos actually have in common

I pulled frame grids and metadata from every clip you sent. They span four
different production methods, but the *format* underneath is one thing.

| # | Handle / style | Method | Len |
|---|---|---|---|
| 1 | Suitcase escalation | Low-poly pastel 3D, minimal humans | 64s |
| 2 | Crane explainer | Mid-poly 3D architecture, keyword pills | 79s |
| 3 | `@ashutoshwithclaude` | Stylized 3D character + UI card overlays | 74s |
| 4 | Cheetah dialogue | 2D vector cartoon | 111s |
| 5 | `@dayzero.story` | 2D flat motion graphics + HUD overlays | 72s |
| 6 | `@youmadeit3d` | Textured realistic 3D survival build | 74s |
| 7 | `@samcotton` | Stock animal footage + doodled props | 32s |
| 8 | Walnut escalation | Sims-style realistic 3D | 47s |
| 9 | `@explaining` | Dark moody 3D + timeline infographic | 49s |
| 10 | `@dog.figures.it.out` | Rounded 3D cartoon, ranting monologue | 96s |
| 11 | Mingdoo cat comic | Hand-drawn 2D | 20s |

**The shared DNA — this is the actual format:**

1. **Vertical 9:16.** Always.
2. **40–95 seconds.** Median ~70s. These are *not* 15-second loops. This
   matters: you are competing on retention, not on loop count.
3. **Deadpan voice-over drives everything.** The visual illustrates the
   voice; it never carries the joke alone.
4. **Burned-in captions, uppercase, heavy outline, bottom third**, often with
   one or two words colour-highlighted.
5. **An "explainer" frame wrapped around nonsense.** This is the key trick.
   The *structure* is documentary — "the real reason X", "here's how Y
   works" — while the *content* is escalating absurdity. That combination is
   exactly what you described: informational-feeling but fundamentally silly.
6. **A persistent handle watermark** on almost every clip.

## 2. Recommended concept

> **WHY IS IT LIKE THIS**
> *Answers. Not correct ones.*

A recurring character explains, with total confidence and zero evidence, the
history of an ordinary object. The explanation is internally consistent,
escalates into nonsense, and lands on a deflating punchline.

**Why this concept specifically:**

- **The topic bank is infinite.** Every object that exists is an episode.
  You will never run out, which is what a 2-a-day cadence actually requires.
- **The format satisfies all three of your goals at once** — it *feels*
  informational, it's complete nonsense, and the narrator is visibly not
  taking any of it seriously.
- **It builds IP, not just views.** A recurring character is a brand asset.
  Compilation channels and trend-chasing accounts cannot be sold, licensed,
  or merchandised. A character can.
- **It is copyright-free by construction** (see §3).
- **It renders cheaply** on the hardware this pipeline targets.

The character in the repo is a deliberately simple low-poly everyman. Keep him
visually simple — simple characters are what become recognisable at thumbnail
size, and they are cheap to animate.

## 3. The copyright-free requirement — how this pipeline delivers it

This was one of your hard requirements, and it is the main reason to use
Blender rather than stock footage or AI video tools.

Every visual asset is **generated in code from primitives**: cubes, spheres,
cylinders. There is no downloaded model, no stock clip, no scraped image, no
third-party texture anywhere in the render path. You own every frame outright.

That rules out the approach in reference #7 (`@samcotton`), which is built on
stock wildlife footage. It is a genuinely funny format, but it is the one
reference here that carries real licensing exposure.

**The three things that will still get you claimed if you are careless:**

1. **Music.** Do not use trending audio. It is the single most common cause of
   demonetisation on otherwise-original channels. Commission or generate
   original beds and keep the receipts.
2. **Voice.** See the ElevenLabs note below.
3. **Brand/IP references.** Avoid naming real companies as the butt of a joke,
   and never render a real logo.

### ElevenLabs licensing — important

Third-party summaries consistently report that the **free tier grants no
commercial rights and requires attribution**, and that a paid plan (Starter,
~$5/month) is the minimum for monetised video. They also conflict on whether
commercial rights survive cancelling the plan.

I could not reach ElevenLabs' own terms from this environment, so **verify
this on their official terms page before you monetise anything.** Budget for
the paid tier from day one — it is ~$5/month and removes the entire question.

## 4. Monetisation — the honest version

### YouTube

Two paths into the Partner Programme, reported consistently across sources:
1,000 subscribers **plus either** 10 million valid public Shorts views in 90
days **or** 4,000 long-form watch hours. Shorts RPM is low — the realistic
read is that Shorts ad revenue is a slow grind, not the prize.

**The real risk to your plan is the inauthentic content policy.** YouTube
renamed its "repetitious content" rule to "inauthentic content" on
2025-07-15, explicitly to cover *mass-produced and repetitive* uploads. It is
not a ban on AI — the test is whether the finished video adds original value.

**A templated 3D pipeline posting twice a day is precisely the shape of thing
that policy was written for.** This is the single biggest threat to the plan,
and it is worth taking seriously rather than hoping. Concrete mitigations:

- **Every episode gets a genuinely original script.** Never template the
  writing. The script is the thing that makes it original value.
- **Vary sets, camera work, and shot counts** between episodes. The repo
  supports this; use it rather than shipping ten episodes on one set.
- **The recurring character is an asset, not a liability** — a consistent host
  reads as a show, not as mass production.
- **Narrate like a person.** Deadpan, specific, opinionated.

I could not open YouTube's official policy page from this environment
(`support.google.com` is outside this session's allowed network domains), so
everything above is from third-party reporting. **Read the official YPP
policies yourself before you build the whole plan on it.**

### Instagram

Reels Bonuses are invite-only and the reported thresholds conflict badly
across sources — treat every number you read as unverified. Consistent
requirements: professional account, 18+, supported country, original content,
no watermarks from other apps, licensed audio.

The reliable Instagram paths are **Gifts** (~500 followers), **Subscriptions
and Badges** (~10,000), and **brand deals** (~1,000). Treat Instagram as an
audience-building and brand-deal channel, not as an ad-revenue channel.

### Where the money actually is

Ranked by realistic expected value for this kind of channel:

1. **Brand deals** once you have 50–100k engaged followers. Highest RPM by far.
2. **Merch / character IP.** This is the long game, and the whole reason to
   build an original character rather than chase trends.
3. **Licensing the pipeline itself.** You are a backend engineer building an
   automated video factory. That is a product.
4. **Platform ad revenue.** Real, but slowest and lowest.

## 5. On posting twice a day

Two a day is 60 videos a month. Be clear-eyed about where the cost actually
sits:

| Stage | Cost per 60s episode | Automatable? |
|---|---|---|
| Writing the script | 20–40 min | **No — and this is the point** |
| Shot planning (JSON) | 10 min | Partly |
| Narration (ElevenLabs) | ~1 min | Yes |
| Rendering | ~27 min at 1080p, unattended | Yes |
| Assembly + captions | ~2 min | Yes |
| Upload + metadata | 5 min | Yes |

**Rendering is not your bottleneck — writing is.** The pipeline removes
roughly 85% of the manual work, but the 15% it cannot remove is the part that
keeps you inside the inauthentic-content rules.

My honest recommendation: **start at one per day, five days a week.** Build a
buffer of 10 finished episodes before you launch, then go to two a day only
once the writing process is genuinely fast and the quality holds. Shipping 60
mediocre videos a month is a worse outcome than 20 good ones — both for the
algorithm and for the policy risk.

## 6. Launch plan

- **Weeks 1–2** — Lock the character design and caption style. Write and
  render 10 episodes. Post nothing.
- **Week 3** — Launch on both platforms, one per day. Same content both
  places; the formats are compatible.
- **Weeks 4–8** — Watch retention, not views. The metric that matters is
  average view duration as a fraction of length. Cut whatever loses people in
  the first three seconds.
- **Month 3** — If retention holds above ~60%, move to two a day.

## Sources

Policy and monetisation claims above come from third-party reporting; neither
YouTube's nor Instagram's nor ElevenLabs' official pages were reachable from
this environment. Verify before relying on any specific number.

- [YouTube Inauthentic Content Policy 2026](https://newmoneymatrix.org/youtube-inauthentic-content-policy-explained/)
- [YouTube Reused Content Policy guide](https://vidiq.com/blog/post/youtube-reused-content-policy-guide/)
- [YouTube Shorts Monetization 2026](https://vidiq.com/blog/post/youtube-shorts-monetization/)
- [YouTube repetitive content & AI slop 2026](https://ytzolo.com/blog/youtube-repetitive-content-policy-ai-slop-2026/)
- [Instagram Reels monetization requirements 2026](https://fluxnote.io/guides/instagram-reels-monetization-requirements-2026)
- [How to monetize Instagram in 2026](https://www.shopify.com/blog/how-to-monetize-instagram)
- [ElevenLabs commercial rights & output ownership](https://terms.law/ai-output-rights/elevenlabs/)
- [ElevenLabs licensing guide](https://www.licenseorg.com/blog/elevenlabs-licensing-guide-ai-voices)
