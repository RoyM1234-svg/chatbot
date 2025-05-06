#!/usr/bin/env python3
import socketio
import uuid
import platform
from urllib.parse import urlencode
from datetime import datetime, timezone
import time
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout

from tidio_client import TidioClient

PPK    = "vnhzrugmnkkoli4nyjz67btaifmokdem"
DEVICE = "desktop"
CMV    = "2_0"


def main() -> None:

    try:
        client = TidioClient(PPK, CMV, DEVICE)
        client.connect()
        print("…waiting for server to register visitor…")
        client.ready.wait()                      
        print("✅ connected – start chatting")

        session = PromptSession()                
        
        with patch_stdout():                 
            while True: 
                try:
                    text = session.prompt("You: ").strip()
                    if text:
                        client.send_message(text)
                except (EOFError, KeyboardInterrupt):
                    break

    finally:
        client.disconnect()
        print("👋 bye")

if __name__ == "__main__":
    main()
