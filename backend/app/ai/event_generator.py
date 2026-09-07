"""
Event Generator
---------------
Converts AI detections + GPS + Bus ID into structured Event objects
ready for storage and dashboard display.
"""
import uuid
import logging
from datetime import datetime
from typing import List, Optional, Dict

from app.models.event import Event, EventType, Severity, EventStatus
from app.ai.detector import Detection
from app.ai.traffic_analyzer import TrafficAnalyzer

logger = logging.getLogger(__name__)

analyzer = TrafficAnalyzer()


def generate_traffic_event(
    bus_id: str,
    latitude: float,
    longitude: float,
    analysis: Dict,
    timestamp: Optional[datetime] = None,
    is_demo: bool = False,
) -> Optional[Event]:
    """
    Create a traffic congestion event if traffic warrants it.
    Returns None if traffic level is low.
    """
    if not analyzer.should_raise_event(analysis):
        return None

    level = analysis["traffic_level"]
    severity = analyzer.get_severity(level)
    confidence = min(0.99, 0.70 + (analysis["traffic_density"] / 200))

    return Event(
        event_id=f"EVT-{str(uuid.uuid4())[:8].upper()}",
        type=EventType.traffic_congestion,
        severity=Severity(severity),
        confidence=round(confidence, 3),
        latitude=latitude,
        longitude=longitude,
        timestamp=timestamp or datetime.utcnow(),
        bus_id=bus_id,
        status=EventStatus.new,
        description=(
            f"Traffic congestion detected. "
            f"{analysis['vehicle_count']} vehicles counted. "
            f"Density: {analysis['traffic_density']}%. Level: {level.upper()}"
        ),
        vehicle_count=analysis.get("vehicle_count"),
        traffic_density=analysis.get("traffic_density"),
        traffic_level=level,
        detected_objects=list(analysis.get("vehicle_types", {}).items()),
        is_demo=is_demo,
    )


def generate_road_defect_event(
    bus_id: str,
    latitude: float,
    longitude: float,
    detection: Detection,
    timestamp: Optional[datetime] = None,
    evidence_image: Optional[str] = None,
    is_demo: bool = False,
) -> Event:
    """
    Create a road defect event from a pothole/damage detection.
    """
    type_map = {
        "pothole": EventType.pothole,
        "road_damage": EventType.road_damage,
        "waterlogging": EventType.waterlogging,
        "traffic_sign_damage": EventType.traffic_sign_damage,
    }
    event_type = type_map.get(detection.class_name, EventType.other)

    severity = _confidence_to_severity(detection.confidence)

    return Event(
        event_id=f"EVT-{str(uuid.uuid4())[:8].upper()}",
        type=event_type,
        severity=severity,
        confidence=round(detection.confidence, 3),
        latitude=latitude,
        longitude=longitude,
        timestamp=timestamp or datetime.utcnow(),
        bus_id=bus_id,
        status=EventStatus.new,
        description=(
            f"{detection.class_name.replace('_', ' ').title()} detected "
            f"with {detection.confidence:.0%} confidence."
        ),
        evidence_image=evidence_image,
        detected_objects=[detection.to_dict()],
        is_demo=is_demo,
    )


def _confidence_to_severity(confidence: float) -> Severity:
    if confidence >= 0.85:
        return Severity.high
    elif confidence >= 0.65:
        return Severity.medium
    else:
        return Severity.low
