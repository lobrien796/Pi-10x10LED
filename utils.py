from pathlib import Path
from PIL import Image
import os
import threading
import pygame
from rpi_ws281x import Color
import time
from constants import *

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

# ── Shared state ───────────────────────────────────────────────
controller_connected    = threading.Event()
controller_count = 0
controller_lock  = threading.Lock()

match_active = threading.Event()  # set = match is live, clear = no match

match_state = {
    "our_score": 0,
    "our_alliance": "red",  # "red" or "blue"
}
match_lock = threading.Lock()

# ── Load a static image into a color[][] array ────────────────
def load(name):
    path = IMAGES_DIR / name
    img = Image.open(path).convert("RGB").transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    if img.size != (GRID_W, GRID_H):
        raise ValueError(f"{name} is not {GRID_W}x{GRID_H} pixels")
    px = img.load()
    return [[list(px[x, y]) for x in range(GRID_W)] for y in range(GRID_H)]

# ── Load a GIF into a list of color[][] arrays (one per frame) ─
def load_gif(name):
    path = IMAGES_DIR / name
    gif = Image.open(path)
    if not hasattr(gif, "n_frames"):
        raise ValueError(f"{name} does not appear to be an animated GIF.")
    frames = []
    for f in range(gif.n_frames):
        gif.seek(f)
        frame_img = gif.convert("RGB").transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        if frame_img.size != (GRID_W, GRID_H):
            raise ValueError(f"{name} frame {f} is not {GRID_W}x{GRID_H} pixels")
        px = frame_img.load()
        frames.append([[[px[x, y][0], px[x, y][1], px[x, y][2]] for x in range(GRID_W)] for y in range(GRID_H)])
    return frames

# ── Pre-load everything once ───────────────────────────────────
green670Frame1 = load("green670Frame1.png")
green670Frame2 = load("green670Frame2.png")
gallop         = load_gif("gallop.gif")
TBA670         = load("TBA670.png")
horseProfile   = load("horseProfile.png")
HHS = load_gif("HHS.gif")
wifi = load_gif("wifi.gif")
shooting = load_gif("shooting.gif")
intaking = load_gif("intaking.gif")

# ── Snake grid mapping ─────────────────────────────────────────
def xy_to_led(x, y):
    if y % 2 == 0:
        return y * GRID_W + x
    else:
        return y * GRID_W + (GRID_W - 1 - x)

# ── Display a single grid ──────────────────────────────────────
def show_frame(strip, grid):
    for y in range(GRID_H):
        for x in range(GRID_W):
            r, g, b = grid[y][x]
            strip.setPixelColor(xy_to_led(x, y), Color(r, g, b))
    strip.show()

# ── Display pong grid (rotated 180°) ─────────────────────────
def show_grid(strip, grid):
    for y in range(GRID_H):
        for x in range(GRID_W):
            r, g, b = grid[GRID_H - 1 - y][GRID_W - 1 - x]
            strip.setPixelColor(xy_to_led(x, y), Color(r, g, b))
    strip.show()

# ── Clear display ──────────────────────────────────────────────
def clear(strip):
    for i in range(LED_COUNT):
        strip.setPixelColor(i, Color(0, 0, 0))
    strip.show()

# ── Controller listener ────────────────────────────────────────
def controller_listener():
    global controller_count
    pygame.init()
    pygame.joystick.init()
    print("Controller listener started.")
    while True:
        count = pygame.joystick.get_count()
        with controller_lock:
            controller_count = count
        if count >= 1 and not controller_connected.is_set():
            print(f"{count} controller(s) detected — switching to Game Selection.")
            controller_connected.set()
        elif count < 1 and controller_connected.is_set():
            print("No controllers — returning to default animation.")
            controller_connected.clear()
        time.sleep(0.5)

def get_controller_count():
    global controller_count
    return controller_count