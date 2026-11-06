"""Contact sheet of a B-roll folder, so Claude can see the footage before picking clips.

  contact_sheet.py <folder> <out.jpg>

Four frames per clip (at 10, 35, 60 and 85%), one row per clip, labelled with the file name, its length and each
frame's time.
"""
import os
import re
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import platform_paths as P

FF = P.ffmpeg()
EXT = (".mov", ".mp4", ".m4v", ".webm")


def dur(p):
    err = subprocess.run([FF, "-i", p], capture_output=True, text=True, errors="replace").stderr
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", err)
    return int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3]) if m else 0


def main(folder, out):
    files = sorted(f for f in os.listdir(folder) if f.lower().endswith(EXT))
    if not files:
        sys.exit("no video files in " + folder)
    W, H = 150, 266
    rows = []
    tmpdir = tempfile.mkdtemp()
    for f in files:
        p = os.path.join(folder, f)
        T = dur(p)
        row = Image.new("RGB", (4 * W + 10, H + 18), "black")
        dr = ImageDraw.Draw(row)
        for i, fr in enumerate((.1, .35, .6, .85)):
            t = T * fr
            tmp = os.path.join(tmpdir, "f.jpg")
            subprocess.run([FF, "-v", "error", "-y", "-ss", str(t), "-i", p, "-frames:v", "1", "-vf",
                            "scale=%d:%d:force_original_aspect_ratio=decrease,pad=%d:%d:(ow-iw)/2:(oh-ih)/2" % (W, H, W, H),
                            tmp])
            if os.path.exists(tmp):
                row.paste(Image.open(tmp), (i * W + i * 3, 18))
                os.remove(tmp)
            dr.text((i * W + i * 3 + 2, 20), "%.1f" % t, fill="yellow")
        dr.text((2, 2), "%s  (%.1fs)" % (f, T), fill="white")
        rows.append(row)
    cols = 3
    per = (len(rows) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (4 * W + 20), per * (H + 22)), "#222")
    for i, r in enumerate(rows):
        sheet.paste(r, ((i // per) * (4 * W + 20), (i % per) * (H + 22)))
    sheet.save(out, quality=80)
    print(out, len(rows), "clips")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
