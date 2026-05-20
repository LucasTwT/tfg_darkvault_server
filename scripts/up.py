#!/usr/bin/env python3
"""Start the DarkVault backend stack.

Usage:
    python scripts/up.py              # Development (hot reload)
    python scripts/up.py --env dev    # Development (hot reload)
    python scripts/up.py --env prod   # Production (optimized, more workers)
    python scripts/up.py --build      # Rebuild images
    python scripts/up.py --db-only    # Start only db
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COMPOSE_BASE = str(ROOT / "docker-compose.base.yml")
COMPOSE_DEV = str(ROOT / "docker-compose.dev.yml")
COMPOSE_PROD = str(ROOT / "docker-compose.prod.yml")


def _docker_compose_files(env: str) -> list[str]:
    """Return compose files based on environment."""
    base = [COMPOSE_BASE]
    if env == "dev":
        return base + [COMPOSE_DEV]
    if env == "prod":
        return base + [COMPOSE_PROD]
    return base + [COMPOSE_DEV]  # Default to dev


def _run(args: list[str], **kwargs) -> int:
    kwargs.setdefault("check", False)
    return subprocess.run(args, **kwargs).returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="Start DarkVault backend stack")
    parser.add_argument(
        "--env",
        choices={"dev", "prod"},
        default="dev",
        help="Environment: dev (hot reload), prod (optimized)",
    )
    parser.add_argument(
        "--build",
        action="store_true",
        help="Rebuild images before starting",
    )
    parser.add_argument(
        "--db-only",
        action="store_true",
        help="Start only the database",
    )
    args = parser.parse_args()

    compose_files = _docker_compose_files(args.env)
    env_name = {"dev": "development", "prod": "production"}[args.env]

    print(f"[darkvault-backend] Starting stack ({env_name})...")

    compose_cmd = ["docker", "compose", "-f", compose_files[0]]
    for f in compose_files[1:]:
        compose_cmd.extend(["-f", f])
    compose_cmd.append("up")
    if args.build:
        compose_cmd.append("--build")
    if args.db_only:
        compose_cmd.extend(["db", "-d"])
    else:
        compose_cmd.append("-d")

    rc = _run(compose_cmd)
    if rc != 0:
        print(f"[darkvault-backend] ✗ Failed to start {env_name} stack", file=sys.stderr)
        return rc

    print(f"[darkvault-backend] ✓ {env_name} stack started")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
