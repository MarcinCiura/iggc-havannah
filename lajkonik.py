from gtp import GTPClient

class Lajkonik(GTPClient):
    def time(self, game, move):
        seconds_per_move = 75  # game // 60 + move
        self.cmd("setoption seconds_per_move %s" % seconds_per_move)
