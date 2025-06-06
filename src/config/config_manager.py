# config/bedrock_config.py

# config/config_manager.py

import yaml
import os
from threading import Lock
import logging
from utils.fsutils import find_workspace_root
from utils.config_logger import setup_logger
from utils.config_logger import get_agent_logger

logger = get_agent_logger()

class ConfigManager:
    def __init__(self, config_file="config.yaml"):

        self.config_path = os.path.join(find_workspace_root(), config_file)
        self._lock = Lock()
        self._load()

    def _load(self):
        with self._lock:
            if not os.path.exists(self.config_path):
                logger.error(f'Config file not found: {self.config_path}')
                self._config = {}
                return
            with open(self.config_path, "r") as f:
                self._config = yaml.safe_load(f) or {}
                logger.info(f"config loaded")

    def get(self, *keys, default=None):
        node = self._config
        logger.debug(f'Get: keys = {keys}')
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

    def get_agents(self) -> list[dict[str, any]]:
        return self._config.get("agents", [])

    def get_agent_by_name(self, name: str) -> dict[str, any]:
        for agent in self.get_agents():
            if agent.get("name") == name:
                return agent
        return None

# Singleton instance
config_manager = ConfigManager()
