"""
Pothole / Road Defect Detector
--------------------------------
IMPORTANT — ARCHITECTURE NOTE:
--------------------------------
Pothole detection requires a custom-trained YOLO model on a road-defect dataset.
The COCO-pretrained model does NOT include pothole or road-damage classes.

This module provides a clean extension point so a custom model can be
plugged in by setting POTHOLE_MODEL_PATH in ai/config.py.

Until a trained model is available:
  → Pothole events are generated via Demo Mode (realistic simulated data)
  → This is clearly labelled as DEMO DATA throughout the system

To add a real model:
  1. Train YOLOv8 on a road-defect dataset (e.g. RDD2022, Roboflow datasets)
  2. Save weights to backend/models/pothole_yolov8.pt
  3. Set POTHOLE_MODEL_PATH = "models/pothole_yolov8.pt" in ai/config.py
"""
import logging
import numpy as np
from typing import List, Optional

from app.ai.detector import BaseDetector, Detection
from app.ai.config import POTHOLE_MODEL_PATH, MIN_DETECTION_CONFIDENCE

logger = logging.getLogger(__name__)


# Custom class IDs your trained model uses:
ROAD_DEFECT_CLASSES = {
    0: "pothole",
    1: "road_damage",
    2: "waterlogging",
    3: "traffic_sign_damage",
}


class PotholeDetector(BaseDetector):
    """
    Road defect detector.
    Uses a custom-trained YOLO model when available.
    Falls back to stub mode (no detections) otherwise.
    """

    def __init__(self, model_path: Optional[str] = POTHOLE_MODEL_PATH):
        self.model_path = model_path
        self._model = None
        self._ready = False

    def load_model(self) -> bool:
        if self.model_path is None:
            logger.warning(
                "No pothole model configured. "
                "Road defect events will use Demo Mode. "
                "Set POTHOLE_MODEL_PATH in ai/config.py to enable real detection."
            )
            return False

        try:
            from ultralytics import YOLO
            logger.info(f"Loading pothole model: {self.model_path}")
            self._model = YOLO(self.model_path)
            self._ready = True
            logger.info("Pothole detector ready")
            return True
        except Exception as e:
            logger.error(f"Failed to load pothole model: {e}")
            return False

    def detect(self, frame: np.ndarray) -> List[Detection]:
        """
        Run road defect detection.
        Returns empty list if no custom model is loaded.
        """
        if not self._ready or self._model is None:
            return []

        try:
            results = self._model(frame, conf=MIN_DETECTION_CONFIDENCE, verbose=False)
            detections: List[Detection] = []
            for result in results:
                for box in result.boxes:
                    class_id = int(box.cls[0])
                    class_name = ROAD_DEFECT_CLASSES.get(class_id, "road_defect")
                    confidence = float(box.conf[0])
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    detections.append(
                        Detection(
                            class_id=class_id,
                            class_name=class_name,
                            confidence=confidence,
                            bbox=[x1, y1, x2, y2],
                        )
                    )
            return detections
        except Exception as e:
            logger.error(f"Pothole detection error: {e}")
            return []

    @property
    def is_ready(self) -> bool:
        return self._ready

    @property
    def model_available(self) -> bool:
        return self.model_path is not None
