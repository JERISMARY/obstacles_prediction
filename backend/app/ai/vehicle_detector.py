"""
Vehicle Detector
----------------
Uses YOLOv8 (ultralytics) to detect vehicles and pedestrians
from road camera frames.

Model: yolov8n.pt (COCO-pretrained, ~6 MB)
Detected classes: car, motorcycle, bus, truck, person, bicycle
"""
import logging
import numpy as np
from typing import List

from app.ai.detector import BaseDetector, Detection
from app.ai.config import VEHICLE_CLASSES, MIN_DETECTION_CONFIDENCE

logger = logging.getLogger(__name__)


class VehicleDetector(BaseDetector):
    def __init__(self, model_path: str = "yolov8n.pt"):
        self.model_path = model_path
        self._model = None
        self._ready = False

    def load_model(self) -> bool:
        try:
            from ultralytics import YOLO
            logger.info(f"Loading YOLO model: {self.model_path}")
            self._model = YOLO(self.model_path)
            self._ready = True
            logger.info("Vehicle detector ready")
            return True
        except ImportError:
            logger.error("ultralytics not installed. Run: pip install ultralytics")
            return False
        except Exception as e:
            logger.error(f"Failed to load YOLO model: {e}")
            return False

    def detect(self, frame: np.ndarray) -> List[Detection]:
        if not self._ready or self._model is None:
            return []

        try:
            results = self._model(
                frame,
                conf=MIN_DETECTION_CONFIDENCE,
                classes=list(VEHICLE_CLASSES.keys()),
                verbose=False,
            )
            detections: List[Detection] = []
            for result in results:
                for box in result.boxes:
                    class_id = int(box.cls[0])
                    class_name = VEHICLE_CLASSES.get(class_id, "unknown")
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
            logger.error(f"Detection error: {e}")
            return []

    @property
    def is_ready(self) -> bool:
        return self._ready
