#!/usr/bin/env python3
"""
Apollo — Terminal Snake Game
Played entirely in the terminal using Python's standard library (curses).
"""

import curses
import datetime
import json
import os
import random
import signal
import sys
import time

# Playfield constants
BOARD_WIDTH = 40   # Playable columns: 1..40
BOARD_HEIGHT = 20  # Playable rows: 1..20
TOTAL_WIDTH = 42   # Playfield width including border (40 + 2)
TOTAL_HEIGHT = 22  # Playfield height including border (20 + 2)

INITIAL_SPEED = 8.0        # Moves per second
SPEED_INCREMENT = 0.5      # Moves per second per food eaten
MAX_SPEED = 20.0           # Capped moves per second
SCORE_PER_FOOD = 10        # Score per food eaten

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SCORES_FILE = os.path.join(SCRIPT_DIR, "scores.json")


class ScoreManager:
    """Manages persistent top-5 high scores in scores.json."""

    def __init__(self, filepath=SCORES_FILE):
        self.filepath = filepath
        self.ensure_initialized()

    def ensure_initialized(self):
        """Create scores.json on first run if it does not exist."""
        if not os.path.exists(self.filepath):
            self._save_raw([])

    def load_scores(self):
        """Load scores from disk. Reset silently if corrupt or unreadable."""
        if not os.path.exists(self.filepath):
            self.ensure_initialized()
            return []
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, list):
                raise ValueError("Scores data must be a JSON array")
            valid_scores = []
            for item in data:
                if (
                    isinstance(item, dict)
                    and "score" in item
                    and "length" in item
                    and "date" in item
                ):
                    valid_scores.append({
                        "score": int(item["score"]),
                        "length": int(item["length"]),
                        "date": str(item["date"])
                    })
                else:
                    raise ValueError("Invalid score entry format")
            return valid_scores
        except Exception:
            # Corrupt or unreadable: reset silently
            self._save_raw([])
            return []

    def _save_raw(self, scores):
        """Write scores to scores.json silently handling errors."""
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(scores, f, indent=2)
        except OSError:
            pass

    def record_run(self, score, length, date_str=None):
        """
        Record a run, keep top 5 sorted highest first, and save to scores.json.
        Returns (top_5_entries, current_entry).
        """
        if date_str is None:
            date_str = datetime.date.today().strftime("%Y-%m-%d")

        current_entry = {
            "score": int(score),
            "length": int(length),
            "date": str(date_str),
            "_is_new": True  # In-memory marker for highlighting
        }

        existing_scores = self.load_scores()
        combined = existing_scores + [current_entry]

        # Sort highest score first; break ties by snake length descending
        combined.sort(key=lambda s: (s["score"], s["length"]), reverse=True)
        top_5 = combined[:5]

        # Persist only top 5 to disk without internal metadata
        disk_data = [
            {"score": s["score"], "length": s["length"], "date": s["date"]}
            for s in top_5
        ]
        self._save_raw(disk_data)

        return top_5, current_entry


def safe_addstr(win, y, x, text, attr=0):
    """Safely write a string to curses window without raising edge errors."""
    try:
        max_y, max_x = win.getmaxyx()
        if y < 0 or y >= max_y or x < 0 or x >= max_x:
            return
        if x + len(text) > max_x:
            text = text[:max_x - x]
        win.addstr(y, x, text, attr)
    except curses.error:
        pass


def safe_addch(win, y, x, ch, attr=0):
    """Safely write a single character to curses window."""
    try:
        max_y, max_x = win.getmaxyx()
        if y < 0 or y >= max_y or x < 0 or x >= max_x:
            return
        # If at bottom-right corner, use insstr to avoid cursor advancing
        if y == max_y - 1 and x == max_x - 1:
            win.insstr(y, x, ch, attr)
        else:
            win.addch(y, x, ch, attr)
    except curses.error:
        pass


def init_colors():
    """Initialize curses color pairs with graceful fallback."""
    if not curses.has_colors():
        return False
    try:
        curses.start_color()
        curses.use_default_colors()
    except curses.error:
        pass

    # Color pairs:
    # 1: Snake head (Bright Green)
    # 2: Snake body (Green)
    # 3: Food (Bright Red / Yellow)
    # 4: Border & Frame (Cyan)
    # 5: Header & Stats (Bold White / Yellow)
    # 6: Game Over accent (Bright Red)
    # 7: High score highlight (Reverse / Bright Yellow)
    try:
        curses.init_pair(1, curses.COLOR_GREEN, -1)
        curses.init_pair(2, curses.COLOR_GREEN, -1)
        curses.init_pair(3, curses.COLOR_RED, -1)
        curses.init_pair(4, curses.COLOR_CYAN, -1)
        curses.init_pair(5, curses.COLOR_YELLOW, -1)
        curses.init_pair(6, curses.COLOR_RED, -1)
        curses.init_pair(7, curses.COLOR_BLACK, curses.COLOR_YELLOW)
        return True
    except curses.error:
        return False


