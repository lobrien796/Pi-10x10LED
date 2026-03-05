from activity import *
import random
import pygame
import time
from utils import *

def get_joysticks():
    pygame.joystick.init()
    joysticks = []
    for i in range(pygame.joystick.get_count()):
        j = pygame.joystick.Joystick(i)
        j.init()
        joysticks.append(j)
    return joysticks

def init_state():
    return {
        "p1y": 4, "p2y": 4,
        "bx": 4.5, "by": 4.5,
        "bdx": 1.0, "bdy": random.choice([-0.4, 0.4]),
        "p1_score": 0, "p2_score": 0,
    }

match_active = threading.Event()

match_state = {
    "our_score": 0,
    "their_score": 0,
    "our_alliance": "red",  # "red" or "blue"
}
match_lock = threading.Lock()


class Pong(Activity):
    PADDLE_COLOR   = [255, 140, 0  ]
    BALL_COLOR     = [255, 255, 255]
    P1_COLOR       = [255, 0,  0 ]
    P2_COLOR       = [0,  0,  255]
    BG_COLOR       = [0,   0,   0  ]
    P1_WIN_COLOR   = [255, 0,   0]
    P2_WIN_COLOR   = [0, 0,   255]

    WINNING_SCORE = 5
    PONG_TICK     = 0.12

    def __init__(self, strip, finished_cond):
        super().__init__(strip, finished_cond)
        self.state = init_state()
        self.joysticks = get_joysticks()

    def bot_move(self, paddle_y, ball_y, ball_vx):
        center = paddle_y + 0.5
        if ball_vx > 0:
            if ball_y < center - 0.3 and paddle_y > 0:
                return paddle_y - 1
            elif ball_y > center + 0.3 and paddle_y < GRID_H - 2:
                return paddle_y + 1
        return paddle_y

    def make_grid(self, st):
        g = [[list(Pong.BG_COLOR) for _ in range(GRID_W)] for _ in range(GRID_H)]

        for i in range(st["p1_score"]):
            g[0][i] = list(Pong.P1_COLOR)
        for i in range(st["p2_score"]):
            g[0][GRID_W - 1 - i] = list(Pong.P2_COLOR)

        for dy in range(2):
            if 0 <= st["p1y"] + dy < GRID_H:
                g[st["p1y"] + dy][0] = list(Pong.PADDLE_COLOR)
            if 0 <= st["p2y"] + dy < GRID_H:
                g[st["p2y"] + dy][GRID_W - 1] = list(Pong.PADDLE_COLOR)

        bxi = int(round(st["bx"]))
        byi = int(round(st["by"]))
        if 0 <= bxi < GRID_W and 0 <= byi < GRID_H:
            g[byi][bxi] = list(Pong.BALL_COLOR)

        return g

    def flash_winner(self, winner_side):
        col = Pong.P1_WIN_COLOR if winner_side == 1 else Pong.P2_WIN_COLOR
        g = [[list(col) for _ in range(GRID_W)] for _ in range(GRID_H)]
        show_grid(self.strip, g)
        time.sleep(1.0)

    def update(self):

        pygame.event.pump()

        with controller_lock:
            count = get_controller_count()

        two_player = count >= 2

        # ── P1 input (always joystick 0) ──────────────────────
        if self.joysticks:
            try:
                axis = self.joysticks[0].get_axis(1)
                if axis < -0.3 and self.state["p1y"] > 0:
                    self.state["p1y"] -= 1
                elif axis > 0.3 and self.state["p1y"] < GRID_H - 2:
                    self.state["p1y"] += 1
            except pygame.error:
                pass

        # ── P2: joystick or bot ────────────────────────────────
        if two_player and len(self.joysticks) >= 2:
            try:
                axis = self.joysticks[1].get_axis(1)
                if axis < -0.3 and self.state["p2y"] > 0:
                    self.state["p2y"] -= 1
                elif axis > 0.3 and self.state["p2y"] < GRID_H - 2:
                    self.state["p2y"] += 1
            except pygame.error:
                pass
        else:
            self.state["p2y"] = self.bot_move(self.state["p2y"], self.state["by"], self.state["bdx"])

        # ── Move ball ──────────────────────────────────────────
        self.state["bx"] += self.state["bdx"]
        self.state["by"] += self.state["bdy"]

        if self.state["by"] <= 0:
            self.state["by"] = 0
            self.state["bdy"] = abs(self.state["bdy"])
        elif self.state["by"] >= GRID_H - 1:
            self.state["by"] = GRID_H - 1
            self.state["bdy"] = -abs(self.state["bdy"])

        bxi = int(round(self.state["bx"]))
        byi = int(round(self.state["by"]))

        # ── Left paddle (P1, x=0) ──────────────────────────────
        if self.state["bdx"] < 0 and bxi <= 1:
            if self.state["p1y"] <= byi <= self.state["p1y"] + 1:
                self.state["bx"] = 1.0
                self.state["bdx"] = abs(self.state["bdx"])
                offset = byi - (self.state["p1y"] + 0.5)
                self.state["bdy"] = offset * 0.9 + random.uniform(-0.1, 0.1)
            elif bxi <= 0:
                self.state["p2_score"] += 1
                print(f"Score — P1:{self.state['p1_score']} P2:{self.state['p2_score']}")
                self.state["bx"], self.state["by"] = 4.5, 4.5
                self.state["bdx"] = 1.0
                self.state["bdy"] = random.choice([-0.4, 0.4])

        # ── Right paddle (P2, x=9) ─────────────────────────────
        if self.state["bdx"] > 0 and bxi >= GRID_W - 2:
            if self.state["p2y"] <= byi <= self.state["p2y"] + 1:
                self.state["bx"] = float(GRID_W - 2)
                self.state["bdx"] = -abs(self.state["bdx"])
                offset = byi - (self.state["p2y"] + 0.5)
                self.state["bdy"] = offset * 0.9 + random.uniform(-0.1, 0.1)
            elif bxi >= GRID_W - 1:
                self.state["p1_score"] += 1
                print(f"Score — P1:{self.state['p1_score']} P2:{self.state['p2_score']}")
                self.state["bx"], self.state["by"] = 4.5, 4.5
                self.state["bdx"] = -1.0
                self.state["bdy"] = random.choice([-0.4, 0.4])

        # ── Win check ──────────────────────────────────────────
        if self.state["p1_score"] >= Pong.WINNING_SCORE:
            show_grid(self.strip, self.make_grid(self.state))
            self.flash_winner(1)
            self.state = init_state()
            self.joysticks = get_joysticks()
        elif self.state["p2_score"] >= Pong.WINNING_SCORE:
            show_grid(self.strip, self.make_grid(self.state))
            self.flash_winner(2)
            self.state = init_state()
            self.joysticks = get_joysticks()

    def render(self):
        show_grid(self.strip, self.make_grid(self.state))
        time.sleep(Pong.PONG_TICK)
