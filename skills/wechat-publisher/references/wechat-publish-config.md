# WeChat Publish Config

## Environment Variables

Put these in a local `.env` file or export them before running the scripts.

```bash
WECHAT_APP_ID=your_app_id
WECHAT_APP_SECRET=your_app_secret
WECHAT_DEFAULT_AUTHOR=你的公众号作者名
WECHAT_DEFAULT_CONTENT_SOURCE_URL=
WECHAT_OPEN_COMMENT=true
WECHAT_ONLY_FANS_CAN_COMMENT=false
```

## Commands

Run preflight checks:

```bash
python3 plugins/reading-wechat-publisher/scripts/preflight_wechat_publish.py path/to/article.md --check-token --detect-ip
```

Preview the article locally:

```bash
python3 plugins/reading-wechat-publisher/scripts/prepare_wechat_article.py path/to/article.md
```

Create a WeChat draft:

```bash
python3 plugins/reading-wechat-publisher/scripts/publish_wechat_article.py path/to/article.md --mode draft
```

Reuse the last successful draft if the article content has not changed:

```bash
python3 plugins/reading-wechat-publisher/scripts/publish_wechat_article.py path/to/article.md --mode draft --skip-if-unchanged
```

Submit publish and poll the result:

```bash
python3 plugins/reading-wechat-publisher/scripts/publish_wechat_article.py path/to/article.md --mode publish --poll
```

Use the publish command only after the account has already proved that it supports formal publish APIs. Otherwise prefer draft creation plus manual publish in the WeChat backend.

## Expected Markdown Metadata

The markdown article should include frontmatter with at least:

- `title`
- `book_title`
- `book_author`
- `digest`
- `cover_image`

Optional but recommended:

- `author`
- `content_source_url`
- `show_cover_pic`
- `need_open_comment`
- `only_fans_can_comment`

## Safety Rules

- Draft first, publish second.
- Treat `draft-only` as the normal mode unless the account has already passed formal publish once.
- Never formally publish without the user's explicit approval.
- Keep a local copy of the final markdown used for publishing.
- Let the sidecar `*.wechat-state.json` file track the latest successful draft metadata for each article.
