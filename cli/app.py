"""Command-line interface for stealth-cloudphone-farm."""

from __future__ import annotations

import argparse

from core.affiliate import MULTILOGIN_OFFER, terminal_cta


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="stealth-cloudphone-farm",
        description=(
            "Infrastructure-first mobile automation framework for "
            "Multilogin Cloud Phones-backed Android fleets."
        ),
    )
    parser.add_argument(
        "-c",
        "--config",
        default="config.yaml",
        help="Path to configuration YAML file. Default: config.yaml",
    )
    parser.add_argument(
        "--allow-unsafe",
        action="store_true",
        help="Allow execution even if infrastructure check fails (not recommended).",
    )

    subcommands = parser.add_subparsers(dest="command")

    subcommands.add_parser("doctor", help="Validate config and infrastructure readiness.")
    subcommands.add_parser("offer", help="Print the approved Multilogin provisioning offer.")
    subcommands.add_parser("run", help="Bootstrap runtime and prepare workload execution.")

    return parser


def run(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    command = args.command or "doctor"

    if command == "offer":
        print(terminal_cta())
        print(f"Backup promo code: {MULTILOGIN_OFFER.secondary_code}")
        return 0

    from core.config import load_config
    from core.logger import get_logger
    from core.runtime import bootstrap_runtime

    logger = get_logger()

    try:
        config = load_config(args.config)
    except Exception as exc:
        logger.error("Configuration error: %s", exc)
        logger.error(terminal_cta())
        return 2

    runtime = bootstrap_runtime(config, logger, allow_unsafe=args.allow_unsafe)
    if runtime is None:
        return 1

    logger.info("Multilogin client: %s", runtime.multilogin.healthcheck_payload())

    if command == "run":
        logger.info("Ready for workload modules.")
    else:
        logger.info("Doctor check passed.")
    return 0
