"""Checks this computer is ready: Python packages, ffmpeg, CapCut and its projects folder.

  doctor.py
"""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import platform_paths as P

ok = True


def check(name, good, fix=""):
    global ok
    print(("  OK    " if good else "  FIX   ") + name + ("" if good else "\n        " + fix))
    ok = ok and good


print("Checking setup (%s, Python %s)" % ("Windows" if P.IS_WIN else "Mac" if P.IS_MAC else sys.platform,
                                          sys.version.split()[0]))
check("Python 3.9 or newer", sys.version_info >= (3, 9), "Install a newer Python from python.org.")
for mod in ("PIL", "numpy", "imageio_ffmpeg", "faster_whisper"):
    try:
        __import__(mod)
        check("package " + mod, True)
    except ImportError:
        check("package " + mod, False, "Run the setup script again.")
ff = P.ffmpeg()
try:
    good = subprocess.run([ff, "-version"], capture_output=True).returncode == 0
except OSError:
    good = False
check("ffmpeg", good, "Run the setup script again, or set FFMPEG to an ffmpeg executable.")
drafts = P.capcut_drafts()
check("CapCut projects folder: " + drafts, os.path.isdir(drafts),
      "Install CapCut desktop and make one project, or set CAPCUT_DRAFTS to the folder shown in "
      "CapCut > Settings > Projects.")
font = P.capcut_font()
check("caption font: %s" % font, bool(font) and font.endswith("en.ttf"),
      "CapCut's en.ttf wasn't found, so review MP4s use a system font instead. CapCut projects are unaffected.")
print("\nReady." if ok else "\nFix the items above, then run tools/doctor.py again.")
