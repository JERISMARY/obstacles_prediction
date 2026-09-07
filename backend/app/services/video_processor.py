"""
Video Processing Service
-------------------------
Handles the full pipeline:
  Video → Frame extraction → YOLO detection → Traffic analysis
  → Event generation → GPS attachment → DB storage

Runs as a background task (FastAPI BackgroundTasks) so the
HTTP response returns immediately and the UI can poll for status.
"""
import cv2
import uuid
import logging
import asyncio
import os
import base64
from datetime import datetime
from typing import Optional, List, Dict
from pathlib import Path

from app.ai.vehicle_detector import VehicleDetector
from app.ai.pothole_detector import PotholeDetector
from app.ai.traffic_analyzer import TrafficAnalyzer
from app.ai.event_generator import generate_traffic_event, generate_road_defect_event
from app.ai.config import FRAME_SAMPLE_RATE, MAX_FRAMES_PER_JOB, TRAFFIC_WINDOW_SECONDS
from app.services.gps_simulator import gps_simulator
from app.config import settings

logger = logging.getLogger(__name__)

# Shared model instances (loaded once)
_vehicle_detector: Optional[VehicleDetector] = None
_pothole_detector: Optional[PotholeDetector] = None
_traffic_analyzer = TrafficAnalyzer()

# In-memory job store (mirrors DB for fast status lookups)
_jobs: Dict[str, Dict] = {}


def get_vehicle_detector() -> VehicleDetector:
    global _vehicle_detector
    if _vehicle_detector is None:
        _vehicle_detector = VehicleDetector(settings.YOLO_MODEL)
        _vehicle_detector.load_model()
    return _vehicle_detector


def get_pothole_detector() -> PotholeDetector:
    global _pothole_detector
    if _pothole_detector is None:
        _pothole_detector = PotholeDetector()
        _pothole_detector.load_model()
    return _pothole_detector


def create_job(bus_id: str, filename: str) -> str:
    job_id = f"JOB-{str(uuid.uuid4())[:8].upper()}"
    _jobs[job_id] = {
        "job_id": job_id,
        "bus_id": bus_id,
        "video_filename": filename,
        "status": "pending",
        "progress": 0,
        "total_frames": 0,
        "processed_frames": 0,
        "events_generated": 0,
        "error_message": None,
        "created_at": datetime.utcnow().isoformat(),
        "completed_at": None,
        "result_summary": None,
    }
    return job_id


def get_job_status(job_id: str) -> Optional[Dict]:
    return _jobs.get(job_id)


def _save_evidence_frame(frame, event_id: str, upload_dir: str) -> Optional[str]:
    """Save a frame as evidence image, return relative URL path."""
    try:
        evidence_dir = os.path.join(upload_dir, "evidence")
        os.makedirs(evidence_dir, exist_ok=True)
        filename = f"{event_id}.jpg"
        filepath = os.path.join(evidence_dir, filename)
        cv2.imwrite(filepath, frame)
        return f"/uploads/evidence/{filename}"
    except Exception as e:
        logger.error(f"Failed to save evidence frame: {e}")
        return None


