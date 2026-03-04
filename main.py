import time
import threading
from pathlib import Path
from PIL import Image
from rpi_ws281x import PixelStrip, Color
import os
import pygame
import random
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

# ── LED Configuration ──────────────────────────────────────────
LED_COUNT      = 100
LED_PIN        = 18
LED_FREQ_HZ    = 800000
LED_DMA        = 10
LED_BRIGHTNESS = 128
LED_INVERT     = False
LED_CHANNEL    = 0

GRID_W = 10
GRID_H = 10
IMAGES_DIR = Path(__file__).parent / "images"

# ── Shared state ───────────────────────────────────────────────
pong_active    = threading.Event()
controller_count = 0
controller_lock  = threading.Lock()

# ── Load a static image into a color[][] array ────────────────
def load(name):
    path = IMAGES_DIR / name
    img = Image.open(path).convert("RGB").transpose(Image.FLIP_TOP_BOTTOM)
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
        frame_img = gif.convert("RGB").transpose(Image.FLIP_TOP_BOTTOM)
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

# ── Define frames ──────────────────────────────────────────────
#   Static image:  (grid,      seconds)
#   GIF:           (gif_grids, fps)
FRAMES = [
    (green670Frame1, 0.5),
    (green670Frame2, 0.5),
    (green670Frame1, 0.5),
    (green670Frame2, 0.5),
    (green670Frame1, 0.5),
    (green670Frame2, 0.5),
    (green670Frame1, 0.5),
    (green670Frame2, 0.5),
    (horseProfile,   5),
    (gallop,         6.0),
    (TBA670,         5),
    (HHS, 12.0),
]

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
        pygame.event.pump()
        count = pygame.joystick.get_count()
        with controller_lock:
            controller_count = count
        if count >= 1 and not pong_active.is_set():
            print(f"{count} controller(s) detected — switching to Pong.")
            pong_active.set()
        elif count < 1 and pong_active.is_set():
            print("No controllers — returning to display.")
            pong_active.clear()
        time.sleep(0.5)

# ── Pong colors ────────────────────────────────────────────────
PADDLE_COLOR   = [255, 140, 0  ]  # orange
BALL_COLOR     = [255, 255, 255]  # white
P1_COLOR       = [220, 40,  40 ]  # red  (left)
P2_COLOR       = [40,  40,  220]  # blue (right)
BG_COLOR       = [0,   0,   0  ]
P1_WIN_COLOR   = [255, 0,   180]  # pink
P2_WIN_COLOR   = [120, 0,   255]  # purple

WINNING_SCORE = 5
PONG_TICK     = 0.12

# ── Bot logic ─────────────────────────────────────────────────
def bot_move(paddle_y, ball_y, ball_vx):
    # Only react when ball is heading toward bot (right side, x=9)
    center = paddle_y + 0.5
    if ball_vx > 0:
        if ball_y < center - 0.3 and paddle_y > 0:
            return paddle_y - 1
        elif ball_y > center + 0.3 and paddle_y < GRID_H - 2:
            return paddle_y + 1
    return paddle_y

