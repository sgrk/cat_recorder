import threading
import time
from pathlib import Path

from camera.recorder import CameraRecorder
from processor.video_processor import VideoProcessor
from storage.manager import StorageManager
from config.config_manager import ConfigManager
from webui.app import start_webui, camera_recorder

class MainController:
    def __init__(self):
        self.config = ConfigManager()
        # Use the shared camera_recorder instance from app.py
        self.camera_recorder = camera_recorder
        self.video_processor = VideoProcessor()
        self.storage_manager = StorageManager()

        self.processing_thread = None
        self.stop_processing = threading.Event()

    def _process_videos_loop(self):
        """Continuously process new videos."""
        while not self.stop_processing.is_set():
            try:
                self.video_processor.process_new_videos()
                self.storage_manager.check_and_cleanup()
            except Exception as e:
                print(f"Error in video processing: {e}")
            
            # Sleep for a short duration before next check
            time.sleep(5)

    def run(self):
        """Start all system components."""
        try:
            # Start camera recording
            self.camera_recorder.start_recording()
            print("Camera recording started")

            # Start video processing thread
            self.stop_processing.clear()
            self.processing_thread = threading.Thread(target=self._process_videos_loop)
            self.processing_thread.start()
            print("Video processing started")

            # Start web UI
            print("Starting web UI...")
            start_webui()

        except KeyboardInterrupt:
            self.shutdown()
        except Exception as e:
            print(f"Error starting system: {e}")
            self.shutdown()

    def shutdown(self):
        """Safely shut down all system components."""
        print("\nShutting down system...")

        # Stop camera recording
        self.camera_recorder.stop_recording()
        print("Camera recording stopped")

        # Stop video processing
        self.stop_processing.set()
        if self.processing_thread:
            self.processing_thread.join()
        print("Video processing stopped")

if __name__ == "__main__":
    # Create necessary directories
    for dir_name in ["recordings", "cat_videos", "models"]:
        Path(dir_name).mkdir(exist_ok=True)

    # Start the system
    controller = MainController()
    controller.run()
