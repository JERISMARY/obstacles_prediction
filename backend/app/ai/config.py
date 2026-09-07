"""
AI Module Configuration
-----------------------
Thresholds and settings for the detection pipeline.
All values are tunable for production deployment.
"""

# ── Traffic Density Thresholds ──────────────────────────────────────
TRAFFIC_THRESHOLDS = {
    "low": 20,        # < 20 vehicles/frame  → Low
    "moderate": 40,   # 20-40               → Moderate
    "high": 60,       # 40-60               → High
    # > 60            → Severe
}

# ── YOLO Vehicle Classes (COCO dataset) ─────────────────────────────
VEHICLE_CLASSES = {
    2: "car",
    3: "motorcycle",
    5: "bus",
    7: "truck",
    0: "person",      # pedestrian
    1: "bicycle",
}

# ── Confidence Thresholds ────────────────────────────────────────────
MIN_DETECTION_CONFIDENCE = 0.35   # below this, discard detection
TRAFFIC_EVENT_CONFIDENCE = 0.80   # min confidence to raise traffic event

# ── Frame Sampling ───────────────────────────────────────────────────
FRAME_SAMPLE_RATE = 5             # analyse every Nth frame
MAX_FRAMES_PER_JOB = 500          # cap for demo purposes

# ── Event Generation ─────────────────────────────────────────────────
TRAFFIC_WINDOW_SECONDS = 10       # aggregate vehicles over this window
MIN_VEHICLES_FOR_EVENT = 5        # min vehicles to create a traffic event

# ── Severity Mapping ─────────────────────────────────────────────────
SEVERITY_BY_DENSITY = {
    "severe": "critical",
    "high": "high",
    "moderate": "medium",
    "low": "low",
}

# ── Pothole Model ─────────────────────────────────────────────────────
# Set this to a custom-trained YOLO weights path when available.
# Leave None to use Demo Mode for pothole events.
POTHOLE_MODEL_PATH = None         # e.g. "models/pothole_yolov8.pt"
