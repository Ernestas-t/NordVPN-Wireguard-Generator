import argparse
import getpass
import os
import sys
from textwrap import dedent

import requests

CREDENTIALS_URL = "https://api.nordvpn.com/v1/users/services/credentials"
SERVERS_URL = "https://api.nordvpn.com/v1/servers?limit=16384"


def get_token(cmd_token: str | None) -> str:
    """Get the NordVPN access token from CLI, env var or prompt."""
    if cmd_token:
        return cmd_token.strip()

    env_token = os.getenv("NORD_ACCESS_TOKEN")
    if env_token:
        return env_token.strip()

    print("Enter your NordVPN access token (input hidden):")
    token = getpass.getpass("> ").strip()
    if not token:
        print("No token provided, exiting.", file=sys.stderr)
        sys.exit(1)
    return token


def fetch_nordlynx_private_key(token: str) -> str:
    """Fetch NordLynx private key using the access token."""
    resp = requests.get(CREDENTIALS_URL, auth=("token", token), timeout=15)
    if resp.status_code == 401:
        print("Unauthorized: your access token is invalid or expired.", file=sys.stderr)
        sys.exit(1)

    resp.raise_for_status()
    data = resp.json()
    key = data.get("nordlynx_private_key")
    if not key:
        print(
            "Could not find 'nordlynx_private_key' in credentials response.",
            file=sys.stderr,
        )
        print("Full response was:", file=sys.stderr)
        print(data, file=sys.stderr)
        sys.exit(1)
    return key


def extract_wireguard_servers(
    all_servers: list[dict], country_filter: str | None
) -> list[dict]:
    """Return only servers that support WireGuard, optionally filtered by country name."""
    servers = []
    for s in all_servers:
        # Skip offline servers just in case
        if s.get("status") != "online":
            continue

        locations = s.get("locations") or []
        if not locations:
            continue
        country = locations[0].get("country", {}).get("name", "Unknown")
        city = locations[0].get("country", {}).get("city", {}).get("name", "")

        if country_filter and country_filter.lower() not in country.lower():
            continue

        wg_tech = None
        for t in s.get("technologies", []):
            if t.get("identifier") == "wireguard_udp":
                wg_tech = t
                break
        if not wg_tech:
            continue

        public_key = None
        for md in wg_tech.get("metadata", []):
            if md.get("name") == "public_key":
                public_key = md.get("value")
                break

        if not public_key:
            continue

        servers.append(
            {
                "id": s.get("id"),
                "name": s.get("name"),
                "hostname": s.get("hostname"),
                "ip": s.get("station"),
                "load": s.get("load"),
                "country": country,
                "city": city,
                "public_key": public_key,
            }
        )

    # Nice ordering: country → city → name
    servers.sort(key=lambda x: (x["country"], x["city"], x["name"]))
    return servers


def fetch_servers(country_filter: str | None) -> list[dict]:
    """Fetch all Nord servers and filter to WireGuard-capable ones."""
    resp = requests.get(SERVERS_URL, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return extract_wireguard_servers(data, country_filter)


def choose_server(servers: list[dict], max_to_show: int) -> dict:
    """Show a numbered list and let the user pick a server."""
    if not servers:
        print("No matching WireGuard servers found.", file=sys.stderr)
        sys.exit(1)

    print()
    print(f"Found {len(servers)} WireGuard-capable servers.")
    print("Showing up to", max_to_show)
    print()

    to_show = servers[:max_to_show]
    for idx, s in enumerate(to_show, start=1):
        print(
            f"[{idx:3}] {s['country']:<15} {s['city']:<15} "
            f"{s['name']:<20} {s['hostname']:<22} load={s['load']:>3}%  ip={s['ip']}"
        )

    print()
    while True:
        try:
            choice = int(input(f"Select server [1-{len(to_show)}]: ").strip())
        except ValueError:
            print("Please enter a number.")
            continue

        if 1 <= choice <= len(to_show):
            return to_show[choice - 1]
        print("Out of range, try again.")


def build_wireguard_config(private_key: str, server: dict) -> str:
    """Create a WireGuard client config string for the given server."""
    # For NordLynx, a fixed address like 10.5.0.2/32 works well.
    address = "10.5.0.2/32"
    dns = "103.86.96.100, 103.86.99.100"

    return (
        dedent(
            f"""
        [Interface]
        PrivateKey = {private_key}
        Address    = {address}
        DNS        = {dns}

        [Peer]
        PublicKey           = {server['public_key']}
        AllowedIPs         = 0.0.0.0/0, ::/0
        Endpoint           = {server['ip']}:51820
        PersistentKeepalive = 25
        """
        ).strip()
        + "\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a NordVPN WireGuard config using the Nord API."
    )
    parser.add_argument(
        "-t",
        "--token",
        help="NordVPN access token (otherwise uses NORD_ACCESS_TOKEN env var or prompts).",
    )
    parser.add_argument(
        "-c",
        "--country",
        help="Optional country name filter (e.g. 'Lithuania').",
    )
    parser.add_argument(
        "-m",
        "--max",
        type=int,
        default=50,
        help="Max number of servers to show for selection (default: 50).",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Output .conf file path (default: <hostname>.conf).",
    )

    args = parser.parse_args()

    token = get_token(args.token)
    print("Fetching NordLynx private key...")
    private_key = fetch_nordlynx_private_key(token)

    print("Fetching server list (this may take a few seconds)...")
    servers = fetch_servers(args.country)

    server = choose_server(servers, args.max)

    config_text = build_wireguard_config(private_key, server)
    filename = args.output or f"{server['hostname']}.conf"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(config_text)

    print()
    print(f"Saved WireGuard config to: {filename}")
    print(f"  Server:  {server['name']} ({server['hostname']})")
    print(f"  Country: {server['country']}, {server['city']}")


if __name__ == "__main__":
    main()
