# config/bedrock_config.py

# config/config_manager.py

import yaml
import os
from threading import Lock

class ConfigManager:
    def __init__(self, config_path="config.yaml"):
        self.config_path = config_path
        self._lock = Lock()
        self._load()

    def _load(self):
        with self._lock:
            if not os.path.exists(self.config_path):
                self._config = {}
                return
            with open(self.config_path, "r") as f:
                self._config = yaml.safe_load(f) or {}

    def get(self, *keys, default=None):
        node = self._config
        for key in keys:
            if isinstance(node, dict) and key in node:
                node = node[key]
            else:
                return default
        return node

    def update(self, key_path, value):
        with self._lock:
            node = self._config
            keys = key_path.split("/")
            for key in keys[:-1]:
                node = node.setdefault(key, {})
            node[keys[-1]] = value
            with open(self.config_path, "w") as f:
                yaml.safe_dump(self._config, f)

    def all(self):
        return self._config

# Singleton instance
config_manager = ConfigManager()
