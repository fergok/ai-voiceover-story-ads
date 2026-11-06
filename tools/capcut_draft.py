#!/usr/bin/env python3
"""Read CapCut desktop projects, so edits made by hand in CapCut can be learned from.

CapCut (desktop, Mac or Windows) saves each project as plain JSON in DRAFTS. The timeline
is in Timelines/<main_timeline_id>/draft_info.json, with an identical copy at the
project root. Times in the file are microseconds; clip positions are fractions of
the half-canvas (x, y from -1 to 1, y up).

  capcut_draft.py list                         projects, newest first
  capcut_draft.py dump <project> [--json]      readable timeline
  capcut_draft.py snapshot <project> <out>     save a timeline to compare against later
  capcut_draft.py diff <before> <after>        what changed (each side a project or snapshot)

<project> is a folder name in DRAFTS or a full path.
"""
import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import platform_paths as P

DRAFTS = P.capcut_drafts()
US = 1_000_000


def project_path(name):
    return name if os.path.isdir(name) else os.path.join(DRAFTS, name)


def draft_file(path):
    try:
        with open(os.path.join(path, "Timelines", "project.json"), encoding="utf-8") as f:
            main = json.load(f)["main_timeline_id"]
        p = os.path.join(path, "Timelines", main, "draft_info.json")
        if os.path.exists(p):
            return p
    except (OSError, KeyError, ValueError):
        pass
    return os.path.join(path, "draft_info.json")


def text_details(m):
    try:
        c = json.loads(m.get("content") or "{}")
    except ValueError:
        c = {}
    styles = c.get("styles") or [{}]
    s = styles[0]
    font = os.path.basename((s.get("font") or {}).get("path", "")) or None
    color = (((s.get("fill") or {}).get("content") or {}).get("solid") or {}).get("color")
    return {
        "text": c.get("text", ""),
        "font": font,
        "size": s.get("size", m.get("font_size")),
        "color": "#%02x%02x%02x" % tuple(round(v * 255) for v in color) if color else m.get("text_color"),
        "bold_parts": sum(1 for x in styles if x.get("bold")),
        "background": m.get("background_color") if m.get("background_alpha") else None,
        "border_width": m.get("border_width"),
    }


def normalise(project):
    """Reduce a project to the parts an editor changes: what plays when, where, and how."""
    with open(draft_file(project), encoding="utf-8") as f:
        d = json.load(f)
    mats = {}
    for kind, items in d["materials"].items():
        if isinstance(items, list):
            for m in items:
                if isinstance(m, dict) and "id" in m:
                    mats[m["id"]] = (kind, m)
    tracks = []
    for ti, t in enumerate(d["tracks"]):
        segs = []
        for s in t["segments"]:
            kind, m = mats.get(s["material_id"], (None, {}))
            tr = s["target_timerange"]
            seg = {
                "id": s["id"],
                "start": round(tr["start"] / US, 3),
                "end": round((tr["start"] + tr["duration"]) / US, 3),
            }
            src = s.get("source_timerange")
            if src:
                seg["src_in"] = round(src["start"] / US, 3)
                seg["src_out"] = round((src["start"] + src["duration"]) / US, 3)
            if kind == "texts":
                seg.update(text_details(m))
            elif m:
                seg["file"] = m.get("material_name") or m.get("name") or os.path.basename(m.get("path", ""))
                seg["path"] = m.get("path")
            elif kind:
                seg["kind"] = kind
            clip = s.get("clip")
            if clip:
                seg["scale"] = round(clip["scale"]["x"], 3)
                seg["x"] = round(clip["transform"]["x"], 3)
                seg["y"] = round(clip["transform"]["y"], 3)
            if t["type"] in ("video", "audio"):
                seg["volume"] = round(s.get("volume", 1.0), 3)
            if s.get("speed", 1.0) != 1.0:
                seg["speed"] = round(s["speed"], 3)
            segs.append(seg)
        tracks.append({"index": ti, "type": t["type"], "id": t.get("id"), "segments": segs})
    return {
        "project": os.path.basename(project.rstrip("/")),
        "read_at": datetime.now().isoformat(timespec="seconds"),
        "duration": round(d["duration"] / US, 3),
        "canvas": [d["canvas_config"]["width"], d["canvas_config"]["height"]],
        "tracks": tracks,
    }


def load(arg):
    if arg.endswith(".json") and os.path.isfile(arg):
        with open(arg, encoding="utf-8") as f:
            return json.load(f)
    return normalise(project_path(arg))


