"""Example: writes edit.json for one story ad. Copy this folder for each new ad and change the parts marked CHANGE.

Run it with the repo's Python:
  Mac:      .venv/bin/python examples/example_ad/make_edit.py
  Windows:  .venv\\Scripts\\python examples\\example_ad\\make_edit.py

Every caption is anchored to the voiceover's own words (Words.at), so timing comes from the audio, not guesses.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "tools"))
from edit_helpers import Words, resolve  # noqa: E402

# CHANGE: this ad's files. Keep working files out of iCloud / OneDrive folders.
VO = os.path.join(HERE, "inputs", "voiceover.mp3")          # hooks first, then the body, as one file
TX = os.path.join(HERE, "inputs", "tx", "voiceover.json")   # from: tools/transcribe.py inputs/voiceover.mp3
BROLL = os.path.expanduser("~/Videos/B-roll")               # your footage library, in folders by subject
MUSIC = None                                                 # or the path to a music file

w = Words(TX)

# CHANGE: the hook lines, in order, as spoken. Each hook runs from its first word to the next hook's first word.
HOOK_LINES = {
    "A": "it's dark by 4pm",
    "B": "20 Christmases together",
    "C": "men always say they don't",
}
BODY_START = "this year"                                     # the body's first words

# CHANGE: the body, one caption phrase per row, with the clip that starts on it (or None to keep the last clip).
# A clip is (file under BROLL, second to start from, extras). Extras: speed, zoom, x, y (CapCut positions).
BODY = [
    ("this year I didn't want to", ("Gifts/IMG_0001.mov", 0.6, {})),
    ("break the bank", ("Gifts/IMG_0002.mov", 0.3, {})),
    ("so I picked him up", ("In Hands/IMG_0003.mov", 1.2, {})),
    ("one of these", None),
    # ...
    ("click shop now to get yours", ("Close/IMG_0099.mov", 0.0, {})),
]

starts = {k: w.at(v) for k, v in HOOK_LINES.items()}
order = sorted(starts, key=starts.get)
body_t = w.at(BODY_START)
w.cur -= 1                                                   # body captions search on from the body's first word
hooks = {}
for i, k in enumerate(order):
    end = starts[order[i + 1]] if i + 1 < len(order) else body_t
    hooks[k] = [max(0.0, starts[k] - 0.05), end - 0.05]

captions, shots = [], []
for text, shot in BODY:
    t = w.at(text)
    captions.append(dict(t=t, text=text))
    if shot:
        clip, src, extra = shot
        shots.append(dict(t=t, clip=resolve(os.path.join(BROLL, clip)), src_in=src, **extra))

edit = {
    "code": "EXAMPLE",                                       # CHANGE: short ad code, used in file names
    "vo": VO,
    "hook_card": os.path.join(HERE, "..", "..", "tools", "templates", "hook_card.mp4"),
    "hooks": hooks,
    "body": [body_t - 0.05, 1e6],
    "cuts": [],                                              # [[from, to]] seconds of voiceover to drop
    "inserts": [],                                           # clips that play with their own sound, e.g. a reaction:
    # {"at": 55.37, "clip": "<file>", "in": 15.25, "out": 16.9, "volume": 1.0, "caption": "look at how bright that is"}
    "end_box": {"at": "click shop now to get yours",         # CHANGE: the call-to-action caption, and the offer
                "stack": ["SHOP NOW FOR\nUP TO 50% OFF 🎁", "60-DAY GUARANTEE ✅", "LOW STOCK ⚠️"]},
    "captions": captions,
    "shots": shots,
}
if MUSIC:
    edit["music"] = {"path": MUSIC, "lufs": -44, "capcut_volume": 0.035}
with open(os.path.join(HERE, "edit.json"), "w", encoding="utf-8") as f:
    json.dump(edit, f, indent=1, ensure_ascii=False)
print(len(captions), "captions,", len(shots), "shots, hooks", {k: [round(a, 2), round(b, 2)] for k, (a, b) in hooks.items()})
