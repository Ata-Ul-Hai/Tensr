<div align="center">

# Tensr

**An autonomous AI coding agent. One prompt in, one build out.**

![status](https://img.shields.io/badge/status-soft%20launch-blue)
![agent](https://img.shields.io/badge/built%20by-Tensr-black)
![demo](https://img.shields.io/badge/demo%20reel-coming%20soon-orange)

</div>

---

## What is Tensr?

Tensr is an autonomous coding agent and developer environment. Describe what you want in plain language, and it takes over from there: it plans the work, creates and edits files, searches the codebase, runs shell commands, and keeps iterating until the thing actually works. You don't babysit it, and you don't copy-paste between a chat window and your editor — it *is* the environment.

A few things it can do today:

- **Run on the models you prefer** — switch between Claude, Gemini, and OpenAI models at any point without losing the session.
- **Work like a developer** — a full toolbelt for file operations, code editing, directory navigation, pattern search, and shell execution.
- **Never lose your place** — sessions are tree-based: branch a conversation, clone a thread, rewind, and take a different route at any point.
- **Be steered, not restarted** — redirect the agent's course mid-run with new instructions, without throwing away its progress.
- **Run anywhere** — an interactive terminal UI for humans, and a headless mode for scripts and CI. Same engine under both.

## Why this repo exists

Tensr is in active private development, and its source is closed for now. This repository is the project's public flight log — a place to show results instead of code.

Everything inside [`atlas/`](atlas) was built end-to-end by Tensr from a single prompt. Each mission ships with its `prompt.md`, so you can read exactly what Tensr was asked and judge exactly what it delivered. That's the whole point: **the prompt is the spec, the folder is the proof.**

## Repo layout

```
.
├── README.md              ← you are here
├── atlas/                 ← every build landed by Tensr
│   └── <codename>/        ← one folder per build
│       ├── prompt.md      ← the exact prompt behind the build
│       └── …              ← the build itself
└── docs/                  ← write-ups & notes (quiet for now)
```

New here? Pick a codename from the mission log below, open its folder, read `prompt.md` first — then look at what Tensr did with it.

## Mission log

Every build gets a codename from spaceflight history — one prompt in, one build out.

| #   | Codename | Build | Stack | Status |
|:---:|:---------|:------|:------|:------:|
| 001 | [`apollo`](atlas/apollo)   | Terminal snake game with a persistent high-score board | Python · curses | landed |
| 002 | [`artemis`](atlas/artemis) | REST API for a todo app with in-memory storage | Python · FastAPI | landed |
| 003 | [`vostok`](atlas/vostok)   | Markdown → HTML converter CLI | Python | landed |

<!-- maintainer: one row per atlas/ build — next codenames: voyager · cassini · juno · kepler · pioneer · skylab · mercury · orion · galileo · hubble -->

---

**Coming soon** — demo reel · more missions · public release of Tensr. Watch this space.
