import argparse


parser = argparse.ArgumentParser()

subparsers = parser.add_subparsers()

a = subparsers.add_parser("b")

def test(t: str):
    print("test")

a.add_argument("-t")
a.set_defaults(func=test)

print(parser.parse_args())

class CLI:
    class Network:
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
        root_sub = root.add_subparsers()

        # network.*
        network = root_sub.add_parser("network")
        network_sub = network.add_subparsers()

        # network.ls
        network_ls = network_sub.add_parser("ls")
        network_ls.set_defaults(func=CLI.Network.create)

        # network.create
        network_create = network_sub.add_parser("create")

        # network.show
        network_show = network_sub.add_parser("show")

        # network.edit
        network_edit = network_sub.add_parser("edit")

        # network.remove
        network_remove = network_sub.add_parser("remove")

        # peer.*
        peer = root_sub.add_parser("peer")
        peer_sub = peer.add_subparsers()

        # peer.ls
        peer_ls = peer_sub.add_parser("ls")

        # peer.create
        peer_create = peer_sub.add_parser("ls")

        # peer.show
        peer_show = peer_sub.add_parser("ls")

        # peer.edit
        peer_edit = peer_sub.add_parser("ls")

        # peer.remove
        peer_remove = peer_sub.add_parser("ls")

        # peer.rekey
        peer_rekey = peer_sub.add_parser("ls")
