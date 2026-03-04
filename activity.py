class Activity:
    def __init__(self, strip):
        pass

    def update(self):
        pass

    def render(self):
        pass

    def run(self, finished_cond):
        while finished_cond():
            self.update()
            self.render()