def label(seg):
    if "text" in seg:
        return '"%s"' % seg["text"].replace("\n", " / ")
    return seg.get("file") or seg.get("kind") or "?"


def dump(n):
    print("%s  %.2fs  %dx%d" % (n["project"], n["duration"], *n["canvas"]))
    for t in n["tracks"]:
        print("\n[track %d: %s, %d segments]" % (t["index"], t["type"], len(t["segments"])))
        for s in t["segments"]:
            bits = ["%6.2f-%6.2f" % (s["start"], s["end"]), label(s)]
            if "src_in" in s:
                bits.append("src %.2f-%.2f" % (s["src_in"], s["src_out"]))
            if "scale" in s and (s["scale"] != 1 or s["x"] or s["y"]):
                bits.append("scale %.2f pos %.2f,%.2f" % (s["scale"], s["x"], s["y"]))
            if "font" in s:
                bits.append("%s %s %s" % (s["font"], s["size"], s["color"]))
            if s.get("volume", 1) != 1:
                bits.append("vol %.2f" % s["volume"])
            if "speed" in s:
                bits.append("speed %.2f" % s["speed"])
            print("  " + "  ".join(bits))


def diff(a, b):
    """List edits from a to b. Segments are matched by CapCut's segment id, which survives moves and trims."""
    out = []
    old = {s["id"]: (t["type"], s) for t in a["tracks"] for s in t["segments"]}
    new = {s["id"]: (t["type"], s) for t in b["tracks"] for s in t["segments"]}
    if a["duration"] != b["duration"]:
        out.append("length %.2fs -> %.2fs" % (a["duration"], b["duration"]))
    for sid, (typ, s) in old.items():
        if sid not in new:
            out.append("removed %s %s at %.2f-%.2f" % (typ, label(s), s["start"], s["end"]))
    # An insert or delete ripples everything after it; report that once, not per clip.
    shifts = {}
    for sid, (typ, s) in new.items():
        o = old.get(sid, (None, None))[1]
        if o and o["start"] != s["start"] and round(o["end"] - o["start"], 2) == round(s["end"] - s["start"], 2):
            delta = round(s["start"] - o["start"], 2)
            shifts.setdefault(delta, []).append(o["start"])
    for delta, starts in sorted(shifts.items()):
        if len(starts) > 2:
            out.append("%d segments from %.2fs on shifted %+.2fs (ripple)" % (len(starts), min(starts), delta))
    ripple = {d for d, starts in shifts.items() if len(starts) > 2}
    for sid, (typ, s) in new.items():
        if sid not in old:
            out.append("added %s %s at %.2f-%.2f" % (typ, label(s), s["start"], s["end"]))
            continue
        o = old[sid][1]
        changes = []
        moved = round(s["start"] - o["start"], 2)
        same_len = round(o["end"] - o["start"], 2) == round(s["end"] - s["start"], 2)
        if (o["start"], o["end"]) != (s["start"], s["end"]) and not (same_len and moved in ripple):
            changes.append("timing %.2f-%.2f -> %.2f-%.2f" % (o["start"], o["end"], s["start"], s["end"]))
        for k in ("src_in", "src_out", "file", "text", "font", "size", "color", "bold_parts",
                  "background", "scale", "x", "y", "volume", "speed"):
            if o.get(k) != s.get(k):
                changes.append("%s %r -> %r" % (k, o.get(k), s.get(k)))
        if changes:
            out.append("changed %s %s: %s" % (typ, label(o), "; ".join(changes)))
    return out


def main(argv):
    if len(argv) < 2:
        sys.exit(__doc__)
    cmd = argv[1]
    if cmd == "list":
        rows = []
        for name in os.listdir(DRAFTS):
            p = os.path.join(DRAFTS, name)
            if os.path.isdir(p) and os.path.exists(os.path.join(p, "draft_info.json")):
                rows.append((os.path.getmtime(draft_file(p)), name))
        for mt, name in sorted(rows, reverse=True):
            print("%s  %s" % (datetime.fromtimestamp(mt).strftime("%Y-%m-%d %H:%M"), name))
    elif cmd == "dump" and len(argv) >= 3:
        n = load(argv[2])
        print(json.dumps(n, indent=1)) if "--json" in argv else dump(n)
    elif cmd == "snapshot" and len(argv) == 4:
        with open(argv[3], "w", encoding="utf-8") as f:
            json.dump(normalise(project_path(argv[2])), f, indent=1)
        print("saved", argv[3])
    elif cmd == "diff" and len(argv) == 4:
        changes = diff(load(argv[2]), load(argv[3]))
        print("\n".join(changes) if changes else "no changes")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv)
