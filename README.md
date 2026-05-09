# mcp-home-server

Self-hostable MCP server that gives Claude tools to run shell scripts and read files on a home server. Runs on a Multipass VM, exposed via Cloudflare Tunnel.

## Tools

| Tool | What it does |
|---|---|
| `run_script(name, args[])` | Runs `/opt/mcp-server/scripts/{name}` on the VM |
| `read_file(path)` | Returns file contents (unrestricted path — VM is the sandbox) |
| `update_self()` | `git pull` + `systemctl restart` — picks up new scripts automatically |

---

## VM Deployment

```bash
git clone git@github.com:Axolotlpi/mcp-home-server.git /opt/mcp-server
cp /opt/mcp-server/.env.example /opt/mcp-server/.env
nano /opt/mcp-server/.env          # set MCP_TOKEN to a long random secret
sudo bash /opt/mcp-server/setup.sh
```

Allow the service to restart itself without a password prompt:

```bash
echo 'ubuntu ALL=(ALL) NOPASSWD: /bin/systemctl restart mcp-server' \
  | sudo tee /etc/sudoers.d/mcp-server
```

---

## Cloudflare Tunnel Setup

This exposes `127.0.0.1:8000` on the VM to a public HTTPS URL without opening firewall ports.

### 1. Install cloudflared

```bash
curl -L https://pkg.cloudflare.com/cloudflare-main.gpg \
  | sudo tee /usr/share/keyrings/cloudflare-main.gpg > /dev/null
echo 'deb [signed-by=/usr/share/keyrings/cloudflare-main.gpg] https://pkg.cloudflare.com/cloudflared jammy main' \
  | sudo tee /etc/apt/sources.list.d/cloudflared.list
sudo apt update && sudo apt install cloudflared -y
```

### 2. Authenticate and create a tunnel

```bash
cloudflared tunnel login           # opens browser — pick your domain
cloudflared tunnel create mcp-server
```

Note the tunnel ID printed after creation.

### 3. Find your credentials file path

The credentials file location depends on which user ran `tunnel login`:

```bash
# if you ran as root
ls /root/.cloudflared/

# if you ran as your normal user
ls ~/.cloudflared/
```

You're looking for a file named `<YOUR_TUNNEL_ID>.json`. Use whichever path exists — you'll need it in the next step.

### 4. Create the config file

```bash
sudo mkdir -p /etc/cloudflared
sudo tee /etc/cloudflared/config.yml <<EOF
tunnel: <YOUR_TUNNEL_ID>
credentials-file: /root/.cloudflared/<YOUR_TUNNEL_ID>.json

ingress:
  - hostname: mcp.yourdomain.com
    service: http://127.0.0.1:8000
  - service: http_status:404
EOF
```

Replace `<YOUR_TUNNEL_ID>` and `mcp.yourdomain.com` with your values.

### 5. Route DNS

```bash
cloudflared tunnel route dns mcp-server mcp.yourdomain.com
```

This creates a `CNAME` record in your Cloudflare dashboard pointing to the tunnel.

### 6. Run as a service

```bash
sudo cloudflared service install
sudo systemctl enable --now cloudflared
```

The tunnel will now start on boot. Your server is reachable at `https://mcp.yourdomain.com`.

---

## Adding to Claude

The MCP server speaks SSE. The endpoint is `https://mcp.yourdomain.com/sse`.

### Claude Desktop

Edit `claude_desktop_config.json`:

- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux:** `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "home-server": {
      "url": "https://mcp.yourdomain.com/sse",
      "headers": {
        "Authorization": "Bearer YOUR_MCP_TOKEN"
      }
    }
  }
}
```

Restart Claude Desktop after saving.

### Claude Code (CLI)

```bash
claude mcp add --transport sse home-server https://mcp.yourdomain.com/sse \
  --header "Authorization: Bearer YOUR_MCP_TOKEN"
```

Or add it to `.claude/settings.json` manually:

```json
{
  "mcpServers": {
    "home-server": {
      "type": "sse",
      "url": "https://mcp.yourdomain.com/sse",
      "headers": {
        "Authorization": "Bearer YOUR_MCP_TOKEN"
      }
    }
  }
}
```

---

## Adding New Scripts

1. Add your script to `scripts/` and push to GitHub
2. Tell Claude: *"run update_self"* — it pulls the latest code and restarts
3. Tell Claude: *"run my-script.sh"* — it executes on the VM

The connection will drop briefly during the restart on step 2. That's expected.

To block a script from being callable via the API, add its filename to `blacklist.txt`.
