"""
Demo Data Seeder
-----------------
Populates MongoDB with realistic sample data for demo purposes.
All seeded data is clearly marked with is_demo=True.

This allows the full dashboard to be demonstrated without:
  - A real bus camera
  - Real GPS hardware
  - A custom-trained pothole model
  - Live city data

⚠ DEMO DATA — Not real-world measurements ⚠
"""
import uuid
import random
import logging
from datetime import datetime, timedelta
from typing import List, Dict

logger = logging.getLogger(__name__)


def _rand_time(hours_ago_max: int = 6) -> datetime:
    delta = random.uniform(0, hours_ago_max * 3600)
    return datetime.utcnow() - timedelta(seconds=delta)


# ── Demo Buses ───────────────────────────────────────────────────────
DEMO_BUSES = [
    {
        "bus_id": "BUS-101",
        "route_name": "Route 1 – Central to Anna Nagar",
        "route_start": "Madurai Central",
        "route_end": "Anna Nagar",
        "status": "active",
        "driver_name": "Rajan K.",
        "driver_phone": "9876543210",
        "current_location": {"latitude": 9.9261, "longitude": 78.1212, "timestamp": datetime.utcnow().isoformat(), "speed_kmh": 24.5, "heading": 45.0},
        "traffic_level": "moderate",
        "incident_count": 3,
        "last_active": datetime.utcnow().isoformat(),
        "is_demo": True,
    },
    {
        "bus_id": "BUS-102",
        "route_name": "Route 2 – Meenakshi Temple to Kochadai",
        "route_start": "Meenakshi Temple",
        "route_end": "Kochadai",
        "status": "active",
        "driver_name": "Selvam P.",
        "driver_phone": "9876543211",
        "current_location": {"latitude": 9.9238, "longitude": 78.1230, "timestamp": datetime.utcnow().isoformat(), "speed_kmh": 18.2, "heading": 120.0},
        "traffic_level": "high",
        "incident_count": 5,
        "last_active": datetime.utcnow().isoformat(),
        "is_demo": True,
    },
    {
        "bus_id": "BUS-103",
        "route_name": "Route 3 – Mattuthavani to Goripalayam",
        "route_start": "Mattuthavani",
        "route_end": "Goripalayam",
        "status": "active",
        "driver_name": "Kumar M.",
        "driver_phone": "9876543212",
        "current_location": {"latitude": 9.9265, "longitude": 78.1220, "timestamp": datetime.utcnow().isoformat(), "speed_kmh": 32.1, "heading": 220.0},
        "traffic_level": "low",
        "incident_count": 1,
        "last_active": datetime.utcnow().isoformat(),
        "is_demo": True,
    },
    {
        "bus_id": "BUS-104",
        "route_name": "Route 4 – Railway Station to Vilangudi",
        "route_start": "Madurai Junction",
        "route_end": "Vilangudi",
        "status": "active",
        "driver_name": "Arjun S.",
        "driver_phone": "9876543213",
        "current_location": {"latitude": 9.9315, "longitude": 78.1193, "timestamp": datetime.utcnow().isoformat(), "speed_kmh": 21.8, "heading": 30.0},
        "traffic_level": "severe",
        "incident_count": 7,
        "last_active": datetime.utcnow().isoformat(),
        "is_demo": True,
    },
    {
        "bus_id": "BUS-105",
        "route_name": "Route 5 – Bypass Road Circuit",
        "route_start": "Bypass Road",
        "route_end": "Bypass Road",
        "status": "maintenance",
        "driver_name": "Vijay R.",
        "driver_phone": "9876543214",
        "current_location": {"latitude": 9.9210, "longitude": 78.1190, "timestamp": datetime.utcnow().isoformat(), "speed_kmh": 0.0, "heading": 0.0},
        "traffic_level": "low",
        "incident_count": 0,
        "last_active": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
        "is_demo": True,
    },
]

