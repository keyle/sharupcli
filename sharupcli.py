import websocket
import thread
import time
import json
import sys
import os

# ----------
usage = """sharup client 0.4
usage:  sharupcli  <nickname>  <#channel>  <gravatar>
e.g:    sharupcli john #johnfriends john.doe@gravatar.com"""

if len(sys.argv) != 4:
    print usage
    sys.exit()

_, NICK, CHAN, GRAVATAR = sys.argv

LOGIN_DATA = {
    "channel": {
        "name": "{{/chan/}}"
    },
    "nick": "{{/nick/}}",
    "email": "{{/mail/}}",
    "type": 0
}

MESSAGE_DATA = {
    "channel": {
        "name": "{{/chan/}}"
    },
    "message": "{{/msg/}}", "type": 3
}

def impl_message(message_object):
    msg = json.dumps(message_object)
    msg = msg.replace("{{/chan/}}", CHAN)
    msg = msg.replace("{{/nick/}}", NICK)
    msg = msg.replace("{{/mail/}}", GRAVATAR)
    return msg

def on_message(ws, message):
    res = json.loads(message)
    t = res['type']

    if t == 11: # status change
        return

    if t == 5: # channel message
        sys.stdout.write('\r')
        sender = res["clientInfo"]["nick"]
        print "<"+sender+">", res["message"]

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

    thread.start_new_thread(THREADED_run, ())

websocket.enableTrace(False)
ws = websocket.WebSocketApp("ws://sharup.com:8080",
                            on_message=on_message,
                            on_error=on_error,
                            on_close=on_close)
ws.on_open = on_open
ws.run_forever()
