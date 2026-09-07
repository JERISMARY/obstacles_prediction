from pydantic import BaseModel, Field
from typing import Optional, Dict
from datetime import datetime
from enum import Enum


class TrafficLevel(str, Enum):
    low = "low"
    moderate = "moderate"
    high = "high"
    severe = "severe"


class TrafficRecord(BaseModel):
    record_id: str
    bus_id: str
    latitude: float
    longitude: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    vehicle_count: int = 0
    vehicle_types: Dict[str, int] = Field(default_factory=dict)
    traffic_density: float = 0.0
    traffic_level: TrafficLevel = TrafficLevel.low
    avg_speed_kmh: float = 0.0
    is_demo: bool = False


class ProcessingJob(BaseModel):
    job_id: str
    bus_id: str
    video_filename: str
    status: str = "pending"   # pending | processing | completed | failed
    progress: int = 0
    total_frames: int = 0
    processed_frames: int = 0
    events_generated: int = 0
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    result_summary: Optional[dict] = None
