#!/usr/bin/env python3
import argparse
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout

from tidio_client import TidioClient

DEVICE = "desktop"
CMV    = "2_0"

def main() -> None:

    parser = argparse.ArgumentParser(description="Tidio chat client")
    parser.add_argument("--ppk", help="PPK authentication key", required=True)
    parser.add_argument("--url", help="Tidio URL", default="https://socket.tidio.co")
    args = parser.parse_args()

    try:
        with TidioClient(args.ppk, CMV, DEVICE, args.url) as client:
            print("connected start chatting")

            session = PromptSession()                
            
            with patch_stdout():                 
                while True: 
                    try:
                        text = session.prompt("You: ").strip()
                        if text == "exit":
                            break
                        elif text:
                            client.send_message(text)
                    except (EOFError, KeyboardInterrupt):
                        break
    except TimeoutError as e:
        print("Timeout when connecting to Tidio server", e)


if __name__ == "__main__":
    main()
