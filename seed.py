from datetime import datetime
from app import models
from app.database import Base, SessionLocal, engine

Base.metadata.create_all(bind=engine)
db = SessionLocal()

if not db.query(models.Route).first():
    r1 = models.Route(code="500T", name="Tuzla - Cevizlibağ")
    r2 = models.Route(code="15F", name="Beykoz - Kadıköy")
    r3 = models.Route(code="34BZ", name="Beylikdüzü - Zincirlikuyu")
    db.add_all([r1, r2, r3])
    db.commit()

    s1 = models.Stop(name="Tuzla Köprüsü")
    s2 = models.Stop(name="Kartal Metro")
    s3 = models.Stop(name="Kadıköy Rıhtım")
    s4 = models.Stop(name="Zincirlikuyu Metrobüs")
    db.add_all([s1, s2, s3, s4])
    db.commit()

    db.add_all([
        models.RouteStop(route_id=r1.id, stop_id=s1.id, stop_order=1),
        models.RouteStop(route_id=r1.id, stop_id=s2.id, stop_order=2),
        models.RouteStop(route_id=r2.id, stop_id=s2.id, stop_order=1),
        models.RouteStop(route_id=r2.id, stop_id=s3.id, stop_order=2),
        models.RouteStop(route_id=r3.id, stop_id=s4.id, stop_order=1),
    ])
    db.commit()

    today_str = datetime.now().strftime("%Y-%m-%d")
    db.add_all([
        models.PassengerCount(
            route_id=r1.id,
            stop_id=s1.id,
            passenger_count=48,
            recorded_at=datetime.fromisoformat(f"{today_str}T08:15:00"),
        ),
        models.PassengerCount(
            route_id=r1.id,
            stop_id=s2.id,
            passenger_count=72,
            recorded_at=datetime.fromisoformat(f"{today_str}T08:45:00"),
        ),
        models.PassengerCount(
            route_id=r1.id,
            stop_id=s2.id,
            passenger_count=60,
            recorded_at=datetime.fromisoformat(f"{today_str}T18:10:00"),
        ),
        models.PassengerCount(
            route_id=r2.id,
            stop_id=s3.id,
            passenger_count=35,
            recorded_at=datetime.fromisoformat(f"{today_str}T09:05:00"),
        ),
        models.PassengerCount(
            route_id=r3.id,
            stop_id=s4.id,
            passenger_count=95,
            recorded_at=datetime.fromisoformat(f"{today_str}T17:40:00"),
        ),
    ])
    db.commit()
    print("Seed verileri başarıyla eklendi!")
else:
    print("Veritabanında zaten veri bulunuyor, seed atlandı.")

db.close()