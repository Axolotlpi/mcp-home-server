import os
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

bearer = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Security(bearer)):
    expected = os.environ.get("MCP_TOKEN")
    if not expected:
        raise HTTPException(status_code=500, detail="MCP_TOKEN not configured")
    if credentials.credentials != expected:
        raise HTTPException(status_code=401, detail="Invalid token")
    return credentials.credentials
