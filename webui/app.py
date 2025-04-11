from flask import Flask, render_template, request, jsonify, send_file, abort
from pathlib import Path
from typing import Dict, Any
import threading
import time
import os

from config.config_manager import ConfigManager
from storage.manager import StorageManager
from camera.recorder import CameraRecorder
from processor.video_processor import VideoProcessor

app = Flask(__name__)
config = ConfigManager()
storage_manager = StorageManager()

# Add custom template filters
@app.template_filter('strftime')
def _jinja2_filter_datetime(timestamp, fmt=None):
    from datetime import datetime
    if fmt is None:
        fmt = '%Y-%m-%d %H:%M:%S'
    return datetime.fromtimestamp(timestamp).strftime(fmt)

# Create shared instances
camera_recorder = CameraRecorder()
video_processor = VideoProcessor()

# Global variables to store system status
system_status: Dict[str, Any] = {
    "recording": False,
    "last_processed": None,
    "last_cat_detection": None,
    "storage_usage": {
        "recordings": 0,
        "cat_videos": 0
    }
}

def update_system_status():
    """Update system status information periodically."""
    while True:
        # Update storage usage
        system_status["storage_usage"]["recordings"] = storage_manager.get_total_size(
            Path(config.storage_config["recordings_dir"])
        )
        system_status["storage_usage"]["cat_videos"] = storage_manager.get_total_size(
            Path(config.storage_config["cat_videos_dir"])
        )
        
        # Check if recording is active by checking if the recording thread is alive
        if hasattr(camera_recorder, 'recording_thread') and camera_recorder.recording_thread:
            system_status["recording"] = camera_recorder.recording_thread.is_alive()
        else:
            system_status["recording"] = False
            
        # Update last cat detection time
        latest_cat_image = video_processor.get_latest_cat_image()
        if latest_cat_image and latest_cat_image.exists():
            system_status["last_cat_detection"] = latest_cat_image.stat().st_mtime
            
        time.sleep(5)  # Update every 5 seconds

# Start system status update thread
threading.Thread(target=update_system_status, daemon=True).start()

@app.route("/")
def dashboard():
    """Render main dashboard."""
    return render_template(
        "dashboard.html",
        config=config._config,
        status=system_status,
        recordings=storage_manager.list_recordings(),
        cat_videos=storage_manager.list_cat_videos()
    )

@app.route("/api/settings", methods=["GET", "POST"])
def handle_settings():
    """Get or update settings."""
    if request.method == "GET":
        return jsonify(config._config)
    
    new_settings = request.json
    for section, values in new_settings.items():
        for key, value in values.items():
            config.set_setting(value, section, key)
    
    return jsonify({"status": "success"})

@app.route("/api/model", methods=["POST"])
def upload_model():
    """Handle model file upload."""
    if "model" not in request.files:
        return jsonify({"error": "No model file provided"}), 400
    
    model_file = request.files["model"]
    if model_file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    
    # Save model file
    temp_path = Path("/tmp") / model_file.filename
    model_file.save(temp_path)
    
    try:
        new_model_path = storage_manager.save_model(temp_path)
        config.set_setting(str(new_model_path), "model", "path")
        return jsonify({"status": "success", "path": str(new_model_path)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        temp_path.unlink(missing_ok=True)

@app.route("/api/video/<folder>/<filename>")
def stream_video(folder, filename):
    """Stream a video file."""
    try:
        # Map folder name to actual directory
        if folder == "recordings":
            video_dir = config.storage_config["recordings_dir"]
        elif folder == "cat_videos":
            video_dir = config.storage_config["cat_videos_dir"]
        else:
            return jsonify({"error": "Invalid video folder"}), 400
        
        # Create the full path
        video_path = Path(video_dir) / filename
        
        # Ensure the path exists and is a file
        if not video_path.exists() or not video_path.is_file():
            return jsonify({"error": "Video file not found"}), 404
        
        # Use send_file with the absolute path and set mimetype
        return send_file(str(video_path.absolute()), mimetype='video/mp4')
    except Exception as e:
        return jsonify({"error": str(e)}), 404

@app.route("/api/latest_cat_image")
def get_latest_cat_image():
    """Get the latest cat detection image."""
    try:
        latest_image = video_processor.get_latest_cat_image()
        if not latest_image or not latest_image.exists():
            return jsonify({"error": "No cat detection image available"}), 404
            
        # Return the image file
        return send_file(str(latest_image.absolute()), mimetype='image/jpeg')
    except Exception as e:
        return jsonify({"error": str(e)}), 500
        
@app.route("/api/status")
def get_status():
    """Get current system status."""
    return jsonify(system_status)

def start_webui():
    """Start the web UI server."""
    host = config.webui_config["host"]
    port = config.webui_config["port"]
    app.run(host=host, port=port)
