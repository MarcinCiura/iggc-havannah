
import getpass
import hashlib
import optparse
import sys
import threading
import time
import urllib
import urllib2
# sudo easy_install beautifulsoup4; sudo easy_install lxml
import bs4

from player import Player

class Error(Exception):
  """Raised on exceptions in this module."""


class IGGCPlayer(Player):
    HAVANNAH_GID = 66
    POLL_INTERVAL_SECS = 5
    WELCOME_MESSAGE = """Hi. I am a Havannah-playing bot. Please take a seat."""
    SWAP_MESSAGE = """I do not understand swap, so please don't play it, as I will probably crash."""
    OPTIONS_MESSAGE = """I don't support changing options, changing them back."""
    RESTART_MESSAGE = """I don't know how to handle the restart event..."""
    THANKS_MESSAGE = """Thank you for playing. Nice game."""

    def __init__(self, login, password, app_id, app_code):
        self.login = login
        m = hashlib.md5()
        m.update(password)
        self.password_md5 = m.hexdigest()
        self.app_id = app_id
        self.app_code = app_code
        self.last_eid = 0
        self.events = []
        self.lock = threading.Lock()

    def boardsize(self, size):
        self.size = size

    def time(self, game, move):
        self.timer_game = game
        self.timer_move = move

    def start(self, my_side):
        login = self.send_request(
            'http://www.iggamecenter.com/api_login.php',
            login=self.login,
            password=self.password_md5,
            md5=1).loginResult
        self.uid = login.uid.string
        self.session_id = login.session_id.string
        session = self.send_request(
            'http://www.iggamecenter.com/api_board_create.php',
            uid=self.uid,
            session_id=self.session_id,
            gid=self.HAVANNAH_GID).sessionInfo
        self.server = (
            'http://%s.iggamecenter.com/api_handler.php' % session.server.string)
        self.sid = session.sid.string
        self.cmd('JOIN')
        self.cmd('SETUP',
            boardSize=self.size,
            timerTotal=self.timer_game,
            timerInc=self.timer_move,
            private=0)
        self.refresh_thread = threading.Thread(target=self.refresh)
        self.running = True
        self.refresh_thread.start()
        if my_side > 0:
            self.cmd('PLACE', place=my_side)
            side = my_side
        else:
            side = 0
        stage = 0  # 0 = waiting, 1 = joined, 2 = placed
        while True:
            event = self.event()
            if event['type'] == 'JOIN':
                self.cmd('MSG', message=self.WELCOME_MESSAGE)
            elif event['type'] == 'MSG':
                self.cmd('MSG', message="Sorry, I don't understand, I'm a bot")
            elif event['type'] == 'LEAVE':
                if my_side == 0 and side != 0:  # Let the next person choose the side.
                    side = 0
                    self.cmd('PLACE', place=side)
            elif event['type'] == 'PLACE':
                if event['data'] == '0':  # Still here, but got up.
                    if my_side == 0 and side != 0:  # I should stand up too.
                        side = 0
                        self.cmd('PLACE', place=side)
                else:  # He sat down.
                    if side == 0:  # I need to sit down.
                        side = int(event['data'])
                        self.cmd('PLACE', place=(3-side))
                    # Both sitting, let's start.
#                    self.cmd(
#                        'SETUP',
#                        boardSize=self.size,
#                        timerTotal=self.timer_game,
#                        timerInc=self.timer_move,
#                        private=1)
                    self.cmd('START')
                    if side == 2:
                        self.cmd('MSG', message=self.SWAP_MESSAGE)
                    self.opponent = event['uid']
            elif event['type'] == 'START':
                return side
            elif event['type'] == 'OPTIONS':
                self.cmd('MSG', message=self.OPTIONS_MESSAGE)
                self.cmd(
                    'SETUP',
                    boardSize=self.size,
                    timerTotal=self.timer_game,
                    timerInc=self.timer_move)

            #'NOTICE' ?

            else:
                sys.stderr.write("Unknown event: %s\n" % (event,))

    def play(self, move):
        l = move[0]
        n = move[1:]
        move = l.upper() + n.zfill(2)
        self.cmd('MOVE', move=move)

    def genmove(self):
        while True:
            event = self.event()
            if event['type'] == 'MOVE':
                m = event['data'].strip()
                return m[0].lower() + m[1:].lstrip('0')
            elif event['type'] == 'LEAVE':
                pass
#                if event['uid'] == self.opponent:
#                    return 'resign'
            elif event['type'] == 'END' and event['data'] == 'GIVEUP':
                return 'resign'
            elif event['type'] == 'NOTICE':
                if event['data'].startswith('PHRASE_GIVES_UP'):
                    return 'resign'
            elif event['type'] == 'UNDO' and event['data'] == 'ASK':
                self.cmd('UNDO', type='FORBID')
            elif event['type'] in ('JOIN', 'MSG'):
                pass
            elif event['type'] == 'RESTART':
                self.cmd('MSG', message=self.RESTART_MESSAGE)
            else:
                sys.stderr.write("Unknown event: %s\n" % (event,))

    def close(self):
        self.cmd('MSG', message=self.THANKS_MESSAGE)
        self.cmd('LEAVE')
        self.running = False
        self.refresh_thread.join()

    def send_request(self, url, **kwargs):
        params = {
            'app_id': self.app_id,
            'app_code': self.app_code,
        }
        params.update(kwargs)
        param_str = urllib.urlencode(params)
        print ">", param_str, "\n"
        headers = {'Content-type': 'application/x-www-form-urlencoded'}
        request = urllib2.Request(url, param_str, headers)
        contents = urllib2.urlopen(request).read()
        result = bs4.BeautifulSoup(contents, 'xml')
        if result.errorMessage is not None:
            raise Error(result.errorMessage.string)
        return result

    def cmd(self, cmd, **kwargs):
        with self.lock:
            params = {
                'uid': self.uid,
                'session_id': self.session_id,
                'sid': self.sid,
                'cmd': cmd,
            }
            if self.last_eid > 0:
                params['lasteid'] = self.last_eid
            params.update(kwargs)
            handler = self.send_request(self.server, **params).handlerData
            for event in handler.eventList('event'):
                eid = int(event['eid'])
                uid = event['uid']
                if self.last_eid < eid: # filter out old events
                    self.last_eid = eid
                    if uid != self.uid: # filter out my events
                        self.events.append(event)
                        print "<", event['type'], event['data']
            return handler

    def event(self):
        while True:
            try:
                with self.lock:
                    if len(self.events) > 0:
                        return self.events.pop(0)
                time.sleep(0.5) # check the queue only every half second, otherwise it'd be a busy wait
            except KeyboardInterrupt:
                self.close()
                sys.exit('Interrupted!')

    def refresh(self):
        while self.running:
            self.cmd('REFRESH')
            time.sleep(self.POLL_INTERVAL_SECS)

