from datetime import date, datetime, time, timezone
from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from app import models, schemas


def create_passenger_record(#yeni yolcu kaydı
    db: Session, payload: schemas.PassengerRecordCreate
) -> models.PassengerCount:
    
    # 1. Seçilen durak gerçekten seçilen hatta tanımlı mı kontrol et
    mapping = ( # routeid ve stopid eşleşme arar
        db.query(models.RouteStop)
        .filter(
            models.RouteStop.route_id == payload.route_id,
            models.RouteStop.stop_id == payload.stop_id,
        )
        .first() #eşleşen ilk kayıt yoksa none döner
    )

    if not mapping:#durak o hatta tanımlı değilse 404 verir
        raise HTTPException(
            status_code=400,
            detail=f"Stop {payload.stop_id} is not assigned to route {payload.route_id}.",
        )

    record_time = payload.recorded_at or datetime.now(timezone.utc)#zman dilimi utc ye çevrilir yoksa şuanki zaman alınır
    if record_time.tzinfo is not None:
        record_time = record_time.astimezone(timezone.utc).replace(tzinfo=None)

    record = models.PassengerCount(#yeni passengercount bellekte oluşur
        route_id=payload.route_id,
        stop_id=payload.stop_id,
        passenger_count=payload.passenger_count,
        recorded_at=record_time,
    )
    db.add(record)#kaydı ekler
    db.commit()#kalıcı veritabanına yazar
    db.refresh(record)#nesneye geri yükler
    return record#kaydı döndürür


def get_hourly_density( #saatlik yoğunluk hesaplama
    db: Session, route_id: int, target_date: date
) -> list[schemas.HourlyDensityItem]:
    route = db.query(models.Route).filter(models.Route.id == route_id).first()# hat var mı bakar
    if not route:
        raise HTTPException(status_code=404, detail="Route not found.")

    start_dt = datetime.combine(target_date, time.min)#gün başlangıcı nesneye çevirir
    end_dt = datetime.combine(target_date, time.max)# gün sonunu nesneye çevirir

    rows = (
        db.query(
            func.strftime("%H", models.PassengerCount.recorded_at).label("hour_str"),#SQL strftime("%H", ...) fonksiyonu ile kaydın saatini ("00"–"23") çıkarır
            func.sum(models.PassengerCount.passenger_count).label("total"), #toplam yolcu sayısını (SUM)
            func.count(models.PassengerCount.id).label("cnt"),#kayıt adedini (COUNT) hesaplar.
        )
        .filter( #İlgili hatta ve gün aralığına filtreler, saate göre gruplar (GROUP BY) ve tüm satırları çeker.
            models.PassengerCount.route_id == route_id,
            models.PassengerCount.recorded_at >= start_dt,
            models.PassengerCount.recorded_at <= end_dt,
        )
        .group_by("hour_str")
        .all()
    )

    hour_map = {int(r.hour_str): (int(r.total), int(r.cnt)) for r in rows}#hızlı erişim için

    return [# 0 ile 23 arası tüm saatler döner, kayıt yoksa 0,0 varsayılan kullanılır
        schemas.HourlyDensityItem(
            hour=h,
            total_passengers=hour_map.get(h, (0, 0))[0],
            record_count=hour_map.get(h, (0, 0))[1],
        )
        for h in range(24)
    ]


def get_route_ranking( # günlük hat sıralaması
    db: Session, target_date: date
) -> list[schemas.RouteRankingItem]:
    start_dt = datetime.combine(target_date, time.min)
    end_dt = datetime.combine(target_date, time.max)

    rows = (
        db.query(
            models.Route.id,#hat bilgilerini alır
            models.Route.code,
            models.Route.name,
            func.coalesce(func.sum(models.PassengerCount.passenger_count), 0).label( # o günkü yolcu toplamını seçer ve kayıt yoksa 0 
                "total_passengers"
            ),
        )
        .outerjoin( # hiç yolcu kaydı olmazsa hat düşmez 0 ile listelenir
            models.PassengerCount,
            (models.PassengerCount.route_id == models.Route.id)
            & (models.PassengerCount.recorded_at >= start_dt)
            & (models.PassengerCount.recorded_at <= end_dt),
        )
        .group_by(models.Route.id)# gruplar azalan sıraya göre sıralanmış
        .order_by(
            func.coalesce(func.sum(models.PassengerCount.passenger_count), 0).desc()
        )
        .all()
    )

    return [
        schemas.RouteRankingItem(
            route_id=r.id,
            route_code=r.code,
            route_name=r.name,
            total_passengers=int(r.total_passengers),
        )
        for r in rows
    ]