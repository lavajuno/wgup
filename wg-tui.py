import argparse
import logging
from enum import Enum

from src import Frontend, Network, Peer, Wireguard

_logger = logging.getLogger("wg-tui")
_logger.setLevel(logging.INFO)
_stderr_handler = logging.StreamHandler()
_stderr_handler.setLevel(logging.DEBUG)
_stderr_handler.setFormatter(logging.Formatter("{levelname:<8} : {message}", style="{"))
_logger.addHandler(_stderr_handler)


def main():
    frontend = Frontend()
    frontend.run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
