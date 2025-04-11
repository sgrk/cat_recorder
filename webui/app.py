from flask import Flask, render_template, request, jsonify, send_file
from pathlib import Path
from typing import Dict, Any
import threading
import time

from config.config_manager import ConfigManager
from storage.manager import StorageManager

app = Flask(__name__)
config = ConfigManager()
storage_manager = StorageManager()

# Global variables to store system status
system_status: Dict[str, Any] = {
    "recording": False,
    "last_processed": None,
    "storage_usage": {
        "recordings": 0,
        "cat_videos": 0
    }
}

def update_storage_usage():
    """Update storage usage information periodically."""
    while True:
        system_status["storage_usage"]["recordings"] = storage_manager.get_total_size(
            Path(config.storage_config["recordings_dir"])
        )
        system_status["storage_usage"]["cat_videos"] = storage_manager.get_total_size(
            Path(config.storage_config["cat_videos_dir"])
        )
        time.sleep(60)  # Update every minute

# Start storage usage update thread
threading.Thread(target=update_storage_usage, daemon=True).start()

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

@app.route("/api/video/<path:video_path>")
def stream_video(video_path):
    """Stream a video file."""
    try:
        return send_file(video_path)
    except Exception as e:
        return jsonify({"error": str(e)}), 404

def start_webui():
    """Start the web UI server."""
    host = config.webui_config["host"]
    port = config.webui_config["port"]
    app.run(host=host, port=port)