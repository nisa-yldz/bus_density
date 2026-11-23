import sqlite3
from contextlib import closing

from fastapi import APIRouter, HTTPException

from app.database import connect_db
from app.schemas_routes import Route, RouteStop, Stop

router = APIRouter(tags=["Routes & Stops"])


@router.get("/routes")
def list_routes():
    with closing(connect_db()) as db:
        rows = db.execute("SELECT id, code, name FROM routes ORDER BY code, id").fetchall()
        return [dict(row) for row in rows]


@router.get("/stops")
def list_stops():
    with closing(connect_db()) as db:
        rows = db.execute("SELECT id, name FROM stops ORDER BY name, id").fetchall()
        return [dict(row) for row in rows]


@router.post("/routes", status_code=201)
def add_route(route: Route):
    code = route.code.strip().upper()
    name = route.name.strip()

    if not code or not name:
        raise HTTPException(status_code=400, detail="Hat kodu ve adı boş bırakılamaz.")

    with closing(connect_db()) as db:
        try:
            cursor = db.execute(
                "INSERT INTO routes (code, name) VALUES (?, ?)",
                (code, name),
            )
            db.commit()
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=409, detail="Bu hat kodu zaten kayıtlı.")

        return {"id": cursor.lastrowid, "code": code, "name": name}


@router.post("/stops", status_code=201)
def add_stop(stop: Stop):
    name = stop.name.strip()

    if not name:
        raise HTTPException(status_code=400, detail="Durak adı boş bırakılamaz.")

    with closing(connect_db()) as db:
        cursor = db.execute(
            "INSERT INTO stops (name) VALUES (?)",
            (name,),
        )
        db.commit()
        return {"id": cursor.lastrowid, "name": name}


@router.post("/routes/{route_id}/stops", status_code=201)
def add_stop_to_route(route_id: int, item: RouteStop):
    with closing(connect_db()) as db:
        route = db.execute(
            "SELECT id FROM routes WHERE id = ?", (route_id,)
        ).fetchone()
        if route is None:
            raise HTTPException(status_code=404, detail="Hat bulunamadı.")

        stop = db.execute(
            "SELECT id FROM stops WHERE id = ?", (item.stop_id,)
        ).fetchone()
        if stop is None:
            raise HTTPException(status_code=404, detail="Durak bulunamadı.")

        try:
            db.execute(
                """
                INSERT INTO route_stops (route_id, stop_id, stop_order)
                VALUES (?, ?, ?)
                """,
                (route_id, item.stop_id, item.stop_order),
            )
            db.commit()
        except sqlite3.IntegrityError:
            raise HTTPException(
                status_code=409,
                detail="Bu hatta bu sıra numarası veya durak zaten dolu.",
            )

        return {
            "route_id": route_id,
            "stop_id": item.stop_id,
            "stop_order": item.stop_order,
        }


@router.get("/routes/{route_id}/stops")
def list_route_stops(route_id: int):
    with closing(connect_db()) as db:
        route = db.execute(
            "SELECT id, code, name FROM routes WHERE id = ?", (route_id,)
        ).fetchone()
        if route is None:
            raise HTTPException(status_code=404, detail="Hat bulunamadı.")

        rows = db.execute(
            """
            SELECT stops.id, stops.name, route_stops.stop_order
            FROM route_stops
            JOIN stops ON stops.id = route_stops.stop_id
            WHERE route_stops.route_id = ?
            ORDER BY route_stops.stop_order ASC
            """,
            (route_id,),
        ).fetchall()

        return {
            "route_id": route["id"],
            "route_code": route["code"],
            "route_name": route["name"],
            "stops": [
                {
                    "stop_id": row["id"],
                    "stop_name": row["name"],
                    "stop_order": row["stop_order"],
                }
                for row in rows
            ],
        }