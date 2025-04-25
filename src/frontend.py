from enum import Enum
import logging

from src import Wireguard, Peer, Network
from src import Config
from src.util import Input

_logger = logging.getLogger()

_FMT_NETWORKS = "| {index:3} | {iface:15} | {port:5} |"

class Frontend:
    class State(Enum):
        SELECT_NETWORK = 0
        CREATE_NETWORK = 1
        MANAGE_NETWORK = 2
        DELETE_NETWORK = 3
        APPLY_NETWORK_CHANGES = 4
        CREATE_PEER = 5
        MANAGE_PEER = 6
        DELETE_PEER = 7
        EXPORT_PEER = 8

    def __init__(self):
        self.config = Config()
        self.state = self.State.SELECT_NETWORK
        self.selected_network: Network | None = None
        self.selected_peer: Peer | None = None

    def run(self):
        while True:
            self.__print_divider()
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
                case self.State.CREATE_PEER:
                    self.__state_create_peer()
                case self.State.MANAGE_PEER:
                    self.__state_manage_peer()
                case self.State.DELETE_PEER:
                    self.__state_delete_peer()
                case self.State.EXPORT_PEER:
                    self.__state_export_peer()
                case _:
                    _logger.error("Frontend: Invalid state.")
                    raise ValueError("Frontend: invalid state.")

    def __state_select_network(self):
        print("Networks:")
        print(
            _FMT_NETWORKS.format(
                index="NO.",
                iface="INTERFACE",
                port="PORT",
            )
        )
        for i in range(len(self.config.networks)):
            net = self.config.networks[i]
            print(
                _FMT_NETWORKS.format(
                    index=i,
                    iface=net.vpn_iface,
                    port=net.port,
                )
            )
        print("Select a network:")
        choice = input()
        match choice:
            case "c":
                self.state = self.State.CREATE_NETWORK
        pass

    def __state_create_network(self):
        print('VPN interface name: (ex. "wg0")')
        ifname = input()
        print('VPN IPv4 address pool (ex. "192.168.254.0/24"):')
        cidr4 = input()
        print('VPN IPv6 address pool (ex. "fd00:cafe:/64"):')
        cidr6 = input()
        pass

    def __state_manage_network(self):
        pass

    def __state_delete_network(self):
        pass

    def __state_apply_network_changes(self):
        pass

    def __state_create_peer(self):
        pass

    def __state_manage_peer(self):
        pass

    def __state_delete_peer(self):
        pass

    def __state_export_peer(self):
        pass

    def __print_divider(self):
        print(f"\n{"=" * 80}\n")