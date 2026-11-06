# AI voiceover story ads

This repo makes AI voiceover story ads and delivers them as CapCut projects. When someone asks for a story ad, hook variants, or says they've changed a CapCut project, use the `ai-voiceover-story` skill in `.claude/skills/ai-voiceover-story/` and follow it step by step.

- Run the tools with the repo's own Python: `.venv/bin/python` on Mac, `.venv\Scripts\python` on Windows. If `.venv` is missing, run the setup script for this computer first (see README.md).
- Put each new ad in its own folder under `ads/` (it's kept out of git), starting from a copy of `examples/example_ad/`.
- Close CapCut before writing any project.
- Save every correction the editor makes as a rule (the skill says where), so it never needs making twice.
