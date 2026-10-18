# Mission 001 — apollo

Terminal snake game with a persistent high-score board, played entirely in the terminal.

## Metadata

| Field | Value |
|-------|-------|
| Codename | `apollo` |
| Mission # | 001 |
| Stack | Python · curses |
| Status | landed |
| Built by | Tensr |
| Date | 2026-10-18 |

## Prompt

The exact prompt given to Tensr for this build:

```text
Build a terminal Snake game in Python using only the standard library (curses).
No third-party packages.

Run it with: python3 snake.py

Gameplay:
- Playfield 40 columns wide by 20 rows tall, with a visible border drawn
  inside the terminal window.
- Snake starts 3 segments long, moving right, at the center of the field.
- Arrow keys steer the snake; the snake can never reverse directly into
  itself.
- Food spawns at a random free cell and is never placed on the snake or the
  border.
- Score starts at 0 and increases by 10 per food eaten.
- Speed starts at 8 moves per second and increases by 0.5 moves per second
  with each food eaten, capped at 20 moves per second.
- Game over on wall collision or self collision: flash the screen, show
  "GAME OVER - Score: N", then show the final high-score board.
- From the game-over screen, R starts a new game and Q quits.

High-score board:
- Stored in scores.json next to the script, created on first run.
- Keeps the top 5 runs: score, snake length, and date (YYYY-MM-DD).
- After every game the run is saved and the board is displayed sorted
  highest first, with the newest run highlighted.

Robustness:
- Handle terminal window resizing without crashing: redraw cleanly, or show
  a "terminal too small" message if below 42x22.
- Ctrl+C, Q, and closing the terminal must all exit cleanly with the cursor
  and terminal state fully restored.
- If scores.json is corrupt or unreadable, reset it silently instead of
  crashing.

Deliverables: snake.py, and a README.md with a one-paragraph description,
the controls, and the run command. scores.json is created at runtime.
```
