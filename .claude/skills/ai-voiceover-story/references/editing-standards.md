# Video editing standards

**This is the main rulebook. It applies to every video.** The style file (`style.md`, next to this one) adds to these rules and can override named defaults. The reviewer's latest notes beat both.

Paid social (Meta, TikTok) performance creative. Read fully before cutting anything. This is the one rulebook for video edits: the `ai-voiceover-story` skill follows it while cutting, and writes new rules back into it when the editor's CapCut changes or review notes teach something new.

Where a rule has a number, the number is the default, not a suggestion. Your reviewer's feedback beats this document; log what changed in section 12.

These rules started as the house standards of a performance creative agency, built from review notes on real ad edits. Make them yours: change any rule your team disagrees with, and add new ones as you review.

**Tags.** Every rule says who handles it:
- `cut`: do it while editing.
- `script`: checked by code (a number or an exact match). Where a script enforces it today, the rule names it (`story_ad.py`, `house_captions.py`); the rest are checked by you before hand-off.
- `eye`: checked by looking at frames or listening.

---

## 1. What a performance edit is for

An ad has one job per second. The first second earns the second, the first three seconds earn the next ten, and everything after that earns the click. Edit backwards from that:

- The hook (0 to 3s) stops the thumb. It is judged on hold rate.
- The body (3s to about 25s) builds belief. It is judged on 50% and 75% completion.
- The close (last few seconds) names the action. It is judged on click-through.

If a cut does not serve one of those three, it is decoration. Remove it.

## 2. Default style: organic

1. **Default to organic** unless the brief says produced: no music unless the reviewer asks for it (section 9), no end card (the end box in section 10 is not one), no transitions, whooshes or sound effects other than the end-box click, no stock footage, and the house text from section 11a (never a display font like Montserrat Black). Captions are lowercase; hook boxes use sentence case or capitals, like the winning ads. `cut`
2. **Never mix organic and produced elements in one ad.** For example: organic text with polished branded before-and-afters, or a single lone greenscreen. `eye`

Sections 9 and 10 (music, end card) apply only when the brief asks for a produced ad.

3. **Style files may override named defaults, never the hook overlay.** For example, an "ugly organic" style skill might turn captions off (overrides 7.6), keep pauses up to about 1.5s (overrides the 0.25s cap in section 4), use no grade and no punch-ins (overrides 5.6) and let length follow the content. A skill that does this says so at the top of its SKILL.md and lists the sections it overrides. `cut`

## 3. Hook text overlay (highest priority, every video)

1. **Every video gets a text overlay on the hook that is not the captions.** Captions alone on the hook are never acceptable. The overlay says something the voice isn't saying: the premise, the category, the tension or the POV. This is how organic ads are run now. `cut` · `script`
2. **While the hook overlay is on screen, hide the captions.** Captions start when it leaves. Show one text element at a time: no headline plus captions plus badge. `cut` · `script`
3. **Hook overlay wording is plain, specific and readable at a glance.** Capitalise "I", "I'm" and proper names (Christmas) even when the hook is supplied in lowercase (reviewer, WHOSKIT v1). Break anything long onto two lines and make the key word biggest. Split a two-part headline into two bubbles (white-on-black, then black-on-white) so the second part pops. Never use internal abbreviations. `cut` · `eye`
4. **The hook overlay stays up until a natural break, then leaves on the exact frame of a camera cut,** at the first scene change (about 5 to 7 seconds in a skit, e.g. the cut to her opening the garage door), even if nobody speaks straight after it; the first caption then appears when the next word starts (reviewer, WHOSKIT v1). Applies to every hook. This also applies to hook text already burned into supplied footage: check it frame by frame, and if it ends early, hold it to the cut. A POV or premise headline can stay for the whole opener. `cut`
5. **The hook has to work muted** and be understood on first read. If the voice doesn't name the category in the first line, the overlay must. `eye`
6. **No logo, no brand name, no "hey guys" in the first three seconds.** `cut`
7. **A hook that is a claim beats a hook that is a question.** "This is why your skin still breaks out after a new routine" beats "Why does my skin keep breaking out?" `cut`

## 4. Pacing

