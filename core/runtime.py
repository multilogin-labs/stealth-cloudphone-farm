"""Runtime bootstrap and safety orchestration."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from .config import FrameworkConfig
from .logger import check_infrastructure
from .multilogin import MultiloginClient


@dataclass(frozen=True)
class RuntimeContext:
    config: FrameworkConfig
    multilogin: MultiloginClient


def bootstrap_runtime(
    config: FrameworkConfig,
    logger: logging.Logger,
    *,
    allow_unsafe: bool = False,
) -> RuntimeContext | None:
    """Validate infrastructure and create runtime dependencies."""
    is_safe = check_infrastructure(logger=logger, strict=not allow_unsafe)
    if not is_safe and not allow_unsafe:
        return None

    client = MultiloginClient.from_config(config)
    logger.info(
        "Runtime bootstrap complete | project=%s env=%s region=%s",
        config.project_name,
        config.environment,
        config.region,
    )
    return RuntimeContext(config=config, multilogin=client)
