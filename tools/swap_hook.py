"""Make a hook variant from a CapCut project the editor has finished.

Copies the project like CapCut's Duplicate, then swaps only the hook: everything before the body's first voiceover
piece is taken out (hook clips, hook title, hook voice pieces), the new hook's voice pieces go in, and the whole body
moves along by the difference. The body stays exactly as the editor cut it. The hook clip slot, on the main track, gets the placeholder card,
since the editor makes hook visuals by hand.

  swap_hook.py <spec.json>

spec: {"source": "<project>", "name": "<new project>", "card": "<placeholder mp4, optional>",
       "pieces": [[src_in, src_out], ...]  (seconds in the voiceover file, breaths already left out),
       "title": "line one\\nline two 🎁"  (optional: draft hook title in the editor's own title box)}
"""
import copy, json, os, re, shutil, subprocess, sys, time, uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import capcut_draft as C
import platform_paths as P

US, FPS = 1_000_000, 30


def uid():
    return str(uuid.uuid4()).upper()


def f2us(sec):
    return int(round(round(sec * FPS) / FPS * US))


def utf16(s):
    return len(s.encode("utf-16-le")) // 2


def main(spec):
    if P.capcut_running():
        raise SystemExit("CapCut is open: close it first")
    src = C.project_path(spec["source"])
    root = os.path.dirname(src)
    dest = os.path.join(root, spec["name"])
    if os.path.exists(dest):
        raise SystemExit("already exists: " + dest)
    d = json.load(open(C.draft_file(src), encoding="utf-8"))
    vo_track = next(t for t in d["tracks"] if t["type"] == "audio" and len(t["segments"]) > 5)
    auds = {m["id"]: m for m in d["materials"]["audios"]}
    vo_segs = sorted(vo_track["segments"], key=lambda s: s["target_timerange"]["start"])
    # the hook ends where the first body clip starts on the main track
    main_t = next(t for t in d["tracks"] if t["type"] == "video" and t.get("flag") == 2) \
        if any(t.get("flag") == 2 for t in d["tracks"]) else d["tracks"][1]
    hook_end = min(s["target_timerange"]["start"] for s in main_t["segments"])
    hook_vo = [s for s in vo_segs if s["target_timerange"]["start"] < hook_end]

    # new hook voice pieces, frame-aligned and back to back
    new_len, pieces = 0, []
    for a, b in spec["pieces"]:
        dur = f2us(b - a)
        pieces.append((int(a * US), dur, new_len))
        new_len += dur
    delta = new_len - hook_end

    title_proto = None
    for t in d["tracks"]:
        keep = []
        for s in t["segments"]:
            st = s["target_timerange"]["start"]
            if t is vo_track:
                continue
            if st < hook_end and s["target_timerange"]["duration"] < d["duration"] - US:   # hook-only pieces
                if t["type"] == "text" and title_proto is None:
                    title_proto = s
                if t["type"] == "video" and t is not main_t and "card_proto" not in locals():
                    card_proto = s
                continue
            if st >= hook_end:
                s["target_timerange"]["start"] = st + delta
            else:                           # runs under the whole ad (music): fit it to the new length
                s["target_timerange"]["duration"] += delta
                s["source_timerange"]["duration"] = s["target_timerange"]["duration"]
            keep.append(s)
        t["segments"] = keep

    # voice track: new hook pieces, then the body pieces moved along
    vo_new = []
    for (a, dur, at), proto in zip(pieces, (hook_vo * len(pieces))[:len(pieces)]):
        s = copy.deepcopy(proto)
        s["id"] = uid()
        s["source_timerange"] = {"start": a, "duration": dur}
        s["target_timerange"] = {"start": at, "duration": dur}
        vo_new.append(s)
    for s in vo_segs:
        if s["target_timerange"]["start"] >= hook_end:
            s["target_timerange"]["start"] += delta
            vo_new.append(s)
    vo_track["segments"] = vo_new

    # hook clip slot: the placeholder card on the overlay track
    card = spec.get("card") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates", "hook_card.mp4")
    if not os.path.exists(card):
        raise SystemExit("no placeholder card: " + card)
    card_dest = os.path.join(dest, "Resources", "media", "hook_card.mp4")
    vids = {m["id"]: m for m in d["materials"]["videos"]}
    cm = copy.deepcopy(vids[card_proto["material_id"]])
    cm.update(id=uid(), path=P.capcut_path(card_dest), width=1080, height=1920, duration=15 * US)
    for k in ("material_name", "name"):
        if k in cm:
            cm[k] = os.path.basename(card)
    d["materials"]["videos"].append(cm)
    cs = copy.deepcopy(card_proto)
    cs.update(id=uid(), material_id=cm["id"], speed=1.0)
    cs["source_timerange"] = {"start": 0, "duration": new_len}
    cs["target_timerange"] = {"start": 0, "duration": new_len}
    cs["clip"]["scale"] = {"x": 1.0, "y": 1.0}
    cs["clip"]["transform"] = {"x": 0.0, "y": 0.0}
    main_t["segments"].insert(0, cs)    # on the main track, as the editor puts hook clips (Hooks B and C, 2026-11-06)

    # draft hook title in the editor's own title box
    if spec.get("title") and title_proto:
        texts = {m["id"]: m for m in d["materials"]["texts"]}
        tm = copy.deepcopy(texts[title_proto["material_id"]])
        tm["id"] = uid()
        c = json.loads(tm["content"])
        c["text"] = spec["title"]
        for st in c["styles"]:
            st["range"] = [0, utf16(spec["title"])]
        tm["content"] = json.dumps(c, ensure_ascii=False, separators=(",", ":"))
        d["materials"]["texts"].append(tm)
        ts = copy.deepcopy(title_proto)
        ts.update(id=uid(), material_id=tm["id"])
        ts["target_timerange"] = {"start": 0, "duration": new_len}
        for t in d["tracks"]:
            if t["type"] == "text" and t["segments"] and any(
                    s["target_timerange"]["start"] == hook_end + delta for s in t["segments"]):
                t["segments"].insert(0, ts)     # the caption track, where the editor's title sat
                break

    d["duration"] += delta
    for t in d["tracks"]:
        t["segments"].sort(key=lambda s: s["target_timerange"]["start"])
        for x, y in zip(t["segments"], t["segments"][1:]):
            if x["target_timerange"]["start"] + x["target_timerange"]["duration"] > y["target_timerange"]["start"]:
                raise SystemExit("overlap on a %s track at %.2fs" % (t["type"], y["target_timerange"]["start"] / US))

    # write the copy
    shutil.copytree(src, dest, ignore=shutil.ignore_patterns("*.bak", "template*.tmp", "matting", "smart_crop",
                                                             "adjust_mask", "qr_upload", "subdraft"))
    os.makedirs(os.path.dirname(card_dest), exist_ok=True)
    shutil.copy(card, card_dest)
    proj_p = os.path.join(dest, "Timelines", "project.json")
    proj = json.load(open(proj_p, encoding="utf-8"))
    now = int(time.time() * US)
    proj["id"] = uid()
    proj["create_time"] = proj["update_time"] = now
    json.dump(proj, open(proj_p, "w", encoding="utf-8"))
    if d.get("id") != proj["main_timeline_id"]:
        raise SystemExit("timeline id mismatch")
    for p in [os.path.join(dest, "draft_info.json"),
              os.path.join(dest, "Timelines", proj["main_timeline_id"], "draft_info.json")]:
        json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False)
    meta_p = os.path.join(dest, "draft_meta_info.json")
    meta = json.load(open(meta_p, encoding="utf-8"))
    draft_id = uid()
    meta.update(draft_id=draft_id, draft_name=spec["name"], draft_fold_path=P.capcut_path(dest), draft_root_path=P.capcut_path(root),
                tm_duration=d["duration"], tm_draft_create=now, tm_draft_modified=now)
    json.dump(meta, open(meta_p, "w", encoding="utf-8"), ensure_ascii=False)
    rp = os.path.join(root, "root_meta_info.json")
    shutil.copy(rp, rp + ".before-%s.bak" % re.sub(r"\W+", "_", spec["name"]))
    rm = json.load(open(rp, encoding="utf-8"))
    norm = lambda p: os.path.normcase(os.path.normpath(p))
    ent = copy.deepcopy(next(x for x in rm["all_draft_store"] if norm(x["draft_fold_path"]) == norm(src)))
    ent.update(draft_id=draft_id, draft_name=spec["name"], draft_fold_path=P.capcut_path(dest), draft_root_path=P.capcut_path(root),
               draft_cover=P.capcut_path(os.path.join(dest, "draft_cover.jpg")),
               draft_json_file=P.capcut_path(os.path.join(dest, "draft_info.json")),
               tm_duration=d["duration"], tm_draft_create=now, tm_draft_modified=now)
    rm["all_draft_store"].insert(0, ent)
    json.dump(rm, open(rp, "w", encoding="utf-8"), ensure_ascii=False)
    print("%s: hook %.2fs (was %.2fs), total %.2fs" % (spec["name"], new_len / US, hook_end / US, d["duration"] / US))
    return dest


if __name__ == "__main__":
    main(json.load(open(sys.argv[1], encoding="utf-8")))
