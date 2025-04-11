import yaml
from pathlib import Path
from typing import Any, Dict

class ConfigManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        
        self._config_path = Path("config.yaml")
        self._config = self._load_config()
        self._initialized = True

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if not self._config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self._config_path}")
        
        with open(self._config_path, "r") as f:
            return yaml.safe_load(f)

    def save_config(self) -> None:
        """Save current configuration to YAML file."""
        with open(self._config_path, "w") as f:
            yaml.dump(self._config, f, default_flow_style=False)

    def get_setting(self, *keys: str) -> Any:
        """Get a setting value using nested keys."""
        value = self._config
        for key in keys:
            value = value[key]
        return value

    def set_setting(self, value: Any, *keys: str) -> None:
        """Set a setting value using nested keys."""
        config = self._config
        for key in keys[:-1]:
            config = config[key]
        config[keys[-1]] = value
        self.save_config()

    @property
    def camera_config(self) -> Dict[str, Any]:
        return self._config["camera"]

    @property
    def storage_config(self) -> Dict[str, Any]:
        return self._config["storage"]

    @property
    def processing_config(self) -> Dict[str, Any]:
        return self._config["processing"]

    @property
    def model_config(self) -> Dict[str, Any]:
        return self._config["model"]

    @property
    def webui_config(self) -> Dict[str, Any]:
        return self._config["webui"]