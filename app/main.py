from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.api import api_router
from app.config import settings
from app.db import init_db
from app.services.workbench import seed_materials
from app.db import SessionLocal

app = FastAPI(title=settings.app_name, version="0.3.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router)


@app.on_event("startup")
def startup() -> None:
    init_db()
    db = SessionLocal()
    try:
        seed_materials(db)
    finally:
        db.close()


@app.get("/")
def index() -> FileResponse:
    return FileResponse(Path("app/static/index.html"))


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
