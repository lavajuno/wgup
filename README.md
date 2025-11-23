# wgup

> NOTE: This project is a very early work in progress. Features and
> documentation WILL be missing.

Scriptable shortcuts for managing Wireguard interfaces.
Works with wg-quick to create common setups in seconds, while leaving room for
more advanced configurations.

## Features
- Automated generation/management of keys
- Automated IP address pool selection and assignment
- Generates firewall rules and NATs

## Dependencies

> Note: Make sure packet forwarding on your system is enabled! If you're unsure,
uncomment `net.ipv4.ip_forward=1` and `net.ipv6.conf.all.forwarding=1` in
`/etc/sysctl.conf`.

wg-tui requires Python >= 3.10, which is almost certainly included in your
distro.

**Ubuntu (22.04,24.04) / Debian (11, 12):** `wireguard-tools`

```
sudo apt install wireguard-tools
```

**Fedora (39,40):** `wireguard-tools`
```
sudo dnf install wireguard-tools
```

**Arch Linux:** `wireguard-tools`

```
sudo pacman -S wireguard-tools
```

## Notes

- wgup will never open a port on your firewall. To ensure that clients can
connect, make sure your interfaces' ports are open to incoming UDP traffic.

- wgup is opinionated. Certain things like the keepalive interval and the host
machine's VPN address are defined by wgup. In the future I hope to provide
defaults that work for most setups, while allowing customization.

- wgup is agentless. If you reconfigure an interface or a peer, you will need to
export and apply the configs before they will work.

- wgup **stores peer keys on the host**. My reasoning is that these keys should
only be used to identify the peer to the host. Keys should be unique to each
interface<->peer connection, so if the host machine is compromised, its peers
connections to other machines are not at risk.

## Usage

### Managing interfaces

The following creates a new interface called "wg0". Peers will be configured to
connect to "vpn.example.com:51820".
```bash
wgup iface create wg0 --host vpn.example.com --port 51820
```

You may also specify IP address pools for the interface to use. If you leave
them out, wgup will choose random private pools to reduce the chance of a
conflict.
```bash
wgup iface create wg0 --cidr4 172.31.0.0/24 --cidr6 2001:db8::/64 --host vpn.example.com --port 51820
```

> The machine hosting the interface will always be assigned the first IP address
> in the pool, both for IPv4 and IPv6.

To see the interface you just created:
```bash
wgup iface show wg0
```

To see all interfaces managed by wgup:
```bash
wgup iface ls
```

### Managing peers

To create a new peer called "laptop":

```bash
wgup peer create wg0 laptop
```

As is the case with interfaces, you can also specify an IP address pool for the
peer to use. Usually these are single addresses (/32 for IPv4, /128 for IPv6),
but it is often desirable to route a pool of addresses to a peer in more
advanced setups.

If you do not specify IP addresses, wgup will choose the next available ones.

```bash
wgup peer create wg0 laptop --cidr4 172.31.0.123/32 --cidr6 2001:db8::beef/32
```


###

> 

## Licensing
wgup is Free and Open Source Software, and is released under the BSD 2-Clause license. (See [`LICENSE`](LICENSE))
