from fastapi import FastAPI

from app.api.routes import bins, greens, lamps
from app.core.config import settings

app = FastAPI(title=settings.app_name)

app.include_router(greens.router, prefix="/api/v1")
app.include_router(lamps.router, prefix="/api/v1")
app.include_router(bins.router, prefix="/api/v1")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
