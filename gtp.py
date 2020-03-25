
from player import Player
from subprocess import Popen, PIPE
import random

class GTPClient(Player):
    def __init__(self, cmdline, params=[]):
        self._proc = Popen(cmdline, stdin=PIPE, stdout=PIPE)
        for p in params:
            self.cmd(p)

    def close(self):
        self.cmd("quit")
        self._proc.terminate()
        self._proc.wait()

    def name(self):
        return self.cmd("name")

    def boardsize(self, size):
        self.cmd("boardsize %s" % (size))

    def time(self, game, move):
        self.cmd("time_settings %s %s 1" % (game, move))

    def start(self, side):
        self._side = ( side if side > 0 else random.randint(1,2))
        return self._side

    def play(self, m):
        self.cmd("play %s %s" % (GTPClient.sides[3 - self._side], m))

    def genmove(self):
        return self.cmd("genmove %s" % (GTPClient.sides[self._side]))

    def cmd(self, c):
        print ">", c.strip()
        self._proc.stdin.write(c.strip() + "\n")
        result = ""
        while True:
            line = self._proc.stdout.readline()
            result += line
            if line == "\n":
                if result[0] != '=':
                    raise Exception(result)
                print result.strip()
                return result[2:].strip()

