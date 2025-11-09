import argparse
import logging
from enum import Enum

from wgtui import Frontend, Interface, Peer, Wireguard

_logger = logging.getLogger("wgtui")
_logger.setLevel(logging.INFO)
_stderr_handler = logging.StreamHandler()
_stderr_handler.setLevel(logging.DEBUG)
_stderr_handler.setFormatter(logging.Formatter("{levelname:<8} : {message}", style="{"))
_logger.addHandler(_stderr_handler)


class CLI:
    class Interface:
        @staticmethod
        def create(args: argparse.Namespace):
            pass

        @staticmethod
        def ls(args: argparse.Namespace):
            pass

        @staticmethod
        def show(args: argparse.Namespace):
            pass

        @staticmethod
        def edit(args: argparse.Namespace):
            pass

        @staticmethod
        def remove(args: argparse.Namespace):
            pass

        @staticmethod
        def up(args: argparse.Namespace):
            pass

        @staticmethod
        def down(args: argparse.Namespace):
            pass

        @staticmethod
        def enable(args: argparse.Namespace):
            pass

        @staticmethod
        def disable(args: argparse.Namespace):
            pass

        @staticmethod
        def restart(args: argparse.Namespace):
            pass

        @staticmethod
        def reload(args: argparse.Namespace):
            pass

    class Peer:
        @staticmethod
        def create(args: argparse.Namespace):
            pass

        @staticmethod
        def ls(args: argparse.Namespace):
            pass

        @staticmethod
        def show(args: argparse.Namespace):
            pass

        @staticmethod
        def edit(args: argparse.Namespace):
            pass

        @staticmethod
        def remove(args: argparse.Namespace):
            pass

        @staticmethod
        def rekey(args: argparse.Namespace):
            pass


    @staticmethod
    def get_parser():
        # root
        root = argparse.ArgumentParser()
        root_sub = root.add_subparsers(help="Subcommands")

        # interface.*
        interface = root_sub.add_parser("interface", help="Manage WireGuard interfaces")
        interface_sub = interface.add_subparsers()

        # interface.ls
        interface_ls = interface_sub.add_parser("ls")
        interface_ls.set_defaults(func=CLI.Interface.ls)

        # interface.create
        interface_create = interface_sub.add_parser("create")
        interface_create.set_defaults(func=CLI.Interface.create)

        # interface.show
        interface_show = interface_sub.add_parser("show")
        interface_show.set_defaults(func=CLI.Interface.show)

        # interface.edit
        interface_edit = interface_sub.add_parser("edit")

        # interface.remove
        interface_remove = interface_sub.add_parser("remove")

        # interface.up
        interface_up = interface_sub.add_parser("up")

        # interface.down
        interface_down = interface_sub.add_parser("down")

        # interface.enable
        interface_enable = interface_sub.add_parser("enable")

        # interface.disable
        interface_disable = interface_sub.add_parser("disable")

        # interface.restart
        interface_restart = interface_sub.add_parser("restart")

        # interface.reload
        interface_reload = interface_sub.add_parser("reload")

        # peer.*
        peer = root_sub.add_parser("peer", help="Manage peers")
        peer_sub = peer.add_subparsers()

        # peer.ls
        peer_ls = peer_sub.add_parser("ls")

        # peer.create
        peer_create = peer_sub.add_parser("create")

        # peer.show
        peer_show = peer_sub.add_parser("show")

        # peer.edit
        peer_edit = peer_sub.add_parser("edit")

        # peer.remove
        peer_remove = peer_sub.add_parser("remove")

        # peer.rekey
        peer_rekey = peer_sub.add_parser("rekey")

        return root # parser


def main():
    frontend = Frontend()
    frontend.run()


if __name__ == "__main__":
    try:
        import sys
        parser = CLI.get_parser()
        parser.parse_args(sys.argv[1:])
        # main()
    except KeyboardInterrupt:
        print("Interrupted")
