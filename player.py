
import random

class Player(object):
    sides = ['', 'white', 'black']

    def close(self):
        '''close the conection, exit the program, etc'''
        raise NotImplementedError

    def name(self):
        '''name of the program'''
        return "Unimplemented player"

    def boardsize(self, size):
        '''set the boardsize, called before start()'''
        raise NotImplementedError

    def time(self, game, move):
        '''set the time per game plus extra time per move, called before start()'''
        raise NotImplementedError

    def start(self, side):
        '''done initialization, if side==0, choose a side and return it, otherwise this is your side'''
        return (side if side > 0 else random.randint(1, 2))

    def play(self, move):
        '''the opponent made move'''
        raise NotImplementedError

    def genmove(self):
        '''generate a move'''
        return "pass"
