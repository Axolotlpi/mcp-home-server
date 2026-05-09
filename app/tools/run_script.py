import os
import subprocess
from pathlib import Path

SCRIPTS_DIR = Path(os.environ.get("SCRIPTS_DIR", "/app/scripts"))
BLACKLIST_PATH = Path(os.environ.get("BLACKLIST_PATH", "/app/blacklist.txt"))


def _load_blacklist() -> set[str]:
    if BLACKLIST_PATH.exists():
        return {line.strip() for line in BLACKLIST_PATH.read_text().splitlines() if line.strip()}
    return set()


def run_script(name: str, args: list[str] | None = None) -> dict:
    blacklist = _load_blacklist()
    if name in blacklist:
        return {"error": f"Script '{name}' is blacklisted"}

    script_path = SCRIPTS_DIR / name
    if not script_path.exists():
        return {"error": f"Script '{name}' not found"}

    if not script_path.is_file():
        return {"error": f"'{name}' is not a file"}

    cmd = [str(script_path)] + (args or [])
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
        )
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {"error": "Script timed out after 60 seconds"}
    except Exception as e:
        return {"error": str(e)}
