import json
import os

from mcp.server.fastmcp import FastMCP
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.tools.read_file import read_file as _read_file
from app.tools.run_script import run_script as _run_script
from app.tools.update_self import update_self as _update_self

mcp = FastMCP("home-server")


@mcp.tool()
def run_script(name: str, args: list[str] | None = None) -> str:
    """Run a shell script from the scripts directory by name."""
    return json.dumps(_run_script(name, args))


@mcp.tool()
def read_file(path: str) -> str:
    """Read a file's contents from the filesystem."""
    return json.dumps(_read_file(path))


@mcp.tool()
def update_self() -> str:
    """Pull the latest code from git and restart the MCP server service."""
    return json.dumps(_update_self())


app = mcp.get_app()


class BearerAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        token = os.environ.get("MCP_TOKEN")
        if not token:
            return Response("MCP_TOKEN not configured", status_code=500)
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer ") or auth[7:] != token:
            return Response("Unauthorized", status_code=401)
        return await call_next(request)


app.add_middleware(BearerAuthMiddleware)
