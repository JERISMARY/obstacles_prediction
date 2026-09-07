"""
Live Analyzer Service
---------------------
Orchestrates the complete real-time road safety pipeline:

  Frame → VehicleDetector → PositionAnalyzer → RiskEngine
        → WarningGenerator → CooldownFilter
        → RouteRecommender → DB storage

Also manages live session state (start/stop, current bus, warnings log).

⚠ DEMO MODE:
  For the SIH prototype, a pre-recorded video simulates the live camera.
  Real camera integration: replace the frame source in run_live_session()
  with a cv2.VideoCapture(0) or RTSP stream URL.
"""
import cv2
import uuid
import logging
import asyncio
import os
import base64
import time
from datetime import datetime
from typing import Optional, Dict, List
from collections import deque

from app.ai.vehicle_detector import VehicleDetector
from app.ai.pothole_detector import PotholeDetector
from app.ai.traffic_analyzer import TrafficAnalyzer
from app.ai.position_analyzer import PositionAnalyzer
from app.ai.risk_engine import RiskEngine
from app.ai.warning_generator import WarningGenerator
from app.ai.route_recommender import RouteRecommender
from app.services.gps_simulator import gps_simulator
from app.config import settings

logger = logging.getLogger(__name__)

# ── Cooldown configuration (seconds) ────────────────────────────────
WARNING_COOLDOWNS = {
    "pothole":           8,
    "road_damage":       8,
    "waterlogging":      10,
    "pedestrian":        5,
    "oncoming_vehicle":  5,
    "vehicle":           10,
    "traffic_congestion": 20,
    "general":           12,
    "critical":          4,   # shorter cooldown for critical
}

# ── Live session store ───────────────────────────────────────────────
_sessions: Dict[str, Dict] = {}


def get_session(session_id: str) -> Optional[Dict]:
    return _sessions.get(session_id)


def get_active_session() -> Optional[Dict]:
    """Return the most recent active session."""
    for s in reversed(list(_sessions.values())):
        if s.get("active"):
            return s
    return None


def stop_all_sessions():
    for s in _sessions.values():
        s["active"] = False


class CooldownFilter:
    """Suppresses repeated warnings of the same type within a cooldown window."""
    def __init__(self):
        self._last_spoken: Dict[str, float] = {}

    def should_speak(self, warning_type: str, priority_label: str) -> bool:
        now = time.time()
        # Critical warnings get shorter cooldown
        if priority_label == "critical":
            cooldown = WARNING_COOLDOWNS.get("critical", 4)
        else:
            cooldown = WARNING_COOLDOWNS.get(warning_type, 12)

        last = self._last_spoken.get(warning_type, 0)
        if now - last >= cooldown:
            self._last_spoken[warning_type] = now
            return True
        return False

    def reset(self):
        self._last_spoken.clear()


