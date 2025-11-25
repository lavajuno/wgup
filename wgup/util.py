import ipaddress
import random
import re
import string

_REGEX_IFNAME = r"[a-zA-Z][a-zA-Z0-9_]{1,14}"
_REGEX_NICKNAME = r"[a-zA-Z][a-zA-Z0-9_]{1,20}"


class ExitException(Exception):
    pass


class ArgsException(ExitException):
    pass


class ConfigVersionException(ExitException):
    pass


class InterfaceNotFoundException(ExitException):
    pass


class PeerNotFoundException(ExitException):
    pass


class Input:
    @staticmethod
    def check_int(
        value: str | int, min_value: int | None = None, max_value: int | None = None
    ):
        try:
            v = int(value)
            if min_value is not None and v < min_value:
                return False, f"Too small! (minimum is {min_value})"
            if max_value is not None and v > max_value:
                return False, f"Too large! (maximum is {max_value})"
        except ValueError:
            return False, "Value is not an integer."
        return True, ""

    @staticmethod
    def check_cidr4(value: str, optional: bool = False):
        if value:
            try:
                ipaddress.IPv4Network(value)
            except ValueError:
                return False, "Not a valid IPv4 CIDR block."
        else:
            if not optional:
                return False, "Value is required."
        return True, ""

    @staticmethod
    def check_cidr6(value: str, optional: bool = False):
        if value:
            try:
                ipaddress.IPv6Network(value)
            except ValueError:
                return False, "Not a valid IPv6 CIDR block."
        else:
            if not optional:
                return False, "Value is required."
        return True, ""

    @staticmethod
    def check_iface(value: str, optional: bool = False):
        if value:
            if not re.fullmatch(_REGEX_IFNAME, value):
                return False, "Not a valid interface name."
        else:
            if not optional:
                return False, "Value is required."
        return True, ""

    @staticmethod
    def check_peer_name(value: str, optional: bool = False):
        if value:
            if not re.fullmatch(_REGEX_NICKNAME, value):
                return (
                    False,
                    f"Not in {_REGEX_NICKNAME}",
                )  # TODO improve explanation / open up nickname regex
        else:
            if not optional:
                return False, "Value is required."
        return True, ""


class IP:
    @staticmethod
    def server_addr4(cidr4: str):
        mask = cidr4.split("/", 2)[1]
        return str(ipaddress.IPv4Network(cidr4)[1]) + f"/{mask}"

    @staticmethod
    def next_addr4(interface_cidr4: str, peers_cidr4: list[str]):
        network = ipaddress.IPv4Network(interface_cidr4)
        pools = [network]
        exclusions: list[ipaddress.IPv4Network] = [
            ipaddress.IPv4Network(network[0]),
            ipaddress.IPv4Network(network[1]),
        ]
        exclusions.extend(
            ipaddress.IPv4Network(peer_cidr4) for peer_cidr4 in peers_cidr4
        )
        for exclusion in exclusions:
            next_pools: list[ipaddress.IPv4Network] = []
            for pool in pools:
                try:
                    next_pools.extend(pool.address_exclude(exclusion))
                except ValueError:
                    # peer pool not in interface pool, skip it
                    next_pools.append(pool)
            pools = next_pools
        assert pools
        return f"{str(sorted(pools)[0][0])}/32"

    @staticmethod
    def auto_cidr4():
        """
        Returns a random /24 of private IPv4 addresses.
        Pool is chosen from 192.168.0.0/16, excluding 192.168.0.* to 192.168.10.*.
        These pools are excluded because they are commonly used for home
        networks and will likely conflict with the created VPN.
        """
        return f"192.168.{random.randint(11, 254)}.0/24"

    @staticmethod
    def server_addr6(cidr6: str):
        mask = cidr6.split("/", 2)[1]
        return str(ipaddress.IPv6Network(cidr6)[1]) + f"/{mask}"

    @staticmethod
    def next_addr6(interface_cidr6: str, peers_cidr6: list[str]):
        network = ipaddress.IPv6Network(interface_cidr6)
        pools = [network]
        exclusions: list[ipaddress.IPv6Network] = [
            ipaddress.IPv6Network(network[0]),
            ipaddress.IPv6Network(network[1]),
        ]
        exclusions.extend(
            ipaddress.IPv6Network(peer_cidr6) for peer_cidr6 in peers_cidr6
        )
        for exclusion in exclusions:
            next_pools: list[ipaddress.IPv6Network] = []
            for pool in pools:
                try:
                    next_pools.extend(pool.address_exclude(exclusion))
                except ValueError:
                    # peer pool not in interface pool, skip it
                    next_pools.append(pool)
            pools = next_pools
        assert pools
        return f"{str(sorted(pools)[0][0])}/128"

    @staticmethod
    def auto_cidr6():
        """
        Returns a random /64 of private IPv6 addresses.
        """
        rh = lambda x: "".join(
            random.choice(string.hexdigits) for i in range(x)
        ).lower()
        return f"fd{rh(2)}:{rh(4)}:{rh(4)}::/64"
