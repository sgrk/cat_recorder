import json
from pathlib import Path

class Config:
    def __init__(self, config_path="config.json"):
        """
        Load configuration from a JSON file
        
        Args:
            config_path: Path to the configuration file
        """
        self.config_path = Path(config_path)
        self.load_config()
    
    def load_config(self):
        """Load configuration from the JSON file"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            config = json.load(f)
        
        # Camera settings
        self.camera = config.get('camera', {})
        self.camera_id = self.camera.get('device_id', 0)
        resolution = self.camera.get('resolution', {})
        self.width = resolution.get('width', 1920)
        self.height = resolution.get('height', 1080)
        self.fps = self.camera.get('fps', 30)
        
        # Recording settings
        self.recording = config.get('recording', {})
        self.recording_dir = self.recording.get('output_dir', 'recorded_videos')
        self.duration = self.recording.get('duration', 60)
        self.max_storage_gb = self.recording.get('max_storage_gb', 2)
        
        # Cat detection settings
        self.cat_detection = config.get('cat_detection', {})
        self.model_path = self.cat_detection.get('model_path', 'detect_kinako_best.pt')
        self.cat_videos_dir = self.cat_detection.get('output_dir', 'cat_videos')
        self.frame_interval = self.cat_detection.get('frame_interval', 30)
        self.threshold = self.cat_detection.get('threshold', 0.5)
    
    @property
    def resolution(self):
        """Get resolution as a tuple"""
        return (self.width, self.height)