#!/usr/bin/env python3
import argparse
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout

from tidio_client import TidioClient

PPK    = "vnhzrugmnkkoli4nyjz67btaifmokdem"
DEVICE = "desktop"
CMV    = "2_0"


def main() -> None:

    parser = argparse.ArgumentParser(description="Tidio chat client")
    parser.add_argument("--ppk", help="PPK authentication key")
    args = parser.parse_args()

    if not args.ppk:
        parser.error("PPK authentication key is required")

    try:
        client = TidioClient(args.ppk, CMV, DEVICE)
        client.connect()
        print("…waiting for server to register visitor…")
        client.ready.wait()                      
        print("connected start chatting")

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
        print("bye")

if __name__ == "__main__":
    main()
