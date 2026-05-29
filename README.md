# Reading Social Publisher

`reading-wechat-publisher` is a Codex plugin for turning books into structured notes, Guizang-style social assets, WeChat Official Account drafts, and Xiaohongshu / Rednote draft packages.

It is designed for a practical publishing workflow:

- analyze a book honestly from the available source material
- shape the note into a WeChat-friendly longform article
- generate stronger covers and cards through Guizang-style visual packaging
- create a WeChat draft
- prepare a Xiaohongshu / Rednote draft package with browser-assisted follow-through

## What This Plugin Does

This repository currently covers four linked jobs:

1. `reading-strategy`
   - turn a book into a structured note
   - support `导读笔记` and `精读笔记`
   - support `结构导读 / 诊断模式 / 战略模式`

2. `wechat-article-designer`
   - turn a note into a mobile-first WeChat article
   - route higher-quality visual work through `guizang-social-card-skill`

3. `wechat-publisher`
   - run preflight checks
   - build local previews
   - upload assets and create WeChat drafts

4. `reading-social-publisher`
   - orchestrate the full cross-channel workflow
   - keep the angle, assets, and publish boundaries aligned across channels

## Workflow

```text
book title / notes / highlights
-> reading-strategy
-> structured markdown note
-> wechat-article-designer
-> Guizang-style covers and cards
-> wechat-publisher
-> WeChat draft

in parallel or later:
structured note
-> reading-social-publisher
-> Xiaohongshu image set + caption
-> browser-assisted draft flow
```

## Repository Layout

```text
.codex-plugin/
assets/
scripts/
skills/
  reading-strategy/
  wechat-article-designer/
  wechat-publisher/
  reading-social-publisher/
```

## Bundled Scripts

- `scripts/preflight_wechat_publish.py`
- `scripts/prepare_wechat_article.py`
- `scripts/publish_wechat_article.py`
- `scripts/wechat_common.py`

## Current Publish Model

- `WeChat`: `draft-only` by default
- `Xiaohongshu / Rednote`: browser-assisted `draft-only`

Current boundary:

- Xiaohongshu still requires a manual image-upload step in the browser before the automation can continue.

## Local Configuration

Copy `.env.example` to `.env` and fill:

- `WECHAT_APP_ID`
- `WECHAT_APP_SECRET`
- `WECHAT_DEFAULT_AUTHOR`
- optional `WECHAT_DEFAULT_CONTENT_SOURCE_URL`

## Quick Start

Example prompts:

- `Use $reading-strategy to analyze this book into a structured note.`
- `Use $wechat-article-designer to turn this note into a WeChat-ready article.`
- `Use $wechat-publisher to preview and create a WeChat draft.`
- `Use $reading-social-publisher to turn this book into a WeChat and Xiaohongshu-ready social package.`

## Status

This repository is public and release-tagged, but it should still be treated as an early workflow plugin.

What is stable today:

- source-mode separation
- WeChat article packaging
- WeChat draft creation
- Guizang-guided visual packaging

What is still partly manual:

- Xiaohongshu image upload
- final Xiaohongshu draft-save interaction on custom page controls

## License

This repository is currently marked `UNLICENSED`.

Do not assume open-source reuse rights until a license is added explicitly.

## Notes

- Generated preview files, Python cache files, and local publish state files are ignored.
- This repository publishes the plugin itself, not generated article drafts or local image output folders.
