"""
Position Analyzer
-----------------
Estimates the position of a detected object relative to the camera:

  Horizontal: LEFT | CENTER | RIGHT
  Distance:   NEAR | MEDIUM | FAR

Method:
  Uses bounding-box geometry against the frame dimensions.
  No depth sensor required — this is a calibrated heuristic suitable
  for a prototype/demo.

  Distance heuristic:
    Large bbox area  → NEAR  (object fills a lot of the frame)
    Medium area      → MEDIUM
    Small area       → FAR

  This is NOT centimeter-accurate distance.
  UI / voice messages clearly use "near / medium / far" language,
  not specific metric distances.

Risk contribution:
  CENTER + NEAR   → highest risk
  SIDE  + FAR     → lowest risk
"""
from typing import List, Dict, Tuple
from app.ai.detector import Detection


# ── Tunable thresholds ────────────────────────────────────────────────
# Horizontal thirds of the frame
LEFT_THRESHOLD   = 0.38   # bbox center_x < this  → LEFT
RIGHT_THRESHOLD  = 0.62   # bbox center_x > this  → RIGHT

# Fraction of frame area occupied by the bounding box
FAR_AREA_THRESHOLD    = 0.02   # < 2%  of frame area → FAR
NEAR_AREA_THRESHOLD   = 0.12   # > 12% of frame area → NEAR
# 2–12% → MEDIUM

# Risk weights (summed to produce object risk contribution)
POSITION_RISK = {
    "center": 1.0,
    "left":   0.6,
    "right":  0.6,
}

DISTANCE_RISK = {
    "near":   1.0,
    "medium": 0.6,
    "far":    0.2,
}


class PositionAnalyzer:
    """Computes spatial context for each detection in a frame."""

    def analyze(
        self,
        detection: Detection,
        frame_width: int = 640,
        frame_height: int = 480,
    ) -> Dict:
        """
        Returns position info dict for a single detection.

        Args:
            detection: Detection object with bbox [x1, y1, x2, y2]
            frame_width, frame_height: video resolution

        Returns:
            {
                "horizontal": "left" | "center" | "right",
                "distance_estimate": "near" | "medium" | "far",
                "risk_contribution": 0.0–1.0,
                "center_x_frac": float,
                "bbox_area_frac": float,
            }
        """
        x1, y1, x2, y2 = detection.bbox
        w = x2 - x1
        h = y2 - y1

        # Normalise to [0, 1]
        cx = (x1 + x2) / 2 / frame_width
        area_frac = (w * h) / (frame_width * frame_height)

        # Horizontal position
        if cx < LEFT_THRESHOLD:
            horizontal = "left"
        elif cx > RIGHT_THRESHOLD:
            horizontal = "right"
        else:
            horizontal = "center"

        # Distance estimate
        if area_frac > NEAR_AREA_THRESHOLD:
            distance = "near"
        elif area_frac < FAR_AREA_THRESHOLD:
            distance = "far"
        else:
            distance = "medium"

        # Combined risk contribution for this object
        risk = POSITION_RISK[horizontal] * DISTANCE_RISK[distance]

        return {
            "horizontal": horizontal,
            "distance_estimate": distance,
            "risk_contribution": round(risk, 3),
            "center_x_frac": round(cx, 3),
            "bbox_area_frac": round(area_frac, 4),
        }

    def analyze_all(
        self,
        detections: List[Detection],
        frame_width: int = 640,
        frame_height: int = 480,
    ) -> List[Dict]:
        """Analyze position for every detection in a frame."""
        results = []
        for det in detections:
            pos = self.analyze(det, frame_width, frame_height)
            results.append({
                "class_name": det.class_name,
                "confidence": det.confidence,
                "bbox": det.bbox,
                **pos,
            })
        return results
