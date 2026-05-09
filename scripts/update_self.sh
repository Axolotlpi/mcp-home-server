#!/usr/bin/env bash
set -euo pipefail
cd /app
git pull
sudo systemctl restart mcp-server
