import sqlite3
from pathlib import Path
from pydantic import BaseModel


class Route(BaseModel):
    code: str
    name: str


class Stop(BaseModel):
    name: str


class RouteStop(BaseModel):
    stop_id: int
    stop_order: int


DB_PATH = Path(__file__).resolve().parent.parent / "bus.db"


def connect_db():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    return db