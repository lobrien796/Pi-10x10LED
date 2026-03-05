import time
import threading
from utils import *
from pong import Pong
from rpi_ws281x import PixelStrip
from animation import Animation
from tba import tba_listener, show_match_score

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
    default_acivity = Animation(strip, lambda: not pong_active.is_set())

    activities = [
        Pong(strip, pong_active.is_set),
        Animation(strip, lambda: not pong_active.is_set())
    ]

    try:
        while True:
            if match_active.is_set():
                show_match_score(strip)
                while match_active.is_set():
                    time.sleep(0.5)
                clear(strip)

            elif activities[current_activity_index].finished_cond():
                activities[current_activity_index].run()
                clear(strip)
            else:
                default_acivity.run()
                clear(strip)

    except KeyboardInterrupt:
        clear(strip)
        print("Stopped.")

main()
