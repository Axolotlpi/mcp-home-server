from pathlib import Path


def read_file(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        return {"error": f"Path '{path}' does not exist"}
    if not p.is_file():
        return {"error": f"'{path}' is not a file"}
    try:
        return {"content": p.read_text(errors="replace")}
    except Exception as e:
        return {"error": str(e)}
