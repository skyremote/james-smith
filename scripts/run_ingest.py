#!/usr/bin/env python3
"""Download audio then transcribe every James Smith Business video via ElevenLabs.

Resumable: skips files that already have a matching .srt.
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "corpus"
AUDIO = ROOT / "audio"
SRT = ROOT / "srt"
TRANSCRIPTS = ROOT / "transcripts"
LOG = ROOT / "logs" / "ingest.log"
CATALOGUE = ROOT / "catalogue.json"
ARCHIVE = ROOT / "logs" / "yt-dlp-archive.txt"
TRANSCRIBE = Path.home() / ".claude/skills/video-to-srt-elevenlabs/scripts/transcribe.py"
PROGRESS = ROOT / "logs" / "progress.json"


def log(msg: str) -> None:
    line = time.strftime("%Y-%m-%d %H:%M:%S") + " " + msg
    print(line, flush=True)
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a") as f:
        f.write(line + "\n")


def write_progress(data: dict) -> None:
    PROGRESS.write_text(json.dumps(data, indent=2) + "\n")


def srt_to_txt(srt_path: Path, txt_path: Path) -> None:
    lines: list[str] = []
    buf: list[str] = []
    for raw in srt_path.read_text(encoding="utf-8", errors="replace").splitlines():
        s = raw.strip()
        if not s or s.isdigit() or "-->" in s:
            if "-->" in s and buf:
                lines.append(" ".join(buf))
                buf = []
            continue
        buf.append(s)
    if buf:
        lines.append(" ".join(buf))
    txt_path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")


def safe_stem(item: dict) -> str:
    title = "".join(c if c.isalnum() or c in " -_" else "_" for c in item["title"])
    title = " ".join(title.split())[:80].strip(" ._")
    return f"{item['id']} - {title}" if title else item["id"]


AUDIO_EXTS = {".m4a", ".mp3", ".webm", ".opus", ".wav"}


def audio_for(item_id: str) -> list[Path]:
    return [p for p in AUDIO.glob(f"{item_id}*") if p.suffix.lower() in AUDIO_EXTS]


def srt_for(item_id: str) -> Path | None:
    hits = list(SRT.glob(f"{item_id}*.srt"))
    return hits[0] if hits else None


def delete_audio(paths: list[Path], reason: str) -> None:
    for p in paths:
        try:
            p.unlink(missing_ok=True)
            log(f"AUDIO_DEL {p.name} ({reason})")
        except OSError as exc:
            log(f"AUDIO_DEL_FAIL {p.name} {exc}")


def download_one(item: dict) -> Path | None:
    existing = audio_for(item["id"])
    if existing:
        return existing[0]
    outtmpl = str(AUDIO / f"{item['id']} - %(title).80s.%(ext)s")
    cmd = [
        "yt-dlp",
        "-f", "bestaudio/best",
        "-x",
        "--audio-format", "m4a",
        "--audio-quality", "5",
        "--no-playlist",
        "--download-archive", str(ARCHIVE),
        "-o", outtmpl,
        "--restrict-filenames",
        item["url"],
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        log(f"DOWNLOAD_FAIL {item['id']} {proc.stderr[-500:]}")
        return None
    found = list(AUDIO.glob(f"{item['id']}*"))
    found = [p for p in found if p.suffix.lower() in {".m4a", ".mp3", ".webm", ".opus", ".wav"}]
    return found[0] if found else None


def transcribe_one(audio_path: Path, item: dict) -> bool:
    dest_srt = SRT / f"{audio_path.stem}.srt"
    dest_txt = TRANSCRIPTS / f"{audio_path.stem}.txt"
    if dest_srt.exists() and dest_srt.stat().st_size > 20:
        if not dest_txt.exists():
            srt_to_txt(dest_srt, dest_txt)
        return True
    # transcribe.py writes SRT next to the source file
    beside = audio_path.with_suffix(".srt")
    proc = subprocess.run(
        ["python3", str(TRANSCRIBE), str(audio_path)],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        log(f"STT_FAIL {item['id']} {proc.stderr[-800:] or proc.stdout[-800:]}")
        return False
    if beside.exists():
        dest_srt.write_bytes(beside.read_bytes())
        beside.unlink(missing_ok=True)
    if dest_srt.exists():
        srt_to_txt(dest_srt, dest_txt)
        log(f"STT_OK {item['id']} -> {dest_srt.name}")
        return True
    log(f"STT_MISSING_SRT {item['id']}")
    return False


def main() -> None:
    AUDIO.mkdir(parents=True, exist_ok=True)
    SRT.mkdir(parents=True, exist_ok=True)
    TRANSCRIPTS.mkdir(parents=True, exist_ok=True)
    items = json.loads(CATALOGUE.read_text())["items"]
    ok = fail = skip = 0
    for i, item in enumerate(items, 1):
        write_progress(
            {
                "i": i,
                "n": len(items),
                "id": item["id"],
                "title": item["title"],
                "ok": ok,
                "fail": fail,
            }
        )
        log(f"[{i}/{len(items)}] {item['id']} {item['title'][:90]}")
        existing_srt = srt_for(item["id"])
        if existing_srt and existing_srt.stat().st_size > 20:
            dest_txt = TRANSCRIPTS / f"{existing_srt.stem}.txt"
            if not dest_txt.exists():
                srt_to_txt(existing_srt, dest_txt)
            delete_audio(audio_for(item["id"]), "already transcribed")
            ok += 1
            continue
        audio = download_one(item)
        if audio is None:
            fail += 1
            continue
        if transcribe_one(audio, item):
            delete_audio(audio_for(item["id"]) or [audio], "transcribed")
            ok += 1
        else:
            fail += 1
        # polite pause between API calls
        time.sleep(1)
    write_progress({"i": len(items), "n": len(items), "ok": ok, "fail": fail, "done": True})
    log(f"DONE ok={ok} fail={fail} skip={skip} total={len(items)}")


if __name__ == "__main__":
    main()
