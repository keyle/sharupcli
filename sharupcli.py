import websocket # `pip install websocket-client`
import thread
import time
import json
import sys
import os
import logging
logging.basicConfig()


# ----------
usage = """sharup client 0.4
usage:  sharupcli  <nickname>  <channel>  <gravatar>
e.g:    sharupcli john johnfriends john.doe@gravatar.com"""

if len(sys.argv) != 4:
    print usage
    sys.exit()

_, NICK, CHAN, GRAVATAR = sys.argv

LOGIN_DATA = {
    "channel": {
        "name": "#{{/chan/}}"
    },
    "nick": "{{/nick/}}",
    "email": "{{/mail/}}",
    "type": 0
}

MESSAGE_DATA = {
    "message": "{{/msg/}}", 
    "type": 3
}

STATUS_CHANGE_DATA = {
    "newStatus": 4,
    "type": 10
}

def impl_message(message_object):
    msg = json.dumps(message_object)
    msg = msg.replace("{{/chan/}}", CHAN)
    msg = msg.replace("{{/nick/}}", NICK)
    msg = msg.replace("{{/mail/}}", GRAVATAR)
    return msg

def on_message(ws, message):
    msg = json.loads(message)
    t = msg['type']

    if t == 1:
        print "-- you have signed in #" + CHAN
        return

    if t == 11: # status change
        return

    if t == 8 or t == 9: # user joined (8) / parted (9)
        present = "-- " + msg['clientInfo']['nick']
        if t == 8:
            present += " has joined"
        if t == 9:
            present += " has left"
        present += " \t-- present users: "
        for p in msg['allClients']:
            present += p['nick'] + ", "
        print present

    if t == 5: # channel message
        sys.stdout.write('\r')
        sender = msg["clientInfo"]["nick"]
        print "<"+sender+">", msg["message"]

def on_error(ws, error):
    print "got error!!!", error

def on_close(ws):
    print "### closed ###"

def on_open(ws):
    print "connected!"
    print NICK, "is on", CHAN

    def THREADED_run(*args):
        loginmsg = impl_message(LOGIN_DATA)
        ws.send(loginmsg)

        while 1:
            try:
                t = raw_input()
            except Exception, e:
                print e
                break

            message_msg = impl_message(MESSAGE_DATA)
            message_msg = message_msg.replace("{{/msg/}}", t)

            try: 
                ws.send(message_msg)
            except Exception, e: 
                break

        try: ws.close()
        finally: os._exit(1)

    def THREADED_pinger(*args):
        # ping to not timeout
        while 1:
            pingmsg = impl_message(STATUS_CHANGE_DATA)
            ws.send(pingmsg)
            time.sleep(121)

    thread.start_new_thread(THREADED_run, ())
    thread.start_new_thread(THREADED_pinger, ())

websocket.enableTrace(False)
ws = websocket.WebSocketApp("ws://sharup.com:8080",
                            on_message=on_message,
                            on_error=on_error,
                            on_close=on_close)
ws.on_open = on_open
ws.run_forever()
