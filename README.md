# AI voiceover story ads → CapCut

A Claude Code skill and toolkit for making **AI voiceover story ads**: a first-person story told by an AI voice ("the gift I bought my husband"), cut to fast, literal B-roll. Claude builds the whole edit and hands it to you as a **CapCut project** you can open and change. Then it reads what you changed and learns from it, so each ad needs fewer fixes than the last.

How it works:

1. You give Claude the script, the voiceover and your footage folder.
2. Claude cuts the breaths and pauses out of the voiceover, picks a B-roll clip for every line, times every caption to the frame the word is spoken, and adds the end stack and music.
3. It writes **one CapCut project per hook**, with a placeholder card where your hook clip goes.
4. You open the project in CapCut, drop in your hook, change anything you like and export.
5. You tell Claude you've made changes. It compares your project with what it handed you and saves the lessons as rules.
6. For the other hooks, Claude copies your finished project and swaps only the hook, so your edit of the body is kept exactly as it is.

Works on **Mac and Windows**. It has been tested on a Mac with CapCut 9.7. Windows support is built in but hasn't been tested on a Windows computer yet, so please report anything that breaks.

## What you need

- **CapCut desktop** (free), opened at least once, with at least one project made in it.
- **Claude Code**, in the Claude desktop app or the terminal.
- **Python 3.9 or newer.** Mac: from [python.org](https://www.python.org/downloads/) (or the one macOS offers to install). Windows: from [python.org](https://www.python.org/downloads/), with **"Add python.exe to PATH"** ticked during install.
- About 3 GB of free space (most of it is the speech-to-text model, which downloads the first time you transcribe).
- An AI voice for the voiceover, for example ElevenLabs. Any MP3 or WAV of the script works.

## Setup (once per computer)

Download this repo (the green **Code** button, then **Download ZIP**, or `git clone`). Put it somewhere that **isn't synced to iCloud or OneDrive**. Big video files in synced folders can go missing partway through a job.

**Mac:** open Terminal in the repo folder and run:

```bash
bash setup/setup_mac.sh
```

**Windows:** open PowerShell in the repo folder and run:

```powershell
powershell -ExecutionPolicy Bypass -File setup\setup_windows.ps1
```

When it's finished it runs a check and should say **Ready**. If CapCut keeps its projects somewhere unusual, set `CAPCUT_DRAFTS` to the folder shown in CapCut's Settings, under Projects. Run the check again any time with `tools/doctor.py`.

## Making an ad

Open the repo folder in Claude Code and ask for an ad, for example:

> Make an AI voiceover story ad. Script: [paste]. Voiceover: `ads/gift-for-him/inputs/voiceover.mp3`. Footage is in `~/Videos/B-roll`. The offer is up to 50% off with a 60-day guarantee.

Claude follows the skill in `.claude/skills/ai-voiceover-story/SKILL.md`. **Close CapCut before Claude writes a project.** When it's done, open CapCut and you'll see one project per hook.

When you've edited one, tell Claude ("I've updated Hook A, have a look"). It compares your version against its own, explains what changed and why, and saves the lessons. To make the other hooks from your finished edit: "Make hooks B and C from my Hook A project."

## What's in here

| Path | What it is |
|---|---|
| `.claude/skills/ai-voiceover-story/SKILL.md` | The workflow Claude follows, step by step |
| `.claude/skills/ai-voiceover-story/references/editing-standards.md` | The editing rulebook: pacing, B-roll, captions, audio. Change it to suit your team. |
| `.claude/skills/ai-voiceover-story/references/style.md` | Notes for this style of ad, learned from winning ads and a human editor's finished edit |
| `tools/story_ad.py` | Builds the CapCut project (and a review MP4 with `--mp4`) from an edit file |
| `tools/swap_hook.py` | Makes a hook variant from a finished CapCut project, keeping its body untouched |
| `tools/capcut_draft.py` | Reads CapCut projects: `list`, `dump`, `snapshot` and `diff` |
| `tools/transcribe.py` | Word-by-word timings for a voiceover (runs offline) |
| `tools/contact_sheet.py` | A contact sheet of a footage folder, so Claude can see the clips |
| `tools/house_captions.py` | The caption engine and its checks (no blank gaps, cuts on caption changes, two lines at most) |
| `tools/templates/` | A blank CapCut project, the caption and end-stack styles, and the hook placeholder card |
| `examples/example_ad/make_edit.py` | A starting point for each new ad's edit file |

## Good to know

- **CapCut must be closed** whenever Claude writes a project. CapCut overwrites files it has open.
- **Fonts, text effects and sounds** come from CapCut's own library on your computer. They aren't included in this repo. If one hasn't been used on your computer yet, CapCut may show it as missing. Add it once from CapCut's library and later builds will find it. The builder tells you when the end-stack click sound is missing.
- **Your ads stay on your computer.** Put them in `ads/`, which git ignores. Videos and audio are never committed.
- **Make it yours.** The rulebook and style notes are plain text. Every correction your editor makes should become a rule there. Claude does this as part of the workflow.

## Troubleshooting

- **"CapCut is open"**: quit CapCut fully (on Mac, use Cmd+Q, not just closing the window) and try again.
- **The project doesn't show in CapCut**: restart CapCut. Check that `tools/doctor.py` shows the same projects folder as CapCut's Settings, under Projects.
- **Windows: "running scripts is disabled"**: use the `powershell -ExecutionPolicy Bypass -File ...` line above exactly as written.
- **The first transcription is slow**: it's downloading the speech model (about 1.6 GB). Later runs take well under a minute for a 90-second voiceover.

## License

MIT. See `LICENSE` and `THIRD_PARTY_NOTICES.md`.
