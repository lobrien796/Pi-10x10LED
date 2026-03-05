import pygame

GRID_W = 10
GRID_H = 10

# ── 3x5 pixel font (digits 0–9) ───────────────────────────────
# Each digit is a list of 5 rows, 3 cols wide. 1 = lit, 0 = off.
DIGITS = {
    ".": [
        [0,0,0],
        [0,0,0],
        [0,0,0],
        [0,0,0],
        [1,0,0]
    ],
    "-": [
        [0,0,0],
        [0,0,0],
        [1,1,1],
        [0,0,0],
        [0,0,0],
    ],
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
BLACK  = [28, 28, 28]
PURPLE = [96, 0, 255]
YELLOW = [255, 192, 0]
RED    = [255, 103, 80]
BLUE   = [0, 84, 255]

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
            x = start_x + col
            curr_color = color

            if row >= 3:
                curr_color = _get_shaded_color(color)

            if 0 <= y < GRID_H and 0 <= x < GRID_W:
                g[y][x] = list(curr_color) if bit else list(BLACK)

def _draw_score(g, score, color1, color2):
    """
    Draw score (-99 to 999) centered horizontally in rows 2–6. It can also draw some decimals but limited. If it is out of range it is clamped to the range.
    """
    score_str = str(max(min(score, 999), -99))

    if len(score_str) < 3:
        score_str = "0" * (3 - len(score_str)) + score_str

    current_x = 0
    iteration = 0

    color = color1

    for character in score_str:
        if iteration == 0 or iteration == 2:
            color = color1
        else:
            color = color2
        _draw_digit(g, character, current_x, 3, color)

        if current_x == 0:
            current_x += 4
        else:
            current_x += 3
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

screen = pygame.display.set_mode((800, 800))

pygame.display.set_caption("Score Display Test")

grid = make_match_grid(150, "blue")

running = True

cell_size = screen.get_width() / GRID_H

num = 0
timer = 0

clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                if event.key == pygame.K_LSHIFT:
                    cell_size -= 5
                cell_size -= 5

            if event.key == pygame.K_UP:
                if event.key == pygame.K_LSHIFT:
                    cell_size += 5
                cell_size += 5

            if event.key == pygame.K_w:
                GRID_W += 1
                GRID_H += 1
            
            if event.key == pygame.K_s:
                GRID_W -= 1
                GRID_H -= 1

            pygame.display.set_mode((cell_size * GRID_H, cell_size * GRID_H))

    screen.fill("white")

    grid = make_match_grid(num, "blue")

    timer += 1
    if timer == 12:
        num += 1
        timer = 0

    for i, row in enumerate(grid):
        for j, color in enumerate(row):
            x = j * cell_size
            y = i * cell_size

            pygame.draw.rect(screen, color, (x, y, cell_size, cell_size))

    pygame.display.update()

    clock.tick(60)