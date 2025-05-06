#!/usr/bin/env python3
import socketio
import uuid
import platform
from urllib.parse import urlencode
from datetime import datetime, timezone
import time

PPK    = "vnhzrugmnkkoli4nyjz67btaifmokdem"
DEVICE = "desktop"
CMV    = "2_0"
VISITOR_ID = uuid.uuid4().hex

# ---------------------------------------------------------------------------
sio = socketio.Client(logger=False, engineio_logger=True)

@sio.event
def connect():
    print("🚀 Connected, sid =", sio.sid)

    payload = {
        "id":                VISITOR_ID,
        "originalVisitorId": VISITOR_ID,
        "name":              "roy@mail.com",
        "email":             "roy@mail.com",
        "project_public_key": PPK,
        "browser":           "Python-socketio",
        "browser_version":   platform.python_version(),
        "lang":              "en-us",
        "url":               "http://localhost:8000/",
        "os_name":           platform.system(),
        "screen_width":      1920,
        "screen_height":     1080,
        "timezone":          "Asia/Jerusalem",
        "mobile":            False,
    }
    sio.emit("visitorRegister", payload)
    print("➡️  visitorRegister sent")

@sio.on("connected")
def on_connected():
    print("➡️  connected sent")
    

def send_text(msg: str):
    body = {
        "device": DEVICE,
        "message": msg,
        "messageId": str(uuid.uuid4()),
        "projectPublicKey": PPK,
        "visitorId": VISITOR_ID,
        "url": "http://localhost:8000/",
        
    }

    def ack(*resp):
        print("visitorNewMessage ACK →", resp)

    sio.emit("visitorNewMessage", body, callback=ack)


###################### 3) handle inbound traffic ##################
@sio.on("newMessage")
def on_new_message(payload):
    print("Server message:", payload["data"]["message"]["message"])
    last_id = payload["data"]["id"]
    sio.emit("visitorReadMessages", {
        "lastReadMessageId": last_id,
        "lastReadMessageTime": datetime.now(timezone.utc).isoformat() + "Z",
        "visitorId": VISITOR_ID,
        "projectPublicKey": PPK,
        "device": "desktop",
    })



@sio.on("*")
def _(event, *args):
    if args:
        print(f"⬅️  {event}: {args[0] if len(args) == 1 else args}")
    else:
        print(f"⬅️  {event} (no payload)")

if __name__ == "__main__":
    try:
        # --- Build the full URL with its query string -----------------------
        qs = urlencode({"ppk": PPK, "device": DEVICE, "cmv": CMV})
        url = f"https://socket.tidio.co/socket.io/?{qs}"

        sio.connect(
            url,
            socketio_path="/socket.io",
            transports=["websocket"],           # skip polling
            headers={
                "Origin": "http://localhost:8000",
                "User-Agent": "Python SocketIO client",
            },
        )
        time.sleep(3)
        send_text("Hello, how are you?")
        sio.wait()
    finally:
        sio.disconnect()
