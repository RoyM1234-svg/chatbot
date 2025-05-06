import socketio
import uuid
import platform
from urllib.parse import urlencode
from datetime import datetime, timezone
import threading


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
        self.ready = threading.Event()

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
        if not self.ready.is_set():
            raise RuntimeError("TidioClient is not registered; wait for the \"connected\" event.")
        
        body = {
            "device": self.device,
            "message": message,
            "messageId": str(uuid.uuid4()),
            "projectPublicKey": self.api_key,
            "visitorId": self.visitor_id,
            "url": "http://localhost:8000/",
            
        }

        def visitor_new_message_ack(*resp):
#            print("visitorNewMessage ACK →", resp)
            pass

        self.sio.emit("visitorNewMessage", body, callback=visitor_new_message_ack)

    def disconnect(self):
        self.sio.disconnect()

    def wait(self):
        self.sio.wait()

    # private methods
    def _register_event_handlers(self):
        @self.sio.event
        def connect():
#            print("🚀 Connected, sid =", self.sio.sid)
            
            payload = {
                "id":                self.visitor_id,
                "originalVisitorId": self.visitor_id,
                "name":              "roy@mail.com",
                "email":             "roy@mail.com",
                "project_public_key": self.api_key,
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

            def register_ack(success: bool, *extra):
                if success:
#                    print("✅ visitorRegister acknowledged")
                    self.ready.set()
                else:
#                    print("❌ visitorRegister failed:", extra)
                    pass
            
            self.sio.emit("visitorRegister", payload, callback=register_ack)
#            print("➡️  visitorRegister sent")

        @self.sio.on("connected")
        def on_connected():
#            print("⬅️  connected sent")
            pass

        @self.sio.on("newMessage")
        def on_new_message(payload):
            message_txt = payload["data"]["message"]["message"]
            if message_txt:
                print("Server message:", message_txt)
            last_id = payload["data"]["id"]
            self.sio.emit("visitorReadMessages", {
                "lastReadMessageId": last_id,
                "lastReadMessageTime": datetime.now(timezone.utc).isoformat() + "Z",
                "visitorId": self.visitor_id,
                "projectPublicKey": self.api_key,
                "device": self.device,
            })
    

        



     
        

