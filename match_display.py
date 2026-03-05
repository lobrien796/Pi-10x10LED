from utils import GRID_W, GRID_H, show_grid, match_state, match_lock

# ── 3x5 pixel font (digits 0–9) ───────────────────────────────
# Each digit is a list of 5 rows, 3 cols wide. 1 = lit, 0 = off.
DIGITS = {
    "0": [
        [1,1,1],
        [1,0,1],
        [1,0,1],
        [1,0,1],
        [1,1,1],
    ],
    "1": [
        [0,1,0],
        [1,1,0],
        [0,1,0],
        [0,1,0],
        [1,1,1],
    ],
    "2": [
        [1,1,1],
        [0,0,1],
        [1,1,1],
        [1,0,0],
        [1,1,1],
    ],
    "3": [
        [1,1,1],
        [0,0,1],
        [1,1,1],
        [0,0,1],
        [1,1,1],
    ],
    "4": [
        [1,0,1],
        [1,0,1],
        [1,1,1],
        [0,0,1],
        [0,0,1],
    ],
    "5": [
        [1,1,1],
        [1,0,0],
        [1,1,1],
        [0,0,1],
        [1,1,1],
    ],
    "6": [
        [1,1,1],
        [1,0,0],
        [1,1,1],
        [1,0,1],
        [1,1,1],
    ],
    "7": [
        [1,1,1],
        [0,0,1],
        [0,1,0],
        [0,1,0],
        [0,1,0],
    ],
    "8": [
        [1,1,1],
        [1,0,1],
        [1,1,1],
        [1,0,1],
        [1,1,1],
    ],
    "9": [
        [1,1,1],
        [1,0,1],
        [1,1,1],
        [0,0,1],
        [1,1,1],
    ],
}

WHITE  = [255, 255, 255]
BLACK  = [0,   0,   0  ]
RED    = [200, 0,   0  ]
BLUE   = [0,   0,   200]

def _draw_digit(g, digit_char, start_x, start_y, color):
    """Draw a single 3x5 digit onto grid g at (start_x, start_y)."""
    pattern = DIGITS.get(digit_char, DIGITS["0"])
    for row, bits in enumerate(pattern):
        for col, bit in enumerate(bits):
            y = start_y + row
            x = start_x + col
            if 0 <= y < GRID_H and 0 <= x < GRID_W:
                g[y][x] = list(color) if bit else list(BLACK)

def _draw_score(g, score, color):
    """
    Draw score (0–999) centered horizontally in rows 2–6.
    Single digit  → centered (x=3)
    Two digits    → side by side with 1px gap, centered
    Three digits  → three digits with 1px gap
    """
    s = str(min(score, 999))
    digit_w = 3
    gap     = 1
    total_w = len(s) * digit_w + (len(s) - 1) * gap
    start_x = (GRID_W - total_w) // 2
    start_y = 2  # rows 2–6, leaving rows 0–1 and 8–9 for alliance bars

    for i, ch in enumerate(s):
        _draw_digit(g, ch, start_x + i * (digit_w + gap), start_y, color)

def make_match_grid(our_score, alliance_color):
    g = [[list(BLACK) for _ in range(GRID_W)] for _ in range(GRID_H)]

    bar_color = RED if alliance_color == "red" else BLUE

    # Top 2 rows — alliance color bar
    for y in range(2):
        for x in range(GRID_W):
            g[y][x] = list(bar_color)

    # Bottom 2 rows — alliance color bar
    for y in range(GRID_H - 2, GRID_H):
        for x in range(GRID_W):
            g[y][x] = list(bar_color)

    # Score in the middle
    _draw_score(g, our_score, WHITE)

    return g

def show_match_score(strip):
    """Called from main loop — renders current match state once."""
    with match_lock:
        score   = match_state["our_score"]
        alliance = match_state["our_alliance"]
    g = make_match_grid(score, alliance)
    show_grid(strip, g)