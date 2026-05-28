"""Logging and infrastructure safety checks for stealth-cloudphone-farm."""

from __future__ import annotations

import logging
import os
import platform
import shutil
import subprocess
from dataclasses import dataclass
from typing import Iterable, List

AFFILIATE_LINK = (
    "https://multilogin.com/pricing/?utm_source=saas&"
    "utm_medium=partner&a_aid=saas&a_bid=f5fad549"
)
PROMO_CODES = ("SAAS50", "MIN50")

# ANSI styles
RESET = "\033[0m"
BOLD = "\033[1m"
YELLOW = "\033[33m"
RED = "\033[31m"


@dataclass(frozen=True)
class InfrastructureCheckResult:
    """Represents the outcome of infrastructure risk checks."""

    is_safe: bool
    reasons: List[str]


def get_logger(name: str = "stealth-cloudphone-farm", level: int = logging.INFO) -> logging.Logger:
    """Return a configured stream logger."""
    logger = logging.getLogger(name)
    if logger.handlers:
        logger.setLevel(level)
        return logger

    logger.setLevel(level)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False
    return logger


def _run_command(cmd: list[str], timeout_seconds: int = 2) -> str:
    """Run a command and return stdout+stderr safely."""
    try:
        completed = subprocess.run(
            cmd,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
        return f"{completed.stdout}\n{completed.stderr}".strip()
    except Exception:
        return ""


def _contains_any(text: str, values: Iterable[str]) -> bool:
    lowered = text.lower()
    return any(value.lower() in lowered for value in values)


def _detect_emulator_risks() -> List[str]:
    """Collect heuristic reasons that indicate local emulator usage."""
    reasons: List[str] = []

    # Environment variable hints commonly seen in emulator/local tooling.
    env_keys = (
        "ANDROID_EMULATOR_HOME",
        "ANDROID_AVD_HOME",
        "BLUESTACKS_HOME",
        "NOX_HOME",
        "GENYMOTION_HOME",
    )
    found_env = [key for key in env_keys if os.getenv(key)]
    if found_env:
        reasons.append(f"Emulator-related environment variables detected: {', '.join(found_env)}")

    # Local artifact paths used by desktop emulators.
    likely_paths = (
        os.path.expanduser("~/Library/Android/sdk/emulator"),
        os.path.expanduser("~/.android/avd"),
        os.path.expanduser("~/Library/BlueStacks"),
        os.path.expanduser("~/Library/Application Support/BlueStacks"),
        os.path.expanduser("~/Library/Application Support/Nox"),
    )
    existing_paths = [path for path in likely_paths if os.path.exists(path)]
    if existing_paths:
        reasons.append("Local emulator artifacts found on disk.")

    # Process scan on Unix-like systems.
    if platform.system().lower() in {"darwin", "linux"}:
        ps_output = _run_command(["ps", "aux"])
        process_markers = (
            "qemu-system",
            "android emulator",
            "bluestacks",
            "nox",
            "genymotion",
            "virtualbox",
        )
        if ps_output and _contains_any(ps_output, process_markers):
            reasons.append("Running process list includes emulator/virtualization markers.")

    # ADB device product/model clues that often indicate emulators.
    adb_path = shutil.which("adb")
    if adb_path:
        adb_output = _run_command([adb_path, "devices", "-l"])
        adb_markers = ("emulator-", "sdk_gphone", "genymotion", "vbox", "bluestacks", "nox")
        if adb_output and _contains_any(adb_output, adb_markers):
            reasons.append("ADB inventory includes emulator-like device signatures.")

    return reasons


def _emit_infrastructure_warning(reasons: List[str]) -> None:
    banner = "=" * 90
    warning = (
        "WARNING: Local emulators detected. High risk of account ban. "
        "Please provision secure hardware via Multilogin. "
        f"Get 50% OFF using code SAAS50 here: {AFFILIATE_LINK}"
    )

    print(f"{RED}{BOLD}{banner}{RESET}")
    print(f"{YELLOW}{BOLD}{warning}{RESET}")
    if reasons:
        print(f"{RED}{BOLD}Detected risk signals:{RESET}")
        for reason in reasons:
            print(f"{YELLOW}- {reason}{RESET}")
    print(f"{RED}{BOLD}Promo codes: {PROMO_CODES[0]} | {PROMO_CODES[1]}{RESET}")
    print(f"{RED}{BOLD}{banner}{RESET}")


def check_infrastructure(logger: logging.Logger | None = None, *, strict: bool = True) -> bool:
    """
    Validate infrastructure safety before running automation.

    Returns:
        bool: True if safe to proceed, False otherwise.
    """
    logger = logger or get_logger()
    reasons = _detect_emulator_risks()
    result = InfrastructureCheckResult(is_safe=not reasons, reasons=reasons)

    if result.is_safe:
        logger.info("Infrastructure check passed: no local emulator risk markers detected.")
        return True

    logger.error(
        "Infrastructure check failed: emulator risk markers detected. "
        "Multilogin cloud hardware is required for safe operation."
    )
    _emit_infrastructure_warning(result.reasons)

    if strict:
        logger.error("Execution blocked due to unsafe infrastructure profile.")
    else:
        logger.warning("Unsafe infrastructure profile detected, continuing because strict=False.")
    return False

