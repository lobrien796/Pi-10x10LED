from activity import Activity
from utils import *
import random
import pygame
from constants import *

pygame.init()
pygame.joystick.init()

BLACK: list[int] = [0, 0, 0]
WHITE: list[int] = [255, 255, 255]
RED:   list[int] = [255, 0, 0]
GREEN: list[int] = [0, 255, 0]

RANGE: float = 0.5
GROUND_Y: int = GRID_H - 2
PLAYER_X: int = 7

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
        _draw_digit(g, character, current_x, 0, color)

        if iteration == 0:
            current_x -= 4
        else:
            current_x -= 3
        iteration += 1


def get_joysticks() -> list[pygame.joystick.JoystickType]:
    pygame.joystick.init()
    joysticks: list[pygame.joystick.JoystickType] = []
    for i in range(pygame.joystick.get_count()):
        j = pygame.joystick.Joystick(i)
        j.init()
        joysticks.append(j)
    return joysticks


class Dino(Activity):
    grid: list[list[list[int]]]
    player_y: int
    jumping: bool
    current_jump_frame: int
    can_jump: bool
    obstacles: list[int]
    obstacle_timer: int
    obstacle_interval: int
    game_over: bool
    flash_timer: int
    score: int
    score_timer: int

    JUMP_FRAMES: dict[int, int] = {
        1: GROUND_Y - 1,
        2: GROUND_Y - 3,
        3: GROUND_Y - 4,
        4: GROUND_Y - 4,
        5: GROUND_Y - 3,
        6: GROUND_Y - 1,
        7: GROUND_Y,
    }
    JUMP_LEN: int = 7

    def __init__(self, strip, finished_cond) -> None:
        super().__init__(strip, finished_cond)
        self.grid = [[list(BLACK) for _ in range(GRID_W)] for _ in range(GRID_H)]
        self._reset()

        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()

    def _reset(self) -> None:
        self.player_y = GROUND_Y
        self.jumping = False
        self.current_jump_frame = 0
        self.can_jump = True
        self.obstacles = []
        self.obstacle_timer = 0
        self.obstacle_interval = random.randint(6, 12)
        self.game_over = False
        self.flash_timer = 0
        self.score = 0
        self.score_timer = 0

    def _joystick_pressed(self) -> bool:
        if pygame.joystick.get_count() > 0:
            return self.joystick.get_button(0)
        else:
            return False

    def update(self) -> None:
        if self.game_over:
            self.flash_timer += 1
            if self._joystick_pressed():
                self._reset()
            return

        pressed: bool = self._joystick_pressed()

        # Jump input
        if self.can_jump and pressed:
            self.jumping = True
            self.can_jump = False
            self.current_jump_frame = 0

        # Process jump arc
        if self.jumping:
            self.current_jump_frame += 1
            self.player_y = self.JUMP_FRAMES.get(self.current_jump_frame, GROUND_Y)
            if self.current_jump_frame >= self.JUMP_LEN:
                self.jumping = False
                self.current_jump_frame = 0
                self.player_y = GROUND_Y
                self.can_jump = True

        # Increment score every 5 frames
        self.score_timer += 1
        if self.score_timer >= 5:
            self.score_timer = 0
            self.score = min(self.score + 1, 999)

        # Spawn obstacles at left edge
        self.obstacle_timer += 1
        if self.obstacle_timer >= self.obstacle_interval:
            self.obstacles.append(0)
            self.obstacle_timer = 0
            self.obstacle_interval = random.randint(6, 14)

        # Move obstacles right (toward player)
        self.obstacles = [x + 1 for x in self.obstacles]
        self.obstacles = [x for x in self.obstacles if x < GRID_W]

        # Collision — range check so fast obstacles can't skip through
        for ox in self.obstacles:
            if abs(ox - PLAYER_X) <= 1 and self.player_y >= GROUND_Y:
                self.game_over = True
                return

    def render(self) -> None:
        self.grid = [[list(BLACK) for _ in range(GRID_W)] for _ in range(GRID_H)]

        if self.game_over:
            color: list[int] = RED if (self.flash_timer // 3) % 2 == 0 else BLACK
            for col in range(GRID_W):
                self.grid[GROUND_Y][col] = list(color)
            _draw_score(self.grid, self.score, PURPLE, YELLOW)
            show_grid(self.strip, self.grid)
            time.sleep(0.1)
            return

        # Draw player (green when jumping, white on ground)
        player_color: list[int] = GREEN if self.jumping else WHITE
        self.grid[self.player_y][PLAYER_X] = list(player_color)

        # Draw obstacles
        for ox in self.obstacles:
            try:
                self.grid[GROUND_Y][ox] = list(RED)
            except:
                self.obstacles.remove(ox)

        # Ground

        for i in range(GRID_W):
            self.grid[GRID_H - 1][i] = WHITE

        _draw_score(self.grid, self.score, PURPLE, YELLOW)

        show_grid(self.strip, self.grid)
        time.sleep(0.1)