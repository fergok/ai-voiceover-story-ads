#!/usr/bin/env python3
"""Build an AI-voiceover story ad from one edit file: a review MP4 and a CapCut project.

  story_ad.py <edit.json> [--hook A] [--mp4] [--capcut] [--name "<project name>"]

The edit file (see Styles/AI voiceover story/) gives the voiceover, the hook ranges,
the body range, cuts, inserts (clips that play with their own sound), captions and
shots. Caption and shot times are in the ORIGINAL voiceover's seconds; the builder
tightens pauses, removes cuts, and maps everything onto the output timeline.

The CapCut project is cloned from the blank project in templates/capcut_base the way CapCut's
own Duplicate does, then its timeline is replaced. The caption look, end stack and click come
from templates/styles.json. CapCut must be closed while writing.
"""
import copy
import json
import os
import re
import shutil
import subprocess
import sys
import time
import uuid

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import capcut_draft as C
import platform_paths as P

FF = P.ffmpeg()
TEMPLATE = os.path.join(HERE, "templates", "capcut_base")      # a blank CapCut project: one video, text, VO and music track
# prototypes from a finished, human-edited ad: the caption look (rulebook 11a), the three-box end stack and the click
USER_TEMPLATE = os.path.join(HERE, "templates", "styles.json")
ROOT_ENTRY = os.path.join(HERE, "templates", "root_entry.json")
STACK = ("SHOP NOW FOR", "60-DAY GUARANTEE", "LOW STOCK")   # end stack boxes, top to bottom (style.md)
VO_VOLUME, MUSIC_VOLUME = 2.0, 0.035                          # a human editor's CapCut levels on a finished ad
ONE_LINE = 24                    # longer captions are broken by hand into two even lines (7.8ac)
W, H, FPS = 1080, 1920, 30
US = 1_000_000


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
    if r.returncode:
        sys.exit("command failed: %s\n%s" % (" ".join(cmd[:6]), r.stderr[-1500:]))
    return r


def uid():
    return str(uuid.uuid4()).upper()


_probe = {}


def probe(path):
    """duration, display width/height (rotation applied) and whether there is sound, from ffmpeg's banner."""
    if path not in _probe:
        err = subprocess.run([FF, "-hide_banner", "-i", path], capture_output=True, text=True, errors="replace").stderr
        m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", err)
        if not m:
            sys.exit("can't read " + path)
        dur = int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3])
        v = re.search(r"Stream .*Video: .*?(\d{2,5})x(\d{2,5})", err)
        w, h = (int(v[1]), int(v[2])) if v else (0, 0)
        rot = re.search(r"rotation of (-?[\d.]+)|rotate\s*:\s*(-?\d+)", err)
        if rot and abs(round(float(rot[1] or rot[2]))) in (90, 270):
            w, h = h, w
        _probe[path] = dict(dur=dur, w=w, h=h, audio="Audio:" in err)
    return _probe[path]


# ---------------------------------------------------------------- timeline

def silences(vo, noise=-38, d=0.12):
    err = run([FF, "-i", vo, "-af", "silencedetect=noise=%ddB:d=%s" % (noise, d), "-f", "null", "-"]).stderr
    st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", err)]
    en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", err)]
    return list(zip(st, en))


def keep(rng, removals):
    """rng minus removals, as a list of (a, b)."""
    a0, b0 = rng
    out, cur = [], a0
    for a, b in sorted(removals):
        if b <= cur or a >= b0:
            continue
        if a > cur:
            out.append((cur, min(a, b0)))
        cur = max(cur, b)
    if cur < b0:
        out.append((cur, b0))
    return [(round(a, 3), round(b, 3)) for a, b in out if b - a > 0.02]


def frame_of(t):
    return int(t * FPS + 1e-6)          # round down: a caption is never late


def balance_lines(text):
    """Over ONE_LINE characters: two lines as even as possible, never top heavy (rulebook 7.8ac)."""
    if len(text) <= ONE_LINE or "\n" in text:
        return text
    w = text.split()
    best = min(range(1, len(w)), key=lambda i: (abs(len(" ".join(w[:i])) - len(" ".join(w[i:])))
                                              + (2 if len(" ".join(w[:i])) > len(" ".join(w[i:])) else 0)))
    return " ".join(w[:best]) + "\n" + " ".join(w[best:])


