import cv2
import os
import time
import datetime
import threading
from pathlib import Path
from cat_detector import CatDetector

def ensure_dir(directory):
    """Create directory if it doesn't exist"""
    Path(directory).mkdir(parents=True, exist_ok=True)

def get_directory_size(directory):
    """
    Calculate the total size of all files in a directory in bytes
    
    Args:
        directory: Path to the directory
        
    Returns:
        int: Total size in bytes
    """
    total_size = 0
    directory_path = Path(directory)
    
    for file_path in directory_path.glob('**/*'):
        if file_path.is_file():
            total_size += file_path.stat().st_size
    
    return total_size

def bytes_to_gb(bytes_value):
    """Convert bytes to gigabytes"""
    return bytes_value / (1024 ** 3)

class ContinuousRecorder:
    def __init__(self, camera_id=0, output_dir="recorded_videos", duration=60, 
                 resolution=(1920, 1080), fps=30, max_storage_gb=2):
        """
        Initialize the continuous video recorder
        
        Args:
            camera_id: Camera device ID (default: 0)
            output_dir: Directory to save recorded videos
            duration: Duration of each video in seconds (default: 60)
            resolution: Video resolution (width, height) (default: FullHD 1920x1080)
            fps: Frames per second (default: 30)
            max_storage_gb: Maximum storage in GB (default: 2)
        """
        self.camera_id = camera_id
        self.output_dir = Path(output_dir)
        self.duration = duration
        self.resolution = resolution
        self.target_fps = fps
        self.max_storage_bytes = max_storage_gb * (1024 ** 3)  # Convert GB to bytes
        self.running = False
        
        # Create output directory
        ensure_dir(self.output_dir)
        
        print(f"Continuous recorder initialized:")
        print(f"  Camera ID: {self.camera_id}")
        print(f"  Output directory: {self.output_dir}")
        print(f"  Video duration: {self.duration} seconds")
        print(f"  Resolution: {self.resolution[0]}x{self.resolution[1]}")
        print(f"  Target FPS: {self.target_fps}")
        print(f"  Maximum storage: {max_storage_gb} GB")

    def start_recording(self):
        """Start the recording process"""
        self.running = True
        self.record_thread = threading.Thread(target=self._recording_loop)
        self.record_thread.daemon = True
        self.record_thread.start()
        print("Recording started. Press Ctrl+C to stop.")

    def stop_recording(self):
        """Stop the recording process"""
        self.running = False
        if hasattr(self, 'record_thread'):
            self.record_thread.join(timeout=2.0)
        print("Recording stopped.")

    def _recording_loop(self):
        """
        Main recording loop - creates a new file every minute
        """
        while self.running:
            # Manage storage before recording a new video
            self._manage_storage()
            
            # Generate timestamp for the video filename
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            video_path = self.output_dir / f"video_{timestamp}.mp4"
            
            print(f"\n--- Starting new 1-minute recording: {video_path.name} ---")
            
            # Record a video for exactly 1 minute (self.duration seconds)
            self._record_video(str(video_path))
            
            # Print current storage usage
            current_size = get_directory_size(self.output_dir)
            print(f"Current storage usage: {bytes_to_gb(current_size):.2f} GB / {bytes_to_gb(self.max_storage_bytes):.2f} GB")
            print(f"--- Completed 1-minute recording: {video_path.name} ---\n")

    def _record_video(self, output_path):
        """
        Record a video for the specified duration
        
        Args:
            output_path: Path to save the video
        """
        # Open the camera
        cap = cv2.VideoCapture(self.camera_id)
        
        # Check if camera opened successfully
        if not cap.isOpened():
            print(f"Error: Could not open camera (device {self.camera_id})")
            return False
        
        # Set camera resolution
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
        
        # Set camera FPS (note: not all cameras support setting FPS)
        cap.set(cv2.CAP_PROP_FPS, self.target_fps)
        
        # Get actual camera properties (may differ from requested)
        actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        actual_fps = int(cap.get(cv2.CAP_PROP_FPS))
        
        print(f"Recording video:")
        print(f"  Output: {output_path}")
        print(f"  Resolution: {actual_width}x{actual_height}")
        print(f"  FPS: {actual_fps} (target: {self.target_fps})")
        print(f"  Duration: {self.duration} seconds")
        
        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, self.target_fps, (actual_width, actual_height))
        
        # Record for the specified duration
        start_time = time.time()
        frames_recorded = 0
        
        # Calculate frame interval to achieve target FPS
        frame_time = 1.0 / self.target_fps
        
        while time.time() - start_time < self.duration and self.running:
            frame_start_time = time.time()
            
            ret, frame = cap.read()
            if not ret:
                print("Error: Failed to capture frame")
                break
            
            # Write the frame to the video file
            out.write(frame)
            frames_recorded += 1
            
            # Calculate time to sleep to maintain target FPS
            processing_time = time.time() - frame_start_time
            sleep_time = max(0, frame_time - processing_time)
            
            if sleep_time > 0:
                time.sleep(sleep_time)
        
        # Release resources
        cap.release()
        out.release()
        
        elapsed_time = time.time() - start_time
        actual_fps = frames_recorded / elapsed_time if elapsed_time > 0 else 0
        
        print(f"Recording completed:")
        print(f"  Frames recorded: {frames_recorded}")
        print(f"  Elapsed time: {elapsed_time:.2f} seconds")
        print(f"  Actual FPS: {actual_fps:.2f}")
        
        return True

    def _manage_storage(self):
        """
        Manage storage by deleting old videos when the folder exceeds the maximum size
        """
        # Get current storage usage
        current_size = get_directory_size(self.output_dir)
        
        # If current size is below the limit, do nothing
        if current_size <= self.max_storage_bytes:
            return
        
        print(f"Storage limit exceeded: {bytes_to_gb(current_size):.2f} GB / {bytes_to_gb(self.max_storage_bytes):.2f} GB")
        print("Cleaning up old videos...")
        
        # Get all video files sorted by creation time (oldest first)
        video_files = sorted(
            [f for f in self.output_dir.glob("*.mp4") if f.is_file()],
            key=lambda f: f.stat().st_ctime
        )
        
        # Delete old videos until we're under the limit
        for video_file in video_files:
            if current_size <= self.max_storage_bytes:
                break
                
            file_size = video_file.stat().st_size
            print(f"Deleting old video: {video_file} ({file_size / (1024 * 1024):.2f} MB)")
            
            # Delete the file
            video_file.unlink()
            
            # Update current size
            current_size -= file_size
        
        # Print final storage usage
        current_size = get_directory_size(self.output_dir)
        print(f"Storage after cleanup: {bytes_to_gb(current_size):.2f} GB / {bytes_to_gb(self.max_storage_bytes):.2f} GB")

def main():
    try:
        # Create and start the video recorder
        recorder = ContinuousRecorder(
            camera_id=0,
            output_dir="recorded_videos",
            duration=60,  # 1 minute
            resolution=(1920, 1080),  # FullHD
            fps=30,  # 30 frames per second
            max_storage_gb=2  # 2 GB maximum storage
        )
        
        # Start recording
        recorder.start_recording()
        
        # Keep running until interrupted
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    finally:
        # Stop recording when the program is interrupted
        if 'recorder' in locals():
            recorder.stop_recording()
        
        print("Program terminated")

if __name__ == "__main__":
    main()
