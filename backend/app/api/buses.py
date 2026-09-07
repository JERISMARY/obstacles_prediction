"""
Bus API Routes
--------------
GET  /api/buses          - List all buses
GET  /api/buses/{bus_id} - Get single bus details
POST /api/buses          - Create bus (admin)
PUT  /api/buses/{bus_id}/location - Update GPS location
GET  /api/buses/{bus_id}/events  - Get events for a bus
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime

from app.database.connection import get_database
from app.services.demo_data import get_in_memory_demo_data
from app.services.gps_simulator import gps_simulator, BUS_ROUTES

router = APIRouter(prefix="/api/buses", tags=["buses"])


def _serialize(doc: dict) -> dict:
    """Remove MongoDB _id and ensure JSON-serializable."""
    doc.pop("_id", None)
    return doc


@router.get("")
async def list_buses(db=Depends(get_database)):
    """List all monitored buses with current status."""
    if db is not None:
        try:
            cursor = db.buses.find({})
            buses = [_serialize(b) async for b in cursor]
            if buses:
                return {"buses": buses, "count": len(buses), "source": "database"}
        except Exception:
            pass

    # Fallback: in-memory demo data
    data = get_in_memory_demo_data()
    buses = data["buses"]
    # Attach live GPS positions
    for bus in buses:
        bus_id = bus["bus_id"]
        if bus["status"] == "active":
            lat, lon = gps_simulator.get_next_location(bus_id)
            bus["current_location"]["latitude"] = lat
            bus["current_location"]["longitude"] = lon
            bus["current_location"]["timestamp"] = datetime.utcnow().isoformat()
    return {"buses": buses, "count": len(buses), "source": "demo"}


@router.get("/{bus_id}")
async def get_bus(bus_id: str, db=Depends(get_database)):
    """Get details for a specific bus."""
    if db is not None:
        try:
            bus = await db.buses.find_one({"bus_id": bus_id})
            if bus:
                return _serialize(bus)
        except Exception:
            pass

    data = get_in_memory_demo_data()
    bus = next((b for b in data["buses"] if b["bus_id"] == bus_id), None)
    if not bus:
        raise HTTPException(status_code=404, detail=f"Bus {bus_id} not found")

    # Update GPS
    if bus["status"] == "active":
        lat, lon = gps_simulator.get_next_location(bus_id)
        bus["current_location"]["latitude"] = lat
        bus["current_location"]["longitude"] = lon
    return bus


@router.get("/{bus_id}/events")
async def get_bus_events(bus_id: str, limit: int = 20, db=Depends(get_database)):
    """Get recent events detected by a specific bus."""
    if db is not None:
        try:
            cursor = db.events.find({"bus_id": bus_id}).sort("timestamp", -1).limit(limit)
            events = [_serialize(e) async for e in cursor]
            return {"events": events, "count": len(events), "bus_id": bus_id}
        except Exception:
            pass

    data = get_in_memory_demo_data()
    events = [e for e in data["events"] if e["bus_id"] == bus_id]
    return {"events": events, "count": len(events), "bus_id": bus_id}


@router.get("/{bus_id}/location")
async def get_bus_location(bus_id: str):
    """Get current GPS location (simulated)."""
    route_info = gps_simulator.get_route_info(bus_id)
    if not route_info:
        raise HTTPException(status_code=404, detail=f"Bus {bus_id} not found")

    lat, lon = gps_simulator.get_next_location(bus_id)
    return {
        "bus_id": bus_id,
        "latitude": lat,
        "longitude": lon,
        "timestamp": datetime.utcnow().isoformat(),
        "source": "gps_simulator",
        "note": "Simulated GPS — real hardware can be plugged in via GPSProvider interface",
    }
