import argparse
from enum import Enum
import logging

from src import Wireguard, Peer, Network, Frontend

_logger = logging.getLogger()
_logger.setLevel(logging.INFO)
_stderr_handler = logging.StreamHandler()
_stderr_handler.setLevel(logging.DEBUG)
_stderr_handler.setFormatter(
    logging.Formatter("{asctime} {levelname:<8} : {message}", style="{")
)
_logger.addHandler(_stderr_handler)

def main():
    frontend = Frontend()
    frontend.run()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")