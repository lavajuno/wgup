import json
import logging
import os

from wgup import defaults
from wgup.wireguard import Interface

_VERSION_SERIAL = 1

_CONFIG_INTERFACES = f"{defaults.CONFIG_DIR}/interfaces.json"

_logger = logging.getLogger("wg-tui")


class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._setup()
        return cls._instance

    def _setup(self):
        self.interfaces: dict[str, Interface] = {}
        os.makedirs(defaults.CONFIG_DIR, exist_ok=True)
        self.load()

    def load(self):
        if not os.path.exists(_CONFIG_INTERFACES):
            return
        with open(_CONFIG_INTERFACES, "rb") as f:
            networks_json = json.loads(f.read())
        if networks_json["version"] != defaults.CONFIG_VERSION:
            raise AssertionError("Incompatible config version.")
        for n in networks_json["interfaces"]:
            interface = Interface.from_json(n)
            self.interfaces[interface.vpn_iface] = interface

    def save(self):
        interfaces_json = {
            "version": _VERSION_SERIAL,
            "interfaces": list(i[1].to_json() for i in sorted(self.interfaces.items())),
        }
        with open(_CONFIG_INTERFACES, "w") as f:
            f.write(json.dumps(interfaces_json, indent=4))
        _logger.info("Saved configuration.")
