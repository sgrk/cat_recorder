import cv2
import os
from pathlib import Path
from ultralytics import YOLO

class CatDetector:
    def __init__(self, model_path="detect_kinako_best.pt", cat_videos_dir="cat_videos"):
        """
        Initialize the cat detector
        
        Args:
            model_path: Path to the YOLO model file
            cat_videos_dir: Directory to store videos with detected cats
        """
        self.model = YOLO(model_path)
        self.cat_videos_dir = Path(cat_videos_dir)
        self.cat_videos_dir.mkdir(parents=True, exist_ok=True)
    
    def extract_frames(self, video_path, frame_interval=30):
        """
        Extract frames from a video at specified intervals
        
        Args:
            video_path: Path to the video file
            frame_interval: Extract one frame every N frames
            
        Returns:
            list: List of extracted frames
        """
        frames = []
        cap = cv2.VideoCapture(str(video_path))
        
        frame_count = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            if frame_count % frame_interval == 0:
                frames.append(frame)
            
            frame_count += 1
        
        cap.release()
        return frames
    
    def detect_cats(self, frames):
        """
        Detect cats in the given frames using YOLO
        
        Args:
            frames: List of frames to process
            
        Returns:
            float: Percentage of frames containing cats
        """
        cat_count = 0
        
        for frame in frames:
            results = self.model(frame)
            
            # Check if class 0 (cat) is detected in the frame
            for result in results:
                if any(box.cls == 0 for box in result.boxes):
                    cat_count += 1
                    break
        
        return cat_count / len(frames) if frames else 0
    
    def process_video(self, video_path):
        """
        Process a video file to detect cats
        
        Args:
            video_path: Path to the video file
            
        Returns:
            bool: True if the video contains cats in more than 50% of frames
        """
        # Extract frames
        frames = self.extract_frames(video_path)
        if not frames:
            print(f"No frames extracted from {video_path}")
            return False
        
        # Detect cats
        cat_percentage = self.detect_cats(frames)
        print(f"Cat detection percentage for {video_path}: {cat_percentage:.2%}")
        
        # If cats are detected in more than 50% of frames, move the video
        if cat_percentage > 0.5:
            video_path = Path(video_path)
            new_path = self.cat_videos_dir / video_path.name
            video_path.rename(new_path)
            print(f"Moved {video_path} to {new_path}")
            return True
            
        return False