def wait_for_min_size(stdscr):
    """
    Check terminal window size. If below 42x22, display message and
    block cleanly until window is resized to at least 42x22 or user quits.
    """
    while True:
        try:
            curses.update_lines_cols()
        except Exception:
            pass
        max_y, max_x = stdscr.getmaxyx()
        if max_y >= TOTAL_HEIGHT and max_x >= TOTAL_WIDTH:
            return max_y, max_x

        stdscr.clear()
        lines = [
            "Terminal too small!",
            f"Required: at least {TOTAL_WIDTH} cols x {TOTAL_HEIGHT} rows",
            f"Current:  {max_x} cols x {max_y} rows",
            "Please resize window or press Q to quit."
        ]
        start_y = max(0, (max_y - len(lines)) // 2)
        for i, line in enumerate(lines):
            row = start_y + i
            if 0 <= row < max_y:
                col = max(0, (max_x - len(line)) // 2)
                safe_addstr(stdscr, row, col, line[:max_x], curses.A_BOLD)
        stdscr.refresh()

        stdscr.timeout(200)
        try:
            ch = stdscr.getch()
            if ch in (ord('q'), ord('Q'), 27):
                sys.exit(0)
        except curses.error:
            pass


class SnakeGame:
    """Manages Snake game state, movement, and collision logic."""

    def __init__(self):
        self.reset()

    def reset(self):
        """Reset game to initial starting state."""
        self.score = 0
        # Playfield rows: 1..20, cols: 1..40.
        # Snake starts 3 segments long, moving right, at center of field.
        center_y = BOARD_HEIGHT // 2       # Row 10
        center_x = BOARD_WIDTH // 2        # Col 20
        self.snake = [
            (center_y, center_x),          # Head: (10, 20)
            (center_y, center_x - 1),      # Body: (10, 19)
            (center_y, center_x - 2)       # Tail: (10, 18)
        ]
        self.direction = (0, 1)            # Moving right (dy=0, dx=1)
        self.input_queue = []              # Input buffer for responsive, safe turns
        self.food = None
        self.spawn_food()

    @property
    def speed(self):
        """
        Speed starts at 8 moves per second and increases by 0.5 moves per
        second with each food eaten, capped at 20 moves per second.
        """
        food_eaten = self.score // SCORE_PER_FOOD
        return min(MAX_SPEED, INITIAL_SPEED + SPEED_INCREMENT * food_eaten)

    @property
    def tick_interval(self):
        """Seconds per move tick."""
        return 1.0 / self.speed

    def spawn_food(self):
        """
        Spawn food at a random free cell. Never placed on snake or border.
        """
        snake_set = set(self.snake)
        free_cells = [
            (r, c)
            for r in range(1, BOARD_HEIGHT + 1)
            for c in range(1, BOARD_WIDTH + 1)
            if (r, c) not in snake_set
        ]
        if free_cells:
            self.food = random.choice(free_cells)
        else:
            self.food = None

    def queue_direction(self, new_dir):
        """
        Queue steering direction. Snake can never reverse directly into itself.
        Input queue prevents rapid-tap reversal glitch.
        """
        ref_dir = self.input_queue[-1] if self.input_queue else self.direction
        dy, dx = new_dir
        ref_dy, ref_dx = ref_dir

        # Ignore 180-degree reversal or duplicate direction
        if (dy == -ref_dy and dx == -ref_dx) or (dy == ref_dy and dx == ref_dx):
            return

        # Buffer up to 2 pending directional turns
        if len(self.input_queue) < 2:
            self.input_queue.append(new_dir)

    def step(self):
        """
        Advance snake by one tick.
        Returns (is_alive, collision_reason).
        """
        if self.input_queue:
            self.direction = self.input_queue.pop(0)

        head_y, head_x = self.snake[0]
        dy, dx = self.direction
        next_head = (head_y + dy, head_x + dx)
        ny, nx = next_head

        # Wall collision: outside 1..20 rows or 1..40 columns
        if ny < 1 or ny > BOARD_HEIGHT or nx < 1 or nx > BOARD_WIDTH:
            return False, "wall"

        # Check food consumption
        eating_food = (next_head == self.food)

        # Self collision: colliding with body segments
        # If not eating, tail vacates its cell this tick
        body_to_check = self.snake if eating_food else self.snake[:-1]
        if next_head in body_to_check:
            return False, "self"

        # Advance snake
        self.snake.insert(0, next_head)
        if eating_food:
            self.score += SCORE_PER_FOOD
            self.spawn_food()
        else:
            self.snake.pop()

        return True, None


def draw_border_and_frame(stdscr, offset_y, offset_x, score, speed, colors_active):
    """Draw the playfield border with embedded score and speed info."""
    border_attr = curses.color_pair(4) if colors_active else curses.A_NORMAL
    stats_attr = curses.color_pair(5) | curses.A_BOLD if colors_active else curses.A_BOLD

    # Top border with score and speed: exact 42 chars width
    info_text = f" Score: {score}  Speed: {speed:.1f}/s "
    fill = BOARD_WIDTH - len(info_text)
    left_fill = max(0, fill // 2)
    right_fill = max(0, fill - left_fill)
    top_middle = ("─" * left_fill) + info_text + ("─" * right_fill)
    top_line = "┌" + top_middle + "┐"
    safe_addstr(stdscr, offset_y, offset_x, top_line, border_attr)

    # Highlight the stats portion inside the top border
    info_start_x = offset_x + 1 + left_fill
    safe_addstr(stdscr, offset_y, info_start_x, info_text, stats_attr)

    # Side borders
    for row in range(1, BOARD_HEIGHT + 1):
        safe_addstr(stdscr, offset_y + row, offset_x, "│", border_attr)
        safe_addstr(stdscr, offset_y + row, offset_x + TOTAL_WIDTH - 1, "│", border_attr)

    # Bottom border with controls: exact 42 chars width
    bottom_info = " [Arrows] Steer   [Q] Quit "
    b_fill = BOARD_WIDTH - len(bottom_info)
    b_left = max(0, b_fill // 2)
    b_right = max(0, b_fill - b_left)
    bottom_middle = ("─" * b_left) + bottom_info + ("─" * b_right)
    bottom_line = "└" + bottom_middle + "┘"
    safe_addstr(stdscr, offset_y + TOTAL_HEIGHT - 1, offset_x, bottom_line, border_attr)


def draw_game(stdscr, game, offset_y, offset_x, colors_active):
    """Draw snake, food, and playfield contents."""
    # Clear interior play area
    empty_row = " " * BOARD_WIDTH
    for r in range(1, BOARD_HEIGHT + 1):
        safe_addstr(stdscr, offset_y + r, offset_x + 1, empty_row)

    # Draw food
    if game.food:
        fy, fx = game.food
        food_attr = curses.color_pair(3) | curses.A_BOLD if colors_active else curses.A_BOLD
        safe_addstr(stdscr, offset_y + fy, offset_x + fx, "*", food_attr)

    # Draw snake body
    body_attr = curses.color_pair(2) if colors_active else curses.A_NORMAL
    for segment in game.snake[1:]:
        sy, sx = segment
        safe_addstr(stdscr, offset_y + sy, offset_x + sx, "o", body_attr)

    # Draw snake head
    if game.snake:
        hy, hx = game.snake[0]
        head_attr = curses.color_pair(1) | curses.A_BOLD if colors_active else curses.A_BOLD
        safe_addstr(stdscr, offset_y + hy, offset_x + hx, "O", head_attr)


def flash_effect(stdscr, offset_y, offset_x):
    """Flash terminal bell and show brief full-screen visual flash."""
    try:
        curses.flash()
    except curses.error:
        pass

    # Visual flash: fill playfield with reverse video for ~80ms
    blank = " " * BOARD_WIDTH
    for r in range(1, BOARD_HEIGHT + 1):
        safe_addstr(stdscr, offset_y + r, offset_x + 1, blank, curses.A_REVERSE)
    stdscr.refresh()
    time.sleep(0.08)


def show_game_over_banner(stdscr, offset_y, offset_x, score, colors_active):
    """Display centered 'GAME OVER - Score: N' announcement before scoreboard."""
    title = "  GAME OVER  "
    score_msg = f"  Score: {score}  "

    y1 = offset_y + (BOARD_HEIGHT // 2) - 1
    y2 = offset_y + (BOARD_HEIGHT // 2) + 1
    x1 = offset_x + (TOTAL_WIDTH - len(title)) // 2
    x2 = offset_x + (TOTAL_WIDTH - len(score_msg)) // 2

    attr_title = (curses.color_pair(6) | curses.A_BOLD | curses.A_REVERSE) if colors_active else (curses.A_BOLD | curses.A_REVERSE)
    attr_score = (curses.color_pair(5) | curses.A_BOLD) if colors_active else curses.A_BOLD

    safe_addstr(stdscr, y1, x1, title, attr_title)
    safe_addstr(stdscr, y2, x2, score_msg, attr_score)
    stdscr.refresh()

    # Pause briefly (~0.7s) to make game over prominent; allow skipping on key
    stdscr.nodelay(True)
    t0 = time.time()
    while time.time() - t0 < 0.7:
        ch = stdscr.getch()
        if ch in (ord('q'), ord('Q'), ord('r'), ord('R'), 27):
            break
        time.sleep(0.02)


def render_high_scores(stdscr, offset_y, offset_x, score, top_5, current_run, colors_active):
    """Render the final high-score board with newest run highlighted."""
    # Clear interior playfield
    empty = " " * BOARD_WIDTH
    for r in range(1, BOARD_HEIGHT + 1):
        safe_addstr(stdscr, offset_y + r, offset_x + 1, empty)

    # Frame lines
    header_attr = curses.color_pair(6) | curses.A_BOLD if colors_active else curses.A_BOLD
    label_attr = curses.color_pair(4) | curses.A_BOLD if colors_active else curses.A_BOLD
    table_head_attr = curses.A_UNDERLINE | curses.A_BOLD
    normal_attr = curses.A_NORMAL
    new_attr = curses.color_pair(7) | curses.A_BOLD if colors_active else (curses.A_REVERSE | curses.A_BOLD)
    prompt_attr = curses.color_pair(5) | curses.A_BOLD if colors_active else curses.A_BOLD

    curr_row = offset_y + 2

    # Title & Final Score
    title = "GAME OVER"
    score_line = f"Final Score: {score}"
    safe_addstr(stdscr, curr_row, offset_x + (TOTAL_WIDTH - len(title)) // 2, title, header_attr)
    curr_row += 1
    safe_addstr(stdscr, curr_row, offset_x + (TOTAL_WIDTH - len(score_line)) // 2, score_line, label_attr)
    curr_row += 2

    # Board header
    sub_title = "── TOP 5 HIGH SCORES ──"
    safe_addstr(stdscr, curr_row, offset_x + (TOTAL_WIDTH - len(sub_title)) // 2, sub_title, label_attr)
    curr_row += 1

    # Table header
    col_header = " #   SCORE   LENGTH      DATE   "
    safe_addstr(stdscr, curr_row, offset_x + (TOTAL_WIDTH - len(col_header)) // 2, col_header, table_head_attr)
    curr_row += 1

    divider = "────────────────────────────────"
    safe_addstr(stdscr, curr_row, offset_x + (TOTAL_WIDTH - len(divider)) // 2, divider, normal_attr)
    curr_row += 1

    made_top_5 = False
    for rank, entry in enumerate(top_5, 1):
        is_new = entry.get("_is_new", False)
        if is_new:
            made_top_5 = True
            prefix = ">"
            suffix = " *"
            row_attr = new_attr
        else:
            prefix = " "
            suffix = "  "
            row_attr = normal_attr

        entry_line = f"{prefix}{rank:<2} {entry['score']:>6}   {entry['length']:>6}   {entry['date']}{suffix}"
        x_pos = offset_x + (TOTAL_WIDTH - len(entry_line)) // 2
        safe_addstr(stdscr, curr_row, x_pos, entry_line, row_attr)
        curr_row += 1

    # Fill empty ranks if fewer than 5 games played
    for rank in range(len(top_5) + 1, 6):
        placeholder = f" {rank:<2}      ─        ─           ─   "
        x_pos = offset_x + (TOTAL_WIDTH - len(placeholder)) // 2
        safe_addstr(stdscr, curr_row, x_pos, placeholder, normal_attr)
        curr_row += 1

    safe_addstr(stdscr, curr_row, offset_x + (TOTAL_WIDTH - len(divider)) // 2, divider, normal_attr)
    curr_row += 1

    if not made_top_5:
        note = f"Your run: {score} pts, len {current_run['length']}"
        safe_addstr(stdscr, curr_row, offset_x + (TOTAL_WIDTH - len(note)) // 2, note, new_attr)
    else:
        note = "★ High Score Recorded! ★"
        safe_addstr(stdscr, curr_row, offset_x + (TOTAL_WIDTH - len(note)) // 2, note, new_attr)
    curr_row += 2

    # Prompt
    prompt = "[R] Play Again    [Q] Quit"
    safe_addstr(stdscr, curr_row, offset_x + (TOTAL_WIDTH - len(prompt)) // 2, prompt, prompt_attr)

    stdscr.refresh()


def handle_game_over(stdscr, game, score_mgr, colors_active):
    """
    Handle Game Over flow:
    1. Flash screen
    2. Show 'GAME OVER - Score: N'
    3. Save run to scores.json
    4. Show top-5 high-score board with newest run highlighted
    5. Wait for R (restart) or Q (quit)
    """
    max_y, max_x = wait_for_min_size(stdscr)
    offset_y = (max_y - TOTAL_HEIGHT) // 2
    offset_x = (max_x - TOTAL_WIDTH) // 2

    # 1. Flash screen
    flash_effect(stdscr, offset_y, offset_x)

    # 2. Show 'GAME OVER - Score: N'
    show_game_over_banner(stdscr, offset_y, offset_x, game.score, colors_active)

    # 3. Save run and load top 5
    top_5, current_run = score_mgr.record_run(game.score, len(game.snake))

    # 4. Wait for player action (R to restart, Q to quit)
    while True:
        max_y, max_x = wait_for_min_size(stdscr)
        offset_y = (max_y - TOTAL_HEIGHT) // 2
        offset_x = (max_x - TOTAL_WIDTH) // 2

        # Redraw frame and high-score board
        draw_border_and_frame(stdscr, offset_y, offset_x, game.score, game.speed, colors_active)
        render_high_scores(stdscr, offset_y, offset_x, game.score, top_5, current_run, colors_active)

        stdscr.timeout(100)
        try:
            ch = stdscr.getch()
        except curses.error:
            continue

        if ch == curses.KEY_RESIZE:
            stdscr.clear()
            continue
        elif ch in (ord('r'), ord('R')):
            return "restart"
        elif ch in (ord('q'), ord('Q'), 27):
            return "quit"


def play_game(stdscr, score_mgr, colors_active):
    """Run one full game of Snake until collision or quit."""
    game = SnakeGame()
    last_tick = time.perf_counter()

    stdscr.clear()
    stdscr.nodelay(True)

    while True:
        # Check window size
        max_y, max_x = wait_for_min_size(stdscr)
        offset_y = (max_y - TOTAL_HEIGHT) // 2
        offset_x = (max_x - TOTAL_WIDTH) // 2

        # Process user input
        while True:
            try:
                ch = stdscr.getch()
            except curses.error:
                break
            if ch == -1:
                break
            elif ch == curses.KEY_RESIZE:
                stdscr.clear()
            elif ch in (ord('q'), ord('Q'), 27):
                return "quit"
            elif ch in (curses.KEY_UP, ord('w'), ord('W')):
                game.queue_direction((-1, 0))
            elif ch in (curses.KEY_DOWN, ord('s'), ord('S')):
                game.queue_direction((1, 0))
            elif ch in (curses.KEY_LEFT, ord('a'), ord('A')):
                game.queue_direction((0, -1))
            elif ch in (curses.KEY_RIGHT, ord('d'), ord('D')):
                game.queue_direction((0, 1))

        # Check if time for next move
        now = time.perf_counter()
        if now - last_tick >= game.tick_interval:
            last_tick = now
            alive, _ = game.step()
            if not alive:
                # Collision occurred!
                action = handle_game_over(stdscr, game, score_mgr, colors_active)
                return action

        # Redraw frame and game entities
        draw_border_and_frame(stdscr, offset_y, offset_x, game.score, game.speed, colors_active)
        draw_game(stdscr, game, offset_y, offset_x, colors_active)
        stdscr.refresh()

        # Brief sleep to avoid CPU spinning
        time.sleep(0.005)


def setup_signal_handlers():
    """Setup clean exit signal handlers for SIGHUP and SIGTERM."""
    def clean_exit(signum, frame):
        sys.exit(0)

    try:
        signal.signal(signal.SIGTERM, clean_exit)
    except Exception:
        pass
    if hasattr(signal, "SIGHUP"):
        try:
            signal.signal(signal.SIGHUP, clean_exit)
        except Exception:
            pass


def main_curses(stdscr):
    """Main curses entry point."""
    # Cursor should be hidden during gameplay
    try:
        curses.curs_set(0)
    except curses.error:
        pass

    stdscr.scrollok(False)
    colors_active = init_colors()
    score_mgr = ScoreManager()

    while True:
        action = play_game(stdscr, score_mgr, colors_active)
        if action == "quit":
            break

    # Restore cursor visibility on exit
    try:
        curses.curs_set(1)
    except curses.error:
        pass


def main():
    """Application entry point with complete terminal state protection."""
    setup_signal_handlers()
    try:
        curses.wrapper(main_curses)
    except KeyboardInterrupt:
        # Ctrl+C cleanly exits
        pass
    finally:
        # Extra guarantee cursor is visible after curses restores terminal
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
