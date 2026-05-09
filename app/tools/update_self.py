import os
import subprocess
from pathlib import Path


def update_self() -> dict:
    repo_dir = Path(os.environ.get("REPO_DIR", "/app"))

    pull = subprocess.run(
        ["git", "pull"],
        cwd=str(repo_dir),
        capture_output=True,
        text=True,
        timeout=60,
    )
    if pull.returncode != 0:
        return {
            "stdout": pull.stdout,
            "stderr": pull.stderr,
            "error": "git pull failed",
        }

    # Fire-and-forget — the service restart will kill this container.
    subprocess.Popen(
        ["sudo", "systemctl", "restart", "mcp-server"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return {
        "stdout": pull.stdout,
        "stderr": pull.stderr,
        "returncode": pull.returncode,
        "note": "systemctl restart dispatched — connection will drop briefly",
    }
