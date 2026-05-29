# Reading Social Publisher

`reading-wechat-publisher` is a local Codex plugin that turns books into structured notes, Guizang-style social assets, WeChat Official Account draft articles, and Xiaohongshu-ready draft packages.

## What It Includes

- `skills/reading-strategy`
  - analyze a book into a structured note
  - support `导读笔记` and `精读笔记`
  - support `结构导读 / 诊断模式 / 战略模式`

- `skills/wechat-article-designer`
  - reshape a note into a mobile-first WeChat article
  - route higher-quality covers and cards through `guizang-social-card-skill`

- `skills/wechat-publisher`
  - run preflight checks
  - generate local previews
  - upload assets and create WeChat drafts

- `skills/reading-social-publisher`
  - orchestrate the full cross-channel workflow
  - coordinate WeChat longform and Xiaohongshu / Rednote draft outputs

## Bundled Scripts

- `scripts/preflight_wechat_publish.py`
- `scripts/prepare_wechat_article.py`
- `scripts/publish_wechat_article.py`
- `scripts/wechat_common.py`

## Current Publish Model

- `WeChat`: default to `draft-only`
- `Xiaohongshu / Rednote`: browser-assisted `draft-only`

The current Xiaohongshu workflow still requires a manual file-upload step in the browser.

## Local Configuration

Copy `.env.example` to `.env` and fill:

- `WECHAT_APP_ID`
- `WECHAT_APP_SECRET`
- `WECHAT_DEFAULT_AUTHOR`
- optional `WECHAT_DEFAULT_CONTENT_SOURCE_URL`

## Notes

- Generated preview files, Python cache files, and local publish state files are ignored.
- This repository is intended to publish the plugin itself, not the generated article drafts.
