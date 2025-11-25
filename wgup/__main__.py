import logging
import sys

from wgup import cli, defaults
from wgup.util import ExitException

_logger = logging.getLogger(defaults.PROG)
_logger.setLevel(logging.INFO)
_stderr_handler = logging.StreamHandler()
_stderr_handler.setLevel(logging.DEBUG)
_stderr_handler.setFormatter(logging.Formatter("{levelname:<8} : {message}", style="{"))
_logger.addHandler(_stderr_handler)


def main():
    parser = cli.get_parser()
    args = parser.parse_args(sys.argv[1:])
    try:
        status = int(args.func(args))
        return status
    except ExitException as e:
        print(str(e))
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nInterrupted")
