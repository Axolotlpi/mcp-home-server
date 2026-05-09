# Claude Development Log

## 2026-05-08 — Initial scaffold

Implemented the full project structure from PLAN.md:
- FastAPI + MCP server with Bearer auth
- `run_script`, `read_file`, `update_self` tools
- systemd unit runs uvicorn directly in a venv (no Docker)
- `setup.sh` for one-time VM deployment
- Shell script for self-update (`scripts/update_self.sh`)

Dropped Docker: the VM is already the security boundary, and running
inside a container would have prevented scripts from reaching host
systemd/processes.
