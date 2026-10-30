# Concept + Episode Bank

## The pick: **NOTHING NEWS**

> *A news network reporting serious events that cannot possibly happen.*

You flagged the `@ro14z_3f` clip — a tsunami arrested for trespassing, tried
in court, and sentenced to ten years — as the best example. That clip is doing
something more specific than "random absurdity", and it is worth naming,
because it is the thing that makes it work:

**It applies a rigidly serious institutional frame to a subject that cannot
participate in it.** The tsunami is not a joke. The *court* is the joke. The
reporting is deadpan, procedural and utterly committed; the absurdity comes
entirely from the mismatch, never from the narrator winking at you.

That is exactly what you described: out-of-context, doesn't make sense, funny,
somewhat informational, and visibly refusing to take anything seriously.

### Why this beats a generic brainrot channel

- **It is a machine for ideas.** The format is `[institution] × [thing that
  cannot be in that institution]`. Two lists multiplied together. You will
  never have a blank page, which is the only way 2-a-day is survivable.
- **It is informational in shape.** News lower-thirds, timelines, court
  filings, statistics, expert interviews — all the furniture of real
  reporting, wrapped around nothing.
- **It builds a brand, not a feed.** The network *is* the IP: an anchor, a
  logo, a lower-third style, a recurring field reporter. That is sellable.
- **Every asset is yours.** No stock footage, no trending audio, no real logos.

### The generator

| Institutional frame | Impossible subject |
|---|---|
| Criminal trial | Weather event |
| Breaking news bulletin | Abstract concept (Tuesday, patience, the number 6) |
| Product recall | Natural phenomenon (gravity, tides, fog) |
| Sports commentary | Household object |
| Obituary / memorial | Bodily function |
| Parliamentary inquiry | Animal with no agency |
| Insurance claim | Geological feature |
| Workplace tribunal | Colour, sound, or smell |
| Archaeological finding | Something invented last week |
| Health & safety briefing | Emotion |

Pick one from each column. That is the episode.

## 60 episode titles, ready to write

**Trials & legal**
1. A Cloud Has Been Charged With Loitering
2. The Sea Is Suing A Man For Emotional Damages
3. Gravity Found Liable In Three Separate Falls
4. A Hill Has Been Served With An Eviction Notice
5. Tuesday Pleads Not Guilty
6. The Moon Fails To Appear In Court For The Fourth Time
7. A Draught Has Been Fined For Trespassing
8. Fog Released On Bail, Immediately Reoffends
9. The Number Six Denies All Involvement
10. A Pigeon Has Been Granted Diplomatic Immunity

**Breaking news**
11. An Entire Lake Has Gone Missing Overnight
12. Local Hill Confirmed To Be Slightly Taller Than Reported
13. A Staircase Has Stopped Cooperating
14. Scientists Confirm The Sky Is Doing It On Purpose
15. A Man Has Been Walking In The Same Direction Since March
16. Breaking: Nothing Has Happened
17. The Wind Has Issued A Statement
18. A Door Has Been Reported Missing By Its Own Frame
19. Authorities Confirm The Ocean Is Full
20. A Field Has Declared Independence

**Product recalls & corporate**
21. All Spoons Recalled Over Minor Shape Concerns
22. Manufacturer Admits Chairs Were Never Tested
23. The Company That Makes Monday Has Issued An Apology
24. Urgent Recall: Several Thursdays Shipped Incorrectly
25. Bread Company Admits It Does Not Know How Bread Works
26. Stairs Recalled After Widespread Misuse
27. A Firm Has Accidentally Manufactured Too Much Silence
28. Every Sock Produced Since 1994 Was Wrong

**Sport**
29. Live Coverage: A Man Attempting To Open A Jar
30. The National Standing Championships, Day Four
31. Commentary: Two Dogs Deciding Who Goes First
32. World Record Broken For Looking At A Fridge
33. A Queue Has Entered Extra Time
34. Half-Time Analysis Of A Man Reversing Into A Space