def vo_envelope(vo, hop=0.01):
    """10ms loudness of the voiceover in dB, for finding where words really start."""
    import numpy as np
    raw = subprocess.run([FF, "-v", "error", "-i", vo, "-ac", "1", "-ar", "16000", "-f", "s16le", "-"], capture_output=True).stdout
    x = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    n = int(16000 * hop)
    x = x[: len(x) // n * n].reshape(-1, n)
    return 20 * np.log10(np.sqrt((x ** 2).mean(1)) + 1e-9)


def onset_out(out_t, vo, env, thresh=-38, hop=0.01):
    """Move a transcript word start (output seconds) to where the voice actually starts.
    Searches only inside the voiceover piece that holds it, back to the silence before the word."""
    p = next((p for p in vo if p["start"] - 1e-6 <= out_t <= p["start"] + p["src_out"] - p["src_in"] + 1e-6), None)
    if not p:
        return out_t
    src = p["src_in"] + out_t - p["start"]
    i = int(src / hop)
    lo, hi = int(max(p["src_in"], src - 0.30) / hop), int(min(p["src_out"], src + 0.40) / hop)
    voiced = lambda k: 0 <= k < len(env) and env[k] > thresh
    if voiced(i):
        j = i
        while j > lo and voiced(j - 1):
            j -= 1
        k = j
    else:
        k = i
        while k < hi and not voiced(k):
            k += 1
        if not voiced(k):
            k = i
    return p["start"] + k * hop - p["src_in"]


def speech_pieces(e, th=-40, wpad=0.06, lead=0.03, tail=0.15, join=0.15):
    """Every word, with no breaths or dead air (never hear an inhale or exhale).
    Keeps only sound that is loud enough AND sits on a transcribed word, so breaths go even when
    they are as loud as quiet speech. Tuned on a human editor's own cuts: 0.03s before the
    first sound, 0.15s after the last, sounds under 0.15s apart stay joined."""
    import numpy as np
    txp = e.get("vo_tx") or os.path.join(os.path.dirname(e["vo"]), "tx", os.path.splitext(os.path.basename(e["vo"]))[0] + ".json")
    words = [(w["start"], w["end"]) for sg in json.load(open(txp, encoding="utf-8"))["segments"] for w in sg.get("words", [])]
    env = vo_envelope(e["vo"])
    near = np.zeros(len(env), bool)
    for a, b in words:
        near[max(0, int((a - wpad) * 100)): int((b + wpad) * 100) + 1] = True
    sp = (env > th) & near
    runs, i = [], 0
    while i < len(sp):
        if sp[i]:
            j = i
            while j < len(sp) and sp[j]:
                j += 1
            if runs and i / 100 - runs[-1][1] < join:
                runs[-1][1] = j / 100
            else:
                runs.append([i / 100, j / 100])
            i = j
        else:
            i += 1
    P = [[max(0.0, a - lead), b + tail] for a, b in runs]
    for x, y in zip(P, P[1:]):
        x[1] = min(x[1], y[0])
    return P


def compile_timeline(e, hook):
    hook_rng = e["hooks"][hook]
    cuts = [tuple(c) for c in e.get("cuts", [])]
    speech = speech_pieces(e)
    gaps = [(a[1], b[0]) for a, b in zip(speech, speech[1:]) if b[0] > a[1]]
    removals = cuts + gaps + [(0, speech[0][0]), (speech[-1][1], 1e9)]
    pieces = keep(hook_rng, removals) + keep(e["body"], removals)
    if e.get("vo_pieces", {}).get(hook):
        # the editor's own voiceover cuts, read from their CapCut edit: use them exactly
        pieces = [tuple(p) for p in e["vo_pieces"][hook]]
    inserts = sorted(e.get("inserts", []), key=lambda i: i["at"])

    # lay pieces and inserts end to end, each piece starting on a whole frame, so caption, shot and
    # voice piece can share one tick (rulebook 7.8ad)
    vo, ins, t = [], [], 0.0
    hook_end = None
    for i, (a, b) in enumerate(pieces):
        b = a + max(1, round((b - a) * FPS)) / FPS
        vo.append(dict(src_in=a, src_out=b, start=t))
        t += b - a
        if b <= hook_rng[1] + 1e-6 and (i + 1 == len(pieces) or pieces[i + 1][0] >= hook_rng[1]):
            hook_end = t
        nxt = pieces[i + 1][0] if i + 1 < len(pieces) else 1e9
        for x in inserts:
            if b <= x["at"] < nxt:
                d = round((x["out"] - x["in"]) * FPS) / FPS
                ins.append(dict(x, start=t, end=t + d))
                t += d
    total_speech = t

    def omap(ts):
        """original VO second -> output second (inside a removed span: the next kept piece)."""
        for p in vo:
            if p["src_in"] - 1e-6 <= ts <= p["src_out"] + 1e-6:
                return p["start"] + ts - p["src_in"]
            if ts < p["src_in"]:
                return p["start"]
        return total_speech

    tail = e.get("tail", 0.5)
    total = total_speech + tail

    # Every caption starts on the frame its first word starts, read from the audio (rulebook 7.8aa).
    # No captions under the hook slot (3.2); the first caption appears the moment it ends (7.7).
    env = vo_envelope(e["vo"])
    body_caps = [c for c in e["captions"] if e["body"][0] - 0.05 <= c["t"] < e["body"][1]]
    piece_f = [int(round(p["start"] * FPS)) for p in vo]
    events, prev = [], -1
    for c in body_caps:
        f = frame_of(onset_out(omap(c["t"]), vo, env))
        # a line that opens a voice piece starts on the piece's own tick (7.8ad): the word onset sits
        # a frame or two in, and a transcript start in the last piece's tail would land early
        near = [pf for pf in piece_f if f - 4 <= pf <= f + 12]
        if near:
            f = min(near, key=lambda pf: abs(pf - f))
        f = max(f, prev + 6)                       # never shorter than 0.2s
        events.append(dict(c, f=f))
        prev = f
    for x in ins:
        x["f"] = frame_of(x["start"])
        events.append(dict(text=x["caption"], t=None, f=x["f"], insert=True))
    events.sort(key=lambda c: c["f"])
    total_f = int(round(total * FPS))
    box = e.get("end_box")
    box_f = next((c["f"] for c in events if box and c["text"] == box["at"]), total_f)
    caps = []
    for i, c in enumerate(events):
        if c["f"] >= box_f:
            break
        end_f = min(events[i + 1]["f"] if i + 1 < len(events) else total_f, box_f)   # hold until the next one: no blanks (7.7)
        caps.append(dict(text=c["text"], f0=c["f"], f1=end_f, start=c["f"] / FPS, end=end_f / FPS))
    off = [(c["text"], c["f0"], pf) for c in caps for pf in piece_f if c["f0"] != pf and -4 <= pf - c["f0"] <= 12]
    if off:
        sys.exit("caption not on its voice piece's tick (7.8ad):\n  " +
                 "\n  ".join("%r at %.2fs, piece starts %.2fs" % (t, a / FPS, p / FPS) for t, a, p in off))
    hook_f = events[0]["f"]
    hook_end = hook_f / FPS

    # B-roll starts on the same frame as the caption it belongs to (7.8b)
    cap_f = {c["t"]: c["f"] for c in events if c.get("t") is not None}
    shots = [dict(clip=e["hook_card"], src_in=0, speed=1, zoom=1, x=0, y=0, mute=True, f0=0, kind="hook")]
    for sh in e["shots"]:
        if sh["t"] in cap_f:
            sh = dict(sh, f0=cap_f[sh["t"]])
            if "zoom" not in sh and os.path.basename(sh["clip"]).startswith("hf_"):
                sh["zoom"] = 1.03                  # AI clips can have thin black edge bars (6.29)
            shots.append(sh)
    for x in ins:
        shots.append(dict(clip=x["clip"], src_in=x["in"], speed=1, zoom=x.get("zoom", 1), x=x.get("x", 0), y=x.get("y", 0),
                          mute=False, volume=x.get("volume", 1.0), f0=x["f"], kind="insert"))
    shots.sort(key=lambda s: s["f0"])
    shots[1]["f0"] = hook_f
    for i, sh in enumerate(shots):
        sh["f1"] = shots[i + 1]["f0"] if i + 1 < len(shots) else total_f
        sh["start"], sh["end"] = sh["f0"] / FPS, sh["f1"] / FPS
    shots = [sh for sh in shots if sh["f1"] > sh["f0"]]
    for sh in shots:
        need = (sh["end"] - sh["start"]) * sh.get("speed", 1)
        info = probe(sh["clip"])
        if sh["src_in"] + need > info["dur"] - 0.04:
            sh["warn"] = "clip too short: wanted %.2f-%.2f of %.2fs" % (sh["src_in"], sh["src_in"] + need, info["dur"])
            sh["src_in"] = max(0, info["dur"] - 0.04 - need)
            if sh["src_in"] == 0 and need > info["dur"]:
                sh["speed"] = round(info["dur"] / (sh["end"] - sh["start"]) * 0.98, 3)
    end_box = dict(box, f0=box_f, start=box_f / FPS) if box and box_f < total_f else None
    HT.check_spans([(c["f0"], c["f1"], c["text"]) for c in caps], [sh["f0"] for sh in shots[1:]],
                   first=hook_f, last=box_f)
    total = total_f / FPS
    return dict(vo=vo, inserts=ins, captions=caps, shots=shots, hook_end=hook_end, total=total, end_box=end_box)


# ---------------------------------------------------------------- house text

import house_captions as HT         # the one caption engine for every style (rulebook 7, 11a)


def text_frames(tl, work):
    """(first frame, last frame + 1, png) for every caption and the end box, on exact frames."""
    os.makedirs(work, exist_ok=True)
    sched = []
    for k, c in enumerate(tl["captions"]):
        pth = os.path.join(work, "cap%03d.png" % k)
        HT.caption_img(balance_lines(c["text"])).save(pth, compress_level=1)
        sched.append((c["f0"], c["f1"], pth))
    b = tl.get("end_box")
    if b:
        # the end stack, at the editor's CapCut positions (style.md). Drawn in the house box font:
        # the CapCut project's Montserrat Bold isn't matched here yet
        texts = b.get("stack") or ["SHOP NOW FOR\nUP TO 50% OFF \U0001F381", "60-DAY GUARANTEE ✅", "LOW STOCK ⚠️"]
        box = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        for txt, cy, red in zip(texts, (0.41, -0.30, -0.46), (False, False, True)):
            lines = txt.split("\n")
            hgt = HT.BOX_H2 if len(lines) > 1 else HT.BOX_H1
            spec = dict(lines=lines, color=HT.RED if red else HT.WHITE, ink=HT.WHITE if red else (0, 0, 0, 255),
                        top=round(H / 2 - cy * H / 2 - hgt / 2), paren=None)
            box.alpha_composite(HT.box_layer(spec))
        ys = H / 2
        f = b["f0"]
        total_f = int(round(tl["total"] * FPS))
        for k in HT.BOUNCE:
            m = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            sc = box.resize((round(W * k), round(H * k)), Image.LANCZOS)
            m.alpha_composite(sc.crop((max(0, round(540 * k - 540)), max(0, round(ys * k - ys)), sc.width, sc.height)),
                              (max(0, round(540 - 540 * k)), max(0, round(ys - ys * k))))
            pth = os.path.join(work, "box%02d.png" % len(sched))
            m.save(pth, compress_level=1)
            sched.append((f, f + 1, pth))
            f += 1
        pth = os.path.join(work, "box.png")
        box.save(pth, compress_level=1)
        sched.append((f, total_f, pth))
    return sched


# ---------------------------------------------------------------- MP4

def render_mp4(e, tl, out, work, reuse=False):
    os.makedirs(work, exist_ok=True)
    segs = []
    video = os.path.join(work, "video.mp4")
    audio = os.path.join(work, "audio.wav")
    shots = [] if reuse and os.path.exists(video) else tl["shots"]
    for i, s in enumerate(shots):
        info = probe(s["clip"])
        dur = s["end"] - s["start"]
        sp = s.get("speed", 1)
        cover = max(W / info["w"], H / info["h"]) * s.get("zoom", 1)
        sw, sh = int(info["w"] * cover / 2) * 2, int(info["h"] * cover / 2) * 2
        ox = int((W - sw) / 2 + s.get("x", 0) * W / 2)
        oy = int((H - sh) / 2 - s.get("y", 0) * H / 2)
        f = os.path.join(work, "shot%03d.mp4" % i)
        vf = ("[0:v]setpts=(PTS-STARTPTS)/%s,fps=%d,scale=%d:%d,setsar=1[v];color=black:s=%dx%d:r=%d[bg];"
              "[bg][v]overlay=%d:%d:shortest=1,eq=contrast=1.03:saturation=1.05,tpad=stop_mode=clone:stop_duration=2,format=yuv420p,setparams=range=tv:color_primaries=bt709:color_trc=bt709:colorspace=bt709[o]"
              % (sp, FPS, sw, sh, W, H, FPS, ox, oy))
        run([FF, "-v", "error", "-y", "-ss", "%.3f" % s["src_in"], "-t", "%.3f" % (dur * sp + 0.3), "-i", s["clip"],
             "-filter_complex", vf, "-map", "[o]", "-frames:v", str(s["f1"] - s["f0"]), "-an", "-c:v", "libx264",
             "-preset", "veryfast", "-crf", "18", f])
        segs.append(f)
    if shots:
        lst = os.path.join(work, "shots.txt")
        open(lst, "w", encoding="utf-8").write("".join("file '%s'\n" % f.replace("\\", "/") for f in segs))
        # re-time by frame number, so frame n of the picture is frame n of the text layer
        run([FF, "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-vf", "setpts=N/(%d*TB)" % FPS, "-r", str(FPS),
             "-c:v", "libx264", "-preset", "ultrafast", "-crf", "12", video])
        got = int(re.findall(r"frame=\s*(\d+)", run([FF, "-i", video, "-map", "0:v", "-f", "null", "-"]).stderr)[-1])
        want = sum(s["f1"] - s["f0"] for s in shots)
        if got != want:
            sys.exit("picture has %d frames, timeline has %d" % (got, want))
        for f in segs:
            os.remove(f)

    # audio: VO pieces, insert sound, music bed
    inputs, parts, n = ["-i", e["vo"]], [], 1
    for j, p in enumerate(tl["vo"]):
        parts.append("[0:a]atrim=%.3f:%.3f,asetpts=PTS-STARTPTS,afade=t=in:d=0.008,afade=t=out:st=%.3f:d=0.008,adelay=%d:all=1[v%d]"
                     % (p["src_in"], p["src_out"], p["src_out"] - p["src_in"] - 0.008, p["start"] * 1000, j))
    labels = ["[v%d]" % j for j in range(len(tl["vo"]))]
    parts.append("%samix=inputs=%d:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=11[vo]" % ("".join(labels), len(labels)))
    mix = ["[vo]"]
    for x in tl["inserts"]:
        inputs += ["-i", x["clip"]]
        parts.append("[%d:a]atrim=%.3f:%.3f,asetpts=PTS-STARTPTS,loudnorm=I=-17:TP=-2,volume=%s,adelay=%d:all=1[i%d]"
                     % (n, x["in"], x["out"], x.get("volume", 1.0), x["start"] * 1000, n))
        mix.append("[i%d]" % n)
        n += 1
    if tl.get("end_box") and e.get("click"):
        inputs += ["-i", e["click"]]
        d = int((tl["end_box"]["start"] + HT.CLICK_DELAY) * 1000)
        parts.append("[%d:a]volume=0.5,adelay=%d:all=1[ck]" % (n, d))
        mix.append("[ck]")
        n += 1
    if e.get("music"):
        inputs += ["-stream_loop", "-1", "-i", e["music"]["path"]]
        parts.append("[%d:a]atrim=%.3f:%.3f,asetpts=PTS-STARTPTS,loudnorm=I=%s,afade=t=out:st=%.3f:d=0.6[m]"
                     % (n, e["music"].get("in", 0), e["music"].get("in", 0) + tl["total"], e["music"].get("lufs", -37),
                        tl["total"] - 0.6))
        mix.append("[m]")
        n += 1
    parts.append("%samix=inputs=%d:normalize=0:duration=longest,atrim=0:%.3f,alimiter=limit=0.82[a]"
                 % ("".join(mix), len(mix), tl["total"]))
    if shots or not os.path.exists(audio):
        run([FF, "-v", "error", "-y"] + inputs + ["-filter_complex", ";".join(parts), "-map", "[a]", "-ar", "48000", audio])

    sched = text_frames(tl, os.path.join(work, "text"))
    blank = os.path.join(work, "text", "blank.png")
    Image.new("RGBA", (W, H), (0, 0, 0, 0)).save(blank)
    pr = subprocess.Popen([FF, "-y", "-v", "error", "-i", video, "-i", audio, "-f", "image2pipe", "-framerate", str(FPS),
                           "-c:v", "png", "-i", "-", "-filter_complex",
                           "[0:v]setpts=N/(%d*TB)[b];[2:v]format=rgba,setpts=N/(%d*TB)[t];[b][t]overlay=0:0:format=auto:shortest=1,format=yuv420p[v]" % (FPS, FPS),
                           "-map", "[v]", "-map", "1:a", "-c:v", "libx264", "-preset", "medium", "-b:v", "12M",
                           "-maxrate", "14M", "-bufsize", "24M", "-r", str(FPS), "-fps_mode", "cfr", "-c:a", "aac", "-b:a", "192k",
                           "-ac", "2", "-movflags", "+faststart", "-t", "%.3f" % tl["total"], out], stdin=subprocess.PIPE)
    cache = {}
    data = lambda pth: cache.setdefault(pth, open(pth, "rb").read())
    pos, total_f = 0, int(round(tl["total"] * FPS)) + 1
    for f0, f1, pth in sorted(sched):
        for _ in range(pos, f0):
            pr.stdin.write(data(blank))
        for _ in range(max(pos, f0), f1):
            pr.stdin.write(data(pth))
        pos = max(pos, f1)
    for _ in range(pos, total_f):
        pr.stdin.write(data(blank))
    pr.stdin.close()
    if pr.wait():
        sys.exit("text pass failed")
    return out


# ---------------------------------------------------------------- CapCut

def localise(obj):
    """Template paths are written with {CAPCUT_FONT} and {CAPCUT_CACHE}; point them at this computer's CapCut."""
    font = P.capcut_path(os.path.dirname(P.capcut_font() or ""))
    cache = P.capcut_path(P.capcut_cache())
    if isinstance(obj, str):
        return obj.replace("{CAPCUT_FONT_DIR}", font).replace("{CAPCUT_CACHE}", cache)
    if isinstance(obj, list):
        return [localise(x) for x in obj]
    if isinstance(obj, dict):
        return {k: localise(v) for k, v in obj.items()}
    return obj


def load_draft(name):
    if name.endswith(".json") and os.path.isfile(name):    # a saved timeline in templates/
        with open(name, encoding="utf-8") as f:
            return json.load(f)
    with open(C.draft_file(C.project_path(name)), encoding="utf-8") as f:
        return json.load(f)


def find_audio(project, pred):
    d = load_draft(project)
    mats = by_id(d)
    for ti, t in enumerate(d["tracks"]):
        if t["type"] == "audio":
            for si, sg in enumerate(t["segments"]):
                if pred(mats[sg["material_id"]][1].get("name", "")):
                    return Proto(d, ti, si)
    sys.exit("no audio prototype in " + project)


def by_id(d):
    return {m["id"]: (k, m) for k, v in d["materials"].items() if isinstance(v, list) for m in v
            if isinstance(m, dict) and "id" in m}


class Proto:
    """A segment plus its material and extra materials, copied with fresh ids."""

    def __init__(self, draft, track_index, seg_index):
        mats = by_id(draft)
        self.track = {k: v for k, v in draft["tracks"][track_index].items() if k != "segments"}
        self.seg = draft["tracks"][track_index]["segments"][seg_index]
        self.mat = mats[self.seg["material_id"]]
        self.refs = [mats[r] for r in self.seg["extra_material_refs"] if r in mats]

    def make(self, out_mats):
        seg = copy.deepcopy(self.seg)
        kind, mat = self.mat[0], copy.deepcopy(self.mat[1])
        mat["id"] = uid()
        seg["id"] = uid()
        seg["material_id"] = mat["id"]
        seg["extra_material_refs"] = []
        refs = {}
        for k, m in self.refs:
            m = copy.deepcopy(m)
            m["id"] = uid()
            out_mats.setdefault(k, []).append(m)
            seg["extra_material_refs"].append(m["id"])
            refs[k] = m
        out_mats.setdefault(kind, []).append(mat)
        seg["keyframe_refs"] = []
        seg["common_keyframes"] = []
        return seg, mat, refs


def tr(start, dur):
    # round the end, not the duration, so back-to-back segments never overlap
    a, b = int(round(start * US)), int(round((start + dur) * US))
    return {"start": a, "duration": b - a}


def text_content(text, proto_content):
    """CapCut text content JSON in the prototype's own style (font, fill, stroke). Ranges count UTF-16 units, as CapCut does."""
    st = copy.deepcopy(json.loads(proto_content)["styles"][0])
    st["range"] = [0, len(text.encode("utf-16-le")) // 2]
    return json.dumps({"styles": [st], "text": text}, ensure_ascii=False)


def find_text(project, pred):
    d = load_draft(project)
    mats = by_id(d)
    for ti, t in enumerate(d["tracks"]):
        if t["type"] == "text":
            for si, sg in enumerate(t["segments"]):
                if pred(json.loads(mats[sg["material_id"]][1]["content"])["text"], sg):
                    return Proto(d, ti, si)
    sys.exit("no text prototype in " + project)


def write_capcut(e, tl, name, cover_jpg):
    root = C.DRAFTS
    dest = os.path.join(root, name)
    if os.path.exists(dest):
        sys.exit("CapCut project already exists: %s" % name)
    if P.capcut_running():
        sys.exit("CapCut is open: close it before writing a project")
    tpl = load_draft(TEMPLATE)
    tidx = {t["type"]: i for i, t in enumerate(tpl["tracks"])}
    vproto = Proto(tpl, 1, 0)
    text_i = [i for i, t in enumerate(tpl["tracks"]) if t["type"] == "text"][0]
    tproto = find_text(USER_TEMPLATE, lambda txt, sg: txt == "caption")
    sprotos = [find_text(USER_TEMPLATE, lambda txt, sg, p=p: txt.startswith(p)) for p in STACK]
    cproto = find_audio(USER_TEMPLATE, lambda n: n.startswith("Click_Mouse_Click_02"))
    audio_tracks = [i for i, t in enumerate(tpl["tracks"]) if t["type"] == "audio"]
    aproto = Proto(tpl, audio_tracks[0], 0)
    mproto = Proto(tpl, audio_tracks[-1], 0)
    d = copy.deepcopy(tpl)
    for k, v in d["materials"].items():
        if isinstance(v, list):
            d["materials"][k] = []
    mats = d["materials"]
    # d["id"] must stay the template's main timeline id: CapCut finds the timeline folder by it
    d["duration"] = int(round(tl["total"] * US))
    d["config"]["subtitle_taskinfo"] = []
    tracks = []

    def new_track(proto, typ):
        t = copy.deepcopy(proto.track)
        t.update(id=uid(), type=typ, segments=[])
        tracks.append(t)
        return t

    vt = new_track(vproto, "video")
    for i, s in enumerate(tl["shots"]):
        seg, mat, refs = vproto.make(mats)
        info = probe(s["clip"])
        sp = s.get("speed", 1)
        dur = s["end"] - s["start"]
        mat.update(path=s["clip"], material_name=os.path.basename(s["clip"]), duration=int(info["dur"] * US),
                   width=info["w"], height=info["h"], type="video")
        for key in ("media_path", "local_material_id"):
            if key in mat:
                mat[key] = "" if key == "media_path" else mat[key]
        if "speeds" in refs:
            refs["speeds"]["speed"] = sp
        fit = min(W / info["w"], H / info["h"])
        cover = max(W / info["w"], H / info["h"])
        sc = round(cover / fit * s.get("zoom", 1), 4)
        seg.update(source_timerange=tr(s["src_in"], dur * sp), target_timerange=tr(s["start"], dur), speed=sp,
                   volume=0.0 if s.get("mute", True) else s.get("volume", 1.0), render_index=i, track_render_index=0)
        seg["last_nonzero_volume"] = 1.0
        seg["clip"]["scale"] = {"x": sc, "y": sc}
        seg["clip"]["transform"] = {"x": s.get("x", 0), "y": s.get("y", 0)}
        vt["segments"].append(seg)

    tt = new_track(tproto, "text")
    cap_y = tproto.seg["clip"]["transform"]["y"]
    for i, c in enumerate(tl["captions"]):
        seg, mat, refs = tproto.make(mats)
        content = text_content(balance_lines(c["text"]), tproto.mat[1]["content"])
        mat.update(content=content, base_content=content, type="text", recognize_task_id="", recognize_text="",
                   words={"start_time": [], "end_time": [], "text": []})
        seg.update(target_timerange=tr(c["start"], c["end"] - c["start"]), track_render_index=1, render_index=14000 + i)
        seg["clip"]["transform"] = {"x": 0.0, "y": cap_y}
        tt["segments"].append(seg)
    b = tl.get("end_box")
    if b:
        # the three-box end stack, each box on its own track at the editor's positions (style.md)
        for k, sp in enumerate(sprotos):
            bt = new_track(sp, "text")
            seg, mat, refs = sp.make(mats)
            if b.get("stack"):
                content = text_content(b["stack"][k], sp.mat[1]["content"])
                mat.update(content=content, base_content=content)
            seg.update(target_timerange=tr(b["start"], tl["total"] - b["start"]), track_render_index=len(tracks) - 1)
            bt["segments"].append(seg)

    at = new_track(aproto, "audio")
    vo_info = probe(e["vo"])
    for p in tl["vo"]:
        seg, mat, refs = aproto.make(mats)
        mat.update(path=e["vo"], name=os.path.basename(e["vo"]), duration=int(vo_info["dur"] * US))
        seg.update(source_timerange=tr(p["src_in"], p["src_out"] - p["src_in"]),
                   target_timerange=tr(p["start"], p["src_out"] - p["src_in"]), volume=e.get("capcut_vo_volume", VO_VOLUME),
                   speed=1.0, track_render_index=2)
        at["segments"].append(seg)
    if b and os.path.exists(localise(cproto.mat[1]["path"])):
        ct = new_track(cproto, "audio")
        seg, mat, refs = cproto.make(mats)
        seg.update(target_timerange=tr(b["start"], seg["target_timerange"]["duration"] / US), track_render_index=3)
        ct["segments"].append(seg)
    if e.get("music"):
        mt = new_track(mproto, "audio")
        m = e["music"]
        mi = probe(m["path"])
        seg, mat, refs = mproto.make(mats)
        mat.update(path=m["path"], name=os.path.basename(m["path"]), duration=int(mi["dur"] * US))
        mdur = min(tl["total"], mi["dur"] - m.get("in", 0))
        seg.update(source_timerange=tr(m.get("in", 0), mdur), target_timerange=tr(0, mdur),
                   volume=m.get("capcut_volume", MUSIC_VOLUME), speed=1.0, track_render_index=3)
        mt["segments"].append(seg)
    d["tracks"] = tracks
    d = localise(d)
    if b and not any(t["type"] == "audio" and t["segments"] and "Click" in by_id(d)[t["segments"][0]["material_id"]][1].get("name", "")
                     for t in tracks):
        print("note: CapCut's Click_Mouse_Click_02 sound isn't in your CapCut cache yet, so the end stack has no click."
              " Add it once from CapCut's sound effects and later builds will include it.")

    # clone the template folder like CapCut's Duplicate, then swap the timeline in
    src = C.project_path(TEMPLATE)
    shutil.copytree(src, dest, ignore=shutil.ignore_patterns("*.bak", "template*.tmp", "matting", "smart_crop",
                                                              "adjust_mask", "qr_upload", "subdraft"))
    main = json.load(open(os.path.join(dest, "Timelines", "project.json"), encoding="utf-8"))
    now = int(time.time() * US)
    main["id"] = uid()
    main["create_time"] = main["update_time"] = now
    json.dump(main, open(os.path.join(dest, "Timelines", "project.json"), "w", encoding="utf-8"))
    # CapCut can't read hidden folders like ~/.video-editing-work, so copy those files into the project
    media = os.path.join(dest, "Resources", "media")
    for k in ("videos", "audios"):
        for m in d["materials"].get(k, []):
            if m.get("path") and (P.hidden(m["path"]) or m["path"].startswith(HERE)):
                os.makedirs(media, exist_ok=True)
                to = os.path.join(media, os.path.basename(m["path"]))
                if not os.path.exists(to):
                    shutil.copy(m["path"], to)
                m["path"] = P.capcut_path(to)
            elif m.get("path"):
                m["path"] = P.capcut_path(m["path"])
    for p in [os.path.join(dest, "draft_info.json"), os.path.join(dest, "Timelines", main["main_timeline_id"], "draft_info.json")]:
        with open(p, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False)
    if cover_jpg:
        shutil.copy(cover_jpg, os.path.join(dest, "draft_cover.jpg"))
        shutil.copy(cover_jpg, os.path.join(dest, "Timelines", main["main_timeline_id"], "draft_cover.jpg"))
    meta_p = os.path.join(dest, "draft_meta_info.json")
    meta = json.load(open(meta_p, encoding="utf-8"))
    draft_id = uid()
    meta.update(draft_id=draft_id, draft_name=name, draft_fold_path=P.capcut_path(dest), draft_root_path=P.capcut_path(root),
                tm_duration=d["duration"], tm_draft_create=now, tm_draft_modified=now,
                draft_timeline_materials_size_=0)
    # start with an empty media panel; the editor imports their own clips (2026-11-05)
    for g in meta.get("draft_materials", []):
        g["value"] = []
    json.dump(meta, open(meta_p, "w", encoding="utf-8"), ensure_ascii=False)

    # list the project in CapCut's index, so it shows on CapCut's home screen
    rp = os.path.join(root, "root_meta_info.json")
    if os.path.exists(rp):
        shutil.copy(rp, rp + ".before-%s.bak" % re.sub(r"\W+", "_", name))
        rm = json.load(open(rp, encoding="utf-8"))
    else:
        rm = {"all_draft_store": [], "draft_ids": 0, "root_path": P.capcut_path(root)}
    ent = json.load(open(ROOT_ENTRY, encoding="utf-8"))
    ent.update(draft_id=draft_id, draft_name=name, draft_fold_path=P.capcut_path(dest), draft_root_path=P.capcut_path(root),
               draft_cover=P.capcut_path(os.path.join(dest, "draft_cover.jpg")),
               draft_json_file=P.capcut_path(os.path.join(dest, "draft_info.json")),
               tm_duration=d["duration"], tm_draft_create=now, tm_draft_modified=now, draft_timeline_materials_size=0)
    rm["all_draft_store"].insert(0, ent)
    json.dump(rm, open(rp, "w", encoding="utf-8"), ensure_ascii=False)
    return dest


def main(argv):
    edit = json.load(open(argv[1], encoding="utf-8"))
    hook = argv[argv.index("--hook") + 1] if "--hook" in argv else "A"
    tl = compile_timeline(edit, hook)
    base = os.path.dirname(os.path.abspath(argv[1]))
    work = os.path.join(base, "build", "Hook" + hook)
    os.makedirs(work, exist_ok=True)
    json.dump(tl, open(os.path.join(work, "timeline.json"), "w", encoding="utf-8"), indent=1)
    print("Hook %s: %.2fs, hook slot %.2fs, %d shots, %d captions, %d VO pieces"
          % (hook, tl["total"], tl["hook_end"], len(tl["shots"]), len(tl["captions"]), len(tl["vo"])))
    for s in tl["shots"]:
        if s.get("warn"):
            print("  WARN %.2f %s: %s" % (s["start"], os.path.basename(s["clip"]), s["warn"]))
        if s["end"] - s["start"] > 3.2 and s.get("kind") != "hook":
            print("  LONG %.2f-%.2f %s" % (s["start"], s["end"], os.path.basename(s["clip"])))
    if "--mp4" in argv:
        out = os.path.join(work, "%s_Hook%s.mp4" % (edit["code"], hook))
        render_mp4(edit, tl, out, os.path.join(work, "parts"), reuse="--reuse" in argv)
        print("mp4:", out)
    if "--capcut" in argv:
        name = argv[argv.index("--name") + 1] if "--name" in argv else "%s Hook%s" % (edit["code"], hook)
        cover = os.path.join(work, "cover.jpg")
        mp4 = os.path.join(work, "%s_Hook%s.mp4" % (edit["code"], hook))
        if os.path.exists(mp4):
            run([FF, "-v", "error", "-y", "-ss", "%.2f" % (tl["hook_end"] + 1), "-i", mp4, "-frames:v", "1", "-vf", "scale=540:-2", cover])
        dest = write_capcut(edit, tl, name, cover if os.path.exists(cover) else None)
        snap = os.path.join(work, "capcut_snapshot.json")
        json.dump(C.normalise(dest), open(snap, "w", encoding="utf-8"), indent=1)
        print("capcut:", dest, "\nsnapshot:", snap)


if __name__ == "__main__":
    main(sys.argv)
