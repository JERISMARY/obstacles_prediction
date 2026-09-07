"""
Events API Routes
-----------------
GET   /api/events              - List events (with filters)
GET   /api/events/{event_id}   - Get single event
POST  /api/events              - Create event
PATCH /api/events/{event_id}   - Update event status/severity
DELETE /api/events/{event_id}  - Delete event (admin)
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from datetime import datetime

from app.database.connection import get_database
from app.models.event import EventCreate, EventUpdate, Event, EventType, Severity, EventStatus
from app.services.demo_data import get_in_memory_demo_data
import uuid

router = APIRouter(prefix="/api/events", tags=["events"])


def _serialize(doc: dict) -> dict:
    doc.pop("_id", None)
    return doc


@router.get("")
async def list_events(
    type: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    bus_id: Optional[str] = Query(None),
    limit: int = Query(100, le=500),
    skip: int = Query(0, ge=0),
    db=Depends(get_database),
):
    """List events with optional filters."""
    query: dict = {}
    if type:
        query["type"] = type
    if severity:
        query["severity"] = severity
    if status:
        query["status"] = status
    if bus_id:
        query["bus_id"] = bus_id

    if db is not None:
        try:
            cursor = db.events.find(query).sort("timestamp", -1).skip(skip).limit(limit)
            events = [_serialize(e) async for e in cursor]
            total = await db.events.count_documents(query)
            return {"events": events, "total": total, "skip": skip, "limit": limit, "source": "database"}
        except Exception:
            pass

    # Fallback: demo data
    data = get_in_memory_demo_data()
    events = data["events"]
    if type:
        events = [e for e in events if e.get("type") == type]
    if severity:
        events = [e for e in events if e.get("severity") == severity]
    if status:
        events = [e for e in events if e.get("status") == status]
    if bus_id:
        events = [e for e in events if e.get("bus_id") == bus_id]

    return {"events": events[skip:skip+limit], "total": len(events), "skip": skip, "limit": limit, "source": "demo"}


@router.get("/{event_id}")
async def get_event(event_id: str, db=Depends(get_database)):
    """Get a single event by ID."""
    if db is not None:
        try:
            evt = await db.events.find_one({"event_id": event_id})
            if evt:
                return _serialize(evt)
        except Exception:
            pass

    data = get_in_memory_demo_data()
    evt = next((e for e in data["events"] if e["event_id"] == event_id), None)
    if not evt:
        raise HTTPException(status_code=404, detail=f"Event {event_id} not found")
    return evt


@router.post("", status_code=201)
async def create_event(payload: EventCreate, db=Depends(get_database)):
    """Manually create an event (also used by video processor)."""
    event = Event(
        event_id=f"EVT-{str(uuid.uuid4())[:8].upper()}",
        **payload.model_dump(),
    )
    doc = event.model_dump()
    if isinstance(doc.get("timestamp"), datetime):
        doc["timestamp"] = doc["timestamp"].isoformat()

    if db is not None:
        try:
            await db.events.insert_one(doc)
            doc.pop("_id", None)
            return {"event": doc, "source": "database"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"DB error: {e}")

    return {"event": doc, "source": "in_memory", "warning": "No DB — event not persisted"}


@router.patch("/{event_id}")
async def update_event(event_id: str, payload: EventUpdate, db=Depends(get_database)):
    """Update event status or severity."""
    update_data = {k: v for k, v in payload.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    if db is not None:
        try:
            result = await db.events.update_one(
                {"event_id": event_id}, {"$set": update_data}
            )
            if result.matched_count == 0:
                raise HTTPException(status_code=404, detail=f"Event {event_id} not found")
            return {"updated": True, "event_id": event_id, "changes": update_data}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return {"updated": True, "event_id": event_id, "changes": update_data, "warning": "No DB — not persisted"}
