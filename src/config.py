import json
import os

from src import Network

_CONFIG_DIR = f"{os.getcwd()}/conf.d"

_CONFIG_NETWORKS = f"{_CONFIG_DIR}/networks.json"


class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._setup()
        return cls._instance
    
    def _setup(self):
        self.networks: list[Network] = []
        os.makedirs(_CONFIG_DIR, exist_ok=True)
        self.load_networks()

    def load_networks(self):
        if not os.path.exists(_CONFIG_NETWORKS):
            return
        with open(_CONFIG_NETWORKS, "rb") as f:
            networks_json = json.loads(f.read())
        self.networks = list(Network.from_json(n) for n in networks_json["networks"])

    def save_networks(self):
        networks_json = {
            "networks": list(n.to_json() for n in self.networks),
        }
        with open(_CONFIG_NETWORKS, "w") as f:
            f.write(json.dumps(networks_json, indent=4))
