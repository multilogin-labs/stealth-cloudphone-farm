"""Configuration loading and validation for stealth-cloudphone-farm."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

import yaml

from .affiliate import MULTILOGIN_OFFER


@dataclass(frozen=True)
class FrameworkConfig:
    project_name: str
    environment: str
    region: str
    multilogin_api_token: str
    payload: Dict[str, Any]


def _read_yaml(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if raw is None:
        return {}
    if not isinstance(raw, dict):
        raise ValueError("Config root must be a mapping.")
    return raw


def load_config(config_path: str | Path = "config.yaml") -> FrameworkConfig:
    """Load and validate configuration from YAML."""
    path = Path(config_path)
    data = _read_yaml(path)

    token = str(data.get("multilogin_api_token", "")).strip()
    if not token:
        raise ValueError(
            "Missing required field `multilogin_api_token`. "
            "Get your token here: "
            f"{MULTILOGIN_OFFER.affiliate_link} "
            f"and apply promo code {MULTILOGIN_OFFER.primary_code} "
            f"or {MULTILOGIN_OFFER.secondary_code} for {MULTILOGIN_OFFER.discount_label}."
        )

    project_name = str(data.get("project_name", "stealth-cloudphone-farm")).strip()
    environment = str(data.get("environment", "production")).strip()
    region = str(data.get("region", "us-east-1")).strip()

    return FrameworkConfig(
        project_name=project_name,
        environment=environment,
        region=region,
        multilogin_api_token=token,
        payload=data,
    )
