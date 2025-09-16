import json
import logging
from pathlib import Path
from threading import RLock
from typing import Dict, List, Any

from services.config import settings

logger = logging.getLogger(__name__)


class SourceConfigService:
    """Manage dynamic news source configuration and persistence."""

    def __init__(self):
        self._lock = RLock()
        self.config_path = Path(settings.data_dir) / "source_config.json"
        self.active_sources: List[str] = []
        self.custom_sources: Dict[str, Dict[str, Any]] = {}
        self._ensure_directory()
        self._load()

    def _ensure_directory(self) -> None:
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

    def _load(self) -> None:
        if not self.config_path.exists():
            logger.info("Source configuration not found. Initializing with defaults.")
            self.active_sources = list(settings.source_list)
            self.custom_sources = {}
            self._save()
            return

        try:
            with self.config_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            self.active_sources = data.get("active_sources", []) or []
            self.custom_sources = data.get("custom_sources", {}) or {}
            self._sanitize_active_sources()
        except Exception as exc:  # pragma: no cover - defensive recovery
            logger.error("Failed to load source configuration: %s", exc)
            self.active_sources = list(settings.source_list)
            self.custom_sources = {}
            self._save()

    def _sanitize_active_sources(self) -> None:
        seen = set()
        cleaned: List[str] = []
        for domain in self.active_sources:
            if not isinstance(domain, str):
                continue
            normalized = domain.strip().lower()
            if normalized and normalized not in seen:
                cleaned.append(normalized)
                seen.add(normalized)
        self.active_sources = cleaned

    def _save(self) -> None:
        with self._lock:
            payload = {
                "active_sources": self.active_sources,
                "custom_sources": self.custom_sources,
            }
            with self.config_path.open("w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)

    def get_active_sources(self) -> List[str]:
        with self._lock:
            return list(self.active_sources)

    def is_custom(self, domain: str) -> bool:
        return domain.lower() in self.custom_sources

    def get_custom_sources(self) -> Dict[str, Dict[str, Any]]:
        with self._lock:
            return {k: dict(v) for k, v in self.custom_sources.items()}

    def set_source_active(self, domain: str, active: bool) -> None:
        normalized = domain.strip().lower()
        if not normalized:
            raise ValueError("Domain is required")

        with self._lock:
            from services.sources import NEWS_SOURCES  # Local import to avoid circular dependency

            if normalized not in NEWS_SOURCES and normalized not in self.custom_sources:
                raise ValueError("Source not found")

            if active:
                if normalized not in self.active_sources:
                    self.active_sources.append(normalized)
            else:
                self.active_sources = [d for d in self.active_sources if d != normalized]
            self._save()

    def add_custom_source(
        self,
        domain: str,
        name: str,
        rss_urls: List[str],
        fallback_urls: List[str],
        activate: bool = True,
    ) -> Dict[str, Any]:
        normalized = domain.strip().lower()
        if not normalized:
            raise ValueError("Domain is required")

        payload = self._sanitize_custom_payload(name, rss_urls, fallback_urls)

        with self._lock:
            if normalized in self.custom_sources:
                raise ValueError("Source already exists")

            from services.sources import NEWS_SOURCES  # Local import to avoid circular dependency

            if normalized in NEWS_SOURCES:
                raise ValueError("Source already exists")

            self.custom_sources[normalized] = payload
            if activate and normalized not in self.active_sources:
                self.active_sources.append(normalized)
            self._save()

        return {"domain": normalized, **payload}

    def _sanitize_custom_payload(
        self, name: str, rss_urls: List[str], fallback_urls: List[str]
    ) -> Dict[str, Any]:
        if not name or not name.strip():
            raise ValueError("Source name is required")

        cleaned_rss = [url.strip() for url in rss_urls if isinstance(url, str) and url.strip()]
        cleaned_fallback = [url.strip() for url in fallback_urls if isinstance(url, str) and url.strip()]

        if not cleaned_rss and not cleaned_fallback:
            raise ValueError("At least one RSS or fallback URL is required")

        return {
            "name": name.strip(),
            "rss_urls": cleaned_rss,
            "fallback_urls": cleaned_fallback,
        }


source_config = SourceConfigService()
