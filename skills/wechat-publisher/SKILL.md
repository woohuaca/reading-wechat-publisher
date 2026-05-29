---
name: wechat-publisher
description: Use when the user has approved a WeChat-ready markdown article and wants preflight checks, asset uploads, draft creation, or conditional publication to WeChat Official Accounts using the bundled scripts and environment configuration.
---

# Wechat Publisher

Use this skill only after the user has reviewed the article. Default to `draft-only`. Move to formal publish only after an explicit go-ahead and only when account capability has been proven.

## Safe Sequence

1. Confirm that the article markdown has frontmatter and a valid `cover_image`.
2. Load WeChat credentials from `.env` or explicit environment variables.
3. Run preflight checks first:
   - `python3 plugins/reading-wechat-publisher/scripts/preflight_wechat_publish.py article.md --check-token --detect-ip`
4. Run a local preview when practical:
   - `python3 plugins/reading-wechat-publisher/scripts/prepare_wechat_article.py article.md`
5. Create a WeChat draft:
   - `python3 plugins/reading-wechat-publisher/scripts/publish_wechat_article.py article.md --mode draft`
6. Treat draft creation as the normal finish state.
7. Only after explicit approval, and only when the account has already proven publish permission, submit formal publish:
   - `python3 plugins/reading-wechat-publisher/scripts/publish_wechat_article.py article.md --mode publish --poll`

## What The Bundled Scripts Do

- Parse frontmatter metadata from the markdown article.
- Convert markdown into WeChat-safe HTML.
- Validate local images and flag risky remote dependencies before publish.
- Upload cover and inline images to WeChat-hosted URLs.
- Create a draft in the official account.
- Optionally submit the draft to formal publish and poll for completion.

## Requirements

- `WECHAT_APP_ID`
- `WECHAT_APP_SECRET`
- A cover image path or URL in `cover_image`
- User confirmation before formal publish
- A realistic expectation that many accounts are `draft-only` for API automation

## Resources

- Config and command guide: [references/wechat-publish-config.md](./references/wechat-publish-config.md)
- Account and workflow model: [references/wechat-publish-operating-model.md](./references/wechat-publish-operating-model.md)
- Main publisher script: [../../scripts/publish_wechat_article.py](../../scripts/publish_wechat_article.py)
- Preflight checker: [../../scripts/preflight_wechat_publish.py](../../scripts/preflight_wechat_publish.py)
- Preview script: [../../scripts/prepare_wechat_article.py](../../scripts/prepare_wechat_article.py)
