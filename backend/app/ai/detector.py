"""
Base Detector Interface
-----------------------
All detectors implement this interface so they can be swapped
or extended without changing the pipeline.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any
import numpy as np


class Detection:
    """Single detection result from a frame."""
    def __init__(
        self,
        class_id: int,
        class_name: str,
        confidence: float,
        bbox: List[float],  # [x1, y1, x2, y2]
    ):
        self.class_id = class_id
        self.class_name = class_name
        self.confidence = confidence
        self.bbox = bbox

    def to_dict(self) -> Dict[str, Any]:
        return {
            "class_id": self.class_id,
            "class_name": self.class_name,
            "confidence": round(self.confidence, 4),
            "bbox": self.bbox,
        }


class BaseDetector(ABC):
    """Abstract base class for all AI detectors."""

    @abstractmethod
    def load_model(self) -> bool:
        """Load the underlying model. Returns True if successful."""
        ...

    @abstractmethod
    def detect(self, frame: np.ndarray) -> List[Detection]:
        """Run inference on a single frame. Returns a list of detections."""
        ...

    @property
    @abstractmethod
    def is_ready(self) -> bool:
        """Returns True if the model is loaded and ready for inference."""
        ...
