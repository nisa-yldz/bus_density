import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app import models  # noqa: F401 (Tabloların create_all sırasında kayıtlı olması için)
from app.database import Base, engine
from app.routers import density, routes

logging.basicConfig(level=logging.INFO)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Bus Density Analysis API", version="1.0.0")

app.include_router(routes.router)
app.include_router(density.router)

BASE_DIR = Path(__file__).resolve().parent  # .../app
STATIC_DIR = BASE_DIR / "static"

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def serve_dashboard():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/routes-ui", include_in_schema=False)
def serve_routes_ui():
    routes_html = STATIC_DIR / "routes.html"
    if routes_html.exists():
        return FileResponse(routes_html)
    return FileResponse(STATIC_DIR / "index.html")