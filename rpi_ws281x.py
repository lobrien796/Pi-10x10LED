import math
import pygame
import threading

pygame.init()

GRID_W = 10
GRID_H = 10

BLACK = [0, 0, 0]

class PixelStrip:
    def loop(self):
        while self.running:
            self.screen.fill("white")
                    
            for i, row in enumerate(self.display_grid):
                for j, color in enumerate(row):
                    x = j * self.cell_size
                    y = i * self.cell_size

                    pygame.draw.rect(self.screen, color, (x, y, self.cell_size, self.cell_size))

            pygame.display.update()

            self.clock.tick(60)

        pygame.quit()
        self.window_thread.join()

    def stop_loop(self):
        self.window_thread.join()

    # Usually it is just one strip that is cut up, but we are going to assume that the dimentions are square
    def __init__(self, num, pin, freq, dma, invert, brightness, channel):
        self.pin = pin
        self.freq = freq
        self.num = num
        self.dma = dma
        self.invert = invert
        self.brightness = brightness
        self.channel = channel

        self.grid = [[list(BLACK) for _ in range(GRID_W)] for _ in range(GRID_H)]

        self.display_grid = self.grid
                
        self.screen = pygame.display.set_mode((800, 800))

        pygame.display.set_caption("Score Display Test")

        self.running = True

        self.cell_size = self.screen.get_width() / GRID_H

        self.clock = pygame.time.Clock()

        self.window_thread = threading.Thread(target=self.loop, daemon=True)
        self.window_thread.start()

    # create the window
    def begin(self):
        pass

    def setPixelColor(self, pos, color):
        offset = pos % GRID_W
        row = math.floor(pos / GRID_W)
        
        if row % 2 == 1:
            self.grid[GRID_H - row - 1][GRID_W-offset-1] = color.color
        else:
            self.grid[GRID_H - row - 1][offset] = color.color

    def show(self):
        self.display_grid = self.grid

class Color:
    def __init__(self, r, g, b):
        self.color = [r, g, b]
