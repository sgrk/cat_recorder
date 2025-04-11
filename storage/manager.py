from pathlib import Path
from abc import ABC, abstractmethod
from typing import List
from config.config_manager import ConfigManager

class StorageStrategy(ABC):
    @abstractmethod
    def cleanup(self, directory: Path, max_size: int) -> None:
        pass

class OldestFirstStrategy(StorageStrategy):
    def cleanup(self, directory: Path, max_size: int) -> None:
        """Delete oldest files first until total size is under max_size."""
        if not directory.exists():
            return

        # Get all MP4 files and their sizes
        files = [(f, f.stat().st_size) for f in directory.glob("*.mp4")]
        total_size = sum(size for _, size in files)

        if total_size <= max_size:
            return

        # Sort files by creation time
        files.sort(key=lambda x: x[0].stat().st_mtime)

        # Delete oldest files until we're under the limit
        while total_size > max_size and files:
            file_path, file_size = files.pop(0)
            file_path.unlink()
            total_size -= file_size

class StorageManager:
    def __init__(self, strategy: StorageStrategy = None):
        self.config = ConfigManager()
        self.strategy = strategy or OldestFirstStrategy()
        
        # Initialize paths
        self.recordings_dir = Path(self.config.storage_config["recordings_dir"])
        self.cat_videos_dir = Path(self.config.storage_config["cat_videos_dir"])
        self.models_dir = Path(self.config.storage_config["models_dir"])
        self.cat_images_dir = Path(self.config.storage_config["cat_images_dir"])
        
        # Create directories if they don't exist
        self.recordings_dir.mkdir(exist_ok=True)
        self.cat_videos_dir.mkdir(exist_ok=True)
        self.models_dir.mkdir(exist_ok=True)
        self.cat_images_dir.mkdir(exist_ok=True)

    def get_total_size(self, directory: Path) -> int:
        """Get total size of MP4 files in directory."""
        if not directory.exists():
            return 0
        return sum(f.stat().st_size for f in directory.glob("*.mp4"))

    def check_and_cleanup(self) -> None:
        """Check storage limits and clean up if necessary."""
        max_size = self.config.storage_config["max_storage_size"]
        
        # Clean up recordings directory
        self.strategy.cleanup(self.recordings_dir, max_size)
        
        # Clean up cat videos directory
        self.strategy.cleanup(self.cat_videos_dir, max_size)

    def list_recordings(self) -> List[dict]:
        """List all recordings with their metadata."""
        recordings = []
        for file_path in self.recordings_dir.glob("*.mp4"):
            stat = file_path.stat()
            recordings.append({
                "name": file_path.name,
                "size": stat.st_size,
                "created": stat.st_mtime,
                "path": str(file_path)
            })
        return recordings

    def list_cat_videos(self) -> List[dict]:
        """List all cat videos with their metadata."""
        cat_videos = []
        for file_path in self.cat_videos_dir.glob("*.mp4"):
            stat = file_path.stat()
            cat_videos.append({
                "name": file_path.name,
                "size": stat.st_size,
                "created": stat.st_mtime,
                "path": str(file_path)
            })
        return cat_videos

    def save_model(self, model_file: Path) -> Path:
        """Save uploaded model file to models directory."""
        if not model_file.exists():
            raise FileNotFoundError(f"Model file not found: {model_file}")
        
        dest_path = self.models_dir / model_file.name
        with open(model_file, "rb") as src, open(dest_path, "wb") as dst:
            dst.write(src.read())
        
        return dest_path
        
    def save_cat_image(self, image: np.ndarray, timestamp: float) -> Path:
        """Save cat detection image to cat_images directory."""
        import cv2
        import time
        from datetime import datetime
        
        # Create filename with timestamp
        filename = f"cat_detected_{int(timestamp)}.jpg"
        image_path = self.cat_images_dir / filename
        
        # Save image
        cv2.imwrite(str(image_path), image)
        
        # Clean up old images if we have more than 20
        self._cleanup_cat_images(20)
        
        return image_path
        
    def _cleanup_cat_images(self, max_count: int) -> None:
        """Keep only the most recent max_count cat images."""
        images = list(self.cat_images_dir.glob("*.jpg"))
        if len(images) <= max_count:
            return
            
        # Sort by modification time (newest first)
        images.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        # Delete oldest images
        for image in images[max_count:]:
            image.unlink()
            
    def get_latest_cat_image(self) -> Path:
        """Get the path to the most recent cat detection image."""
        images = list(self.cat_images_dir.glob("*.jpg"))
        if not images:
            return None
            
        # Sort by modification time (newest first)
        images.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        return images[0]