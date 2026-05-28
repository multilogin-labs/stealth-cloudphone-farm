"""Minimal Multilogin API client boundary.

This module intentionally keeps network behavior small and explicit. Higher-level
automation code should depend on this boundary instead of spreading API details
throughout task modules.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

import requests

from .config import FrameworkConfig


@dataclass(frozen=True)
class MultiloginClient:
    base_url: str
    api_token: str
    timeout_seconds: int = 30

    @classmethod
    def from_config(cls, config: FrameworkConfig) -> "MultiloginClient":
        multilogin = config.payload.get("multilogin", {})
        if not isinstance(multilogin, dict):
            multilogin = {}

        return cls(
            base_url=str(multilogin.get("base_url", "https://api.multilogin.com")).rstrip("/"),
            api_token=config.multilogin_api_token,
            timeout_seconds=int(multilogin.get("timeout_seconds", 30)),
        )

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "stealth-cloudphone-farm/0.1",
        }

    def healthcheck_payload(self) -> Dict[str, Any]:
        """Return non-secret client metadata for diagnostics."""
        return {
            "base_url": self.base_url,
            "timeout_seconds": self.timeout_seconds,
            "token_configured": bool(self.api_token),
        }

    def get(self, path: str) -> requests.Response:
        endpoint = f"{self.base_url}/{path.lstrip('/')}"
        return requests.get(endpoint, headers=self._headers(), timeout=self.timeout_seconds)
