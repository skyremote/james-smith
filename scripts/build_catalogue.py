#!/usr/bin/env python3
"""Build a JSON catalogue of @JamesSmithBusiness videos and shorts."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path("/Users/sky/Documents/james-smith-corpus")
OUT = ROOT / "catalogue.json"

SOURCES = [
    ("video", "https://www.youtube.com/@JamesSmithBusiness/videos"),
    ("short", "https://www.youtube.com/@JamesSmithBusiness/shorts"),
]


def dump_flat(url: str) -> list[dict]:
    cmd = [
        "yt-dlp",
        "--flat-playlist",
        "--dump-json",
        url,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        print(proc.stderr[-2000:], file=sys.stderr)
        raise SystemExit(f"yt-dlp failed for {url}: {proc.returncode}")
    rows = []
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        rows.append(json.loads(line))
    return rows


def main() -> None:
    items: dict[str, dict] = {}
    for kind, url in SOURCES:
        print(f"listing {kind}s…", flush=True)
        for row in dump_flat(url):
            vid = row.get("id")
            if not vid:
                continue
            existing = items.get(vid)
            entry = {
                "id": vid,
                "title": row.get("title") or (existing or {}).get("title") or vid,
                "duration": row.get("duration") or (existing or {}).get("duration"),
                "url": f"https://www.youtube.com/watch?v={vid}",
                "kind": kind if not existing else "both",
            }
            items[vid] = entry
    catalogue = {
        "channel": "https://www.youtube.com/@JamesSmithBusiness",
        "count": len(items),
        "items": sorted(items.values(), key=lambda x: x["title"].lower()),
    }
    OUT.write_text(json.dumps(catalogue, indent=2) + "\n")
    print(f"wrote {OUT} ({catalogue['count']} unique ids)", flush=True)


if __name__ == "__main__":
    main()
