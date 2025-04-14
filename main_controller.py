import threading
import time
from pathlib import Path

from camera.recorder import CameraRecorder
from processor.video_processor import VideoProcessor
from storage.manager import StorageManager
from config.config_manager import ConfigManager
from restart_manager import RestartManager
from webui.app import start_webui, camera_recorder

class MainController:
    def __init__(self):
        self.config = ConfigManager()
        # Use the shared camera_recorder instance from app.py
        self.camera_recorder = camera_recorder
        self.video_processor = VideoProcessor()
        self.storage_manager = StorageManager()
        self.restart_manager = RestartManager()

        # Clear all files in the recordings folder at startup
        self.storage_manager.clear_directory(self.storage_manager.recordings_dir)
        print("Cleared all files in recordings folder")

        self.processing_thread = None
        self.stop_processing = threading.Event()
        
        # Register modules for restart
        self.register_restart_handlers()

    def register_restart_handlers(self):
        """Register all modules that can be restarted."""
        self.restart_manager.register_module("camera", self.restart_camera)
        self.restart_manager.register_module("processor", self.restart_processor)
        self.restart_manager.register_module("storage", self.restart_storage)
        
    def restart_camera(self):
        """Restart the camera recorder module."""
        print("Restarting camera recorder...")
        self.camera_recorder.stop_recording()
        # Reload config
        self.camera_recorder = CameraRecorder()
        self.camera_recorder.start_recording()
        print("Camera recorder restarted")
        
    def restart_processor(self):
        """Restart the video processor module."""
        print("Restarting video processor...")
        # Create a new processor instance with updated config
        self.video_processor = VideoProcessor()
        print("Video processor restarted")
        
    def restart_storage(self):
        """Restart the storage manager module."""
        print("Restarting storage manager...")
        self.storage_manager = StorageManager()
        print("Storage manager restarted")

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
    for dir_name in ["recordings", "cat_videos", "models", "cat_images"]:
        Path(dir_name).mkdir(exist_ok=True)

    # Start the system
    controller = MainController()
    
    # Make the controller instance accessible to the restart manager
    # This allows the WebUI to access the controller for module restarts
    RestartManager()._controller = controller
    
    controller.run()
