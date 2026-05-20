#!/usr/bin/env python3
"""Stop the DarkVault backend stack.

Usage:
    python scripts/down.py              # Stop dev stack
    python scripts/down.py --env dev    # Stop dev stack
    python scripts/down.py --env prod   # Stop prod stack
    python scripts/down.py --db-only    # Stop only db
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
    return base + [COMPOSE_DEV]


def main() -> int:
    parser = argparse.ArgumentParser(description="Stop DarkVault backend stack")
    parser.add_argument(
        "--env",
        choices={"dev", "prod"},
        default="dev",
        help="Environment to stop",
    )
    parser.add_argument(
        "--db-only",
        action="store_true",
        help="Stop only the database",
    )
    args = parser.parse_args()

    compose_files = _docker_compose_files(args.env)
    env_name = {"dev": "development", "prod": "production"}[args.env]

    print(f"[darkvault-backend] Stopping stack ({env_name})...")

    compose_cmd = ["docker", "compose", "-f", compose_files[0]]
    for f in compose_files[1:]:
        compose_cmd.extend(["-f", f])
    compose_cmd.append("down")
    if args.db_only:
        compose_cmd.extend(["db"])

    rc = subprocess.run(compose_cmd, check=False).returncode
    if rc != 0:
        print(f"[darkvault-backend] ✗ Failed to stop {env_name} stack", file=sys.stderr)
        return rc

    print(f"[darkvault-backend] ✓ {env_name} stack stopped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
