import time

def play_game(p1, p2, boardsize, timegame, timemove):
    players = [p1, p2]

    for p in players:
        p.time(timegame, timemove)
        p.boardsize(boardsize)

    turn = players[0].start(0) # turn is the side chosen by first player
    players[1].start(3-turn)   # so give second player the other side

    move = None;
    passes = 0;  # Game is over if there are two pass moves in a row.
    log = open(time.strftime('log-%Y%m%d-%H%M%S'), 'w')
    while True:
        # Ask for a move.
        move = players[turn - 1].genmove()
        log.write('%s ' % move)

        # Game over if one player resigns or both pass in succession.
        if move in ('resign', 'none'): break
        passes = (passes + 1 if move == 'pass' else 0)
        if passes >= 2: break

        # Pass the move to the other player.
        turn = 3 - turn;
        players[turn - 1].play(move)

    log.close()
    for p in players:
        p.close()

