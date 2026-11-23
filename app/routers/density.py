# dısarıdan gelen yolcu kaydı ve yoğunluk için 
import logging
from datetime import date
from fastapi import APIRouter, BackgroundTasks, Depends, Query
from sqlalchemy.orm import Session
from app import schemas
from app.database import get_db
from app.services import density_service

logger = logging.getLogger("bus_density")#uyg. çalışırken konsola kayıt düşmek için
router = APIRouter(prefix="/api/v1/density", tags=["Density Analysis"])# tüm adres başına prefix eklenir ve swagger /docs a density analysis başlığı altında toplar

#Background Logging Function-Arka Plan Günlük Kaydı
def log_passenger_record(route_id: int, stop_id: int, passenger_count: int) -> None: # yeni yolcu kaydı none: geriye değer dönmez
    logger.info(
        "[RECORD CREATED] route_id=%s stop_id=%s passenger_count=%s",
        route_id,
        stop_id,
        passenger_count,
    )# gelen hat,durak,yolcu sayılarını %s yerine yerleştirip log kaydı yapar

#Passenger Record Insertion Endpoint-Yolcu Kaydı Ekleme
@router.post("/records", response_model=schemas.PassengerRecordOut, status_code=201)# post isteğini karşılar. başarılı ise 201 created döner
def add_passenger_record( #isteği işler
    payload: schemas.PassengerRecordCreate, #json veriyi alır kurallara göre doğrular
    background_tasks: BackgroundTasks, # arkada ek iş çalıştırır
    db: Session = Depends(get_db),#veri tabanı açar ve kapatır
):
    record = density_service.create_passenger_record(db, payload)#asıl kaydı yaptırır ve record içine alır
    background_tasks.add_task( #arka planda çalıştırarak kullanıcı log yazımını yavaşlatmaz
        log_passenger_record,
        record.route_id,
        record.stop_id,
        record.passenger_count,
    )
    return record # veri tabanına eklenen kaydı json olarak geri döndürür

#Hourly Occupancy Endpoint-Saatlik Yoğunluk Ucu
@router.get("/routes/{route_id}/hourly", response_model=list[schemas.HourlyDensityItem])# isteği karşılar sonucu liste olarak döndürür
def get_route_hourly_density( # saatlik yoğunluk verisi getirir
    route_id: int,
    target_date: date = Query(default_factory=date.today, description="Tarih (YYYY-MM-DD)"),# tarih girilmezse o günü baz alır
    db: Session = Depends(get_db), # database sağlar
):
    return density_service.get_hourly_density(db, route_id, target_date)#yoğunluk hesabını servisten ister ve sonucu döndürür

#Route Ranking Endpoint-Hat Sıralama Ucu.
@router.get("/routes/ranking", response_model=list[schemas.RouteRankingItem])# adrese gelen get karşılanır sonuç schemas sonunda yazanda döner
def get_routes_ranking( # hatları yoğunluğa göre sıralar
    target_date: date = Query(default_factory=date.today, description="Tarih (YYYY-MM-DD)"),# tarih aır verilmezse yine bugün
    db: Session = Depends(get_db),# database sağlar
):
    return density_service.get_route_ranking(db, target_date)#servisten sogu alır ve döndürür