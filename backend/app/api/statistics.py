"""
Statistics & Traffic API Routes
--------------------------------
GET /api/statistics  - Dashboard summary stats
GET /api/traffic     - Traffic records
GET /api/heatmap     - Heatmap data points for congestion
"""
from fastapi import APIRouter, Depends, Query
from typing import Optional
from datetime import datetime, timedelta

from app.database.connection import get_database
from app.services.demo_data import get_in_memory_demo_data

router = APIRouter(prefix="/api", tags=["statistics"])


def _serialize(doc: dict) -> dict:
    doc.pop("_id", None)
    return doc


@router.get("/statistics")
async def get_statistics(db=Depends(get_database)):
    """Dashboard summary statistics."""
    if db is not None:
        try:
            total_buses = await db.buses.count_documents({})
            active_buses = await db.buses.count_documents({"status": "active"})
            total_incidents = await db.events.count_documents({})
            road_defects = await db.events.count_documents({
                "type": {"$in": ["pothole", "road_damage", "waterlogging", "traffic_sign_damage"]}
            })
            traffic_alerts = await db.events.count_documents({"type": "traffic_congestion"})
            high_priority = await db.events.count_documents({
                "severity": {"$in": ["high", "critical"]},
                "status": {"$ne": "resolved"}
            })
            new_events = await db.events.count_documents({"status": "new"})
            resolved = await db.events.count_documents({"status": "resolved"})

            # Severity breakdown
            severity_pipeline = [
                {"$group": {"_id": "$severity", "count": {"$sum": 1}}}
            ]
            severity_cursor = db.events.aggregate(severity_pipeline)
            severity_breakdown = {}
            async for doc in severity_cursor:
                severity_breakdown[doc["_id"]] = doc["count"]

            # Type breakdown
            type_pipeline = [
                {"$group": {"_id": "$type", "count": {"$sum": 1}}}
            ]
            type_cursor = db.events.aggregate(type_pipeline)
            type_breakdown = {}
            async for doc in type_cursor:
                type_breakdown[doc["_id"]] = doc["count"]

            return {
                "buses": {"total": total_buses, "active": active_buses},
                "incidents": {
                    "total": total_incidents,
                    "road_defects": road_defects,
                    "traffic_alerts": traffic_alerts,
                    "high_priority": high_priority,
                    "new": new_events,
                    "resolved": resolved,
                },
                "severity_breakdown": severity_breakdown,
                "type_breakdown": type_breakdown,
                "source": "database",
                "generated_at": datetime.utcnow().isoformat(),
            }
        except Exception:
            pass

    # Fallback
    data = get_in_memory_demo_data()
    events = data["events"]
    buses = data["buses"]

    road_defect_types = {"pothole", "road_damage", "waterlogging", "traffic_sign_damage"}
    severity_breakdown = {}
    type_breakdown = {}
    for e in events:
        s = e.get("severity", "low")
        severity_breakdown[s] = severity_breakdown.get(s, 0) + 1
        t = e.get("type", "other")
        type_breakdown[t] = type_breakdown.get(t, 0) + 1

    return {
        "buses": {
            "total": len(buses),
            "active": sum(1 for b in buses if b.get("status") == "active"),
        },
        "incidents": {
            "total": len(events),
            "road_defects": sum(1 for e in events if e.get("type") in road_defect_types),
            "traffic_alerts": sum(1 for e in events if e.get("type") == "traffic_congestion"),
            "high_priority": sum(1 for e in events if e.get("severity") in ("high", "critical") and e.get("status") != "resolved"),
            "new": sum(1 for e in events if e.get("status") == "new"),
            "resolved": sum(1 for e in events if e.get("status") == "resolved"),
        },
        "severity_breakdown": severity_breakdown,
        "type_breakdown": type_breakdown,
        "source": "demo",
        "generated_at": datetime.utcnow().isoformat(),
    }


@router.get("/traffic")
async def get_traffic_records(
    bus_id: Optional[str] = Query(None),
    limit: int = Query(50, le=200),
    db=Depends(get_database),
):
    """Get traffic records."""
    if db is not None:
        try:
            query = {"bus_id": bus_id} if bus_id else {}
            cursor = db.traffic_records.find(query).sort("timestamp", -1).limit(limit)
            records = [_serialize(r) async for r in cursor]
            return {"records": records, "count": len(records)}
        except Exception:
            pass

    data = get_in_memory_demo_data()
    records = data["traffic_records"]
    if bus_id:
        records = [r for r in records if r["bus_id"] == bus_id]
    return {"records": records[:limit], "count": len(records)}


@router.get("/heatmap")
async def get_heatmap_data(db=Depends(get_database)):
    """
    Return heatmap data points for congestion/incidents.
    Format: [{lat, lon, intensity}]
    """
    points = []

    if db is not None:
        try:
            # Aggregate by location with count as intensity
            pipeline = [
                {"$group": {
                    "_id": {
                        "lat": {"$round": ["$latitude", 3]},
                        "lon": {"$round": ["$longitude", 3]},
                    },
                    "count": {"$sum": 1},
                    "max_severity": {"$max": "$severity"},
                }},
                {"$limit": 200},
            ]
            cursor = db.events.aggregate(pipeline)
            async for doc in cursor:
                severity_weight = {"low": 0.3, "medium": 0.5, "high": 0.75, "critical": 1.0}
                intensity = min(1.0, doc["count"] * 0.2) * severity_weight.get(doc.get("max_severity", "low"), 0.3)
                points.append({
                    "lat": doc["_id"]["lat"],
                    "lon": doc["_id"]["lon"],
                    "intensity": round(intensity, 3),
                    "count": doc["count"],
                })
            return {"points": points, "source": "database"}
        except Exception:
            pass

    # Demo heatmap points
    data = get_in_memory_demo_data()
    for evt in data["events"]:
        severity_weight = {"low": 0.3, "medium": 0.5, "high": 0.75, "critical": 1.0}
        points.append({
            "lat": evt["latitude"],
            "lon": evt["longitude"],
            "intensity": severity_weight.get(evt.get("severity", "low"), 0.3),
            "count": 1,
            "type": evt.get("type"),
        })
    return {"points": points, "source": "demo"}
