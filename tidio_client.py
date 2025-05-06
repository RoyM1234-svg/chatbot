import socketio
import uuid
import platform
from urllib.parse import urlencode
from datetime import datetime, timezone


class TidioClient:
    def __init__(self, api_key: str, cmv: str, device: str, debug: bool = False):
        self.api_key = api_key
        self.visitor_id = uuid.uuid4().hex
        self.cmv = cmv
        self.device = device
        self.debug = debug
        self.sio = socketio.Client(logger=self.debug, engineio_logger=self.debug)
        qs = urlencode({"ppk": self.api_key, "device": self.device, "cmv": self.cmv})
        self.socket_url = f"https://socket.tidio.co/socket.io/?{qs}"

        self._register_event_handlers()

    def connect(self):
        self.sio.connect(
            self.socket_url,
            socketio_path="/socket.io",
            transports=["websocket"],
            headers={
                "Origin": "http://localhost:8000",
                "User-Agent": "Python SocketIO client",
            },
        )

    def send_message(self, message: str):
        body = {
            "device": self.device,
            "message": message,
            "messageId": str(uuid.uuid4()),
            "projectPublicKey": self.api_key,
            "visitorId": self.visitor_id,
            "url": "http://localhost:8000/",
            
        }

        def ack(*resp):
            print("visitorNewMessage ACK →", resp)

        self.sio.emit("visitorNewMessage", body, callback=ack)

    def disconnect(self):
        self.sio.disconnect()

    def wait(self):
        self.sio.wait()

    # private methods
    def _register_event_handlers(self):
        @self.sio.event
        def connect():
            print("🚀 Connected, sid =", self.sio.sid)

        @self.sio.on("connected")
        def on_connected():
            print("➡️  connected sent")

        @self.sio.on("newMessage")
        def on_new_message(payload):
            print("Server message:", payload["data"]["message"]["message"])
            last_id = payload["data"]["id"]
            self.sio.emit("visitorReadMessages", {
                "lastReadMessageId": last_id,
                "lastReadMessageTime": datetime.now(timezone.utc).isoformat() + "Z",
                "visitorId": self.visitor_id,
                "projectPublicKey": self.api_key,
                "device": self.device,
            })

        @self.sio.on("*")
        def _(event, *args):
            if self.debug:
                if args:
                    print(f"⬅️  {event}: {args[0] if len(args) == 1 else args}")
                else:
                    print(f"⬅️  {event}")
    

        



     
        

