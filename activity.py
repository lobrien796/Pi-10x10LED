from typing import Callable
import pygame
import sys

class Activity:
    def __init__(self, strip, finished_cond: Callable[[], bool]):
        self.finished_cond = finished_cond
        self.strip = strip

    def update(self):
        pass

    def render(self):
        pass

    def run(self):
        while self.finished_cond():
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit(0)

            self.update()
            self.render()