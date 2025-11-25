import json
import subprocess

from wgup import defaults
from wgup.util import IP

CONFIG_FW_VPN_FWD = """
# Firewall: Allow traffic flow within VPN interface
PostUp = iptables -I FORWARD -i {vpn_iface} -o {vpn_iface} -j ACCEPT
PostUp = ip6tables -I FORWARD -i {vpn_iface} -o {vpn_iface} -j ACCEPT

PreDown = iptables -D FORWARD -i {vpn_iface} -o {vpn_iface} -j ACCEPT
PreDown = ip6tables -D FORWARD -i {vpn_iface} -o {vpn_iface} -j ACCEPT
"""

CONFIG_FW_NAT_FLOW = """
# Firewall: Allow traffic flow between VPN interface and NAT interface
PostUp = iptables -I FORWARD -i {vpn_iface} -o {nat_iface} -j ACCEPT
PostUp = ip6tables -I FORWARD -i {vpn_iface} -o {nat_iface} -j ACCEPT
PostUp = iptables -I FORWARD -i {nat_iface} -o {vpn_iface} -j ACCEPT
PostUp = ip6tables -I FORWARD -i {nat_iface} -o {vpn_iface} -j ACCEPT

PreDown = iptables -D FORWARD -i {vpn_iface} -o {nat_iface} -j ACCEPT
PreDown = ip6tables -D FORWARD -i {vpn_iface} -o {nat_iface} -j ACCEPT
PreDown = iptables -D FORWARD -i {nat_iface} -o {vpn_iface} -j ACCEPT
PreDown = ip6tables -D FORWARD -i {nat_iface} -o {vpn_iface} -j ACCEPT
"""

CONFIG_FW_NAT_DEST = """
# Firewall: NAT the following traffic coming from the VPN
PostUp = iptables -t nat -I POSTROUTING -o {nat_iface} -d {nat_cidr4} -j MASQUERADE
PostUp = ip6tables -t nat -I POSTROUTING -o {nat_iface} -d {nat_cidr6} -j MASQUERADE

PreDown = iptables -t nat -D POSTROUTING -o {nat_iface} -d {nat_cidr4} -j MASQUERADE
PreDown = ip6tables -t nat -D POSTROUTING -o {nat_iface} -d {nat_cidr6} -j MASQUERADE
"""

CONFIG_PEER_HEADER = """
# Peer "{name}"
[Interface]
PrivateKey = {private_key}
Address = {cidr4}
Address = {cidr6}
"""

CONFIG_PEER_DNS = """DNS = {dns}
"""

CONFIG_PEER_ENDPOINT = """
[Peer]
PublicKey = {public_key}
PresharedKey = {preshared_key}
AllowedIPs = {cidr4}
AllowedIPs = {cidr6}
Endpoint = {endpoint}
PersistentKeepalive = 10  # Keeps peers behind NATs accessible
"""

CONFIG_INTERFACE_HEADER = """
[Interface]
PrivateKey = {private_key}
Address = {cidr4}
Address = {cidr6}
ListenPort = {port}
"""

CONFIG_INTERFACE_PEER = """
[Peer]
PublicKey = {public_key}
PresharedKey = {preshared_key}
AllowedIPs = {cidr4}
AllowedIPs = {cidr6}
"""


class CommandLine:
    @staticmethod
    def generate_private_key() -> str:
        result = subprocess.run(["wg", "genkey"], stdout=subprocess.PIPE)
        result.check_returncode()
        return result.stdout.decode("utf-8").strip()

    @staticmethod
    def generate_public_key(private_key: str) -> str:
        result = subprocess.run(
            ["wg", "pubkey"], stdout=subprocess.PIPE, input=private_key.encode("utf-8")
        )
        result.check_returncode()
        return result.stdout.decode("utf-8").strip()

    @staticmethod
    def generate_preshared_key() -> str:
        result = subprocess.run(["wg", "genpsk"], stdout=subprocess.PIPE)
        result.check_returncode()
        return result.stdout.decode("utf-8").strip()

    @staticmethod
    def service_up(if_name: str):
        subprocess.run(
            ["sudo", "systemctl", "enable", "wg-quick@{}".format(if_name)],
        ).check_returncode()
        subprocess.run(
            ["sudo", "systemctl", "restart", "wg-quick@{}".format(if_name)],
        ).check_returncode()

    @staticmethod
    def service_down(if_name: str):
        subprocess.run(
            ["sudo", "systemctl", "disable", "wg-quick@{}".format(if_name)],
        ).check_returncode()
        subprocess.run(
            ["sudo", "systemctl", "stop", "wg-quick@{}".format(if_name)],
        ).check_returncode()

    @staticmethod
    def service_reload(if_name: str):
        subprocess.run(
            ["sudo", "systemctl", "reload", "wg-quick@{}".format(if_name)],
        ).check_returncode()