# ── Demo Events ──────────────────────────────────────────────────────
DEMO_EVENTS = [
    {
        "event_id": "EVT-DEMO001",
        "type": "pothole",
        "severity": "high",
        "confidence": 0.91,
        "latitude": 9.9252,
        "longitude": 78.1198,
        "timestamp": _rand_time(1),
        "bus_id": "BUS-102",
        "status": "new",
        "description": "[DEMO] Large pothole detected on carriageway. High risk to vehicles.",
        "evidence_image": None,
        "is_demo": True,
    },
    {
        "event_id": "EVT-DEMO002",
        "type": "traffic_congestion",
        "severity": "critical",
        "confidence": 0.96,
        "latitude": 9.9238,
        "longitude": 78.1230,
        "timestamp": _rand_time(0.5),
        "bus_id": "BUS-102",
        "status": "verified",
        "description": "[DEMO] Severe traffic congestion. 63 vehicles counted. Density: 82%. Level: SEVERE",
        "vehicle_count": 63,
        "traffic_density": 82.0,
        "traffic_level": "severe",
        "is_demo": True,
    },
    {
        "event_id": "EVT-DEMO003",
        "type": "road_damage",
        "severity": "medium",
        "confidence": 0.74,
        "latitude": 9.9275,
        "longitude": 78.1230,
        "timestamp": _rand_time(2),
        "bus_id": "BUS-101",
        "status": "in_progress",
        "description": "[DEMO] Road surface damage detected. Cracking and edge wear visible.",
        "is_demo": True,
    },
    {
        "event_id": "EVT-DEMO004",
        "type": "traffic_congestion",
        "severity": "high",
        "confidence": 0.88,
        "latitude": 9.9318,
        "longitude": 78.1280,
        "timestamp": _rand_time(1.5),
        "bus_id": "BUS-101",
        "status": "new",
        "description": "[DEMO] High traffic congestion. 47 vehicles counted. Density: 61%. Level: HIGH",
        "vehicle_count": 47,
        "traffic_density": 61.0,
        "traffic_level": "high",
        "is_demo": True,
    },
    {
        "event_id": "EVT-DEMO005",
        "type": "waterlogging",
        "severity": "high",
        "confidence": 0.83,
        "latitude": 9.9195,
        "longitude": 78.1193,
        "timestamp": _rand_time(3),
        "bus_id": "BUS-103",
        "status": "resolved",
        "description": "[DEMO] Standing water detected on road surface. Risk of skidding.",
        "is_demo": True,
    },
    {
        "event_id": "EVT-DEMO006",
        "type": "pothole",
        "severity": "medium",
        "confidence": 0.69,
        "latitude": 9.9310,
        "longitude": 78.1180,
        "timestamp": _rand_time(4),
        "bus_id": "BUS-103",
        "status": "verified",
        "description": "[DEMO] Medium pothole detected. Depth estimated 4-7 cm.",
        "is_demo": True,
    },
    {
        "event_id": "EVT-DEMO007",
        "type": "traffic_sign_damage",
        "severity": "low",
        "confidence": 0.61,
        "latitude": 9.9290,
        "longitude": 78.1162,
        "timestamp": _rand_time(5),
        "bus_id": "BUS-104",
        "status": "new",
        "description": "[DEMO] Damaged or missing traffic sign detected at intersection.",
        "is_demo": True,
    },
    {
        "event_id": "EVT-DEMO008",
        "type": "traffic_congestion",
        "severity": "critical",
        "confidence": 0.97,
        "latitude": 9.9342,
        "longitude": 78.1222,
        "timestamp": _rand_time(0.2),
        "bus_id": "BUS-104",
        "status": "new",
        "description": "[DEMO] Severe gridlock. 71 vehicles detected. Density: 89%. Level: SEVERE",
        "vehicle_count": 71,
        "traffic_density": 89.0,
        "traffic_level": "severe",
        "is_demo": True,
    },
    {
        "event_id": "EVT-DEMO009",
        "type": "pothole",
        "severity": "high",
        "confidence": 0.88,
        "latitude": 9.9225,
        "longitude": 78.1215,
        "timestamp": _rand_time(2.5),
        "bus_id": "BUS-102",
        "status": "new",
        "description": "[DEMO] Deep pothole detected near junction. Immediate repair needed.",
        "is_demo": True,
    },
    {
        "event_id": "EVT-DEMO010",
        "type": "road_damage",
        "severity": "low",
        "confidence": 0.55,
        "latitude": 9.9180,
        "longitude": 78.1160,
        "timestamp": _rand_time(6),
        "bus_id": "BUS-105",
        "status": "resolved",
        "description": "[DEMO] Minor road surface cracking detected. Monitoring recommended.",
        "is_demo": True,
    },
]

