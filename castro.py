
from gtp import GTPClient

class Castro(GTPClient):
    def time(self, game, move):
        self.cmd("time -g %s -m %s" % (game, move))

