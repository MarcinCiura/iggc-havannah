#!/usr/bin/python

from player import Player
from castro import Castro
from lajkonik import Lajkonik
from wanderer import Wanderer
from iggc_player import IGGCPlayer
from game import play_game

def main():
    while True:
        try:
            play_game(
#                IGGCPlayer(login='Lajkonik_bot', password='...', app_id=18, app_code='navaha8730'),
#                IGGCPlayer(login='Castro_bot', password='...', app_id=19, app_code='vhaaan2783'),
                IGGCPlayer(login='Wanderer_bot', password='...', app_id=18, app_code='navaha8730'),
#                Lajkonik('../lajkonik/lajkonik-10'),
#                Castro('../castro/castro'),
                Wanderer('../wanderer/wanderer'),
                boardsize=10, timegame=3600, timemove=15
                )
        except Exception as e:
            print e

if __name__ == '__main__':
  main()

