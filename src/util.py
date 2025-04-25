import ipaddress
import re

_REGEX_IFNAME = r"[a-z][a-z0-9_]{1,14}"


class Input:
    @staticmethod
    def get_int(min_value: int | None = None, max_value: int | None = None):
        while True:
            value = input()
            valid = True
            try:
                value = int(value)
            except ValueError:
                valid = False
            if min_value is not None and value < min_value:
                print(f"Too small! (minimum is {min_value})")
                valid = False
            if max_value is not None and value > max_value:
                print(f"Too small! (minimum is {max_value})")
                valid = False
            if valid:
                return value
            else:
                print("Please try again:")

    @staticmethod
    def get_cidr4(optional: bool = False):
        while True:
            value = input()
            valid = True
            if value:
                try:
                    ipaddress.IPv4Network(value)
                except ValueError:
                    print("Not a valid IPv4 CIDR block.")
                    valid = False
            else:
                if not optional:
                    print("Value is required.")
                    valid = False
            if valid:
                return value
            else:
                print("Please try again:")

    @staticmethod
    def get_cidr6(optional: bool = False):
        while True:
            value = input()
            valid = True
            if value:
                try:
                    ipaddress.IPv6Network(value)
                except ValueError:
                    print("Not a valid IPv6 CIDR block.")
                    valid = False
            else:
                if not optional:
                    print("Value is required.")
                    valid = False
            if valid:
                return value
            else:
                print("Please try again:")

    @staticmethod
    def get_iface():
        while True:
            value = input()
            valid = True
            if not re.fullmatch(_REGEX_IFNAME, value):
                print("Not a valid interface name.")
                valid = False
            if valid:
                return value
            else:
                print("Please try again:")

    @staticmethod
    def get_str(optional: bool = False):
        while True:
            value = input()
            valid = True
            if not value and not optional:
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