class LiveAnalyzer:
    """
    Runs the full live AI pipeline on a video source.
    Manages a named session so the frontend can poll for results.
    """

    def __init__(self):
        self.vehicle_detector: Optional[VehicleDetector] = None
        self.pothole_detector: Optional[PotholeDetector] = None
        self.traffic_analyzer = TrafficAnalyzer()
        self.position_analyzer = PositionAnalyzer()
        self.risk_engine = RiskEngine()
        self.warning_generator = WarningGenerator()
        self.route_recommender = RouteRecommender()
        self.cooldown = CooldownFilter()

    def _ensure_detectors(self):
        if self.vehicle_detector is None:
            self.vehicle_detector = VehicleDetector(settings.YOLO_MODEL)
            self.vehicle_detector.load_model()
        if self.pothole_detector is None:
            self.pothole_detector = PotholeDetector()
            self.pothole_detector.load_model()

    def _encode_frame(self, frame) -> str:
        """Encode a cv2 frame as base64 JPEG for API delivery."""
        try:
            _, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 60])
            return base64.b64encode(buf.tobytes()).decode("utf-8")
        except Exception:
            return ""

    def _draw_overlays(self, frame, positioned_detections, risk_assessment, bus_id, lat, lon):
        """Draw bounding boxes and risk overlay on frame."""
        try:
            import numpy as np
            h, w = frame.shape[:2]

            # Colour by risk
            colors = {
                "critical": (0, 0, 220),
                "warning":  (0, 100, 240),
                "caution":  (0, 200, 240),
                "safe":     (0, 200, 80),
            }
            risk_level = risk_assessment.get("risk_level", "safe")
            border_color = colors.get(risk_level, (128, 128, 128))

            # Risk level border
            cv2.rectangle(frame, (0, 0), (w - 1, h - 1), border_color, 3)

            # Bounding boxes
            hazard_objects = {"pothole", "road_damage", "waterlogging", "person"}
            for det in positioned_detections:
                bbox = det.get("bbox", [])
                if len(bbox) < 4:
                    continue
                x1, y1, x2, y2 = int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])
                cls = det.get("class_name", "")
                conf = det.get("confidence", 0)
                pos = det.get("horizontal", "")
                dist = det.get("distance_estimate", "")

                box_color = (0, 60, 220) if cls in hazard_objects else (0, 180, 50)
                cv2.rectangle(frame, (x1, y1), (x2, y2), box_color, 2)

                label = f"{cls.upper()} {conf:.0%} {pos} {dist}"
                cv2.putText(frame, label, (x1, max(y1 - 6, 12)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, box_color, 1, cv2.LINE_AA)

            # HUD overlay
            hud_lines = [
                f"BUS: {bus_id}",
                f"GPS: {lat:.4f}, {lon:.4f}",
                f"RISK: {risk_level.upper()} ({risk_assessment.get('risk_score', 0):.0f})",
            ]
            for i, line in enumerate(hud_lines):
                cv2.putText(frame, line, (8, 20 + i * 18),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

            # Demo watermark
            cv2.putText(frame, "DEMO MODE", (w - 120, h - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 180, 255), 1, cv2.LINE_AA)
        except Exception as e:
            logger.warning(f"Overlay error: {e}")

        return frame

    async def run_session(
        self,
        session_id: str,
        video_path: str,
        bus_id: str,
        db,
        target_fps: float = 6.0,
    ):
        """
        Main async loop. Processes video frame-by-frame.
        Updates the session dict continuously so the frontend can poll.
        """
        self._ensure_detectors()
        self.cooldown.reset()

        session = _sessions[session_id]
        session["active"] = True
        session["status"] = "running"

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            session["status"] = "error"
            session["error"] = f"Cannot open video: {video_path}"
            session["active"] = False
            return

        video_fps = cap.get(cv2.CAP_PROP_FPS) or 25
        sample_every = max(1, int(video_fps / target_fps))

        frame_idx = 0
        window_frames = []
        window_size = int(target_fps * 5)   # 5-second traffic window
        processed = 0
        max_frames = 2000

        logger.info(f"Live session {session_id}: bus={bus_id}, fps={target_fps}")

        try:
            while session.get("active") and processed < max_frames:
                ret, frame = cap.read()
                if not ret:
                    # Loop video for demo
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    ret, frame = cap.read()
                    if not ret:
                        break

                frame_idx += 1
                if frame_idx % sample_every != 0:
                    continue

                processed += 1
                ts = datetime.utcnow()
                lat, lon = gps_simulator.get_next_location(bus_id)
                h, w = frame.shape[:2]

                # ── Detection ─────────────────────────────────────────
                vehicle_dets = []
                if self.vehicle_detector and self.vehicle_detector.is_ready:
                    vehicle_dets = self.vehicle_detector.detect(frame)

                pothole_dets = []
                if self.pothole_detector and self.pothole_detector.is_ready:
                    pothole_dets = self.pothole_detector.detect(frame)

                all_dets = vehicle_dets + pothole_dets

                # ── Position analysis ──────────────────────────────────
                positioned = self.position_analyzer.analyze_all(all_dets, w, h)

                # ── Traffic analysis ──────────────────────────────────
                window_frames.append(vehicle_dets)
                if len(window_frames) > window_size:
                    window_frames.pop(0)
                traffic = self.traffic_analyzer.analyze_window(window_frames)

                # ── Risk assessment ────────────────────────────────────
                risk = self.risk_engine.assess(positioned, traffic, w, h)

                # ── Route recommendation ───────────────────────────────
                route_rec = None
                if traffic.get("traffic_level") in ("high", "severe"):
                    route_rec = self.route_recommender.recommend(
                        bus_id,
                        current_traffic_level=traffic.get("traffic_level"),
                        current_risk_score=risk.get("risk_score"),
                    )
                    session["route_recommendation"] = route_rec

                # ── Warning generation ─────────────────────────────────
                warning = self.warning_generator.generate(risk, route_rec)
                if warning:
                    wtype = warning["type"]
                    plabel = warning["priority_label"]
                    if self.cooldown.should_speak(wtype, plabel):
                        warning["speak"] = True
                        warning["warning_id"] = f"WARN-{str(uuid.uuid4())[:8].upper()}"
                        warning["timestamp"] = ts.isoformat()
                        warning["latitude"] = lat
                        warning["longitude"] = lon
                        warning["bus_id"] = bus_id

                        session["warnings"].appendleft(warning)
                        session["latest_warning"] = warning

                        # Store in DB
                        if db is not None:
                            try:
                                await db.warnings.insert_one(dict(warning))
                            except Exception:
                                pass
                    else:
                        if warning:
                            warning["speak"] = False

                # ── Draw overlay ──────────────────────────────────────
                annotated = self._draw_overlays(
                    frame.copy(), positioned, risk, bus_id, lat, lon
                )
                frame_b64 = self._encode_frame(annotated)

                # ── Update session state ──────────────────────────────
                session["frame_count"] = processed
                session["latest_frame"] = frame_b64
                session["latest_detections"] = positioned
                session["latest_risk"] = risk
                session["latest_traffic"] = traffic
                session["latest_gps"] = {"latitude": lat, "longitude": lon}
                session["last_updated"] = ts.isoformat()

                # Yield to event loop
                await asyncio.sleep(0)

        except Exception as e:
            logger.error(f"Live session {session_id} error: {e}", exc_info=True)
            session["status"] = "error"
            session["error"] = str(e)
        finally:
            cap.release()
            session["active"] = False
            session["status"] = "stopped"
            logger.info(f"Live session {session_id} ended. Frames: {processed}")


def create_session(bus_id: str, video_path: str) -> str:
    session_id = f"LIVE-{str(uuid.uuid4())[:8].upper()}"
    _sessions[session_id] = {
        "session_id": session_id,
        "bus_id": bus_id,
        "video_path": video_path,
        "active": False,
        "status": "created",
        "frame_count": 0,
        "latest_frame": None,
        "latest_detections": [],
        "latest_risk": {},
        "latest_traffic": {},
        "latest_gps": {},
        "latest_warning": None,
        "warnings": deque(maxlen=100),
        "route_recommendation": None,
        "error": None,
        "created_at": datetime.utcnow().isoformat(),
        "last_updated": None,
    }
    return session_id


# Singleton analyzer
_live_analyzer: Optional[LiveAnalyzer] = None


def get_live_analyzer() -> LiveAnalyzer:
    global _live_analyzer
    if _live_analyzer is None:
        _live_analyzer = LiveAnalyzer()
    return _live_analyzer
