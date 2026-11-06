---
name: ai-voiceover-story
description: Make an AI voiceover story video ad (a first-person story told by an AI voice, cut to fast, literal B-roll) and deliver it as a CapCut project the editor can open and change, with one project per hook. Learns from the editor's CapCut changes by diffing them against what was handed off. Use whenever someone asks for a story ad, an AI voiceover ad with B-roll, a "gift for him/her" style ad, hook variants of a finished story ad, or says they've changed a CapCut project and wants the changes learned.
---

# AI voiceover story ads

You build the ad; the editor finishes it in CapCut. You do the voiceover cut, captions, B-roll picks and timing, the end stack and the sound. The editor makes the hook visuals and hook text by hand, tweaks the edit in CapCut, and exports. Then you read what they changed and turn it into rules, so the next ad needs fewer changes.

All commands run from the repo folder with the repo's Python: `.venv/bin/python` on Mac, `.venv\Scripts\python` on Windows (written `PY` below). If `.venv` is missing, run the setup first (README). Keep each ad's working files in its own folder outside iCloud and OneDrive.

## Read first, every time

1. `references/editing-standards.md`, in full. It's the rulebook and it wins.
2. `references/style.md`, the notes for this style. The B-roll rules (rulebook 6.20 to 6.30) and caption rules (7.8ab to 7.8ad) matter most.
3. Any brand notes the user keeps (product facts, offer, banned claims). Only make claims the brief or brand notes support.

## Make an ad

1. **Inputs.** Get the script, the voiceover (or make it), the footage folder and the offer. The voiceover is one file: every hook line first, in order, then the body. Lines marked "(Him)" or "(Her)" aren't voiced: they're played by a real clip with its own sound. If anything the brief already says is missing, use the brief as written rather than asking.
2. **Transcribe:** `PY tools/transcribe.py <ad>/inputs/voiceover.mp3`. That writes `inputs/tx/voiceover.json` with every word's timing. Check the words against the script.
3. **See the footage:** `PY tools/contact_sheet.py "<footage folder>" <ad>/sheets/<folder>.jpg` for each relevant folder, then look at the sheets. Check every clip you pick at its in-point: the action on the line has to really happen on screen (rulebook 6.23), the people have to fit the story's characters (6.26), and there can be no other captions or watermarks on it (6.28).
4. **Write the edit:** copy `examples/example_ad/` to the ad's folder and fill in `make_edit.py`: the hook lines, the body as caption phrases with the clip that starts on each, inserts for reaction clips, the end stack's offer and the music. Split captions at the sentence's natural break (7.8ab). Run it to write `edit.json`.
5. **Build each hook's CapCut project.** CapCut must be closed.
   `PY tools/story_ad.py <ad>/edit.json --hook A --capcut --name "<Ad name> - Hook A"`
   The builder cuts every breath and pause, puts each caption on the frame its first word starts, snaps captions, B-roll and voice pieces to the same tick (7.8ad), balances line breaks, and refuses to write if any caption check fails. Read every `WARN` and `LONG` line it prints and fix the edit before handing off. Add `--mp4` for a review render (slow: several minutes).
6. **Hand off.** Tell the editor the project names, what's in the hook slot (the placeholder card), any marked gaps where no clip fitted, and what you haven't checked. The builder saves a snapshot of each project next to the edit (`build/Hook<X>/capcut_snapshot.json`), which you'll diff against later.

## Hook variants on a finished edit

When the editor has finished one hook's project and wants the others, don't rebuild: copy their project and swap only the hook, so their body stays exactly as they cut it.
1. Find the new hook's voice pieces, with breaths left out:
   `PY -c "import sys; sys.path.insert(0,'tools'); from edit_helpers import find_pieces; print(find_pieces('<voiceover>', <hook start>, <hook end>))"`
2. Write a spec and run it (CapCut closed):
   `{"source": "<their finished project>", "name": "<Ad name> - Hook B", "pieces": [[5.44, 8.99]]}`
   `PY tools/swap_hook.py hookB.json`
3. Check it with `PY tools/capcut_draft.py dump "<Ad name> - Hook B"`: the hook slot starts at 0, the body starts where the hook ends, and nothing else moved. Listen back to the hook audio if you can.

## Learn from the editor's changes

This is how the skill gets better. Do it every time the editor says they've changed a project.
1. Make sure CapCut has saved (closing it is safest), then diff your hand-off snapshot against their project:
   `PY tools/capcut_draft.py diff <ad>/build/HookA/capcut_snapshot.json "<project name>"`
   For a hook variant, diff it against the project it was copied from. `dump` shows the whole timeline when you need the details (positions, speed, zoom, volume, transitions).
2. For each change, work out the reason: a clip swapped for a better example of the line, a caption split differently, music turned up for the hook. Ask the editor when the reason isn't clear. Don't guess a rule from one change they made for taste.
3. Write each lasting lesson down as a rule, with the date and where it came from: rules for every edit go in `references/editing-standards.md`, and rules for this style go in `references/style.md`. Log it in the rulebook's section 12.
4. If they changed something the builder does (a level, a position, a caption look), change the builder or `tools/templates/styles.json` too, so it doesn't need fixing twice.
5. Don't save anything the editor says not to remember, such as a look they're still trying out.

## CapCut notes

- CapCut keeps each project as plain JSON in its projects folder (`PY tools/doctor.py` prints where). Times are in microseconds. Positions run from -1 to 1, with y going up.
- Always close CapCut before writing a project; it overwrites files it has open. Reading while it's open is fine.
- CapCut can't read hidden folders, so the builder copies voiceover and template files into the project's own `Resources/media`.
- Fonts, text effects and sounds in the templates point into CapCut's own cache. If one hasn't been used on this computer yet, CapCut may show it as missing until it's added once from CapCut's library. The builder says so for the end-stack click.
