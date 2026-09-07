"""
Risk Engine
-----------
Converts a set of positioned detections + traffic analysis into a
structured risk assessment.

Risk Score: 0–100
  0–30   Safe
  31–60  Caution
  61–80  Warning
  81–100 Critical

The engine:
  1. Scores each detected object individually.
  2. Combines scores (not additive — uses weighted-max to avoid
     inflating score when the same hazard is detected twice).
  3. Applies traffic-density penalty.
  4. Detects possible oncoming vehicles via frame-to-frame tracking.
  5. Handles multiple simultaneous hazards.

SAFETY NOTE:
  This is a prototype risk estimator, not a certified ADAS system.
  Confidence thresholds are deliberately conservative.
  Low-confidence detections contribute smaller risk scores.
  Messages use language like "possible" / "caution" for uncertain cases.
"""
import logging
from typing import List, Dict, Optional
from collections import deque

logger = logging.getLogger(__name__)

# ── Object risk weights ───────────────────────────────────────────────
OBJECT_BASE_RISK = {
    # Road defects
    "pothole":             85,
    "road_damage":         70,
    "waterlogging":        65,
    "traffic_sign_damage": 40,
    # Vehicles (depend on position + direction)
    "car":                 30,
    "motorcycle":          35,
    "bus":                 40,
    "truck":               45,
    "person":              55,   # pedestrian in road — high risk
    "bicycle":             35,
    # Generic
    "unknown":             25,
}

# Objects that are always concerning when center+near
HIGH_PRIORITY_OBJECTS = {"pothole", "road_damage", "waterlogging", "person"}

# ── Risk thresholds ──────────────────────────────────────────────────
RISK_LEVELS = [
    (81, "critical"),
    (61, "warning"),
    (31, "caution"),
    (0,  "safe"),
]

# ── Traffic penalty ──────────────────────────────────────────────────
TRAFFIC_DENSITY_PENALTY = {
    "severe":   20,
    "high":     12,
    "moderate":  5,
    "low":       0,
}

# ── Oncoming vehicle detection ───────────────────────────────────────
# We track bbox center-x across N frames.
# If a vehicle's center-x is moving toward the frame center over
# multiple frames AND it's in the center horizontal zone, we flag it
# as a possible oncoming vehicle.
TRACKING_HISTORY = 8   # frames to track
ONCOMING_CONFIDENCE_THRESHOLD = 0.60


class ObjectTracker:
    """
    Simple centroid tracker for estimating object motion direction.
    Tracks detected objects across frames using IoU / proximity.
    """
    def __init__(self, max_history: int = TRACKING_HISTORY):
        self.max_history = max_history
        # track_id → deque of (cx, cy, area) tuples
        self._tracks: Dict[str, deque] = {}
        self._next_id = 0

    def update(self, positioned_detections: List[Dict]) -> List[Dict]:
        """
        Match current detections to existing tracks.
        Returns detections enriched with motion info.
        """
        enriched = []
        for det in positioned_detections:
            cx = det.get("center_x_frac", 0.5)
            area = det.get("bbox_area_frac", 0.05)
            track_id = self._find_or_create(cx, area, det["class_name"])

            history = list(self._tracks[track_id])
            motion = self._estimate_motion(history)

            enriched.append({
                **det,
                "track_id": track_id,
                "motion": motion,  # "approaching" | "receding" | "lateral" | "unknown"
            })
        return enriched

    def _find_or_create(self, cx: float, area: float, cls: str) -> str:
        """Find closest existing track or create a new one."""
        best_id = None
        best_dist = 0.15  # max proximity threshold

        for tid, history in self._tracks.items():
            if not history:
                continue
            last_cx, last_area, last_cls = history[-1]
            if last_cls != cls:
                continue
            dist = abs(cx - last_cx) + abs(area - last_area)
            if dist < best_dist:
                best_dist = dist
                best_id = tid

        if best_id is None:
            best_id = str(self._next_id)
            self._next_id += 1
            self._tracks[best_id] = deque(maxlen=self.max_history)

        self._tracks[best_id].append((cx, area, cls))
        return best_id

    def _estimate_motion(self, history: list) -> str:
        """
        Estimate motion direction from bbox area change.
        Increasing area → approaching (object getting closer).
        Decreasing area → receding.
        """
        if len(history) < 3:
            return "unknown"

        areas = [h[1] for h in history[-4:]]
        area_change = areas[-1] - areas[0]

        if area_change > 0.01:
            return "approaching"
        elif area_change < -0.01:
            return "receding"
        else:
            return "lateral"


