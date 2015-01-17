import websocket
import thread
import time
import json

logindata = {
    "channel": {
        "name": "#fraise2"
    },
    "nick": "morbo_terminal",
    "email": "nicolas@noben.org",
    "type": 0
}

messagedata = {
    "channel": {
        "name": "#fraise2"
    },
    "message": "erergs", "type": 3
}


def on_message(ws, message):
    print "got message:", message


def on_error(ws, error):
    print "got error!!!", error


def on_close(ws):
    print "### closed ###"


def on_open(ws):
    def run(*args):
        loginmsg = json.dumps(logindata)
        ws.send(loginmsg)

        #while 1:
        #    t = raw_input()
        time.sleep(3)
        ws.send(messagedata)
        time.sleep(2)


        ws.close()
        print "thread terminating..."

    thread.start_new_thread(run, ())
    # run()


websocket.enableTrace(True)
ws = websocket.WebSocketApp("ws://sharup.com:8080",
                            on_message=on_message,
                            on_error=on_error,
                            on_close=on_close)
ws.on_open = on_open
ws.run_forever()
