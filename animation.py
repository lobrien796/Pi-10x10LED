from activity import Activity
from utils import *

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
    (wifi, 3.0),
    (intaking, 6.0),
    (shooting, 6.0),
    (load_gif("question.gif"), 3.0),
    # (load_gif("bad_apple.gif"), 30.0)
]

class Animation(Activity):
    def __init__(self, a, b):
        super().__init__(a, b)
        self.frame = 0

    def update(self):
        data = FRAMES[self.frame][0]
        timing = FRAMES[self.frame][1]

        if isinstance(data[0][0][0], list):
            spf = 1.0 / timing
            for f, grid in enumerate(data):
                if controller_connected.is_set():
                    break
                print(f"Frame {self.frame+1}/{len(FRAMES)}, GIF frame {f+1}/{len(data)} at {timing}fps")
                show_frame(self.strip, grid)
                time.sleep(spf)
        else:
            print(f"Frame {self.frame+1}/{len(FRAMES)} for {timing}s")
            show_frame(self.strip, data)
            time.sleep(timing)

        self.frame = (self.frame + 1)%len(FRAMES)
