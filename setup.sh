#!/usr/bin/env bash
# Run once on the VM after cloning the repo to /opt/mcp-server.
set -euo pipefail

REPO=/opt/mcp-server

python3 -m venv "$REPO/venv"
"$REPO/venv/bin/pip" install -r "$REPO/requirements.txt" -q

cp "$REPO/mcp-server.service" /etc/systemd/system/mcp-server.service
systemctl daemon-reload
systemctl enable --now mcp-server

echo "Done. Check status with: systemctl status mcp-server"