# ── Traffic Records ──────────────────────────────────────────────────
DEMO_TRAFFIC_RECORDS = [
    {
        "record_id": f"TRF-DEMO{str(i+1).zfill(3)}",
        "bus_id": bus,
        "latitude": lat,
        "longitude": lon,
        "timestamp": _rand_time(i * 0.5),
        "vehicle_count": count,
        "vehicle_types": types,
        "traffic_density": density,
        "traffic_level": level,
        "avg_speed_kmh": speed,
        "is_demo": True,
    }
    for i, (bus, lat, lon, count, types, density, level, speed) in enumerate([
        ("BUS-102", 9.9238, 78.1230, 63, {"car": 42, "motorcycle": 12, "bus": 5, "truck": 4}, 82.0, "severe", 8.5),
        ("BUS-104", 9.9342, 78.1222, 71, {"car": 51, "motorcycle": 14, "bus": 4, "truck": 2}, 89.0, "severe", 5.2),
        ("BUS-101", 9.9318, 78.1280, 47, {"car": 31, "motorcycle": 10, "bus": 4, "truck": 2}, 61.0, "high", 15.3),
        ("BUS-101", 9.9275, 78.1230, 28, {"car": 18, "motorcycle": 7, "bus": 2, "truck": 1}, 35.0, "moderate", 22.1),
        ("BUS-103", 9.9265, 78.1220, 12, {"car": 8, "motorcycle": 3, "bus": 1}, 15.0, "low", 35.8),
    ])
]


async def seed_demo_data(db) -> Dict:
    """Insert demo data into MongoDB. Skip if already seeded."""
    if db is None:
        logger.warning("No DB connection — skipping seed")
        return {"seeded": False, "reason": "no_db"}

    results = {"buses": 0, "events": 0, "traffic_records": 0}

    try:
        # Only seed if collections are empty
        bus_count = await db.buses.count_documents({"is_demo": True})
        if bus_count == 0:
            # Convert datetime objects to ISO strings for MongoDB
            buses_to_insert = []
            for bus in DEMO_BUSES:
                b = dict(bus)
                if isinstance(b.get("last_active"), datetime):
                    b["last_active"] = b["last_active"].isoformat()
                buses_to_insert.append(b)
            await db.buses.insert_many(buses_to_insert)
            results["buses"] = len(DEMO_BUSES)
            logger.info(f"Seeded {len(DEMO_BUSES)} demo buses")

        event_count = await db.events.count_documents({"is_demo": True})
        if event_count == 0:
            events_to_insert = []
            for ev in DEMO_EVENTS:
                e = dict(ev)
                if isinstance(e.get("timestamp"), datetime):
                    e["timestamp"] = e["timestamp"].isoformat()
                events_to_insert.append(e)
            await db.events.insert_many(events_to_insert)
            results["events"] = len(DEMO_EVENTS)
            logger.info(f"Seeded {len(DEMO_EVENTS)} demo events")

        traffic_count = await db.traffic_records.count_documents({"is_demo": True})
        if traffic_count == 0:
            records_to_insert = []
            for rec in DEMO_TRAFFIC_RECORDS:
                r = dict(rec)
                if isinstance(r.get("timestamp"), datetime):
                    r["timestamp"] = r["timestamp"].isoformat()
                records_to_insert.append(r)
            await db.traffic_records.insert_many(records_to_insert)
            results["traffic_records"] = len(DEMO_TRAFFIC_RECORDS)
            logger.info(f"Seeded {len(DEMO_TRAFFIC_RECORDS)} demo traffic records")

        return {"seeded": True, "results": results}

    except Exception as e:
        logger.error(f"Error seeding demo data: {e}")
        return {"seeded": False, "reason": str(e)}


def get_in_memory_demo_data():
    """Return demo data as plain dicts for fallback (no DB needed)."""
    return {
        "buses": DEMO_BUSES,
        "events": DEMO_EVENTS,
        "traffic_records": DEMO_TRAFFIC_RECORDS,
    }
