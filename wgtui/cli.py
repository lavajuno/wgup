import argparse
import logging
from enum import Enum
from typing import Any

from wgtui import Config, Frontend, Interface, Peer, Wireguard
from wgtui.util import Input

_logger = logging.getLogger("wgtui")

_FMT_INTERFACES = "{iface:15} : {host}:{port}"
_FMT_PEERS = "{name:20} : {cidr4:14} : {cidr6}"
_FMT_ATTRS = "{:20} : {}"


class CLI:
    @staticmethod
    def assert_inputs(l: list[Any]):
        for item in l:
            if not item:
                return False
        return True

    class Interface:
        @staticmethod
        def ls(_: argparse.Namespace):
            c = Config()
            if c.interfaces:
                print("[i] Showing all interfaces.")
                for k, v in c.interfaces.items():
                    print(_FMT_INTERFACES.format(iface=k, port=v.port, host=v.host))
            else:
                print("[i] No interfaces have been defined.")
            return 0

        @staticmethod
        def create(args: argparse.Namespace):
            c = Config()
            if args.interactive:
                print("[i] Creating a new VPN interface.")
                print('-> Enter VPN interface name (ex. "wgchangeme"):')
                iface_name = Input.get_iface()
                if c.interfaces.get(iface_name):
                    print(
                        "An interface with this name already exists! Please choose a different name."
                    )
                    return 1
                print('-> Enter VPN IPv4 block (ex. "169.254.0.0/16"):')
                cidr4 = Input.get_cidr4()
                print('-> Enter VPN IPv6 block (ex. "2001:db8::/64"):')
                cidr6 = Input.get_cidr6()
                print('-> Enter port peers will use to connect (ex. "12345"):')
                port = Input.get_int(min_value=1, max_value=65535)
                print(
                    '-> Enter hostname/address peers will use to connect (ex. "vpn.example.com"):'
                )
                host = Input.get_str(optional=True)
            else:
                # sanitize params
                # TODO(lavajuno): write library for command line forms
                iface_name = str(args.name)
                valid, reason = Input.check_iface(iface_name)
                if not valid:
                    print("[!] Interface name is invalid:")
                    print(reason)
                    return 1
                if c.interfaces.get(iface_name):
                    print(
                        "[!] An interface with this name already exists! Please choose a different name."
                    )
                    return 1
                cidr4 = str(args.cidr4)
                valid, reason = Input.check_cidr4(cidr4)
                if not valid:
                    print("[!] IPv4 CIDR block is invalid:")
                    print(reason)
                    return 1
                cidr6 = str(args.cidr6)
                valid, reason = Input.check_cidr6(cidr6)
                if not valid:
                    print("[!] IPv4 CIDR block is invalid:")
                    print(reason)
                    return 1
                port = int(args.port)
                valid, reason = Input.check_int(port, min_value=1, max_value=65535)
                if not valid:
                    print("[!] Port is invalid:")
                    print(reason)
                    return 1
                host = str(args.host)
                if not host:
                    print("[!] Host is required.")
                    return 1
            iface = Interface.create(
                vpn_iface=iface_name,
                vpn_cidr4=cidr4,
                vpn_cidr6=cidr6,
                host=host,
                port=port,
            )
            c.interfaces[iface_name] = iface
            c.save()
            print(f'[i] Created interface "{iface_name}".')
            return 0

        @staticmethod
        def show(args: argparse.Namespace):
            c = Config()
            iface = c.interfaces.get(args.interface)
            if iface is None:
                print(f'[!] Interface "{args.interface}" does not exist.')
                return 1
            print(f'[i] Showing interface "{iface.vpn_iface}".')
            print(_FMT_ATTRS.format("Public Key", iface.public_key))
            print(_FMT_ATTRS.format("VPN IPv4 Pool", iface.vpn_cidr4))
            print(_FMT_ATTRS.format("VPN IPv6 Pool", iface.vpn_cidr6))
            print(
                _FMT_ATTRS.format("NAT", "Enabled" if iface.nat_iface else "Disabled")
            )
            return 0

        @staticmethod
        def edit(args: argparse.Namespace):
            pass

        @staticmethod
        def remove(args: argparse.Namespace):
            c = Config()
            iface = c.interfaces.get(args.interface)
            if iface is None:
                print(f'[!] Interface "{args.interface}" does not exist.')
                return 1
            print("Are you sure you want to remove this interface?")
            print("This operation is irreversible!")
            print("-> (y/N):")
            if input().lower() == "y":
                del c.interfaces[args.interface]
                print(f'Removed interface "{args.interface}".')
                c.save()
            else:
                print("[!] Operation cancelled by user. No action taken.")
                return 1
            return 0

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
            c = Config()
            if not c.interfaces.get(args.interface):
                print(f'No such interface: "{args.interface}".')
                return 1
            interface = c.interfaces[args.interface]
            if args.interactive:
                print(f'[i] Creating a new peer for interface "{args.interface}".')
                print('-> Enter peer nickname (ex. "kitchen_pc"):')
                peer_name = Input.get_peer_name()
                if interface.peers.get(peer_name):
                    print(
                        "[!] A peer with this name already exists! Please choose a different name."
                    )
                    return 1
                print('-> Enter peer IPv4 CIDR block (ex. "169.254.0.5/32"):')
                cidr4 = Input.get_cidr4()
                print('-> Enter peer IPv6 CIDR block (ex. "2001:db8::5/128"):')
                cidr6 = Input.get_cidr6()
            else:
                # sanitize params
                # TODO(lavajuno): write library for command line forms
                peer_name = str(args.name)
                valid, reason = Input.check_peer_name(peer_name)
                if not valid:
                    print("[!] Peer name is invalid:")
                    print(reason)
                    return 1
                if interface.peers.get(peer_name):
                    print(
                        "[!] A peer with this name already exists! Please choose a different name."
                    )
                    return 1
                cidr4 = str(args.cidr4)
                valid, reason = Input.check_cidr4(cidr4)
                if not valid:
                    print("[!] IPv4 CIDR block is invalid:")
                    print(reason)
                    return 1
                cidr6 = str(args.cidr6)
                valid, reason = Input.check_cidr6(cidr6)
                if not valid:
                    print("[!] IPv4 CIDR block is invalid:")
                    print(reason)
                    return 1
            peer = Peer.create(name=peer_name, cidr4=cidr4, cidr6=cidr6)
            interface.peers[peer_name] = peer
            c.save()
            print(f'[i] Created peer "{peer_name}" for interface "{args.interface}".')
            return 0

        @staticmethod
        def ls(args: argparse.Namespace):
            c = Config()
            iface = c.interfaces.get(args.interface)
            if iface is None:
                print(f'[!] Interface "{args.interface}" does not exist.')
                return 1
            if iface.peers:
                print(f'[i] Showing peers for "{iface.vpn_iface}".')
                for k, v in iface.peers.items():
                    print(_FMT_PEERS.format(name=k, cidr4=v.cidr4, cidr6=v.cidr6))
            else:
                print("[i] No peers have been defined for this interface.")
            return 0

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
        root_sub = root.add_subparsers(title="subcommands", required=True)

        # interface.*
        interface = root_sub.add_parser("interface", help="Manage interfaces")
        interface_sub = interface.add_subparsers(title="subcommands", required=True)

        # interface.ls
        interface_ls = interface_sub.add_parser("ls", help="List all interfaces")
        interface_ls.set_defaults(func=CLI.Interface.ls)

        # interface.create
        interface_create = interface_sub.add_parser(
            "create", help="Create an interface"
        )
        interface_create.set_defaults(func=CLI.Interface.create)
        interface_create.add_argument("-i", "--interactive", action="store_true")
        interface_create.add_argument("--name", type=str, default="")
        interface_create.add_argument("--cidr4", type=str, default="")
        interface_create.add_argument("--cidr6", type=str, default="")
        interface_create.add_argument("--host", type=str, default="")
        interface_create.add_argument("--port", type=int, default=0)

        # interface.show
        interface_show = interface_sub.add_parser(
            "show", help="Show details for an interface"
        )
        interface_show.set_defaults(func=CLI.Interface.show)
        interface_show.add_argument("interface", type=str)

        # interface.edit
        interface_edit = interface_sub.add_parser("edit", help="Edit an interface")

        # interface.remove
        interface_remove = interface_sub.add_parser(
            "remove", help="Remove an interface"
        )
        interface_remove.set_defaults(func=CLI.Interface.remove)
        interface_remove.add_argument("interface", type=str)

        # interface.up
        interface_up = interface_sub.add_parser("up", help="Bring an interface up")

        # interface.down
        interface_down = interface_sub.add_parser(
            "down", help="Bring an interface down"
        )

        # interface.enable
        interface_enable = interface_sub.add_parser(
            "enable", help="Enable the systemd target for an interface"
        )

        # interface.disable
        interface_disable = interface_sub.add_parser(
            "disable", help="Disable the systemd target for an interface"
        )

        # interface.restart
        interface_restart = interface_sub.add_parser(
            "restart", help="Restart an interface managed by systemd"
        )

        # interface.reload
        interface_reload = interface_sub.add_parser(
            "reload", help="Reload an interface's config with systemd"
        )

        # peer.*
        peer = root_sub.add_parser("peer", help="Manage peers")
        peer_sub = peer.add_subparsers()

        # peer.ls
        peer_ls = peer_sub.add_parser("ls")
        peer_ls.set_defaults(func=CLI.Peer.ls)
        peer_ls.add_argument("interface", type=str)

        # peer.create
        peer_create = peer_sub.add_parser("create")
        peer_create.set_defaults(func=CLI.Peer.create)
        peer_create.add_argument("interface", type=str)
        peer_create.add_argument("-i", "--interactive", action="store_true")
        peer_create.add_argument("--name", type=str, default="")
        peer_create.add_argument("--cidr4", type=str, default="")
        peer_create.add_argument("--cidr6", type=str, default="")
        # peer.show
        peer_show = peer_sub.add_parser("show")

        # peer.edit
        peer_edit = peer_sub.add_parser("edit")

        # peer.remove
        peer_remove = peer_sub.add_parser("remove")

        # peer.rekey
        peer_rekey = peer_sub.add_parser("rekey")

        return root  # parser
