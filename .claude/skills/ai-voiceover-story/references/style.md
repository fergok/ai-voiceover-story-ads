# AI voiceover story: style notes

A first-person story told by an AI voiceover, such as "the gift I bought him" or "the founder's story", cut to fast, literal B-roll of real people using the product. It runs longer than a plain deal ad and tells more of a story. These notes come from a set of winning ads in this style and from a human editor's own finished edit of one, explained shot by shot in a recorded walkthrough.

**The main rulebook comes first and wins:** `editing-standards.md`, next to this file. Read it in full before every edit. Sections 6, 7 and 11a, on B-roll, captions and timing, apply to this style as written. Captions and their timing come from the one engine, `tools/house_captions.py` (rulebook 7.0). `tools/story_ad.py` uses it and runs its checks before writing anything. A first version that skipped this failed review on every caption rule:
- Captions were single long lines. They must be short phrases of up to two lines, split at commas and pauses (7.6, 7.8a).
- Captions blinked off and back on. There must be no blanks: each caption holds until the next one starts (7.7).
- A caption arrived a beat after its shot changed. Caption and B-roll change on the same frame, taken from the audio onset (7.8aa, 7.8b).
- Scene changes felt jittery. Keep clips about 1.5–3.5s, entered on motion (6.7, 6.8), with no clip used twice (6.13).

**The most important part is how the editor picks, times and trims B-roll** (rulebook 6.20 to 6.30, captions 7.8ab to 7.8ad). That matters more than any one look.

## Division of work
- **The editor makes the hook visuals** (AI clips made by hand) **and the hook text.** Build everything else: leave the hook slot for the length of each hook's voiceover line, filled with the placeholder card, and make one CapCut project per hook. Don't draft hook text unless asked: the editor is still working out its look.
- **Deliver a CapCut project**, plus a review MP4 when asked, so the editor can tweak it or drop in B-roll. Snapshot it at hand-off. When the editor changes it, diff the snapshot against their project and turn each change into a rule in these notes or the rulebook (see the skill's "Learn from the editor's changes").
- If no clip fits a line, leave a marked gap the right length and tell the editor, who can make one.

## Voiceover
- Cut every breath and every pause between phrases before timing anything (rulebook 4, first rule). `story_ad.py` does this from the word timings. One finished 69s ad had 36 voice pieces.
- The voiceover sits at 2.0 volume in CapCut (about +6 dB), so it sits well on top.
- **Lines marked "(Him)" or "(Her)" in brackets are not voiced.** That line is played by a real B-roll clip of someone saying something like it, with the clip's own sound. Cut the line out of the voiceover and put the clip in its place (an `insert` in the edit file). Give the clip's spoken words a caption. Let the whole clip play.
- Record all the hooks and the body as one voiceover file, hooks first. Each hook's start and end seconds go in the edit file's `hooks`.

## Characters and story
- Know who the story is about and cast every shot to match (rulebook 6.26). In a story about a wife of 20 years buying for her husband, "he" lines show older men, ideally the same man again and again, and "20 years together" shows an older couple. Lines about the speaker ("that was when I knew I nailed it") can show the gift itself.
- Seasonal framing comes through in the B-roll: for a Christmas gift ad, a man reaching for a wrapped gift (trimmed so he touches it on screen), the product in a hand against a plain festive background.
- One clip can cover a two-caption list ("socks and aftershave / he'll never use"): one clip of an older man looking unhappy with socks beats two clips of two different men.
- **Reaction line:** a clip of someone filming another person's reaction to the product, with its own sound. Zoom slowly in on the person the story is about.

## Pacing and B-roll
- A new shot on most caption phrases, usually 1.5–3.5s, changing on the same frame as the caption. Short one- or two-word captions share the next phrase's clip, and one continuous action can run across several captions (rulebook 6.20, 6.21). Quick bursts on lists only if the editor asks: the 0.3s minimum shot applies (5.7).
- B-roll is literal to the phrase. "Rushing to the store" shows a store front, "grabbing whatever's left" shows socks, "spending 60 bucks" shows a red "-$60" over the shot, "my 15-year-old rolls his eyes" shows a kid rolling his eyes.
- Mostly real people of all ages using and reacting to the product, many different creators, plus AI clips. AI clips are zoomed 1.03 and often sped up 1.1–1.3x (6.29). Real clips are muted, except on a reaction line.
- Feature lines show the feature working, on its word (6.23). Comparisons can get small labels over the shot ("OURS" vs "OTHERS").
- Close on the product: the box, the product in hand, any free extra (a case) being shown off with it, the colours on "colours still in stock".

## Text
- **Captions:** the house captions from rulebook 7 and 11a, in the CapCut caption look stored in `tools/templates/styles.json`, split and broken as in 7.8ab and 7.8ac. The hook voiceover gets no captions; the body's captions start with the body.
- **Checklists:** near the end, feature ticks can stack up one per line ("✅ It's USB rechargeable").
- **End stack (last 2–3s):** three boxes appear together on the call to action ("click shop now to get yours") and hold to the end. Captions stop as they appear. From one of the style's top spenders:
  - "SHOP NOW FOR / UP TO 50% OFF 🎁": white box, black text, top (y 0.41 in CapCut).
  - "60-DAY GUARANTEE ✅": white box, black text (y -0.30).
  - "LOW STOCK ⚠️": red box, white text (y -0.46). Red draws the eye and signals urgency.
  - Montserrat Bold, size 12 in CapCut, inside the 4:5 safe zone, with CapCut's `Click_Mouse_Click_02` click at about 0.34. The texts follow the brief's offer: set `end_box.stack` in the edit file (rulebook 8.5).

## Sound
- A music bed, very low: about 0.035 in CapCut.
- One subtle effect can mark a feature switch (for example CapCut's "Correct answer good!" at about 0.24).
- **Music is a variable to test between hook variants**, not fixed. In one set of three hooks, the editor kept the music but turned it up for the hook and first 19s (0.115, then 0.074), and swapped another variant to a different track at 0.02.

## Hook variants
- Once the editor has finished one hook's project, build the other hooks on it with `tools/swap_hook.py`: it copies the project, swaps in the new hook's voice pieces (breaths left out), and moves the body along unchanged. The body is the editor's, so never rebuild it from scratch for a variant.
- The hook clip goes on the main track, not an overlay. A hook can be two shots (an AI clip under the setup line, a product clip on the payoff).
- A transition is allowed between the hook and the body: CapCut's "Pull in" (about 0.47s) from the hook clip into the first body clip, with a "swish_whoosh (large)" starting 0.23s before the cut, at about 0.32 volume.

## Length
55–90s is normal for this style, so the rulebook's 60s limit doesn't apply.
