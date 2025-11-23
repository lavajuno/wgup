import json
from unittest import TestCase

from wgup import wireguard
from wgup.util import IP


class TestWireguard(TestCase):
    def setUp(self):
        self.iface = wireguard.Interface.create(
            vpn_iface="wg0",
            vpn_cidr4=IP.auto_cidr4(),
            vpn_cidr6=IP.auto_cidr6(),
            host="example.com",
            port=12345,
        )
        self.peer0 = wireguard.Peer.create(
            name="peer0",
            cidr4=IP.next_addr4(self.iface.vpn_cidr4, []),
            cidr6=IP.next_addr6(self.iface.vpn_cidr6, []),
        )

    def test_iface_json(self):
        orig_iface_json = json.dumps(self.iface.to_json())
        loaded_iface = wireguard.Interface.from_json(json.loads(orig_iface_json))
        loaded_iface_json = json.dumps(loaded_iface.to_json())
        self.assertEqual(orig_iface_json, loaded_iface_json)
