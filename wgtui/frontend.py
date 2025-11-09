import logging
from enum import Enum

from .config import Config
from .util import IP, Input
from .wireguard import Interface, Peer, Wireguard

_logger = logging.getLogger("wg-tui")

_FMT_NETWORKS = "| {id:3} | {iface:15} | {port}"
_FMT_PEERS = "| {id:3} | {nickname:15} | {cidr4:14} | {cidr6}"
_FMT_ATTRS = "| {:20} | {}"


class Frontend:
    class State(Enum):
        NETWORK_SELECT = 0
        NETWORK_CREATE = 1
        NETWORK_MANAGE = 2
        NETWORK_DELETE = 3
        NETWORK_APPLY = 4
        NETWORK_BULK_EXPORT = 5
        PEER_SELECT = 6
        PEER_CREATE = 7
        PEER_MANAGE = 8
        PEER_DELETE = 9
        PEER_EXPORT = 10
        QUIT = 11
        NAT_RECONFIGURE = 12

    def __init__(self):
        self.config = Config()
        self.state = self.State.NETWORK_SELECT
        self.selected_network: Interface | None = None
        self.selected_peer: Peer | None = None

    def run(self):
        while True:
            print(f"\n{"=" * 80}\n")
            match self.state:
                case self.State.NETWORK_SELECT:
                    self.__state_network_select()
                case self.State.NETWORK_CREATE:
                    self.__state_network_create()
                case self.State.NETWORK_MANAGE:
                    self.__state_network_manage()
                case self.State.NETWORK_DELETE:
                    self.__state_network_delete()
                case self.State.NETWORK_APPLY:
                    self.__state_network_apply()
                case self.State.NETWORK_BULK_EXPORT:
                    self.__state_network_bulk_export()
                case self.State.PEER_SELECT:
                    self.__state_peer_select()
                case self.State.PEER_CREATE:
                    self.__state_peer_create()
                case self.State.PEER_MANAGE:
                    self.__state_peer_manage()
                case self.State.PEER_DELETE:
                    self.__state_peer_delete()
                case self.State.PEER_EXPORT:
                    self.__state_peer_export()
                case self.State.NAT_RECONFIGURE:
                    self.__state_nat_reconfigure()
                case self.State.QUIT:
                    print("[i] Exiting.")
                    return
                case _:
                    _logger.error("Frontend: Invalid state.")
                    raise ValueError("Frontend: invalid state.")

    def __state_network_select(self):
        print("[i] Select a network to manage.")
        print(
            _FMT_NETWORKS.format(
                id="ID",
                iface="INTERFACE",
                port="PORT",
            )
        )
        for k, v in self.config.networks.items():
            print(
                _FMT_NETWORKS.format(
                    id=k,
                    iface=v.vpn_iface,
                    port=v.port,
                )
            )
        print("\n[i] Options:")
        print("  (ID): Select network   c: Create network   q: Quit")
        print("-> Choose an option:")
        choice = input()
        match choice:
            case "c":
                self.state = self.State.NETWORK_CREATE
            case "q":
                self.state = self.State.QUIT
            case _:
                try:
                    choice = int(choice)
                    self.selected_network = self.config.networks[choice]
                    self.state = self.State.NETWORK_MANAGE
                except:
                    return

    def __state_network_create(self):
        print("[i] Creating a new network.")
        print("\n1. VPN setup:\n")
        print('-> Enter VPN interface name (ex. "wgchangeme"):')
        iface = Input.get_iface()
        print('-> Enter VPN IPv4 block (ex. "169.254.0.0/16"):')
        cidr4 = Input.get_cidr4()
        print('-> Enter VPN IPv6 block (ex. "2001:db8::/64"):')
        cidr6 = Input.get_cidr6()
        print("\n2. Endpoint setup:\n")
        print('-> Enter port peers will use to connect (ex. "12345"):')
        port = Input.get_int(min_value=0, max_value=65535)
        print(
            '-> Enter hostname/address peers will use to connect (ex. "vpn.example.com"):'
        )
        host = Input.get_str(optional=True)
        id = max(self.config.networks.keys(), default=0) + 1
        network = Interface.create(
            id=id,
            vpn_iface=iface,
            vpn_cidr4=cidr4,
            vpn_cidr6=cidr6,
            port=port,
            host=host,
        )
        self.config.networks[id] = network
        self.config.save_networks()
        self.selected_network = network
        self.state = self.State.NETWORK_MANAGE

    def __state_network_manage(self):
        net = self.selected_network
        assert net is not None
        print(f'[i] Managing network "{net.vpn_iface}"')
        print(_FMT_ATTRS.format("ATTRIBUTE", "VALUE"))
        print(_FMT_ATTRS.format("Public Key", net.public_key))
        print(_FMT_ATTRS.format("VPN IPv4 Pool", net.vpn_cidr4))
        print(_FMT_ATTRS.format("VPN IPv6 Pool", net.vpn_cidr6))
        print(_FMT_ATTRS.format("NAT", "Enabled" if net.nat_iface else "Disabled"))
        if net.nat_iface:
            print(_FMT_ATTRS.format("NAT interface", net.nat_iface))
            print(_FMT_ATTRS.format("NAT dest (v4)", net.nat_cidr4))
            print(_FMT_ATTRS.format("NAT dest (v6)", net.nat_cidr6))
        print("\n[i] Options:")
        print("  m: Manage peers            n: Configure NAT   d: Delete network")
        print("  b: Back to networks list   q: Quit")
        print("-> Choose an option:")
        choice = Input.get_str(optional=True)
        match choice:
            case "m":
                self.state = self.State.PEER_SELECT
            case "n":
                self.state = self.State.NAT_RECONFIGURE
            case "d":
                self.state = self.State.NETWORK_DELETE
            case "b":
                self.state = self.State.NETWORK_SELECT
            case "q":
                self.state = self.State.QUIT

    def __state_network_delete(self):
        net = self.selected_network
        assert net is not None
        print(f'[i] Deleting network "{net.vpn_iface}"')
        print("[i] YOU ARE ABOUT TO DELETE THIS NETWORK AND ALL ITS PEERS!")
        print("    Are you sure?")
        print("-> Enter the network interface name to delete it.")
        print("   Leave blank to cancel.")
        choice = Input.get_str(optional=True)
        if choice == net.vpn_iface:
            del self.config.networks[net.id]
            self.selected_network = None
            self.config.save_networks()
            self.state = self.State.NETWORK_SELECT
        else:
            self.state = self.State.NETWORK_MANAGE

    def __state_network_apply(self):
        _logger.warning("Not implemented")
        self.state = self.State.NETWORK_MANAGE

    def __state_network_bulk_export(self):
        _logger.warning("Not implemented")
        self.state = self.State.NETWORK_MANAGE

    def __state_peer_select(self):
        net = self.selected_network
        assert net is not None
        print("[i] Select a peer to manage.")
        print(
            _FMT_PEERS.format(
                id="ID",
                nickname="NICKNAME",
                cidr4="IPV4 ADDRS",
                cidr6="IPV6 ADDRS",
            )
        )
        for k, v in net.peers.items():
            print(
                _FMT_PEERS.format(
                    id=k,
                    nickname=v.name,
                    cidr4=v.cidr4,
                    cidr6=v.cidr6,
                )
            )
        print("\n[i] Options:")
        print("  (ID): Select peer       c: Create peer")
        print("     b: Back to network   q: Quit")
        print("-> Choose an option:")
        choice = input()
        match choice:
            case "c":
                self.state = self.State.PEER_CREATE
            case "b":
                self.state = self.State.NETWORK_MANAGE
            case "q":
                self.state = self.State.QUIT
            case _:
                try:
                    choice = int(choice)
                    self.selected_peer = net.peers[choice]
                    self.state = self.State.PEER_MANAGE
                except:
                    return

    def __state_peer_create(self):
        net = self.selected_network
        assert net is not None
        print("[i] Creating a new peer.")
        print('-> Enter peer nickname (ex. "laptop"):')
        nickname = Input.get_str()
        print("-> Enter peer IPv4 address  (leave blank to assign automatically):")
        cidr4 = Input.get_cidr4(optional=True)
        print("-> Enter peer IPv6 address (leave blank to assign automatically):")
        cidr6 = Input.get_cidr6(optional=True)
        id = max(net.peers.keys(), default=0) + 1
        if not cidr4:
            cidr4 = IP.nth_addr4(net.vpn_cidr4, id) + "/32"
        if not cidr6:
            cidr6 = IP.nth_addr6(net.vpn_cidr6, id) + "/128"
        peer = Peer.create(
            id=id,
            nickname=nickname,
            cidr4=cidr4,
            cidr6=cidr6,
        )
        net.peers[id] = peer
        self.config.save_networks()
        self.selected_peer = peer
        self.state = self.State.PEER_MANAGE

    def __state_peer_manage(self):
        net = self.selected_network
        assert net is not None
        peer = self.selected_peer
        assert peer is not None
        print(f'[i] Managing peer "{peer.name}" in network "{net.vpn_iface}".')
        print(_FMT_ATTRS.format("ATTRIBUTE", "VALUE"))
        print(_FMT_ATTRS.format("Nickname", peer.name))
        print(_FMT_ATTRS.format("Public Key", peer.public_key))
        print(_FMT_ATTRS.format("IPv4 Addr(s)", peer.cidr4))
        print(_FMT_ATTRS.format("IPv6 Addr(s)", peer.cidr6))
        print("\n[i] Options:")
        print("  e: Export peer config   n: Change nickname   d: Delete peer")
        print("  b: Back to peers list   q: Quit")
        print("-> Choose an option:")
        choice = Input.get_str(optional=True)
        match choice:
            case "e":
                self.state = self.State.PEER_EXPORT
            case "n":
                peer.name = Input.get_str(min_length=1, max_length=20)
                self.config.save_networks()
            case "d":
                self.state = self.State.PEER_DELETE
            case "b":
                self.state = self.State.PEER_SELECT
            case "q":
                self.state = self.State.QUIT

    def __state_peer_delete(self):
        net = self.selected_network
        assert net is not None
        peer = self.selected_peer
        assert peer is not None
        _logger.warning("Not implemented")
        print("-> Are you sure you want to delete this peer? (y/N):")
        choice = Input.get_str(optional=True)
        if choice.lower() == "y":
            del net.peers[peer.id]
            _logger.info("Peer deleted.")
        else:
            _logger.warning("Deletion cancelled, no changes were made.")
        self.state = self.State.PEER_SELECT

    def __state_peer_export(self):
        net = self.selected_network
        assert net is not None
        peer = self.selected_peer
        assert peer is not None
        filename = f"{net.vpn_iface}__{peer.name}.conf"
        with open(filename, "w") as f:
            f.write(
                peer.get_config(
                    vpn_cidr4=net.vpn_cidr4,
                    vpn_cidr6=net.vpn_cidr6,
                    nat_cidr4=net.nat_cidr4,
                    nat_cidr6=net.nat_cidr6,
                    endpoint_public_key=net.public_key,
                    endpoint_host=f"{net.host}:{net.port}",
                )
            )
        _logger.info("Wrote %s", filename)
        self.state = self.State.PEER_MANAGE

    def __state_nat_reconfigure(self):
        net = self.selected_network
        assert net is not None
        print(f'[i] Configuring NAT for network "{net.vpn_iface}"')
        try:
            print('-> (optional) Enter NAT interface name (ex. "eth0"):')
            print("   Leave blank to disable NAT.")
            nat_iface = Input.get_iface(optional=True)
            nat_cidr4: list[str] = []
            nat_cidr6: list[str] = []
            if nat_iface:
                print('-> Enter NAT dest IPv4 block (ex. "0.0.0.0/0"):')
                nat_cidr4.append(Input.get_cidr4())
                while True:
                    print(
                        '-> (optional) Enter another NAT dest IPv4 block (ex. "0.0.0.0/0"):'
                    )
                    print("   Leave blank to continue.")
                    choice = Input.get_cidr4(optional=True)
                    if choice:
                        nat_cidr4.append(choice)
                    else:
                        break
                print('-> Enter NAT dest IPv6 block (ex. "::/0"):')
                nat_cidr6.append(Input.get_cidr6())
                while True:
                    print(
                        '-> (optional) Enter another NAT dest IPv6 block (ex. "::/0"):'
                    )
                    print("   Leave blank to continue.")
                    choice = Input.get_cidr4(optional=True)
                    if choice:
                        nat_cidr6.append(choice)
                    else:
                        break
            net.nat_iface = nat_iface
            net.nat_cidr4 = nat_cidr4
            net.nat_cidr6 = nat_cidr6
            self.config.save_networks()
        except KeyboardInterrupt:
            print("[i] Interrupted.")
            pass
        self.state = self.State.NETWORK_MANAGE
