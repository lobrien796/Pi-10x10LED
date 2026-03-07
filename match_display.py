from utils import show_grid, match_state, match_lock
from constants import *

def _get_shaded_color(color):
    return [
        max(color[0] - 20, 0),
        max(color[1] - 40, 0),
        max(color[2] - 40, 0)
        ]

def _draw_digit(g, digit_char, start_x, start_y, color):
    """Draw a single 3x5 digit onto grid g at (start_x, start_y)."""
    pattern = DIGITS.get(digit_char, DIGITS["0"])
    for row, bits in enumerate(pattern):
        for col, bit in enumerate(bits):
            y = start_y + row
            x = start_x - col
            curr_color = color

            if row >= 3:
                curr_color = _get_shaded_color(color)

            if 0 <= y < GRID_H and 0 <= x < GRID_W:
                g[y][x] = list(curr_color) if bit else list(BLACK)

def _draw_score(g, score, color1, color2):
    score_str = str(max(min(score, 999), -99))

    if len(score_str) < 3:
        score_str = " " * (3 - len(score_str)) + score_str

    current_x = GRID_W - 1
    iteration = 0

    color = color1

    for character in score_str:
        if iteration == 0 or iteration == 2:
            color = color1
        else:
            color = color2
        _draw_digit(g, character, current_x, 3, color)

        if iteration == 0:
            current_x -= 4
        else:
            current_x -= 3
        iteration += 1

def make_match_grid(our_score, alliance_color):
    g = [[list(BLACK) for _ in range(GRID_W)] for _ in range(GRID_H)]

    bar_color = RED if alliance_color == "red" else BLUE

    # Top row
    for x in range(GRID_W):
        g[0][x] = list(bar_color)

    # Bottom row
    for x in range(GRID_W):
        g[GRID_H - 1][x] = list(_get_shaded_color(bar_color))

    # Score in the middle
    _draw_score(g, our_score, PURPLE, YELLOW)

    return g

def show_match_score(strip):
    """Called from main loop — renders current match state once."""
    with match_lock:
        score = match_state["our_score"]
        alliance = match_state["our_alliance"]
    g = make_match_grid(score, alliance)
    show_grid(strip, g)