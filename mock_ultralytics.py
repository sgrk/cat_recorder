"""
Mock implementation of the YOLO model for testing purposes.
This avoids having to install the full ultralytics package.
"""
import numpy as np
import random
from pathlib import Path

class Box:
    def __init__(self, cls, conf):
        self.cls = np.array([cls])
        self.conf = np.array([conf])
    
    def item(self):
        return self.cls[0] if hasattr(self, 'cls') else self.conf[0]

class Boxes:
    def __init__(self, num_boxes=1, cat_class_id=0):
        self.boxes = []
        for _ in range(num_boxes):
            cls = cat_class_id if random.random() > 0.5 else 1
            conf = random.uniform(0.5, 0.9)
            self.boxes.append(Box(cls, conf))
    
    @property
    def cls(self):
        return [box.cls for box in self.boxes]
    
    @property
    def conf(self):
        return [box.conf for box in self.boxes]

class Results:
    def __init__(self, frame, cat_class_id=0):
        self.orig_img = frame
        self.boxes = Boxes(num_boxes=random.randint(0, 3), cat_class_id=cat_class_id)
    
    def plot(self):
        """Return a copy of the image with detection boxes drawn."""
        return self.orig_img.copy()

class YOLO:
    def __init__(self, model_path):
        self.model_path = model_path
        print(f"Loaded mock YOLO model from {model_path}")
    
    def __call__(self, frame, classes=None, conf=0.5):
        """Process a frame and return detection results."""
        cat_class_id = classes[0] if classes else 0
        return [Results(frame, cat_class_id)]