class Peer:
    def __init__(
        self,
        *,
        name: str,
        private_key: str,
        public_key: str,
        preshared_key: str,
        cidr4: str,
        cidr6: str,
    ):
        self.name = name
        self.private_key = private_key
        self.public_key = public_key
        self.preshared_key = preshared_key
        self.cidr4 = cidr4
        self.cidr6 = cidr6

    @classmethod
    def create(cls, *, name: str, cidr4: str, cidr6: str):
        private_key = CommandLine.generate_private_key()
        public_key = CommandLine.generate_public_key(private_key)
        preshared_key = CommandLine.generate_preshared_key()
        return cls(
            name=name,
            private_key=private_key,
            public_key=public_key,
            preshared_key=preshared_key,
            cidr4=cidr4,
            cidr6=cidr6,
        )

    def rekey(self):
        self.private_key = CommandLine.generate_private_key()
        self.public_key = CommandLine.generate_public_key(self.private_key)
        self.preshared_key = CommandLine.generate_preshared_key()

    def __get_peer_header(self) -> str:
        return CONFIG_PEER_HEADER.format(
            private_key=self.private_key,
            cidr4=self.cidr4,
            cidr6=self.cidr6,
        )

    def __get_peer_endpoint(
        self,
        public_key: str,
        vpn_cidr4: str,
        vpn_cidr6: str,
        nat_cidr4: list[str],
        nat_cidr6: list[str],
        endpoint: str,
    ) -> str:
        return CONFIG_PEER_ENDPOINT.format(
            public_key=public_key,
            preshared_key=self.preshared_key,
            cidr4=",".join([vpn_cidr4, *nat_cidr4]),
            cidr6=",".join([vpn_cidr6, *nat_cidr6]),
            endpoint=endpoint,
        )

    def get_config(
        self,
        vpn_cidr4: str,
        vpn_cidr6: str,
        nat_cidr4: list[str],
        nat_cidr6: list[str],
        endpoint_public_key: str,
        endpoint_host: str,
    ):
        return "# Generated by {}\n{}{}".format(
            defaults.PROG,
            self.__get_peer_header(),
            self.__get_peer_endpoint(
                endpoint_public_key,
                vpn_cidr4,
                vpn_cidr6,
                nat_cidr4,
                nat_cidr6,
                endpoint_host,
            ),
        )

    def to_json(self):
        return {
            "name": self.name,
            "private_key": self.private_key,
            "public_key": self.public_key,
            "preshared_key": self.preshared_key,
            "cidr4": self.cidr4,
            "cidr6": self.cidr6,
        }

    @classmethod
    def from_json(cls, data: dict):
        return cls(
            name=data["name"],
            private_key=data["private_key"],
            public_key=data["public_key"],
            preshared_key=data["preshared_key"],
            cidr4=data["cidr4"],
            cidr6=data["cidr6"],
        )


