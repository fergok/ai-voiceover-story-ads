"""House captions and on-screen text: the one engine for every video with speech and captions, any style, any brand.

Rulebook section 7 and 11a in code. Taken unchanged from the finished Red Light Skit (REDSKIT) template, where every
number was fitted to the reference ads and passed review. Don't write captions any other way: import from here.

  caption_img(text)       -> 1080x1920 RGBA: white text, black stroke, soft shadow, wraps to two lines (7.6, 11a)
  box_layer(spec)         -> hook / end box: CapCut system font with its bold, rounded joined bars (3.3, 11a)
  hook_img(spec)          -> hook box plus optional bracket line
  voice_onset(...)        -> where a word really starts in the audio, so captions change on that frame (7.8aa)
  BOUNCE, CLICK_DELAY     -> end-box Bounce In and the Click_Mouse_Click_02 timing (11a)
  check_spans(caps, cuts) -> hard checks: no blanks between captions (7.7), every cut on a caption change (7.8b)
"""
import json, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import platform_paths as P
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FONT = P.capcut_font()      # CapCut's system font (en.ttf), found on Mac or Windows
EMOJI = P.emoji_font()
RED, WHITE = (255, 60, 60, 255), (255, 255, 255, 255)   # from the reference CapCut project

BOX_SIZE, CAP_SIZE, PAD_X = 75, 69, 22
ABOVE, PITCH = 81, 76            # baseline positions under the top of the box, fitted to the reference ads
BOX_H1, BOX_H2, STEP_UP, STEP_DOWN = 119, 195, 72, 117
EMOJI_PX, EMOJI_CENTER, EMOJI_ADV = 72, 58, 76
FPS = 30
# end-box bounce, measured frame by frame from the reference ad (box width / final width)
BOUNCE = [.225, .424, .600, .751, .879, .982, 1.053, 1.094, 1.096, 1.055, 1.029, 1.014, 1.006, 1.002]
CLICK_DELAY = 0.014   # CapCut's Click_Mouse_Click_02, timed as in the reference ad


def is_emoji(c):
    return ord(c) > 0x2600 or 0x2300 <= ord(c) <= 0x23FF


def split_runs(line):
    return [c for c in line if is_emoji(c)], "".join(c for c in line if not is_emoji(c)).rstrip()


def emoji_img(c):
    im = Image.new("RGBA", (220, 220), (0, 0, 0, 0))
    try:   # Apple's emoji font only has 160px bitmaps; Windows' Segoe UI Emoji scales
        f = ImageFont.truetype(EMOJI, 160 if EMOJI and EMOJI.endswith(".ttc") else 109)
        ImageDraw.Draw(im).text((110, 110), c, font=f, embedded_color=True, anchor="mm")
    except (OSError, TypeError, ValueError):
        pass
    if not im.getbbox():
        return Image.new("RGBA", (1, 1), (0, 0, 0, 0))   # no colour emoji font: leave it out of the review MP4
    im = im.crop(im.getbbox())
    k = min(EMOJI_PX / im.width, EMOJI_PX / im.height)
    return im.resize((max(1, round(im.width * k)), max(1, round(im.height * k))), Image.LANCZOS)


def box_layer(spec):
    """CapCut text with its background on: Metropolis with CapCut's bold, each line on a rounded bar, fused into one shape.
    Every number below is fitted to the reference ads."""
    S = 3
    f = ImageFont.truetype(FONT, BOX_SIZE * S)
    meas = ImageDraw.Draw(Image.new("L", (4, 4)))
    rows = []
    for ln in spec["lines"]:
        em, txt = split_runs(ln)
        tw = meas.textlength(txt, font=f) / S
        rows.append((txt, em, tw, tw + (20 + EMOJI_ADV * len(em) if em else 0)))
    top = spec["top"]
    spans = [r[3] for r in rows]
    if len(spans) == 2 and abs(spans[0] - spans[1]) < 28:
        spans = [max(spans)] * 2
    r, fil = 14 * S, 10 * S
    mask = Image.new("L", (1080 * S, 1920 * S), 0)
    d = ImageDraw.Draw(mask)
    X = lambda w: ((540 - w / 2 - PAD_X) * S, (540 + w / 2 + PAD_X) * S)
    if len(spans) == 1 or spans[0] == spans[1]:
        h = BOX_H1 if len(spans) == 1 else BOX_H2
        d.rounded_rectangle([X(spans[0])[0], top * S, X(spans[0])[1], (top + h) * S], r, fill=255)
    else:
        a_wide = spans[0] > spans[1]
        seam = (top + (STEP_DOWN if a_wide else STEP_UP)) * S
        d.rounded_rectangle([X(spans[0])[0], top * S, X(spans[0])[1], seam + (0 if a_wide else 2 * r)], r, fill=255)
        d.rounded_rectangle([X(spans[1])[0], seam - (2 * r if a_wide else 0), X(spans[1])[1], (top + BOX_H2) * S], r, fill=255)
        thin = X(spans[1]) if a_wide else X(spans[0])
        sgn = 1 if a_wide else -1
        for xc, side in ((thin[0], -1), (thin[1], 1)):
            x0, x1 = sorted((xc, xc + side * fil))
            y0, y1 = sorted((seam, seam + sgn * fil))
            d.rectangle([x0, y0, x1, y1], fill=255)
            cx, cy = xc + side * fil, seam + sgn * fil
            d.ellipse([cx - fil, cy - fil, cx + fil, cy + fil], fill=0)
    txt_l = Image.new("L", (1080 * S, 1920 * S), 0)
    td = ImageDraw.Draw(txt_l)
    emojis = []
    for i, (txt, em, tw, w) in enumerate(rows):
        base = top + ABOVE + i * PITCH
        x = 540 - w / 2
        td.text((x * S, base * S), txt, font=f, fill=255, anchor="ls", stroke_width=2, stroke_fill=255)   # CapCut's bold
        for k, c in enumerate(em):
            e = emoji_img(c)
            cx = x + tw + EMOJI_CENTER + k * EMOJI_ADV
            emojis.append((e, int(cx - e.width / 2), int(base - 29 - e.height / 2)))
    soft = ImageFilter.GaussianBlur(0.6)   # the reference text isn't razor sharp
    mask = mask.resize((1080, 1920), Image.LANCZOS).filter(soft)
    txt_l = txt_l.resize((1080, 1920), Image.LANCZOS).filter(soft)
    im = Image.new("RGBA", (1080, 1920), spec["color"])      # colour everywhere, shape only in the alpha: no dark edge
    im.paste(Image.new("RGBA", (1080, 1920), spec["ink"]), (0, 0), txt_l)
    im.putalpha(mask)
    for e, x, y in emojis:
        im.alpha_composite(e, (x, y))
    return im


