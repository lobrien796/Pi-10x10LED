from typing import Callable

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
            self.update()
            self.render()