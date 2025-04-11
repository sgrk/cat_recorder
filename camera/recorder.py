import cv2
import time
from pathlib import Path
from datetime import datetime
from threading import Thread, Event
from typing import Optional

from config.config_manager import ConfigManager

class CameraRecorder:
    def __init__(self):
        self.config = ConfigManager()
        self.recording_thread: Optional[Thread] = None
        self.stop_event = Event()
        
        # Initialize camera settings
        self.device_id = self.config.camera_config["device_id"]
        self.fps = self.config.camera_config["fps"]
        self.width = self.config.camera_config["resolution"]["width"]
        self.height = self.config.camera_config["resolution"]["height"]
        self.recording_duration = self.config.camera_config["recording_duration"]
        
        # Initialize paths
        self.recordings_dir = Path(self.config.storage_config["recordings_dir"])
        self.recordings_dir.mkdir(exist_ok=True)

    def start_recording(self) -> None:
        """Start recording in a separate thread."""
        if self.recording_thread and self.recording_thread.is_alive():
            return

        self.stop_event.clear()
        self.recording_thread = Thread(target=self._record_video)
        self.recording_thread.start()

    def stop_recording(self) -> None:
        """Stop the recording thread."""
        if self.recording_thread and self.recording_thread.is_alive():
            self.stop_event.set()
            self.recording_thread.join()

    def _record_video(self) -> None:
        """Record video in chunks of specified duration."""
        cap = cv2.VideoCapture(self.device_id)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        cap.set(cv2.CAP_PROP_FPS, self.fps)

        if not cap.isOpened():
            raise RuntimeError(f"Failed to open camera device {self.device_id}")

        try:
            while not self.stop_event.is_set():
                # Create a new video file
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = self.recordings_dir / f"video_{timestamp}.mp4"
                
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                out = cv2.VideoWriter(
                    str(output_path),
                    fourcc,
                    self.fps,
                    (self.width, self.height)
                )

                start_time = time.time()
                frames_written = 0
                expected_frames = self.recording_duration * self.fps

                while not self.stop_event.is_set():
                    ret, frame = cap.read()
                    if not ret:
                        break

                    out.write(frame)
                    frames_written += 1

                    # Check if we've recorded enough frames
                    if frames_written >= expected_frames:
                        break

                    # Add small delay to maintain FPS
                    time.sleep(1/self.fps)

                out.release()

                # Check if we need to stop
                if time.time() - start_time >= self.recording_duration:
                    self.check_storage_limit()

        finally:
            cap.release()

    def check_storage_limit(self) -> None:
        """Check storage limit and delete oldest files if necessary."""
        max_size = self.config.storage_config["max_storage_size"]
        current_size = sum(f.stat().st_size for f in self.recordings_dir.glob("*.mp4"))

        if current_size > max_size:
            files = sorted(
                self.recordings_dir.glob("*.mp4"),
                key=lambda x: x.stat().st_mtime
            )
            
            while current_size > max_size and files:
                oldest_file = files.pop(0)
                current_size -= oldest_file.stat().st_size
                oldest_file.unlink()