# ── Pong game ─────────────────────────────────────────────────
def run_pong(strip):
    global controller_count

    def init_state():
        return {
            "p1y": 4, "p2y": 4,
            "bx": 4.5, "by": 4.5,
            "bdx": 1.0, "bdy": random.choice([-0.4, 0.4]),
            "p1_score": 0, "p2_score": 0,
        }

    s = init_state()

    def get_joysticks():
        pygame.joystick.init()
        js = []
        for i in range(pygame.joystick.get_count()):
            j = pygame.joystick.Joystick(i)
            j.init()
            js.append(j)
        return js

    js = get_joysticks()

    def make_grid(st):
        g = [[list(BG_COLOR) for _ in range(GRID_W)] for _ in range(GRID_H)]

        # Score: P1 red dots bottom-left, P2 blue dots bottom-right
        for i in range(st["p1_score"]):
            g[0][i] = list(P1_COLOR)
        for i in range(st["p2_score"]):
            g[0][GRID_W - 1 - i] = list(P2_COLOR)

        # Paddles (2 tall)
        for dy in range(2):
            if 0 <= st["p1y"] + dy < GRID_H:
                g[st["p1y"] + dy][0] = list(PADDLE_COLOR)
            if 0 <= st["p2y"] + dy < GRID_H:
                g[st["p2y"] + dy][GRID_W - 1] = list(PADDLE_COLOR)

        # Ball
        bxi = int(round(st["bx"]))
        byi = int(round(st["by"]))
        if 0 <= bxi < GRID_W and 0 <= byi < GRID_H:
            g[byi][bxi] = list(BALL_COLOR)

        return g

    def flash_winner(winner_side):
        col = P1_WIN_COLOR if winner_side == 1 else P2_WIN_COLOR
        g = [[list(col) for _ in range(GRID_W)] for _ in range(GRID_H)]
        show_grid(strip, g)
        time.sleep(1.0)

    while pong_active.is_set():
        pygame.event.pump()

        with controller_lock:
            count = controller_count

        # If controller count changed, reset and re-grab joysticks
        old_count = len(js)
        if count != old_count:
            print(f"Controller count changed {old_count}→{count}, resetting game.")
            js = get_joysticks()
            s = init_state()
            continue

        two_player = count >= 2

        # ── P1 input (always joystick 0) ──────────────────────
        if js:
            try:
                axis = js[0].get_axis(1)
                if axis < -0.3 and s["p1y"] > 0:
                    s["p1y"] -= 1
                elif axis > 0.3 and s["p1y"] < GRID_H - 2:
                    s["p1y"] += 1
            except pygame.error:
                pass

        # ── P2: joystick or bot ────────────────────────────────
        if two_player and len(js) >= 2:
            try:
                axis = js[1].get_axis(1)
                if axis < -0.3 and s["p2y"] > 0:
                    s["p2y"] -= 1
                elif axis > 0.3 and s["p2y"] < GRID_H - 2:
                    s["p2y"] += 1
            except pygame.error:
                pass
        else:
            s["p2y"] = bot_move(s["p2y"], s["by"], s["bdx"])

        # ── Move ball ──────────────────────────────────────────
        s["bx"] += s["bdx"]
        s["by"] += s["bdy"]

        # Wall bounce (top/bottom)
        if s["by"] <= 0:
            s["by"] = 0
            s["bdy"] = abs(s["bdy"])
        elif s["by"] >= GRID_H - 1:
            s["by"] = GRID_H - 1
            s["bdy"] = -abs(s["bdy"])

        bxi = int(round(s["bx"]))
        byi = int(round(s["by"]))

        # ── Left paddle (P1, x=0) ──────────────────────────────
        if s["bdx"] < 0 and bxi <= 1:
            hit_y_min = s["p1y"]
            hit_y_max = s["p1y"] + 1
            if hit_y_min <= byi <= hit_y_max:
                # Deflect: push ball back to x=1 so it can't tunnel
                s["bx"] = 1.0
                s["bdx"] = abs(s["bdx"])
                offset = byi - (s["p1y"] + 0.5)
                s["bdy"] = offset * 0.9 + random.uniform(-0.1, 0.1)
            elif bxi <= 0:
                # Missed — point to P2
                s["p2_score"] += 1
                print(f"Score — P1:{s['p1_score']} P2:{s['p2_score']}")
                s["bx"], s["by"] = 4.5, 4.5
                s["bdx"] = 1.0
                s["bdy"] = random.choice([-0.4, 0.4])

        # ── Right paddle (P2, x=9) ─────────────────────────────
        if s["bdx"] > 0 and bxi >= GRID_W - 2:
            hit_y_min = s["p2y"]
            hit_y_max = s["p2y"] + 1
            if hit_y_min <= byi <= hit_y_max:
                s["bx"] = float(GRID_W - 2)
                s["bdx"] = -abs(s["bdx"])
                offset = byi - (s["p2y"] + 0.5)
                s["bdy"] = offset * 0.9 + random.uniform(-0.1, 0.1)
            elif bxi >= GRID_W - 1:
                # Missed — point to P1
                s["p1_score"] += 1
                print(f"Score — P1:{s['p1_score']} P2:{s['p2_score']}")
                s["bx"], s["by"] = 4.5, 4.5
                s["bdx"] = -1.0
                s["bdy"] = random.choice([-0.4, 0.4])

        # ── Win check ──────────────────────────────────────────
        if s["p1_score"] >= WINNING_SCORE:
            show_grid(strip, make_grid(s))
            flash_winner(1)
            s = init_state()
            js = get_joysticks()
        elif s["p2_score"] >= WINNING_SCORE:
            show_grid(strip, make_grid(s))
            flash_winner(2)
            s = init_state()
            js = get_joysticks()

        show_grid(strip, make_grid(s))
        time.sleep(PONG_TICK)

# ── Main loop ──────────────────────────────────────────────────
def main():
    strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ,
                       LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    strip.begin()
    print("LED strip initialized.")

    t = threading.Thread(target=controller_listener, daemon=True)
    t.start()

    try:
        while True:
            if pong_active.is_set():
                run_pong(strip)
                clear(strip)
            else:
                for i, (data, timing) in enumerate(FRAMES):
                    if pong_active.is_set():
                        break
                    if isinstance(data[0][0][0], list):
                        spf = 1.0 / timing
                        for f, grid in enumerate(data):
                            if pong_active.is_set():
                                break
                            print(f"Frame {i+1}/{len(FRAMES)}, GIF frame {f+1}/{len(data)} at {timing}fps")
                            show_frame(strip, grid)
                            time.sleep(spf)
                    else:
                        print(f"Frame {i+1}/{len(FRAMES)} for {timing}s")
                        show_frame(strip, data)
                        time.sleep(timing)

    except KeyboardInterrupt:
        clear(strip)
        print("Stopped.")

if __name__ == "__main__":
    main()
