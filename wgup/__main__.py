import logging
import sys

from wgup.cli import CLI

_logger = logging.getLogger("wgup")
_logger.setLevel(logging.INFO)
_stderr_handler = logging.StreamHandler()
_stderr_handler.setLevel(logging.DEBUG)
_stderr_handler.setFormatter(logging.Formatter("{levelname:<8} : {message}", style="{"))
_logger.addHandler(_stderr_handler)


def main():
    parser = CLI.get_parser()
    args = parser.parse_args(sys.argv[1:])
    if args.func:
        status = int(args.func(args))
        return status
    else:
        print("Please specify an action (--help for help)")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nInterrupted")
