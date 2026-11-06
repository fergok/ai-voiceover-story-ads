"""Helpers for writing an edit file (edit.json) for story_ad.py. Import them in an ad's make_edit.py:

    import sys; sys.path.insert(0, "<repo>/tools")
    from edit_helpers import Words, resolve, find_pieces

  Words(tx_json).at("phrase")   start time of the phrase's first word, searching forward from the last match,
                                so the same words later in the script find their own place
  resolve(path)                 the exact file, or the one file in that folder whose name starts the same way
  find_pieces(vo, a, b)         voice pieces between a and b seconds with pauses and breaths left out, for a
                                hook variant (swap_hook.py)
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import platform_paths as P  # noqa: F401

norm = lambda x: re.sub(r"[^a-z0-9]", "", x.lower())


class Words:
    def __init__(self, tx_json):
        with open(tx_json, encoding="utf-8") as f:
            tx = json.load(f)
        self.words = [(w["word"].strip(), w["start"], w["end"]) for s in tx["segments"] for w in s["words"]]
        self.cur = 0

    def at(self, phrase):
        toks = [norm(t) for t in phrase.split() if norm(t)]
        # the full phrase first; then its opening words, since brand names are often transcribed differently
        # (a made-up brand name heard as two words)
        for n in range(len(toks), min(len(toks), 2) - 1, -1):
            for i in range(self.cur, len(self.words)):
                seq = "".join(norm(w) for w, _, _ in self.words[i:i + n + 2])
                if seq.startswith(toks[0]) and "".join(toks[:n]) in seq:
                    if n < len(toks):
                        print("note: matched %r on its first %d words" % (phrase, n))
                    self.cur = i + 1
                    return round(self.words[i][1], 3)
        raise SystemExit("not in the transcript (after the last match): " + phrase)

    def end_of(self, phrase):
        """end time of the phrase's last word"""
        t = self.at(phrase)
        i = next(k for k, w in enumerate(self.words) if abs(w[1] - t) < 1e-6)
        n = len([x for x in phrase.split() if norm(x)])
        return round(self.words[min(i + n - 1, len(self.words) - 1)][2], 3)


def resolve(p):
    if os.path.exists(p):
        return p
    d, stem = os.path.split(p)
    stem = os.path.splitext(stem)[0][:20]
    hits = [f for f in os.listdir(d) if f.startswith(stem)]
    if len(hits) != 1:
        raise SystemExit("no single match for %s: %s" % (p, hits))
    return os.path.join(d, hits[0])


def find_pieces(vo, a, b):
    """Voice pieces inside [a, b] seconds, with pauses and breaths left out: the same word-based cut story_ad.py
    uses (tuned on a human editor's own cuts). Needs the transcript from transcribe.py in tx/ next to the audio."""
    import story_ad
    return [[round(max(x, a), 3), round(min(y, b), 3)] for x, y in story_ad.speech_pieces({"vo": vo}) if x < b and y > a]
