from typing import Optional
from fastapi import Header, HTTPException
import hmac
from .config import API_TOKEN

def require_token(authorization: Optional[str] = Header(default=None)):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer token")

    token = authorization.split(" ", 1)[1].strip()
    
    # Use constant-time comparison to prevent timing attacks
    if not hmac.compare_digest(token.encode('utf-8'), API_TOKEN.encode('utf-8')):
        raise HTTPException(status_code=403, detail="Invalid token")
