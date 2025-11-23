from fastapi import Header, HTTPException, status

from app.core.config import settings


def require_api_token(x_api_token: str | None = Header(None, alias="X-API-TOKEN")) -> str:
    tokens = settings.telemetry_tokens
    if not x_api_token or x_api_token not in tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API token",
        )
    return x_api_token
