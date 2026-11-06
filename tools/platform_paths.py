"""Where things live on this computer, for Mac and Windows. Everything machine-specific is here.

Override any of these with an environment variable if your setup is different:
  CAPCUT_DRAFTS   CapCut's projects folder (CapCut > Settings > Projects shows it)
  CAPCUT_FONT     CapCut's system font, en.ttf
  FFMPEG          an ffmpeg executable
"""
import glob
import os
import subprocess
import sys

IS_WIN = sys.platform.startswith("win")
IS_MAC = sys.platform == "darwin"
HOME = os.path.expanduser("~")
if IS_WIN:   # Windows consoles default to an old code page: captions with emoji would crash a print
    for _s in (sys.stdout, sys.stderr):
        try:
            _s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
LOCAL = os.environ.get("LOCALAPPDATA", os.path.join(HOME, "AppData", "Local"))


def _first(paths):
    for p in paths:
        for hit in sorted(glob.glob(p), reverse=True):      # newest CapCut version first
            if os.path.exists(hit):
                return hit
    return None


def capcut_drafts():
    if os.environ.get("CAPCUT_DRAFTS"):
        return os.environ["CAPCUT_DRAFTS"]
    if IS_WIN:
        cands = [os.path.join(LOCAL, "CapCut", "User Data", "Projects", "com.lveditor.draft")]
    else:
        cands = [os.path.join(HOME, "Movies", "CapCut", "User Data", "Projects", "com.lveditor.draft"),
                 os.path.join(HOME, "Library", "Containers", "com.lemon.lvoverseas", "Data", "Movies", "CapCut",
                              "User Data", "Projects", "com.lveditor.draft")]
    return _first(cands) or cands[0]


def capcut_cache():
    """CapCut's download cache (fonts, effects and sounds you've used in CapCut)."""
    if IS_WIN:
        cands = [os.path.join(LOCAL, "CapCut", "User Data", "Cache")]
    else:
        cands = [os.path.join(HOME, "Library", "Containers", "com.lemon.lvoverseas", "Data", "Movies", "CapCut",
                              "User Data", "Cache"),
                 os.path.join(HOME, "Movies", "CapCut", "User Data", "Cache")]
    return _first(cands) or cands[0]


def capcut_font():
    if os.environ.get("CAPCUT_FONT"):
        return os.environ["CAPCUT_FONT"]
    if IS_WIN:
        cands = [os.path.join(LOCAL, "CapCut", "Apps", "*", "Resources", "Font", "SystemFont", "en.ttf"),
                 os.path.join(os.environ.get("ProgramFiles", r"C:\Program Files"), "CapCut", "Apps", "*",
                              "Resources", "Font", "SystemFont", "en.ttf")]
    else:
        cands = ["/Applications/CapCut.app/Contents/Resources/Font/SystemFont/en.ttf"]
    hit = _first(cands)
    if hit:
        return hit
    # no CapCut font: the review MP4 falls back to a bold system font (the CapCut project is unaffected)
    return _first([r"C:\Windows\Fonts\arialbd.ttf", "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
                   "/Library/Fonts/Arial Bold.ttf"])


def emoji_font():
    return _first(["/System/Library/Fonts/Apple Color Emoji.ttc", r"C:\Windows\Fonts\seguiemj.ttf"])


def ffmpeg():
    if os.environ.get("FFMPEG"):
        return os.environ["FFMPEG"]
    try:
        import imageio_ffmpeg            # installed by setup: a working ffmpeg on Mac and Windows
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        return "ffmpeg"


def capcut_running():
    try:
        if IS_WIN:
            out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq CapCut.exe"], capture_output=True, text=True).stdout
            return "CapCut.exe" in out
        return subprocess.run(["pgrep", "-x", "CapCut"], capture_output=True).returncode == 0
    except OSError:
        return False


def capcut_path(p):
    """A path the way CapCut writes it in project files (forward slashes on Windows too)."""
    return p.replace("\\", "/") if IS_WIN else p


def hidden(p):
    """True for paths CapCut can't read (a folder starting with a dot, on Mac)."""
    return any(part.startswith(".") and part not in (".", "..") for part in os.path.normpath(p).split(os.sep))
