import pygame

from activity import Activity
from typing import Callable
from dino import Dino
from pong import Pong

from utils import *

def no_condition():
    return False

games = [
    [
        lambda strip: Dino(strip, no_condition),
        "dino_cover.png"
    ],
    [
        lambda strip: Pong(strip, no_condition),
        "pong_cover.png"
    ],
]

class GameSelector(Activity):
    def __init__(self, strip, finish_cond):
        super().__init__(strip, finish_cond)
        self.current_game_index = 0

        self.current_game = None

        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)

    def right_pressed(self, zone=0.5):
        if pygame.joystick.get_count() > 0:
            return self.joystick.get_axis(5) > zone
        return False
    
    def left_pressed(self, zone=0.5):
        if pygame.joystick.get_count() > 0:
            return self.joystick.get_axis(2) > zone
        return False
    
    def a_pressed(self):
        if pygame.joystick.get_count() > 0:
            return self.joystick.get_button(0)
        else:
            return False

    def update(self):
        if self.current_game:
            if self.current_game.finished_cond():
                self.current_game.update()
            else:
                self.current_game = None
        else:
            if self.left_pressed(): self.current_game_index -= 1
            if self.right_pressed(): self.current_game_index += 1
            if self.a_pressed():
                self.current_game = games[self.current_game_index][0]()


    def render(self):
        if self.current_game_index >= len(games) or self.current_game_index < 0:
            self.current_game_index = self.current_game_index % len(games)
            
        if self.current_game and self.current_game.finished_cond():
            self.current_game.render()
        else:
            current_image = load(games[self.current_game_index][1])

            grid = current_image

            # Arrows

            grid[5][9] = WHITE
            grid[6][9] = WHITE
            grid[4][8] = WHITE
            grid[5][8] = WHITE
            grid[6][8] = WHITE
            grid[7][8] = WHITE
            
            grid[5][0] = WHITE
            grid[6][0] = WHITE
            grid[4][0] = WHITE
            grid[5][0] = WHITE
            grid[6][0] = WHITE
            grid[7][0] = WHITE

            show_grid(self.strip, grid)