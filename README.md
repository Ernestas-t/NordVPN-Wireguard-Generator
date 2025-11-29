# NordVPN WireGuard Config Generator

A small Python script that talks to the NordVPN API, fetches your **NordLynx (WireGuard)** credentials and server list, and generates a ready-to-use WireGuard `.conf` file.

Perfect for routers (e.g., Asus ExpertWiFi / VPN Fusion) or any other device where you want a plain WireGuard config instead of using the NordVPN app.

## Features

- 🔐 **Automatic credential fetching** - Retrieves your NordLynx private key using a NordVPN access token
- 🌍 **Server filtering** - Fetches all servers, filters to WireGuard-capable ones
- 🎯 **Country filtering** - Optional country-specific server selection (e.g., Lithuania only)
- 📋 **Interactive selection** - Displays servers with country, city, load percentage, and IP address
- ⚡ **Ready-to-use configs** - Generates complete WireGuard configuration files

## Requirements

- **Python 3.10+** (earlier versions might work but aren't tested)
- `requests` package:
  ```bash
  pip install requests
  ```
- **NordVPN account** with access token

## Getting a NordVPN Access Token

1. Log into your [Nord Account dashboard](https://my.nordaccount.com/)
2. Navigate to the **manual configuration / access token** page
3. Generate a new access token (choose an expiry that suits you)
4. Copy and save the token securely

You can provide the token via:

- Environment variable: `NORD_ACCESS_TOKEN`
- Command line flag: `--token`
- Interactive prompt (if neither above is provided)

## Usage

### Basic Usage

```bash
# Token from environment variable or prompt
python3 nord_wg_gen.py

# Explicit token
python3 nord_wg_gen.py --token "YOUR_ACCESS_TOKEN_HERE"
```

### Filter by Country

```bash
python3 nord_wg_gen.py --country Lithuania
```

### Server Selection

The script displays an interactive list:

```
Found 8 WireGuard-capable servers.
Showing up to 50

[  1] Lithuania       Vilnius        Lithuania #21      lt21.nordvpn.com       load=  8%  ip=185.65.50.141
[  2] Lithuania       Vilnius        Lithuania #23      lt23.nordvpn.com       load= 10%  ip=45.82.33.91
...

Select server [1-8]: 2
```

### Custom Output Path

```bash
python3 nord_wg_gen.py --country Lithuania --output nordwg.conf
```

## Generated Configuration

The script creates a complete WireGuard configuration:

```ini
[Interface]
PrivateKey = <your_nordlynx_private_key>
Address    = 10.5.0.2/32
DNS        = 103.86.96.100, 103.86.99.100

[Peer]
PublicKey           = <server_public_key>
AllowedIPs         = 0.0.0.0/0, ::/0
Endpoint           = <server_ip>:51820
PersistentKeepalive = 25
```

### Using the Configuration

- **Linux/macOS**: Use with `wg-quick up <config-file>`
- **Routers**: Upload to devices supporting WireGuard imports (e.g., Asus VPN Fusion)
- **Mobile/Desktop**: Import into WireGuard apps

## CLI Options

```
usage: nord_wg_gen.py [-h] [-t TOKEN] [-c COUNTRY] [-m MAX] [-o OUTPUT]

Generate a NordVPN WireGuard config using the Nord API.

options:
  -h, --help            show this help message and exit
  -t TOKEN, --token TOKEN
                        NordVPN access token (otherwise uses NORD_ACCESS_TOKEN env var or prompts)
  -c COUNTRY, --country COUNTRY
                        Optional country name filter (e.g. "Lithuania")
  -m MAX, --max MAX     Max number of servers to show for selection (default: 50)
  -o OUTPUT, --output OUTPUT
                        Output .conf file path (default: <hostname>.conf)
```

## Security Notes

⚠️ **Important Security Considerations:**

- Your NordVPN access token and NordLynx private key are **highly sensitive**
- Treat generated `.conf` files like passwords:
  - Don't commit them to version control
  - Don't share them publicly
  - Delete old configurations when regenerating
- If you suspect a compromise, immediately revoke the access token in your Nord account

## Installation

Clone this repository:

```bash
git clone https://github.com/yourusername/nordvpn.git
cd nordvpn
pip install requests
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details.

```

This formatted README includes:

1. **Clean structure** with proper headings and sections
2. **GitHub-friendly formatting** with emojis and code blocks
3. **Better organization** of information
4. **Security warnings** prominently displayed
5. **Installation instructions**
6. **Contributing section** for open source projects
7. **Proper code block formatting** with syntax highlighting
8. **Clear usage examples** with expected output

The README is now ready to drop into your GitHub repository!
```
