#!/usr/bin/env bash
set -euo pipefail
cd /opt/mcp-server
git pull
/opt/mcp-server/venv/bin/pip install -r requirements.txt -q
sudo systemctl restart mcp-server
