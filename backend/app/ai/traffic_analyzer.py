"""
Traffic Analyzer
-----------------
Takes vehicle detections from a frame window and computes:
  - vehicle_count
  - vehicle_types breakdown
  - traffic_density (0–100 score)
  - traffic_level (low / moderate / high / severe)
"""
from typing import List, Dict, Tuple
from app.ai.detector import Detection
from app.ai.config import TRAFFIC_THRESHOLDS, SEVERITY_BY_DENSITY


class TrafficAnalyzer:
    def __init__(self):
        self.thresholds = TRAFFIC_THRESHOLDS

    def analyze(self, detections: List[Detection]) -> Dict:
        """
        Analyze a list of detections from one frame.
        Returns traffic summary dict.
        """
        # Count by type
        vehicle_types: Dict[str, int] = {}
        for det in detections:
            name = det.class_name
            vehicle_types[name] = vehicle_types.get(name, 0) + 1

        total = len(detections)
        density = self._compute_density(total)
        level = self._classify_level(total)

        return {
            "vehicle_count": total,
            "vehicle_types": vehicle_types,
            "traffic_density": density,
            "traffic_level": level,
        }

    def analyze_window(self, frame_detections: List[List[Detection]]) -> Dict:
        """
        Analyze detections across multiple frames (a time window).
        Returns averaged summary.
        """
        if not frame_detections:
            return {
                "vehicle_count": 0,
                "vehicle_types": {},
                "traffic_density": 0.0,
                "traffic_level": "low",
            }

        totals: Dict[str, int] = {}
        counts = []
        for frame in frame_detections:
            counts.append(len(frame))
            for det in frame:
                totals[det.class_name] = totals.get(det.class_name, 0) + 1

        avg_count = sum(counts) / len(counts)
        peak_count = max(counts)

        # Use peak for level classification (worst case)
        level = self._classify_level(peak_count)
        density = self._compute_density(avg_count)

        # Average type counts across frames
        avg_types = {k: round(v / len(frame_detections)) for k, v in totals.items()}

        return {
            "vehicle_count": round(avg_count),
            "peak_vehicle_count": peak_count,
            "vehicle_types": avg_types,
            "traffic_density": density,
            "traffic_level": level,
        }

    def _compute_density(self, vehicle_count: float) -> float:
        """Convert vehicle count to 0–100 density score."""
        max_vehicles = 80  # calibration: 80 vehicles = 100% density
        return min(100.0, round((vehicle_count / max_vehicles) * 100, 1))

    def _classify_level(self, vehicle_count: float) -> str:
        if vehicle_count < self.thresholds["low"]:
            return "low"
        elif vehicle_count < self.thresholds["moderate"]:
            return "moderate"
        elif vehicle_count < self.thresholds["high"]:
            return "high"
        else:
            return "severe"

    def should_raise_event(self, analysis: Dict) -> bool:
        """Returns True if traffic analysis warrants generating an event."""
        return analysis["traffic_level"] in ("high", "severe")

    def get_severity(self, traffic_level: str) -> str:
        return SEVERITY_BY_DENSITY.get(traffic_level, "low")
