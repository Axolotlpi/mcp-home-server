# MCP Home Server - Project Plan

## Intent
Build a self-hostable MCP server that gives Claude tools to run shell scripts and read files
on a home server, with the ability to update and restart itself via git. Runs inside a
Multipass VM for security isolation (sudo available inside VM). Deployed via Docker +
systemd inside the VM. Exposed to the internet via Cloudflare Tunnel → Caddy reverse proxy.

## Architecture
- FastAPI MCP server (Python)
- Runs as a systemd service managing a Docker container
- Auth: Bearer token from environment variable
- Scripts directory: any script present is allowed unless blacklisted
- Blacklist: config file (blacklist.txt), one script name per line

## Tools Exposed
- run_script(name, args[]) — runs /scripts/{name} with optional args, returns stdout/stderr
- read_file(path) — returns file contents as text, unrestricted path (VM is sandboxed)
- update_self() — runs git pull on the repo then restarts the systemd service; connection
  will drop briefly, this is expected and acceptable

## Repo Structure
mcp-server/
  app/
    main.py          # FastAPI + MCP tool definitions
    auth.py          # Bearer token middleware
    tools/
      run_script.py
      read_file.py
      update_self.py
  scripts/           # Shell scripts go here
    update_self.sh   # git pull && sudo systemctl restart mcp-server
  blacklist.txt      # One script name per line
  Dockerfile
  docker-compose.yml
  mcp-server.service # systemd unit file for the VM
  .env.example
  PLAN.md
  claude-log.md

## Deployment (done manually after git push)
1. SSH into Multipass VM
2. Clone repo
3. Copy .env.example to .env, fill in token
4. sudo systemctl enable --now mcp-server

## Security Notes
- Bearer token should be treated as a root-equivalent credential
- Scripts directory is the execution boundary (no arbitrary string execution)
- read_file is unrestricted by design (VM is the security boundary)
- update_self.sh is the only script with hardcoded sudo systemctl access

## Out of Scope (for now)
- Zero-downtime deploys
- Binary file transfer
- Multiple auth tokens / token rotation
