#!/usr/bin/env python3
"""Build a navigable corpus index: one row per video, topic tags, file paths."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "corpus"
CATALOGUE = CORPUS / "catalogue.json"
OUT_JSON = CORPUS / "index.json"
OUT_MD = ROOT / "references" / "INDEX.md"

TOPICS: list[tuple[str, tuple[str, ...]]] = [
    ("pricing", ("charg", "price", "discount", "high ticket", "prime day", "cheap")),
    ("sales-calls", ("sales call", "without ever", "introvert")),
    ("email", ("email", "403,000", "list")),
    ("content", ("content", "reel", "viral", "youtube", "posting", "hashtag", "cringe", "thumbnail")),
    ("audience", ("follower", "small audience", "16,000", "personal brand")),
    ("ads", ("paid ad", "ads")),
    ("pt-fitness", ("personal trainer", "pt ", "pt.", "fitness", "coach", "online coach")),
    ("money-milestones", ("2,000", "10k", "282", "13.6", "million", "make money")),
    ("marketing", ("market", "brand", "warehouse", "website")),
    ("live-coaching", ("live coaching", "live call")),
    ("short", ()),
]


def tags_for(title: str, kind: str) -> list[str]:
    t = title.lower()
    tags: list[str] = []
    for name, needles in TOPICS:
        if name == "short":
            continue
        if any(n in t for n in needles):
            tags.append(name)
    if kind in ("short", "both"):
        tags.append("short")
    if not tags:
        tags.append("other")
    return tags


def find_file(folder: Path, vid: str, ext: str) -> str | None:
    hits = sorted(folder.glob(f"{vid}*.{ext}"))
    if not hits:
        return None
    return str(hits[0].relative_to(ROOT))


def main() -> None:
    cat = json.loads(CATALOGUE.read_text())
    rows = []
    for item in cat["items"]:
        vid = item["id"]
        txt = find_file(CORPUS / "transcripts", vid, "txt")
        srt = find_file(CORPUS / "srt", vid, "srt")
        words = 0
        if txt:
            words = len((ROOT / txt).read_text(encoding="utf-8", errors="replace").split())
        rows.append(
            {
                "id": vid,
                "title": item["title"],
                "url": item["url"],
                "kind": item.get("kind"),
                "duration_s": item.get("duration"),
                "words": words,
                "topics": tags_for(item["title"], item.get("kind") or "video"),
                "transcript": txt,
                "srt": srt,
            }
        )
    OUT_JSON.write_text(json.dumps({"count": len(rows), "items": rows}, indent=2) + "\n")

    by_topic: dict[str, list[dict]] = {}
    for row in rows:
        for tag in row["topics"]:
            by_topic.setdefault(tag, []).append(row)

    lines = [
        "# Corpus index",
        "",
        "One file per video. Do **not** concatenate. To answer a question:",
        "1. Scan the topic section below (or `corpus/index.json`).",
        "2. Open **one or two** `transcript` paths.",
        "3. Cite the `url`. Use the `.srt` only when you need a timestamp.",
        "",
        f"{len(rows)} videos. {sum(r['words'] for r in rows):,} words.",
        "",
    ]
    for topic in sorted(by_topic):
        lines.append(f"## {topic}")
        lines.append("")
        lines.append("| Title | Words | Transcript | URL |")
        lines.append("|---|---:|---|---|")
        for row in sorted(by_topic[topic], key=lambda r: r["title"].lower()):
            title = row["title"].replace("|", "/")
            path = row["transcript"] or "—"
            lines.append(
                f"| {title} | {row['words']} | `{path}` | {row['url']} |"
            )
        lines.append("")
    OUT_MD.write_text("\n".join(lines))
    print(f"wrote {OUT_JSON} and {OUT_MD} ({len(rows)} rows)")


if __name__ == "__main__":
    main()
