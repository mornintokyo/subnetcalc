#!/usr/bin/env python3
"""
subnet_calc.py - a simple IPv4 subnet calculator for network engineers.

Examples:
    python3 subnet_calc.py 192.168.1.37/26
    python3 subnet_calc.py 10.0.0.0/24 --split 26
    python3 subnet_calc.py              (interactive mode)
"""

import argparse
import ipaddress
import sys

MAX_SUBNETS_TO_PRINT = 256


def describe(net: ipaddress.IPv4Network) -> dict:
    """Collect the main facts about a network."""
    if net.prefixlen <= 30:
        first = net.network_address + 1
        last = net.broadcast_address - 1
        hosts = net.num_addresses - 2
    elif net.prefixlen == 31:  # point-to-point link (RFC 3021)
        first, last = net.network_address, net.broadcast_address
        hosts = 2
    else:  # /32 - a single host
        first = last = net.network_address
        hosts = 1

    return {
        "Network address": net.network_address,
        "Prefix": f"/{net.prefixlen}",
        "Subnet mask": net.netmask,
        "Wildcard mask": net.hostmask,
        "Broadcast address": net.broadcast_address,
        "First usable host": first,
        "Last usable host": last,
        "Usable hosts": hosts,
        "Private network": net.is_private,
    }


def print_network(net: ipaddress.IPv4Network) -> None:
    for name, value in describe(net).items():
        print(f"{name:<20}: {value}")


def split_network(net: ipaddress.IPv4Network, new_prefix: int) -> None:
    """Split a network into smaller subnets with the given prefix length."""
    if not net.prefixlen < new_prefix <= 32:
        sys.exit(f"Error: new prefix must be bigger than /{net.prefixlen} and at most /32.")

    count = 2 ** (new_prefix - net.prefixlen)
    print(f"\n{net} split into /{new_prefix}: {count} subnets\n")

    for i, sub in enumerate(net.subnets(new_prefix=new_prefix), start=1):
        if i > MAX_SUBNETS_TO_PRINT:
            print(f"... and {count - MAX_SUBNETS_TO_PRINT} more")
            break
        info = describe(sub)
        print(f"{i:>3}. {str(sub):<18} hosts: {info['First usable host']} - {info['Last usable host']}")


def parse_network(text: str) -> ipaddress.IPv4Network:
    try:
        # strict=False lets you enter a host address like 192.168.1.37/26
        return ipaddress.IPv4Network(text, strict=False)
    except ValueError as error:
        sys.exit(f"Error: {error}")


def main() -> None:
    parser = argparse.ArgumentParser(description="IPv4 subnet calculator")
    parser.add_argument("network", nargs="?", help="network in CIDR form, e.g. 192.168.1.0/24")
    parser.add_argument("--split", type=int, metavar="PREFIX",
                        help="split the network into subnets with this prefix length")
    args = parser.parse_args()

    text = args.network or input("Enter network (e.g. 192.168.1.0/24): ").strip()
    net = parse_network(text)

    print()
    print_network(net)

    if args.split:
        split_network(net, args.split)


if __name__ == "__main__":
    main()
