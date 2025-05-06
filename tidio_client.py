import socketio
import uuid
import platform
from urllib.parse import urlencode
import threading
from models.tidio_message import TidioMessage


class TidioClient:
    LOCAL_URL = "http://localhost:8000"

    def __init__(self, api_key: str, cmv: str, device: str, tidio_url: str, debug: bool = False):
        self._api_key = api_key
        self._visitor_id = uuid.uuid4().hex
        self._cmv = cmv
        self._device = device
        self._debug = debug
        self._sio = socketio.Client(logger=self._debug, engineio_logger=self._debug)
        qs = urlencode({"ppk": self._api_key, "device": self._device, "cmv": self._cmv})
        self._socket_url = f"{tidio_url}/socket.io/?{qs}"
        self._ready = threading.Event()

        self._register_event_handlers()

    def send_message(self, message: str):
        if not self._ready.is_set():
            print("TidioClient is not registered; wait for the \"connected\" event.")
            return
        
        body = TidioMessage(
            device=self._device,
            message=message,
            message_id=str(uuid.uuid4()),
            project_public_key=self._api_key,
            visitor_id=self._visitor_id,
            url=self.LOCAL_URL,
        )

        self._sio.emit("visitorNewMessage", body.model_dump())

    def __enter__(self):
        
        self._sio.connect(
            self._socket_url,
            socketio_path="/socket.io",
            transports=["websocket"],
            headers={
            "Origin": self.LOCAL_URL,
            "User-Agent": "Python SocketIO client",
            },
            wait_timeout=1
        )
        print("…waiting for server to register visitor…")
        self._ready.wait()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._sio.disconnect()

    def _register_event_handlers(self):
        @self._sio.event
        def connect():            
            payload = {
                "id":                self._visitor_id,
                "originalVisitorId": self._visitor_id,
                "name":              "roy@mail.com",
                "email":             "roy@mail.com",
                "project_public_key": self._api_key,
                "browser":           "Python-socketio",
                "browser_version":   platform.python_version(),
                "lang":              "en-us",
                "url":               self.LOCAL_URL,
                "os_name":           platform.system(),
                "screen_width":      1920,
                "screen_height":     1080,
                "timezone":          "Asia/Jerusalem",
                "mobile":            False,
            }

            def _register_ack(success: bool, *extra_args):
                if success:
                    self._ready.set()
            
            self._sio.emit("visitorRegister", payload, callback=_register_ack)

        @self._sio.on("newMessage")
        def _on_new_message(payload):
            message_txt = payload["data"]["message"]["message"]
            if message_txt:
                print("Server message:", message_txt)
    
        @self._sio.event
        def connect_error(e):
            print("connect_error", e)

        @self._sio.event
        def disconnect(reason):
            if reason == self._sio.reason.CLIENT_DISCONNECT:
                print('the client disconnected')
            elif reason == self._sio.reason.SERVER_DISCONNECT:
                print('the server disconnected the client')
            else:
                print('disconnect reason:', reason)