- **Never an inhale or exhale in a voiceover (user, 2026-11-05, every style and brand).** Before any caption or clip is placed, cut every breath and all the dead air between phrases, including at the end of lines. Cut the whole pause, not down to a target gap: keep about 0.03s before the first sound and about 0.15s after the last. Breaths kill the flow and waste time. This comes first, because captions and B-roll are timed to the cut voiceover, so cutting breaths afterwards throws the whole timeline out of sync. It overrides the 0.15s / 0.10s gap targets below for voiceovers. `cut` · `script` (built: `tools/capcut/story_ad.py` `speech_pieces`, which keeps only sound that sits on a transcribed word, tuned on the user's own GIFT4HIM cuts. When the user re-cuts the voiceover in CapCut, read their pieces into `vo_pieces` and rebuild, never nudge the old timeline.)
- **Target length.** Talking-head UGC: 25 to 45 seconds. B-roll plus voiceover: 20 to 35 seconds. Anything over 60 seconds needs a reason written in the brief. `script`
- **Gap between sentences: about 0.15s.** Gap between clauses inside a sentence: about 0.10s. Longer reads as hesitation; shorter sounds like a glitch. `cut` · `script` (built: `story_ad.py` cuts every pause and breath)
- **No pause longer than 0.25s anywhere in the voice track**, except one deliberate beat before the close, which may run to 0.4s. `script` (built: `story_ad.py` cuts every pause and breath)
- **A visual change every 2 to 3 seconds** in the body: a cut, a punch-in, a b-roll insert, a caption appearing, or a callout. `cut`
- **Don't hold a shot too long: about 4s maximum**, shorter on low-motion b-roll, or return to the talking head. `cut` · `script`
- **Front-load.** The strongest proof or most surprising claim goes before the 8-second mark. Most of the audience never sees the end. `cut`
- **Trim room tone off every piece.** About 0.04s lead-in before the first word and about 0.06s tail after the last. Clipping a word's tail ("use", "pool", "free") is the most common audible mistake; when in doubt leave 0.15s of tail. `cut`

## 5. Cutting and structure

1. **Cut filler and throat-clearing:** leading "basically", "like", "okay so", "well", "hey everyone", "yeah", "if you don't know me", "that's it". Keep one only if the join sounds worse without it. "And", "so", "but" and "then" at a sentence start are judged in context: keep them when they carry the story (a contrast, a consequence, the next step), cut them when they are just a verbal run-up and the line reads the same without them. `video-qa` does not flag these four, so the cut is the editor's call. `cut` · `script`
2. **Cut repetition:** any claim, adjective or beat said twice, including the same word stacked across joins. `cut` · `script`
3. **Start later than the creator did.** The first few seconds of a take are usually warm-up, so open on the first line that carries the premise. `cut`
4. **When building hooks or hook variants, scan the whole take** for the strongest 3–4 seconds (a reaction, a line, a moment), not only the scripted hooks. A great moment buried at the end is wasted. `cut`
5. **Cut on silence, not on timecode.** Find the gap in the waveform and cut there. Transcript word timings are a guide, not a cut point; they drift on restarts and repeated words. `cut`
6. **Jump cuts are the default** for talking head. Each one gets an alternating punch-in (about 1.0x then about 1.12x) so the frame changes with the audio. `cut`
7. **Minimum shot length is 0.3s.** Fold anything shorter into its neighbour; slivers of 1 to 7 frames flash like errors. `script`
8. **Take selection:** energy and clarity first, then eye line, then background. Never splice two takes mid-word. `cut`
9. **Remove stumbles, restarts and fillers, then listen to the splice on its own.** A repair that produces "now we, now we" or a half "and" is worse than the original stumble. Never clip the first or last word of a line. `cut` · `script`
10. **Default: don't cut away during the number.** If the creator says "47%" or "three weeks", the face or the proof stays on screen. Exception: a reviewer can ask for b-roll of people using the product over an offer line. `cut`

## 6. Footage and b-roll

1. **B-roll answers "show me".** Insert it when the voice makes a claim that can be seen: texture, before and after, mechanism, unboxing, size in hand. The footage must literally show what the line says. `cut` · `script`
2. **Use the best clip available, not the first one that fits.** Reject dark, blurry, crooked, over-exposed or dull clips. `eye`
3. **Flip mirrored footage.** Front-camera clips show text backwards on phones, boxes and bags, so check any clip containing text. `eye`
4. **Check the background and edges of every shot** for clutter and distractions (socks, studio lights, a TV, a shower caddy over the brand name). Crop, reframe or swap. `eye`
5. **The person on screen matches the persona in the script** (age, gender, situation). Keep the same creator on "I" lines. `eye`
6. **Order of preference:** product in use by the creator > product in use by anyone > product close-up > lifestyle context > screen recording. No stock in organic ads (section 2). `cut`
7. **Ratio and holds.** Talking-head body: 30 to 50% b-roll coverage. B-roll holds 1.5 to 3 seconds. `cut`
8. **Cut b-roll on motion.** Enter a clip while something is moving (a pour, a hand reaching). Entering on a still frame looks like a slideshow. `cut`
9. **Picture-in-picture** is for keeping the creator visible while a demo plays: rounded corners, bottom-left or bottom-right, never covering a caption. `cut`
10. **Verify in-points at quarter-second resolution.** Contact sheets at two-second steps misplace shot changes by about a second. `cut`
11. **B-roll enters between lines, not mid-sentence.** Start an insert on the line's first word (or in the gap before it); switching halfway through a sentence feels like a harsh cut. Exceptions are fine when they're deliberate, e.g. a list where each item gets its own shot, or the product shown as it's named. When a line is meant to be covered, cover it from its start so the A-roll isn't seen for it. Don't leave a flash of A-roll (under about 0.5s) between two inserts; it reads as a glitch. `cut`
11a. **Prefer real people over AI footage when both exist, and show the whole product when showing a feature.** Don't cut to a stranger on a personal line when the speakers can carry it. `cut`
11b. **Colour-correct HDR iPhone clips (HLG) before use,** or they look flat and tinted. `eye`
12. **Show a wearable feature on a person using it,** not on a surface (e.g. a wave sensor being used on someone's head). `cut`
13. **Don't reuse a clip, or a near-identical one, in the same ad.** Two takes of the same prop in the same style (e.g. two handheld shots of the same old product) count as the same clip. If nothing else fits, stay on the creator. `cut` · `eye`
14. **Mix up B-roll between ads.** Before choosing, check which clips recent edits used (their `make_edit.py` files) and pick different ones, even when the old clip works. Reuse one only if nothing else shows the line, and say so in the hand-off. `cut`
15. **Show the product being used on claims about how it performs,** so viewers can picture themselves using it. A product shot on a surface suits a named feature like "230 degree beam". Show the beam in the dark or strongly lit, not in daylight, where it has no impact. `cut`
15a. **Check it's actually our product before using a clip.** Competitors' products can appear in your footage library, sometimes in the same locations as yours. Check a close frame for your product's own shape and details. `eye`
16. **Match the proof to the line.** "So light": someone holding it up on their hand. Scales only when the line names the weight. "Clunky" or "heavy": the old bulky torches being handled roughly so they look heavy. `cut`
17. **When a shot sells the product's features, show the product clearly on the person, switched on and facing camera.** Someone with their back turned doing the activity doesn't show the feature. `cut` · `eye`
18. **Use a mix of people across an ad's shots when the footage allows.** Don't fill every shot with the same creator when there are other relevant clips. `cut`
19. **The hook clip shows the persona's activity at a glance** (a camping ad opens at a campsite), not a generic shot of the product. `cut`

**How the editor picks and times B-roll (from a walkthrough of a finished edit, 2026-11-06, every style):**

20. **Shots hold about 3.5s at most.** Go up to 4s, never more, only when the clip is full of movement (colour swatches being thrown about). A still or slow clip that long is dull. On a long line held by one clip, add a slow punch-in partway through, or cut the same clip into two different angles so it feels like a new scene. `cut`
21. **No clip so short it can't register.** A one- or two-word caption ("plus", "this year") doesn't get its own clip. The clip runs on across it into the next caption. One clip can also run across several captions when it shows one continuous action, like a wave on and off. Not every caption change needs a cut, but every cut is on a caption change (7.8b). `cut`
22. **Dead clips are wasted.** If nothing happens in a clip ("and check this" over a still hand), start the next demo clip earlier instead, for example showing the button press from "and check this". `cut`
23. **Show exactly the line, and check it really happens in the clip.** "Press the button once" needs the button actually pressed on screen. "Greasy hands or gloves" needs someone in gloves, or wiping their hands, using the wave sensor. "Lit up one tiny spot" needs a cheap headlamp's small spot beam, which should look bad. "Turning his head to see" shows the head turning. "Flies drawn to white light" shows bugs at a white light. A feature beat lands on its word: the switch to red light happens on "switch". `cut` · `eye`
24. **Wave sensor clips show the wave on and the wave off in the same shot,** before the scene changes. Speed the clip up (1.4 to 1.7x) to fit both into the line, rather than cutting off the return wave. Skip clips where the light goes on as the voice says "off". If nothing lines up, a clip of someone waving it on and off repeatedly is fine. `cut`
25. **Speed a slow clip up so the whole action fits the line,** rather than cutting it off. Slow one slightly (about 0.9x) when the clip's own next scene would otherwise creep in at the end. `cut`
26. **Keep the story's characters consistent and believable.** Know who the script is about (for example, a woman married 20 years buying for her husband) and show that demographic: an older man for "he" lines, an older couple for "20 years together". The bare minimum is the right person doing the thing: no woman in a stable for "his night vision". Come back to the same man across the ad where you can, and don't jump between strangers on lines about one person. Avoid people who contradict it (a young man for an older husband, or a gift tag saying "dad" on a husband line, which should be cropped out). When no clip fits, use the closest and tell the user, who makes the missing clip. `cut` · `eye`
27. **No two clips of the same thing back to back with different people** (two different men opening socks). They read as one repeated beat with a cast change. `cut`
28. **Only our captions on screen.** Clips found online (TikTok, snaptik) often have their own captions, CapCut template text or watermarks. Use a part of the clip without them, or crop and zoom them out of frame. If neither works, don't use the clip. `eye`
29. **AI clips (for example Higgsfield's `hf_…` files) go at 1.03 scale,** because they sometimes have thin black bars at the edges. Speed slow ones up about 1.1x, and cut before a moment that looks fake. `cut`
30. **Pick the clearest example of the feature or setting.** For "picked him up one of these", prefer the light in someone's hand, front and centre against a plain Christmas background, over a busy shot. For "230-degree wide beam", the whole beam must be visible, not a glimpse. `eye`

## 7. Captions

0. **One caption engine for every video with speech and captions,** whatever the style or brand: voiceover, skit, BOF, talking head or anything new. Build captions, hook and end boxes, and caption timing with `tools/house_captions.py`, and run its `check_spans` before rendering. It fails on blanks, on cuts that aren't on a caption change, and on captions over two lines. Never write new caption code, and never copy a reference ad's caption look over it. Styles with no captions, like Benefit Stack chips, are exempt. A style may only change what its style file names (user, 2026-11-05). `cut` · `script` (built: `check_spans`)
1. **Captions match the spoken words exactly.** After rendering, check the caption words against a transcription of the final audio, separately from the voice-track check. Catch ghost words that survive a cut and doubled words ("every every"). `script`
2. **Brand, product and URL names always appear in their exact house form, every time.** Run a find-and-replace from the brand's name list in the brand notes before export (`fix_words` in the plan). `script`
3. **Spelling follows the brand's market (US or UK), not the creator's accent.** The market is in the brand notes. `script`
4. **House style for numbers and units:** digits with units (45 lbs, 100+, 12 MINUTES, 500 LEDs) and $ on dollar amounts; hyphenated compound modifiers (2-in-1, 90-day money-back guarantee, follow-up, walk-in); "drugstore" as one word. `script`
5. **Captions are lowercase with no punctuation at line ends, except a question mark on a question.** Keep proper names as written (brand names, USB, Christmas) and capitalise "I". `cut`
6. **Captions on every spoken word after the hook overlay leaves,** in sync with the voice, in short phrases of up to two lines, at one fixed position (section 11a). No active-word highlight. No emoji in captions, except a deliberate one for a joke. `cut`
7. **Keep text on screen with no blanks.** Each caption holds until the next one starts, even through a pause, and the first caption appears the moment the hook overlay leaves. A caption only changes once the current speaker has finished. `cut`
8. **List items get their own caption, one at a time, with no commas** ("camping", then "fishing"). `cut`
8a. **Split captions at commas and spoken pauses so viewers can't read ahead of the voice** ("but I'm thinking", then "if we want to"). No commas on screen. `cut`
8ab. **Split where the sentence has its natural break, and leave them wanting the rest** (user, 2026-11-06). "Not only can he" then "switch to red light mode". "This year I didn't want to" then "break the bank": the viewer asks "didn't want to what?", which holds attention. Never the whole sentence in one caption, because they read ahead and drop off. But don't chop so fine that a caption flashes past ("this year" alone, 0.5s). Join it to the next words. `cut`
8ac. **Line breaks (user, 2026-11-06).** Up to about 24 characters fits on one line ("switch to red light mode"). Anything longer is broken by hand into two lines, so it never runs wide into the platform's buttons at the sides. Make the two lines as even as possible ("because his / old headlamp", "so they stay / out of his face"). Never top heavy, with a long top line over one or two words. If they can't be even, a longer bottom line is better. Keep words that belong together on one line, and split the caption instead when they can't be ("this has a", then "230-degree wide beam"). Two stacked lines are fine when the voice reads at the speed of the text. Split into two captions when the line is long and the voice is slower than reading. `cut` · `script` (built: `balance_lines` in `tools/capcut/story_ad.py`)
8aa. **A caption changes on the exact frame its first word starts, through the whole ad.** Take the start from the audio itself, not the transcript's timings, which can be several frames late or early. The B-roll for that line starts on the same frame. `script` (built: `voice_onset` in `Styles/UGC skit/edit_template.py`)
8ad. **When a line starts a new voiceover piece, the caption, the B-roll and the voice piece start on the same tick** (user, 2026-11-06, "complete congruency"). On the timeline the three edges form one straight line. Not a frame before, not a frame after, and not at the word inside the piece. Line them up to where the new voice piece starts. It is neater, and it can't drift out of sync. `script` (built: `story_ad.py` snaps caption and shot starts to the piece start and fails the build if any is off)
8b. **B-roll starts and ends on a caption change, on the same frame.** A caption never spills from one shot into the next. `cut`
8c. **Text changes land on the footage's own cuts:** the hook leaves and the end box arrives on a camera cut, and b-roll never ends a frame or two before one. `cut`
9. **Don't switch caption colour mid-video** without a reason (e.g. a second speaker, applied throughout). `eye`

## 8. On-screen text

1. **All text stays inside the Meta safe zone, which is the centred 4:5 box.** At 1080x1920: x 65 to 1015, y 285 to 1635. Outside it, text is hidden in the feed until someone taps in. This covers hook boxes, end boxes, captions and graphics. Within the box there's no fixed spot for a hook box: place it for the footage under it, clear of faces and the product (8.5a), never by a fixed third of the frame (user, 2026-11-03). `script`
2. **Text legibility:** add a background box, shadow or border when text sits on busy footage. A multi-line background box is one solid joined shape, with no gaps where the lines meet. Never let the text colour disappear against the background. Keep text size consistent across the video and its variations. `eye`
3. **On-screen lists are complete and consistent.** "3 signs" means three are shown. No "#1" without a "#2". Same number format on every item. If the voice says "first, second", the screen matches, or neither does. `eye`
4. **Callouts** sit at y 300 or lower, wrap at 160px side margins (break lines over about 26 characters), and stay up for the full duration of the claim they support. `script`
5. **Numbers on screen match the voice and the brief.** If the script says 30 days and the creator says a month, the screen says a month and the brief gets flagged. The same goes for offers: if the footage says 50% off, every caption and text box says 50% off, so the ad never contradicts itself. Don't query it against past ads. `eye`
5a. **No text box covers a face or the product, even in a fixed-position style.** Viewers look at faces first, then the product. Move the box for that clip (for example, the close box to the lower third, still inside the safe zone), reframe the clip, or pick another. `cut` · `eye`
6. **Font sizing at 1080 width:** captions and bracket lines 69px, hook and end boxes 75px, callouts 48 to 56px. `cut`

## 9. Audio

- **Voice is the priority.** Normalise dialogue to about -16 LUFS integrated, peaks under -1 dBTP. Both channels, every variation at the same level. `script`
- **Music only when the reviewer asks,** and on some versions rather than all, so it can be tested. Details in section 11a. The only sound effect is the end-box click.
- **Produced only:** a music bed at -22 to -26 LUFS under the voice, sidechain-ducked; the track's drop lands on the end card, not mid-sentence. Sound effects land on the word or not at all. `cut`

## 10. End card and CTA

- **Organic: no end card.** End on the last spoken line, holding about half a second on the final shot. **Every ad ends with the end box** (section 11a), unless the reviewer says otherwise, even when hook text is already in the footage or the brief puts the CTA in the post caption. Its offer matches what's spoken in the ad (8.5). `cut`
- **Produced only, when the brief asks:** 3 to 5 seconds, product shot, one-line offer, one-line CTA ("Shop the bundle, 30% off this week", not "Learn more"), inside the safe zone. The voice carries over it. `cut`

## 11. Variations, delivery and QC

1. **Every concept ships with four hooks:** A is the scripted one; B, C and D are variations with different opening visuals (Meta groups visually similar ads under one Entity ID). **The reviewer decides how many hooks to build and when.** If they ask for several at once, build them all on the same body. Otherwise build A first and the rest once A is approved. Hooks differ only in the opening, unless the reviewer asks for something else such as music on some versions. `cut`
1a. **When applying notes, change only what a note names.** Leave every other clip, line and text as it was, even ones a nearby note's general comment could apply to. If a note is unclear about which shot it means, ask on the note. `cut`
2. **A fix on one variation is applied to every variation.** The hand-off includes a per-variation checklist confirming each requested change on A, B, C and so on. `cut`
3. **Flag any competitor branding visible in the footage** (logos, labels, shop signs, clothing). Don't use the clip, or blur the branding. `eye`
4. **Formats:** 9:16 at 1080x1920, 30fps, H.264 about 12 Mbps, AAC 192kbps; 4:5 at 1080x1350 when asked. Name files `<CODE>_Hook<X>_v<N>.mp4`, e.g. `ACM08_HookB_v3.mp4` (or your own ad naming convention).
5. **Every delivery includes** the hook cuts, the gap report on the voice track, the safe-zone result, a frame-by-frame look at any shot under 0.4s, the headline-duration choice (3.4) and the per-variation checklist (11.2).

**Review checklist before anything ships**

1. Watch it muted. Does the hook overlay stop you, and does the story still make sense?
2. Listen with eyes closed. Any stumble, filler, repetition, clipped word or gap over 0.25s?
3. Captions: exact words, house brand names, market spelling, number style, sentence casing, hidden under the hook overlay.
4. Scrub for slivers and zoom flicker. Any shot under 0.3s, or over 4s?
5. Every clip: relevant, best available, not mirrored, clean background, persona matches, no competitor branding.
6. Text bounds inside the safe zone (the 4:5 box); one text element at a time.
7. Organic stayed organic: no music, end card, transitions, SFX or stock.
8. Every requested fix is on every variation.

## 11a. House look, timing, b-roll and music (every style)

Learned over six rounds of reviewer notes. The working code for all of it is `tools/house_captions.py` (7.0), which the builder imports.

**Start from the reference.** If the reference ad has a CapCut project (in CapCut's projects folder, which `tools/doctor.py` prints; search `draft_info.json` for the hook wording), take the font, colours, sound effects and music volume from it. Don't estimate them from frames.

**Hook and end boxes**
- Font is CapCut's system font (Metropolis, `en.ttf` in CapCut's `Resources/Font/SystemFont` folder) with CapCut's bold, not Proxima Nova or Montserrat. Size 75 at 1080 wide, plus a thin bold stroke (about 0.67px).
- Box colour is `#ff3c3c` with white text, or `#ffffff` with black text. The bars join as one solid shape with no gaps or dark edges, and the edges are slightly soft, not razor sharp.
- From the top of the box: first baseline 81px down, second 157px down, box bottom 195px down. A one-line box is 119px tall. Corner radius about 14px, side padding 22px, concave corners about 10px where the lines step. Emoji about 72px. The box top sits at about y 973 to 984.

**Bracket lines and captions**
- Metropolis with CapCut's text effect: white text, black stroke, soft black shadow to the lower right. Brackets are size 69 with bold; captions are size 69 without.
- Bracket line baseline sits at about y 1243. Caption baselines are y 1465 for one line, or y 1430 and 1500 for two.
- **The user's preferred caption look, in CapCut (2026-11-06):** the stroke and shadow look above is "sometimes quite hard to read". In CapCut they use the text effect `7563094611254627601` (Text, then Effects, then Trending), set to white fill. Size is 11 in CapCut, a bit bigger than 10, still Metropolis (`en.ttf`) at y -0.535. CapCut projects take this from `tools/templates/styles.json`. The MP4 renderer in `house_captions.py` still draws the older look, so a rendered MP4 won't match the CapCut project exactly until it's matched to frames.

**Timing**
- Each caption holds until the next one starts, with no blanks (7.7). Split at commas and spoken pauses (7.8a). B-roll and captions change on the same frame (7.8b). Text changes land on the footage's own cuts (7.8c).
- The end box, "Click Shop Now for [current offer] + FREE CASE 🚨", arrives on a camera cut with CapCut's Bounce In over about 0.5s and CapCut's `Click_Mouse_Click_02` sound. Captions stop when it appears.

**B-roll**
- The clip must show the exact feature named, and match the product in the video (orange video, orange torch where one exists):
  - 230° beam: the whole torch in a hand with the beam on. Not half a torch, and not someone doing the wave.
  - Wave sensor: on someone's head, being used.
  - Carry case: the logo case being unzipped and opened with the torch inside, sped up if needed, held through the whole line.
- Check every clip's colour: HDR iPhone footage needs correcting or it looks tinted (6.11b).
- Don't illustrate niche activities in a passing list, and don't cut to a stranger on a personal line.
- Prefer real people to AI clips. Use AI only where the reviewer picks it or no real clip exists.
- Search the whole footage library. If a clip the reviewer remembers can't be found, ask for the file name; it may not be uploaded yet.

**Music, only when asked**
- Use the track from the reference project when there is one, on some versions only.
- Start it from the first frame. Level out its peaks and trim the harsh top end, so its loudest part never competes with the voices. One finished ad settled at about -50 dB against voices at -22 dB. The reviewer found -45 dB too strong at the song's peak.

## 11b. Carried over from the old setup

Earlier reviewer rules that still apply. Where anything here differs from the sections above, the sections above win.

- **Never show the client's product as the failed option.** When a script mocks other solutions, use generic or unbranded footage.
- **Only the product the brief is about, in its current packaging.** Other products don't appear, even in the background. If two packaging versions appear, ask which is current.
- **Nothing covers a face,** and hook text doesn't cover the head or the product. Move the text or change the shot.
- **Show the action as it happens:** "add it to the water" shows it going in, not the moment after. Check in-points on a timecoded sheet.
- **Check AI clips for a wrongly generated product,** especially when it turns to show its back.
- **Don't ask what the brief already answers.** The offer, discount, prices and anything else the script states go on screen as written, without checking with the user (user, 2026-11-03).
- **Say plainly what hasn't been checked,** including that the audio hasn't been listened to.
- **Keep working files out of iCloud.** Use a working folder outside iCloud or OneDrive. Documents syncs to iCloud and big files can be offloaded mid-job. If a file there won't open, run `brctl download <path>` first.
- **Loom feedback:** a public Loom page has a transcript under its Transcript tab. Screen demos need the picture too, so ask before downloading. Save the rules before changing anything, and wait if more feedback is coming.

## 12. Revision log

Log every rule you add or change here, one line each, with the date and where it came from (a review note, a CapCut diff, a walkthrough). Newest last.
