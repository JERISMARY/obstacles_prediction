from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class BusStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    maintenance = "maintenance"


class BusLocation(BaseModel):
    latitude: float
    longitude: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    speed_kmh: float = 0.0
    heading: float = 0.0


class Bus(BaseModel):
    bus_id: str
    route_name: str
    route_start: str
    route_end: str
    status: BusStatus = BusStatus.active
    driver_name: str = ""
    driver_phone: str = ""
    current_location: Optional[BusLocation] = None
    incident_count: int = 0
    traffic_level: str = "low"
    last_active: datetime = Field(default_factory=datetime.utcnow)
    is_demo: bool = False


class BusCreate(BaseModel):
    bus_id: str
    route_name: str
    route_start: str
    route_end: str
    driver_name: str = ""


class BusUpdate(BaseModel):
    status: Optional[BusStatus] = None
    current_location: Optional[BusLocation] = None
    traffic_level: Optional[str] = None
    incident_count: Optional[int] = None