async def process_video(
    job_id: str,
    video_path: str,
    bus_id: str,
    db,
    upload_dir: str,
):
    """
    Main video processing pipeline. Runs as background task.
    Updates job status in _jobs dict (and DB if available).
    """
    job = _jobs.get(job_id)
    if not job:
        logger.error(f"Job {job_id} not found")
        return

    logger.info(f"Starting video processing job {job_id} for bus {bus_id}")
    job["status"] = "processing"

    try:
        # ── Load detectors ───────────────────────────────────────────
        vehicle_det = get_vehicle_detector()
        pothole_det = get_pothole_detector()

        if not vehicle_det.is_ready:
            raise RuntimeError(
                "Vehicle detector not ready. "
                "Ensure ultralytics is installed and model can be downloaded."
            )

        # ── Open video ───────────────────────────────────────────────
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise RuntimeError(f"Cannot open video: {video_path}")

        fps = cap.get(cv2.CAP_PROP_FPS) or 25
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        total_frames = min(total_frames, MAX_FRAMES_PER_JOB * FRAME_SAMPLE_RATE)
        job["total_frames"] = total_frames

        # ── GPS state ────────────────────────────────────────────────
        lat, lon = gps_simulator.get_current_location(bus_id)

        # Sliding window for traffic analysis (frames grouped by time window)
        window_frames = []
        window_seconds = TRAFFIC_WINDOW_SECONDS
        frames_per_window = int(fps * window_seconds / FRAME_SAMPLE_RATE)
        if frames_per_window < 1:
            frames_per_window = 10

        events_generated = 0
        frame_idx = 0
        processed = 0
        all_events = []

        # ── Main processing loop ─────────────────────────────────────
        while processed < MAX_FRAMES_PER_JOB:
            ret, frame = cap.read()
            if not ret:
                break

            frame_idx += 1

            # Sample every Nth frame
            if frame_idx % FRAME_SAMPLE_RATE != 0:
                continue

            processed += 1
            job["processed_frames"] = processed
            job["progress"] = min(99, int((frame_idx / total_frames) * 100)) if total_frames > 0 else 0

            # Advance GPS
            lat, lon = gps_simulator.get_next_location(bus_id)
            timestamp = datetime.utcnow()

            # ── Vehicle detection ────────────────────────────────────
            vehicle_detections = vehicle_det.detect(frame)
            window_frames.append(vehicle_detections)

            # ── Road defect detection ─────────────────────────────────
            if pothole_det.is_ready:
                road_detections = pothole_det.detect(frame)
                for det in road_detections:
                    evt = generate_road_defect_event(
                        bus_id=bus_id,
                        latitude=lat,
                        longitude=lon,
                        detection=det,
                        timestamp=timestamp,
                        is_demo=False,
                    )
                    # Save evidence frame
                    evidence_path = _save_evidence_frame(frame, evt.event_id, upload_dir)
                    evt.evidence_image = evidence_path
                    all_events.append(evt)
                    events_generated += 1

            # ── Traffic analysis every window ─────────────────────────
            if len(window_frames) >= frames_per_window:
                analysis = _traffic_analyzer.analyze_window(window_frames)
                window_frames = []  # reset window

                traffic_evt = generate_traffic_event(
                    bus_id=bus_id,
                    latitude=lat,
                    longitude=lon,
                    analysis=analysis,
                    timestamp=timestamp,
                    is_demo=False,
                )
                if traffic_evt:
                    all_events.append(traffic_evt)
                    events_generated += 1

                # Store traffic record
                if db is not None:
                    try:
                        await db.traffic_records.insert_one({
                            "record_id": f"TRF-{str(uuid.uuid4())[:8].upper()}",
                            "bus_id": bus_id,
                            "latitude": lat,
                            "longitude": lon,
                            "timestamp": timestamp.isoformat(),
                            **analysis,
                            "is_demo": False,
                        })
                    except Exception as e:
                        logger.warning(f"Failed to store traffic record: {e}")

            # Yield to event loop periodically
            if processed % 10 == 0:
                await asyncio.sleep(0)

        cap.release()

        # ── Store events in DB ───────────────────────────────────────
        if db is not None and all_events:
            try:
                event_docs = [e.model_dump() for e in all_events]
                for doc in event_docs:
                    if isinstance(doc.get("timestamp"), datetime):
                        doc["timestamp"] = doc["timestamp"].isoformat()
                await db.events.insert_many(event_docs)
                logger.info(f"Stored {len(event_docs)} events in DB")
            except Exception as e:
                logger.error(f"Failed to store events: {e}")

        # ── Final analysis summary ────────────────────────────────────
        if window_frames:
            final_analysis = _traffic_analyzer.analyze_window(window_frames)
        else:
            final_analysis = {"vehicle_count": 0, "traffic_level": "low", "traffic_density": 0}

        result_summary = {
            "total_frames_processed": processed,
            "events_generated": events_generated,
            "final_traffic_analysis": final_analysis,
            "events": [
                {
                    "event_id": e.event_id,
                    "type": e.type,
                    "severity": e.severity,
                    "confidence": e.confidence,
                    "latitude": e.latitude,
                    "longitude": e.longitude,
                }
                for e in all_events
            ],
        }

        job["status"] = "completed"
        job["progress"] = 100
        job["events_generated"] = events_generated
        job["completed_at"] = datetime.utcnow().isoformat()
        job["result_summary"] = result_summary

        logger.info(
            f"Job {job_id} completed: {processed} frames, {events_generated} events"
        )

    except Exception as e:
        logger.error(f"Job {job_id} failed: {e}", exc_info=True)
        job["status"] = "failed"
        job["error_message"] = str(e)
        job["completed_at"] = datetime.utcnow().isoformat()

    # ── Update DB job record ─────────────────────────────────────────
    if db is not None:
        try:
            await db.processing_jobs.update_one(
                {"job_id": job_id},
                {"$set": {
                    "status": job["status"],
                    "progress": job["progress"],
                    "events_generated": job.get("events_generated", 0),
                    "error_message": job.get("error_message"),
                    "completed_at": job.get("completed_at"),
                    "result_summary": job.get("result_summary"),
                }},
                upsert=True,
            )
        except Exception as e:
            logger.warning(f"Failed to update job in DB: {e}")
