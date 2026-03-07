from activity import Activity
from utils import *
from constants import *
import pygame
import random

class FlappyBird(Activity):
    def __init__(self, strip, cond):
        super().__init__(strip, cond)

        self.player_y = 4

        self.player_vel = 0
        
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)

        self.mode = "play"

        self.pipex = 0
        self.pipey = random.randint(0, 9)

        self.opening_size = 2

    def reset(self):
        self.player_vel = 0
        self.player_y = 4
        self.mode = "play"
        
        self.pipex = 0
        self.pipey = random.randint(0, 9)

    def a_pressed(self):
        if pygame.joystick.get_count() > 0:
            return self.joystick.get_button(0)
        else:
            return False

    def update(self):
        pygame.event.pump()

        if self.mode == "play":
            self.player_y += self.player_vel
            self.player_vel += 0.0000002

            if self.a_pressed():
                self.player_vel = -0.0008

            if self.player_y < 0 or self.player_y > 9 or (self.pipex > 7 and self.pipex <= 8 and abs(self.pipey-self.player_y) > self.opening_size):
                self.mode = "dead"

            self.pipex += 0.001

            if self.pipex > 9:
                self.pipex = 0
                self.pipey = random.randint(2, 7)

        else:
            if self.a_pressed():
                self.reset()

    def render(self):
        if self.mode == "play":
            grid = [[list([50, 100, 255]) for _ in range(GRID_W)] for _ in range(GRID_H)]

            grid[int(self.player_y)][7] = YELLOW

            for i in range(GRID_H):
                if abs(self.pipey-i) > self.opening_size:
                    grid[i][int(self.pipex)] = GREEN

            show_grid(self.strip, grid)
        else:
            show_grid(self.strip, [[list(RED) for _ in range(GRID_W)] for _ in range(GRID_H)])