class RiskEngine:
    """
    Computes road risk from positioned+tracked detections + traffic.
    """
    def __init__(self):
        self.tracker = ObjectTracker()

    def assess(
        self,
        positioned_detections: List[Dict],
        traffic_analysis: Optional[Dict] = None,
        frame_width: int = 640,
        frame_height: int = 480,
    ) -> Dict:
        """
        Full risk assessment for one frame.

        Returns:
        {
            "risk_score": 0–100,
            "risk_level": "safe"|"caution"|"warning"|"critical",
            "hazards": [...],         # significant threats
            "oncoming_vehicles": [...],
            "traffic_penalty": int,
            "combined_message_context": {...},
        }
        """
        # Track objects across frames
        tracked = self.tracker.update(positioned_detections)

        # Score each detection
        scored_hazards = []
        oncoming_vehicles = []

        for det in tracked:
            base = OBJECT_BASE_RISK.get(det["class_name"], 25)
            pos_factor = det.get("risk_contribution", 0.5)
            conf_factor = det.get("confidence", 0.5)

            # Scale risk by position and confidence
            score = base * pos_factor * min(conf_factor / 0.5, 1.2)
            score = min(score, 95)

            # Detect oncoming vehicles
            is_oncoming = False
            if det["class_name"] in ("car", "motorcycle", "bus", "truck", "bicycle"):
                if (det.get("motion") == "approaching"
                        and det.get("horizontal") == "center"
                        and det.get("confidence", 0) >= ONCOMING_CONFIDENCE_THRESHOLD):
                    is_oncoming = True
                    score = min(score * 1.4, 95)  # boost score for oncoming

            hazard = {
                "object": det["class_name"],
                "position": det.get("horizontal", "center"),
                "distance": det.get("distance_estimate", "medium"),
                "motion": det.get("motion", "unknown"),
                "confidence": det.get("confidence", 0),
                "score": round(score, 1),
                "is_oncoming": is_oncoming,
                "in_path": det.get("horizontal") == "center",
            }
            scored_hazards.append(hazard)
            if is_oncoming:
                oncoming_vehicles.append(hazard)

        # Traffic penalty
        traffic_level = "low"
        traffic_penalty = 0
        if traffic_analysis:
            traffic_level = traffic_analysis.get("traffic_level", "low")
            traffic_penalty = TRAFFIC_DENSITY_PENALTY.get(traffic_level, 0)

        # Composite risk — weighted-max (not pure sum, to avoid inflation)
        if scored_hazards:
            max_score = max(h["score"] for h in scored_hazards)
            # Secondary hazards add partial contribution
            secondary_sum = sum(h["score"] for h in scored_hazards if h["score"] < max_score)
            composite = max_score + min(secondary_sum * 0.25, 20)
        else:
            composite = 0

        composite = min(100, composite + traffic_penalty)

        # Classify level
        risk_level = "safe"
        for threshold, level in RISK_LEVELS:
            if composite >= threshold:
                risk_level = level
                break

        # Sort hazards by score descending
        scored_hazards.sort(key=lambda h: h["score"], reverse=True)

        return {
            "risk_score": round(composite, 1),
            "risk_level": risk_level,
            "hazards": scored_hazards[:5],   # top 5 hazards
            "oncoming_vehicles": oncoming_vehicles,
            "traffic_level": traffic_level,
            "traffic_penalty": traffic_penalty,
            "total_detections": len(positioned_detections),
        }