**Inquiries & tribunals**
35. Parliamentary Inquiry Into Why Beaches Are Like That
36. A Giraffe Has Been Asked To Explain Itself
37. Tribunal Finds Owl Acted Reasonably
38. Official Investigation Into The Behaviour Of Soup
39. A Committee Has Been Formed To Address The Horizon
40. Inquiry Concludes Nobody Was In Charge Of Autumn

**Obituaries & memorials**
41. A Local Puddle Has Passed Away After A Long Illness
42. Memorial Held For A Sneeze That Never Arrived
43. The Last Original Thursday Has Died Aged Unknown
44. Beloved Pothole Finally Filled After Twelve Years

**Science & archaeology**
45. Archaeologists Discover A Chair From Last Tuesday
46. New Study Finds Most Walls Are Load Bearing By Accident
47. Researchers Confirm Birds Have Been Improvising
48. Ancient Civilisation Discovered Behind A Sofa
49. Scientists Still Unable To Explain The Middle Of A Week
50. Study Finds Ninety Percent Of Doors Open The Wrong Way

**Health, safety & civic**
51. Public Warned Not To Make Direct Eye Contact With The Sea
52. New Guidance Issued On Standing Near Things
53. Residents Told To Remain Calm About The Hill
54. Council Confirms The Roundabout Is Now Self-Governing
55. Safety Briefing: What To Do If You Encounter A Corridor
56. The Government Has Lost A Small Amount Of Weather

**Infrastructure & transport**
57. A Bridge Has Been Suspended Without Pay
58. The Motorway Has Requested Some Time Off
59. Delays Expected After A Roundabout Changed Its Mind
60. A Train Has Been Found Somewhere It Should Not Be

## How to write one (the formula that makes it land)

The reference clip is 102 seconds and follows a strict shape. Copy it:

1. **Cold open, 0–3s.** State the impossible fact flatly, as established
   reality. *"A tsunami has escaped."* No setup, no wink. This is the entire
   retention battle — win it here or lose the video.
2. **Procedural detail, 3–25s.** Treat it completely seriously. Charges,
   dates, named officials, a timeline graphic. The more bureaucratic the
   better. **This is where the "informational" feeling comes from.**
3. **Escalation, 25–70s.** Each beat raises the stakes while keeping the same
   flat tone. The tsunami gets a lawyer. The lawyer has concerns.
4. **A detail that is too specific, ~70s.** One oddly precise fact — a case
   number, an exact distance, a surname. Specificity is what makes absurdity
   funny rather than random.
5. **Deflating landing, last 5–8s.** Undercut everything with something
   mundane. Resist the urge to explain the joke.

**Rules that matter:**

- **Never acknowledge the absurdity.** The moment the narrator finds it funny,
  the audience stops.
- **Short sentences.** Reference clips run ~165 words/minute with hard stops.
- **One idea per caption.** Captions are the pacing instrument.
- **Name things.** "A man" is weaker than "Gerald, 51".
- **Never explain the premise.** Start mid-situation.

## Visual direction

Match the `@ro14z_3f` palette, not bright pastel — use `"theme": "retro"` in
the episode JSON. Muted sage, teal, cream, rust accent. Angular low-poly
figures in dark suits read as "officials" and sell the institutional frame at
almost no polygon cost.

Captions: sentence case, heavy outline, bottom third, with the key word in
rust orange. The assembler does this via the `hilite` field.

News furniture — `LIVE` badge and a lower-third headline band — is available
per shot via the `overlay` field, drawn in the caption layer so it costs no
render time.

## A note on the second format

The pipeline also ships `ep001` ("Why Do Suitcases Have Wheels?"), built on
the escalating-object-history format from your first reference clip. Keep it
as a **secondary format** on the same channel: same character, same voice,
same captions, different frame. Two formats is better than one for the
inauthentic-content rules — it demonstrably is not one template on repeat.
