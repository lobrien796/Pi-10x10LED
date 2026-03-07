import time
import threading
from utils import *
from game_selector import GameSelector
from animation import Animation
from tba import tba_listener
from match_display import show_match_score
from rpi_ws281x import PixelStrip
import sys

# ── Main loop ──────────────────────────────────────────────────
def main():
    strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ,
                       LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    strip.begin()
    print("LED strip initialized.")

    controller_thread = threading.Thread(target=controller_listener, daemon=True)
    controller_thread.start()
    
    t2 = threading.Thread(target=tba_listener, daemon=True)
    t2.start()

    current_activity_index = 0
    default_acivity = lambda: Animation(strip, lambda: not controller_connected.is_set())

    activities = [
        lambda: GameSelector(strip, controller_connected.is_set),
        lambda: Animation(strip, lambda: not controller_connected.is_set())
    ]

    is_playing = False

    try:
        while True:
            if match_active.is_set() and is_playing:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        sys.exit(0)
                show_match_score(strip)

            elif activities[current_activity_index]().finished_cond():
                activities[current_activity_index]().run()
                clear(strip)
            else:
                default_acivity().run()
                clear(strip)

    except KeyboardInterrupt:
        clear(strip)
        print("Stopped.")

main()
