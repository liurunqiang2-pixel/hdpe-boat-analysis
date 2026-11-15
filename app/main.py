from __future__ import annotations

from fastapi import FastAPI
from app.api import api_router
from app.db import init_db

app = FastAPI(title="HDPE Ship Design Workbench", version="0.1.0")
app.include_router(api_router)

@app.on_event("startup")
def startup() -> None:
    init_db()

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
