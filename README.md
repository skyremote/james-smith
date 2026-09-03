# James Smith

Private teaching skill: James Smith's public YouTube
([@JamesSmithBusiness](https://www.youtube.com/@JamesSmithBusiness)),
cited, not impersonated.

256 videos, each its own transcript and SRT. Navigate via
`references/INDEX.md` or `corpus/index.json`. Do not concatenate.

| Path | What it is |
|---|---|
| `SKILL.md` | When to fire, how to navigate the corpus |
| `PLAYBOOK.md` | Distilled rules with citations |
| `EXAMPLES.md` | Worked coaching jobs |
| `references/INDEX.md` | Topic → video → file path |
| `references/claims-index.md` | Hard numbers, sourced |
| `corpus/transcripts/` | One `.txt` per video |
| `corpus/srt/` | One `.srt` per video (timestamps only) |
| `scripts/run_ingest.py` | Resume download + ElevenLabs if new videos appear |

## Install

```bash
git clone git@github.com:skyremote/james-smith.git ~/Documents/GitHub/james-smith
for d in ~/.claude/skills ~/.cursor/skills ~/.codex/skills ~/.agents/skills; do
  mkdir -p "$d" && ln -sfn ~/Documents/GitHub/james-smith "$d/james-smith"
done
```
