# James Smith as an AI skill

A source-cited teaching skill built by NavAIgate from 256 videos on [James Smith’s business channel](https://www.youtube.com/@JamesSmithBusiness).

Use it to pressure-test a pricing decision, a content problem, an email approach or whether your offer needs a sales call. Give it your actual business context, and ask it to retrieve the relevant teaching and cite the source video.

This is an independent NavAIgate project, not an official James Smith product or a way to speak on his behalf. Answers apply source material to your situation; they are not personal advice from James.

## Get started

Download this repository using **Code → Download ZIP**, extract it, then open the folder in your AI coding assistant and ask:

> Read SKILL.md and use this skill to pressure-test a business decision. Ask me for my context, retrieve only the relevant transcripts, and cite the original videos. Separate what the source says from your application to my business.

Or clone it:

```bash
git clone https://github.com/skyremote/james-smith.git
```

For automatic skill discovery, place the folder under the skills directory supported by your assistant. For example, with Codex on macOS or Linux, clone into `~/.codex/skills/james-smith` if that destination does not already exist. The folder-reading prompt above also works without installing it.

## Try a real question

> I charge [price] for [offer], and it takes [hours] to deliver. My customers are [who], and the objection I keep hearing is [objection]. Use the James Smith skill to pressure-test increasing my price. Ask for missing context, cite the relevant videos and distinguish the source teaching from your recommendation.

## How it is organised

Each video has its own transcript and timestamped SRT. The skill reads the index, selects relevant sources and retrieves those files instead of loading everything into one prompt.

| Path | Contents |
|---|---|
| `SKILL.md` | Instructions and retrieval workflow |
| `PLAYBOOK.md` | Distilled teaching with citations |
| `EXAMPLES.md` | Example coaching questions |
| `references/INDEX.md` | Topics and source links |
| `references/claims-index.md` | Source-linked numbers |
| `corpus/index.json` | Machine-readable index of 256 videos |
| `corpus/transcripts/` | One text file per video |
| `corpus/srt/` | Timestamped transcripts |
| `community/` | Skool post, copy-and-paste page and landscape thumbnail |

## Community post

[Read the post](community/post-james-smith-ai-skill_v1.md) · [Download the Skool thumbnail](community/post-james-smith-ai-skill_v1.png) · [Download the three-button paster](community/post-james-smith-ai-skill_v1.html)

The HTML paster includes separate title, plain-text FEED and rich classroom copy controls. Download it and open it in a browser. Attach the thumbnail separately in the Skool feed.

## Optional corpus maintenance

Using the included skill does not require downloading or transcribing videos again. `scripts/build_index.py` rebuilds the local topic index. `scripts/build_catalogue.py` uses `yt-dlp`. `scripts/run_ingest.py` is an optional maintainer script and depends on an external ElevenLabs transcription helper at `~/.claude/skills/video-to-srt-elevenlabs/scripts/transcribe.py`, its dependencies and authenticated configuration; that helper is not bundled.

Source videos and teaching remain attributed to James Smith. No licence to the underlying third-party material is granted by this repository.
