import logging
from enum import Enum

from src import Config, Network, Peer, Wireguard
from src.util import IP, Input

_logger = logging.getLogger()

_FMT_NETWORKS = "| {id:3} | {iface:15} | {port}"
_FMT_PEERS = "| {id:3} | {nickname:15} | {cidr4:14} | {cidr6}"
_FMT_ATTRS = "| {:20} | {}"


class Frontend:
    class State(Enum):
        SELECT_NETWORK = 0
        CREATE_NETWORK = 1
        MANAGE_NETWORK = 2
        DELETE_NETWORK = 3
        APPLY_NETWORK_CHANGES = 4
        SELECT_PEER = 5
        CREATE_PEER = 6
        MANAGE_PEER = 7
        DELETE_PEER = 8
        EXPORT_PEER = 9
        QUIT = 10

    def __init__(self):
        self.config = Config()
        self.state = self.State.SELECT_NETWORK
        self.selected_network: Network | None = None
        self.selected_peer: Peer | None = None

    def run(self):
        while True:
            print(f"\n{"=" * 80}\n")
            match self.state:
                case self.State.SELECT_NETWORK:
                    self.__state_select_network()
                case self.State.CREATE_NETWORK:
                    self.__state_create_network()
                case self.State.MANAGE_NETWORK:
                    self.__state_manage_network()
                case self.State.DELETE_NETWORK:
                    self.__state_delete_network()
                case self.State.APPLY_NETWORK_CHANGES:
                    self.__state_apply_network_changes()
                case self.State.SELECT_PEER:
                    self.__state_select_peer()
                case self.State.CREATE_PEER:
                    self.__state_create_peer()
                case self.State.MANAGE_PEER:
                    self.__state_manage_peer()
                case self.State.DELETE_PEER:
                    self.__state_delete_peer()
                case self.State.EXPORT_PEER:
                    self.__state_export_peer()
                case self.State.QUIT:
                    return
                case _:
                    _logger.error("Frontend: Invalid state.")
                    raise ValueError("Frontend: invalid state.")

    def __state_select_network(self):
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
        print("[i] Options:")
        print("  (ID): Select network   c: Create network   q: Quit")
        print("-> Choose an option:")
        choice = input()
        match choice:
            case "c":
                self.state = self.State.CREATE_NETWORK
            case "q":
                self.state = self.State.QUIT
            case _:
                try:
                    choice = int(choice)
                    self.selected_network = self.config.networks[choice]
                    self.state = self.State.MANAGE_NETWORK
                except:
                    return

    def __state_create_network(self):
        print("[i] Creating a new network.")
        print("\n1. VPN setup:\n")
        print('-> Enter VPN interface name (ex. "wgchangeme"):')
        iface = Input.get_iface()
        print('-> Enter VPN IPv4 address pool (ex. "169.254.0.0/16"):')
        cidr4 = Input.get_cidr4()
        print('-> Enter VPN IPv6 address pool (ex. "2001:db8::/64"):')
        cidr6 = Input.get_cidr6()
        print("\n2. Endpoint setup:\n")
        print('-> Enter port peers will use to connect (ex. "12345"):')
        port = Input.get_int(min_value=0, max_value=65535)
        print(
            '-> Enter hostname/address peers will use to connect (ex. "vpn.example.com"):'
        )
        host = Input.get_str(optional=True)
        id = max(self.config.networks.keys(), default=0) + 1
        network = Network.create(
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
        self.state = self.State.MANAGE_NETWORK

    def __state_manage_network(self):
        net = self.selected_network
        print(f'[i] Managing network "{net.vpn_iface}"')
        print(_FMT_ATTRS.format("ATTRIBUTE", "VALUE"))
        print(_FMT_ATTRS.format("Public Key", net.public_key))
        print(_FMT_ATTRS.format("VPN IPv4 Pool", net.vpn_cidr4))
        print(_FMT_ATTRS.format("VPN IPv6 Pool", net.vpn_cidr6))
        print("[i] Options:")
        print("  m: Manage peers            n: Configure NAT   d: Delete network")
        print("  b: Back to networks list   q: Quit")
        print("-> Choose an option:")
        choice = Input.get_str(optional=True)
        match choice:
            case "m":
                self.state = self.State.SELECT_PEER
            case "n":
                _logger.warning("Not implemented")
            case "d":
                self.state = self.State.DELETE_NETWORK
            case "b":
                self.state = self.State.SELECT_NETWORK
            case "q":
                self.state = self.State.QUIT

    def __state_delete_network(self):
        _logger.warning("Not implemented")
        self.state = self.State.MANAGE_NETWORK

    def __state_apply_network_changes(self):
        _logger.warning("Not implemented")
        self.state = self.State.MANAGE_NETWORK

    def __state_select_peer(self):
        net = self.selected_network
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
                    nickname=v.nickname,
                    cidr4=v.cidr4,
                    cidr6=v.cidr6,
                )
            )
        print("[i] Options:")
        print("  (ID): Select peer       c: Create peer")
        print("     b: Back to network   q: Quit")
        print("-> Choose an option:")
        choice = input()
        match choice:
            case "c":
                self.state = self.State.CREATE_PEER
            case "b":
                self.state = self.State.MANAGE_NETWORK
            case "q":
                self.state = self.State.QUIT
            case _:
                try:
                    choice = int(choice)
                    self.selected_peer = net.peers[choice]
                    self.state = self.State.MANAGE_PEER
                except:
                    return

        pass

    def __state_create_peer(self):
        print("[i] Creating a new peer.")
        print('-> Enter peer nickname (ex. "laptop"):')
        nickname = Input.get_str()
        print("-> Enter peer IPv4 address  (leave blank to assign automatically):")
        cidr4 = Input.get_cidr4(optional=True)
        print("-> Enter peer IPv6 address (leave blank to assign automatically):")
        cidr6 = Input.get_cidr6(optional=True)
        id = max(self.selected_network.peers.keys(), default=0) + 1
        if not cidr4:
            cidr4 = IP.nth_addr4(self.selected_network.vpn_cidr4, id)
        if not cidr6:
            cidr6 = IP.nth_addr6(self.selected_network.vpn_cidr6, id)
        peer = Peer.create(
            id=id,
            nickname=nickname,
            cidr4=cidr4,
            cidr6=cidr6,
        )
        self.selected_network.peers[id] = peer
        self.config.save_networks()
        self.selected_peer = peer
        self.state = self.State.MANAGE_PEER

    def __state_manage_peer(self):
        net = self.selected_network
        peer = self.selected_peer
        print(f'[i] Managing peer "{peer.nickname}" in network "{net.vpn_iface}".')
        print(_FMT_ATTRS.format("ATTRIBUTE", "VALUE"))
        print(_FMT_ATTRS.format("Nickname", peer.nickname))
        print(_FMT_ATTRS.format("Public Key", peer.public_key))
        print(_FMT_ATTRS.format("IPv4 Addr(s)", peer.cidr4))
        print(_FMT_ATTRS.format("IPv6 Addr(s)", peer.cidr6))
        print("[i] Options:")
        print("  e: Export peer config    n: Change nickname   d: Delete peer")
        print("  b: Back to peers list    q: Quit")
        print("-> Choose an option:")
        choice = Input.get_str(optional=True)
        match choice:
            case "e":
                self.state = self.State.EXPORT_PEER
            case "n":
                _logger.warning("Not implemented")
            case "d":
                self.state = self.State.DELETE_PEER
            case "b":
                self.state = self.State.SELECT_PEER
            case "q":
                self.state = self.State.QUIT

    def __state_delete_peer(self):
        _logger.warning("Not implemented")
        self.state = self.State.SELECT_NETWORK

    def __state_export_peer(self):
        _logger.warning("Not implemented")
        self.state = self.State.SELECT_NETWORK