def wrap(text, f):
    if "\n" in text:                     # broken by hand into even lines (rulebook 7.8ac)
        return text.split("\n")
    meas = ImageDraw.Draw(Image.new("RGB", (4, 4)))
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if meas.textlength(t, font=f) > 885 and cur:
            lines.append(cur)
            cur = w
        else:
            cur = t
    return lines + [cur]


def outlined(lines, bases, size=CAP_SIZE, bold=False):
    """CapCut's caption effect from the reference project: white text, black stroke, soft black drop shadow to the lower right."""
    S = 3
    f = ImageFont.truetype(FONT, size * S)
    def draw(stroke, fill_w):
        lay = Image.new("L", (1080 * S, 1920 * S), 0)
        d = ImageDraw.Draw(lay)
        for ln, b in zip(lines, bases):
            w = d.textlength(ln, font=f)
            d.text((540 * S - w / 2, b * S), ln, font=f, fill=255, anchor="ls", stroke_width=stroke, stroke_fill=255)
        return lay.resize((1080, 1920), Image.LANCZOS)
    edge = draw(11, 0).filter(ImageFilter.GaussianBlur(0.7))
    shadow = Image.new("L", (1080, 1920), 0)
    shadow.paste(edge, (4, 4))
    shadow = shadow.filter(ImageFilter.GaussianBlur(3)).point(lambda v: int(v * 0.8))
    im = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    black = Image.new("RGBA", (1080, 1920), (0, 0, 0, 255))
    im.paste(black, (0, 0), shadow)
    im.paste(black, (0, 0), edge)
    fill = draw(1 if bold else 0, 0).filter(ImageFilter.GaussianBlur(0.5))
    im.paste(Image.new("RGBA", (1080, 1920), (255, 255, 255, 255)), (0, 0), fill)
    return im


def caption_img(text):
    f = ImageFont.truetype(FONT, CAP_SIZE)
    ls = wrap(text, f)
    return outlined(ls, [1465] if len(ls) == 1 else [1430, 1500])


def hook_img(h):
    im = box_layer(h)
    if h["paren"]:
        im.alpha_composite(outlined([h["paren"]], [1243], bold=True))
    return im


def fr(t):
    return round(t * FPS) / FPS


def voice_onset(cap_t, t, e, voiced, prev, word_ends=()):
    """The audio's real start of the word. Whisper can be a few frames late or early, so it only says roughly where to look.
    Never searches back past the end of the word before it (word_ends, from tx/skit.json)."""
    import numpy as np
    i = int(np.searchsorted(t, cap_t))
    before = [w for w in word_ends if w <= cap_t + 0.02]
    lo = int(np.searchsorted(t, max(cap_t - 0.30, prev + 0.1, before[-1] if before else 0)))
    if voiced[i]:
        j = i
        while j > lo and voiced[j]:
            j -= 1
        if not voiced[j]:           # silence just before: the word starts where it ends
            return float(t[j + 1])
        a, b = int(np.searchsorted(t, cap_t - 0.12)), int(np.searchsorted(t, cap_t + 0.06))
        return float(t[a + int(np.argmin(e[a:b + 1]))])   # no silence in continuous speech: take the dip between words
    j = i
    while j < len(t) - 1 and not voiced[j] and t[j] < cap_t + 0.4:
        j += 1
    return float(t[j]) if voiced[j] else cap_t


def check_spans(caps, cut_frames, first=None, last=None):
    """caps: [(first frame, end frame, text)] in order. Fails loudly instead of letting a broken edit reach the reviewer."""
    errs = []
    for (a0, a1, at), (b0, b1, bt) in zip(caps, caps[1:]):
        if a1 != b0:
            errs.append("blank or overlap between %r (ends %d) and %r (starts %d)" % (at, a1, bt, b0))
    starts = {c[0] for c in caps}
    if last is not None:
        starts.add(last)
    for f in cut_frames:
        if (first is None or f >= first) and (last is None or f <= last) and f not in starts:
            errs.append("shot change at frame %d (%.2fs) is not on a caption change" % (f, f / FPS))
    f = ImageFont.truetype(FONT, CAP_SIZE)
    for a0, a1, t in caps:
        if len(wrap(t, f)) > 2:
            errs.append("caption over two lines: %r" % t)
        if a1 - a0 < 6:
            errs.append("caption under 0.2s: %r" % t)
    if errs:
        raise SystemExit("caption check failed:\n  " + "\n  ".join(errs))
    return True
