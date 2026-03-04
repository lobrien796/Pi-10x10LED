import time
import threading
import pygame
import random
from utils import *
from pong import Pong

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
                pong = Pong(strip)
                pong.run(pong_active.is_set)
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
