from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum
import uuid


class EventType(str, Enum):
    pothole = "pothole"
    road_damage = "road_damage"
    waterlogging = "waterlogging"
    traffic_sign_damage = "traffic_sign_damage"
    traffic_congestion = "traffic_congestion"
    accident = "accident"
    other = "other"


class Severity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class EventStatus(str, Enum):
    new = "new"
    verified = "verified"
    in_progress = "in_progress"
    resolved = "resolved"


class Event(BaseModel):
    event_id: str = Field(default_factory=lambda: f"EVT-{str(uuid.uuid4())[:8].upper()}")
    type: EventType
    severity: Severity
    confidence: float = Field(ge=0.0, le=1.0)
    latitude: float
    longitude: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    bus_id: str
    status: EventStatus = EventStatus.new
    evidence_image: Optional[str] = None
    description: str = ""
    vehicle_count: Optional[int] = None
    traffic_density: Optional[float] = None
    traffic_level: Optional[str] = None
    detected_objects: Optional[List[dict]] = None
    is_demo: bool = False


class EventCreate(BaseModel):
    type: EventType
    severity: Severity
    confidence: float
    latitude: float
    longitude: float
    bus_id: str
    description: str = ""
    vehicle_count: Optional[int] = None
    traffic_density: Optional[float] = None
    traffic_level: Optional[str] = None
    detected_objects: Optional[List[dict]] = None
    is_demo: bool = False


class EventUpdate(BaseModel):
    status: Optional[EventStatus] = None
    severity: Optional[Severity] = None
    description: Optional[str] = None
