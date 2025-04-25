import ipaddress
import re

_REGEX_CIDR = r".*\/\d{1,2}"
_REGEX_IFNAME = r"[a-z][a-z0-9_]{1,14}"

class Input:
    @staticmethod
    def get_int(min: int | None = None, max: int | None = None):
        while True:
            value = input()
            valid = True
            try:
                value = int(value)
            except ValueError: 
                valid = False
            if min is not None and value < min:
                print(f"Too small! (minimum is {min})")
                valid = False
            if max is not None and value > max:
                print(f"Too small! (minimum is {max})")
                valid = False
            if valid:
                return value
            else:
                print("Please try again:")

    @staticmethod
    def get_cidr4():
        while True:
            value = input()
            valid = True
            if not re.fullmatch(_REGEX_CIDR, value):
                print("Not a valid CIDR block.")
                valid = False
            try:
                ipaddress.IPv4Address(value)
            except ValueError:
                print("Not a valid base address.")
                valid = False
            if valid:
                return value
            else:
                print("Please try again:")

    @staticmethod
    def get_cidr6():
        while True:
            value = input()
            valid = True
            if not re.fullmatch(_REGEX_CIDR, value):
                print("Not a valid CIDR block.")
                valid = False
            try:
                ipaddress.IPv6Address(value)
            except ValueError:
                print("Not a valid base address.")
                valid = False
            if valid:
                return value
            else:
                print("Please try again:")

    @staticmethod
    def get_ifname():
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
