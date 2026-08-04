#!/usr/bin/env python3
"""Check optional travel-planning credentials without printing secret values."""

import os


VARS = {
    "AMAP_WEB_SERVICE_KEY": "Gaode/Amap Web Service API key",
    "XHS_COOKIE": "Xiaohongshu Web login cookie",
    "XHS_SERVICE_ENDPOINT": "Optional user-provided Xiaohongshu bridge endpoint",
    "XHS_SERVICE_TOKEN": "Optional Xiaohongshu bridge token",
}


def mask(value: str) -> str:
    if not value:
        return "missing"
    if len(value) <= 8:
        return "set"
    return f"set ({value[:3]}...{value[-3:]}, {len(value)} chars)"


def main() -> None:
    print("Travel planning environment")
    for name, label in VARS.items():
        print(f"- {name}: {mask(os.getenv(name, ''))} - {label}")


if __name__ == "__main__":
    main()
