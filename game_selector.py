import pygame

from activity import Activity
from typing import Callable
from dino import Dino
from flappybird import FlappyBird
from pong import Pong

from utils import *

def no_condition():
    return False

games = [
    [
        lambda strip: Dino(strip, no_condition),
        load("dino_cover.png")
    ],
    [
        lambda strip: Pong(strip, no_condition),
        load("pong_cover.png")
    ],
    [
        lambda strip: FlappyBird(strip, no_condition),
        load("flappybird_cover.png")
    ],
]

class GameSelector(Activity):
    def __init__(self, strip, finish_cond):
        super().__init__(strip, finish_cond)
        self.current_game_index = 0

        self.current_game = None

        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()

    def right_pressed(self, zone=0.5):
        if pygame.joystick.get_count() > 0:
            return self.joystick.get_axis(5) > zone or self.joystick.get_button(5)
        return False
    
    def left_pressed(self, zone=0.5):
        if pygame.joystick.get_count() > 0:
            return self.joystick.get_axis(4) > zone or self.joystick.get_button(4)
        return False
    
    def a_pressed(self):
        if pygame.joystick.get_count() > 0:
            return self.joystick.get_button(0)
        else:
            return False
        
    def menu_pressed(self):
        if pygame.joystick.get_count() > 0:
            return self.joystick.get_button(7)
        else:
            return pygame.key.get_just_pressed()[pygame.K_m]

    def update(self):
        if self.current_game:
            if not self.current_game.finished_cond():
                self.current_game.update()
                if self.menu_pressed():
                    del self.current_game
                    self.current_game = None
            else:
                del self.current_game
                self.current_game = None
        else:
            if self.left_pressed(): self.current_game_index -= 1
            if self.right_pressed(): self.current_game_index += 1
            if self.a_pressed():
                self.current_game = games[self.current_game_index][0](self.strip)


    def render(self):
        if self.current_game_index >= len(games) or self.current_game_index < 0:
            self.current_game_index = self.current_game_index % len(games)

        if self.current_game:
            if not self.current_game.finished_cond():
                self.current_game.render()
            else:
                self.current_game = None
            
        else:
            current_image = games[self.current_game_index][1]

            grid = list(current_image)
            grid.reverse()

            # Arrows

            grid[4][9] = WHITE
            grid[5][9] = WHITE
            grid[3][8] = WHITE
            grid[4][8] = WHITE
            grid[5][8] = WHITE
            grid[6][8] = WHITE
            
            grid[4][0] = WHITE
            grid[5][0] = WHITE
            grid[3][1] = WHITE
            grid[4][1] = WHITE
            grid[5][1] = WHITE
            grid[6][1] = WHITE

            show_grid(self.strip, grid)
            time.sleep(0.1)