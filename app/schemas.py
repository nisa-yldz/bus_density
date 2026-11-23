from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class PassengerRecordCreate(BaseModel):
    route_id: int = Field(..., gt=0, description="Hattın ID numarası")
    stop_id: int = Field(..., gt=0, description="Durağın ID numarası")
    passenger_count: int = Field(..., ge=0, le=500, description="Binen yolcu sayısı (0-500 arası)")
    recorded_at: datetime | None = Field(
        default=None,
        description="ISO 8601 tarih-saat (boş bırakılırsa şu anki zaman alınır)",
    )


class PassengerRecordOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    route_id: int
    stop_id: int
    passenger_count: int
    recorded_at: datetime


class HourlyDensityItem(BaseModel):
    hour: int = Field(..., ge=0, le=23)
    total_passengers: int
    record_count: int


class RouteRankingItem(BaseModel):
    route_id: int
    route_code: str
    route_name: str
    total_passengers: int