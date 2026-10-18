# Apollo — Terminal Snake Game

Apollo is a classic arcade Snake game built entirely in Python using only the standard library (`curses`) and played directly in the terminal. Navigate a 40x20 playfield surrounded by a visible border, steering the snake with arrow keys to collect food that increases your score by 10 points and dynamically ramps movement speed from 8.0 up to 20.0 moves per second. Wall collisions and self-collisions trigger a screen flash, a game-over summary, and an updated top-5 high-score leaderboard that persists across sessions in `scores.json` with your newest run highlighted.

## Run Command

```bash
python3 snake.py
```

## Controls

| Key | Action |
| --- | --- |
| `↑` / `W` | Move Up |
| `↓` / `S` | Move Down |
| `←` / `A` | Move Left |
| `→` / `D` | Move Right |
| `R` | Play Again (from Game Over screen) |
| `Q` / `Esc` | Quit the game cleanly |
| `Ctrl+C` | Force exit cleanly with restored terminal state |