class Interface:
    def __init__(
        self,
        *,
        private_key: str,
        public_key: str,
        vpn_iface: str,
        vpn_cidr4: str,
        vpn_cidr6: str,
        addr4: str,
        addr6: str,
        host: str,
        port: int,
        nat_iface: str | None = None,
        nat_cidr4: list[str] | None = None,
        nat_cidr6: list[str] | None = None,
        dns: list[str] | None = None,
        peers: dict[str, Peer] | None = None,
    ):
        self.private_key = private_key
        self.public_key = public_key
        self.vpn_iface = vpn_iface
        self.vpn_cidr4 = vpn_cidr4
        self.vpn_cidr6 = vpn_cidr6
        self.addr4 = addr4
        self.addr6 = addr6
        self.host = host
        self.port = port
        if nat_iface is None:
            nat_iface = ""
        self.nat_iface = nat_iface
        if nat_cidr4 is None:
            nat_cidr4 = []
        self.nat_cidr4 = nat_cidr4
        if nat_cidr6 is None:
            nat_cidr6 = []
        self.nat_cidr6 = nat_cidr6
        if dns is None:
            dns = []
        self.dns = dns
        if peers is None:
            peers = {}
        self.peers = peers

    @classmethod
    def create(
        cls,
        *,
        vpn_iface: str,
        vpn_cidr4: str,
        vpn_cidr6: str,
        host: str,
        port: int,
    ):
        private_key = CommandLine.generate_private_key()
        public_key = CommandLine.generate_public_key(private_key)
        return cls(
            private_key=private_key,
            public_key=public_key,
            vpn_iface=vpn_iface,
            vpn_cidr4=vpn_cidr4,
            vpn_cidr6=vpn_cidr6,
            addr4=IP.server_addr4(vpn_cidr4),
            addr6=IP.server_addr6(vpn_cidr6),
            host=host,
            port=port,
        )

    def __get_fw_vpn_fwd(self) -> str:
        return CONFIG_FW_VPN_FWD.format(vpn_iface=self.vpn_iface)

    def __get_fw_nat_flow(self) -> str:
        return CONFIG_FW_NAT_FLOW.format(
            vpn_iface=self.vpn_iface, nat_iface=self.nat_iface
        )

    def __get_fw_nat_dest(self) -> str:
        return CONFIG_FW_NAT_DEST.format(
            nat_iface=self.nat_iface,
            nat_cidr4=",".join(self.nat_cidr4),
            nat_cidr6=",".join(self.nat_cidr6),
        )

    def __get_network_header(self) -> str:
        return CONFIG_INTERFACE_HEADER.format(
            private_key=self.private_key,
            cidr4=self.addr4,
            cidr6=self.addr6,
            port=self.port,
        )

    def __get_peers_config(self):
        return "".join(
            CONFIG_INTERFACE_PEER.format(
                public_key=peer.public_key,
                preshared_key=peer.preshared_key,
                cidr4=peer.cidr4,
                cidr6=peer.cidr6,
            )
            for peer in self.peers.values()
        )

    def __get_nat_config(self) -> str:
        if not self.nat_iface:
            return ""
        return "{}{}".format(
            self.__get_fw_nat_flow(),
            self.__get_fw_nat_dest(),
        )

    def get_config(self) -> str:
        return "# Generated by {}\n{}{}{}{}".format(
            defaults.PROG,
            self.__get_network_header(),
            self.__get_fw_vpn_fwd(),
            self.__get_nat_config(),
            self.__get_peers_config(),
        )

    def to_json(self):
        return {
            "private_key": self.private_key,
            "public_key": self.public_key,
            "vpn_iface": self.vpn_iface,
            "vpn_cidr4": self.vpn_cidr4,
            "vpn_cidr6": self.vpn_cidr6,
            "addr4": self.addr4,
            "addr6": self.addr6,
            "host": self.host,
            "port": self.port,
            "nat_iface": self.nat_iface,
            "nat_cidr4": self.nat_cidr4,
            "nat_cidr6": self.nat_cidr6,
            "peers": list(p[1].to_json() for p in sorted(self.peers.items())),
        }

    @classmethod
    def from_json(cls, data: dict):
        peers: dict[str, Peer] = {}
        for p in data["peers"]:
            peer = Peer.from_json(p)
            peers[peer.name] = peer
        return cls(
            private_key=data["private_key"],
            public_key=data["public_key"],
            vpn_iface=data["vpn_iface"],
            vpn_cidr4=data["vpn_cidr4"],
            vpn_cidr6=data["vpn_cidr6"],
            addr4=data["addr4"],
            addr6=data["addr6"],
            host=data["host"],
            port=int(data["port"]),
            nat_iface=data["nat_iface"],
            nat_cidr4=data["nat_cidr4"],
            nat_cidr6=data["nat_cidr6"],
            peers=peers,
        )
