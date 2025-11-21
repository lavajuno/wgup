import ipaddress
import re

_REGEX_IFNAME = r"[a-z][a-z0-9_]{1,14}"
_REGEX_NICKNAME = r"[a-z][a-z0-9_ ]{1,20}"


class Input:
    @classmethod
    def get_int(cls, min_value: int | None = None, max_value: int | None = None):
        while True:
            value = input()
            valid, reason = cls.check_int(
                value, min_value=min_value, max_value=max_value
            )
            if valid:
                return int(value)
            else:
                print(reason)
                print("Please try again:")

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

    @classmethod
    def get_cidr4(cls, optional: bool = False):
        while True:
            value = input()
            valid, reason = cls.check_cidr4(value, optional=optional)
            if valid:
                return value
            else:
                print(reason)
                print("Please try again:")

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

    @classmethod
    def get_cidr6(cls, optional: bool = False):
        while True:
            value = input()
            valid, reason = cls.check_cidr6(value, optional=optional)
            if valid:
                return value
            else:
                print(reason)
                print("Please try again:")

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

    @classmethod
    def get_iface(cls, optional: bool = False):
        while True:
            value = input()
            valid, reason = cls.check_iface(value, optional=optional)
            if valid:
                return value
            else:
                print(reason)
                print("Please try again:")

    @staticmethod
    def check_iface(value: str, optional: bool = False):
        if value:
            if not re.fullmatch(_REGEX_IFNAME, value):
                return False, "Not a valid interface name."
        else:
            if not optional:
                return False, "Value is required."
        return True, ""

    @classmethod
    def get_peer_name(cls, optional: bool = False):
        while True:
            value = input()
            valid, reason = cls.check_peer_name(value, optional=optional)
            if valid:
                return value
            else:
                print(reason)
                print("Please try again:")

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

    @staticmethod
    def get_str(
        optional: bool = False,
        min_length: int | None = None,
        max_length: int | None = None,
    ):
        while True:
            value = input()
            valid = True
            if value:
                if min_length is not None and len(value) < min_length:
                    print(f"Too short (minimum length is {min_length}).")
                if max_length is not None and len(value) > max_length:
                    print(f"Too long (maximum length is {max_length}).")
            else:
                if not optional:
                    print("Value is required.")
                    valid = False
            if valid:
                return value
            else:
                print("Please try again:")


class IP:
    @staticmethod
    def nth_addr4(cidr4: str, index: int):
        return str(ipaddress.IPv4Network(cidr4)[index])

    @staticmethod
    def nth_addr6(cidr6: str, index: int):
        return str(ipaddress.IPv6Network(cidr6)[index])
