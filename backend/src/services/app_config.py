import json
import logging
import os
from pathlib import Path
from threading import RLock
from typing import Optional, Dict, Any

from services.config import settings


logger = logging.getLogger(__name__)


class AppConfigService:
    """Manage persisted application configuration (e.g., API keys)."""

    def __init__(self) -> None:
        self._lock = RLock()
        self.config_path = Path(settings.data_dir) / "app_config.json"
        self._config: Dict[str, Any] = {}
        self._ensure_directory()
        self._load()

    def _ensure_directory(self) -> None:
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

    def _load(self) -> None:
        if self.config_path.exists():
            try:
                with self.config_path.open("r", encoding="utf-8") as fh:
                    self._config = json.load(fh)
            except Exception as exc:  # pragma: no cover - defensive fallback
                logger.error("Failed to load app configuration: %s", exc)
                self._config = {}
        else:
            self._config = {}

        # Bootstrap from environment if provided and not already persisted
        if not self.get_openai_api_key():
            env_key = os.environ.get("OPENAI_API_KEY")
            if env_key and not env_key.startswith("your_openai_api_key_here"):
                self._config["openai_api_key"] = env_key.strip()
                self._save()

    def _save(self) -> None:
        with self.config_path.open("w", encoding="utf-8") as fh:
            json.dump(self._config, fh, indent=2, ensure_ascii=False)

    def get_openai_api_key(self) -> Optional[str]:
        with self._lock:
            key = self._config.get("openai_api_key")
            if key:
                return key.strip()
            # Fallback to settings for backward compatibility
            if settings.openai_api_key and not settings.openai_api_key.startswith("your_openai_api_key_here"):
                return settings.openai_api_key.strip()
            return None

    def set_openai_api_key(self, api_key: str) -> None:
        normalized = api_key.strip()
        if not normalized:
            raise ValueError("API key cannot be empty")
        with self._lock:
            self._config["openai_api_key"] = normalized
            self._save()

    def clear_openai_api_key(self) -> None:
        with self._lock:
            if "openai_api_key" in self._config:
                self._config.pop("openai_api_key")
                self._save()

    def get_openai_key_metadata(self) -> Dict[str, Any]:
        key = self.get_openai_api_key()
        if not key:
            return {"configured": False, "masked_key": None}
        masked = f"sk-...{key[-4:]}" if len(key) > 4 else "sk-..."
        return {"configured": True, "masked_key": masked}


app_config = AppConfigService()

