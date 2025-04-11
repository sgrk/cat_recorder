import cv2
import numpy as np
from pathlib import Path
from typing import List, Tuple
from ultralytics import YOLO

from config.config_manager import ConfigManager

class ModelFactory:
    @staticmethod
    def create_model(model_path: str) -> YOLO:
        """Create and return a YOLO model instance."""
        return YOLO(model_path)

class VideoProcessor:
    def __init__(self):
        self.config = ConfigManager()
        self.model = ModelFactory.create_model(self.config.model_config["path"])
        self.frame_interval = self.config.processing_config["frame_interval"]
        self.cat_detection_threshold = self.config.processing_config["cat_detection_threshold"]
        self.confidence_threshold = self.config.processing_config["confidence_threshold"]
        self.cat_class_id = self.config.model_config["cat_class_id"]

        # Initialize paths
        self.recordings_dir = Path(self.config.storage_config["recordings_dir"])
        self.cat_videos_dir = Path(self.config.storage_config["cat_videos_dir"])
        self.cat_videos_dir.mkdir(exist_ok=True)

    def extract_frames(self, video_path: Path) -> List[np.ndarray]:
        """Extract frames from video at specified intervals."""
        frames = []
        cap = cv2.VideoCapture(str(video_path))
        
        try:
            frame_count = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                if frame_count % self.frame_interval == 0:
                    frames.append(frame)
                frame_count += 1
        finally:
            cap.release()

        return frames

    def detect_objects(self, frames: List[np.ndarray]) -> List[List[Tuple[int, float]]]:
        """Detect objects in frames using YOLO model."""
        results = []
        
        for frame in frames:
            frame_results = self.model(frame,classes=[int(self.cat_class_id)], conf=self.confidence_threshold)[0]
            
            # Extract class IDs and confidence scores
            detections = []
            for box in frame_results.boxes:
                class_id = int(box.cls.item())
                confidence = float(box.conf.item())
                detections.append((class_id, confidence))
            
            results.append(detections)

        return results

    def classify_video(self, video_path: Path) -> bool:
        """Classify video based on cat detection results."""
        # Extract frames
        frames = self.extract_frames(video_path)
        if not frames:
            return False

        # Detect objects in frames
        detection_results = self.detect_objects(frames)

        # Count frames with cats
        cat_frames = 0
        for frame_detections in detection_results:
            for class_id, confidence in frame_detections:
                if class_id == self.cat_class_id:
                    cat_frames += 1
                    break

        # Calculate cat detection ratio
        cat_ratio = cat_frames / len(frames)

        # Move or delete video based on classification
        if cat_ratio >= self.cat_detection_threshold:
            # Move to cat videos directory
            new_path = self.cat_videos_dir / video_path.name
            video_path.rename(new_path)
            return True
        else:
            # Delete video
            video_path.unlink()
            return False

    def process_new_videos(self) -> None:
        """Process all videos in the recordings directory."""
        for video_path in self.recordings_dir.glob("*.mp4"):
            self.classify_video(video_path)