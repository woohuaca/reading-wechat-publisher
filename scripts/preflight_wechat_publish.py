#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from wechat_common import (
    WeChatClient,
    WeChatPublishError,
    build_article_validation_report,
    detect_public_ip,
    load_env_file,
    load_markdown_document,
    render_markdown_to_wechat_html,
    resolve_article_metadata,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run preflight checks before creating a WeChat draft or publish."
    )
    parser.add_argument("article", help="Path to the markdown article")
    parser.add_argument("--env-file", help="Optional .env file with WeChat credentials")
    parser.add_argument(
        "--check-token",
        action="store_true",
        help="Check whether the account can retrieve an access token",
    )
    parser.add_argument(
        "--detect-ip",
        action="store_true",
        help="Detect the current public egress IP to compare against the whitelist",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    article_path = Path(args.article).resolve()
    env = {**load_env_file(args.env_file), **os.environ}

    metadata, markdown_body = load_markdown_document(article_path)
    resolved = resolve_article_metadata(metadata, env, article_path)
    _, image_refs = render_markdown_to_wechat_html(markdown_body, article_path.parent)
    validation = build_article_validation_report(article_path, metadata, resolved, image_refs)

    report: dict[str, object] = {
        "article": str(article_path),
        "title": resolved.get("title"),
        "source_mode": metadata.get("source_mode", ""),
        "validation": validation,
        "credentials": {
            "has_app_id": bool(str(env.get("WECHAT_APP_ID", "")).strip()),
            "has_app_secret": bool(str(env.get("WECHAT_APP_SECRET", "")).strip()),
            "has_default_author": bool(str(env.get("WECHAT_DEFAULT_AUTHOR", "")).strip()),
        },
        "checks": {},
        "recommended_next_step": "create_draft" if validation["publish_ready"] else "fix_blockers",
        "operating_mode": "draft_only",
        "notes": [
            "Formal publish should remain opt-in until the account has already proved publish capability.",
        ],
    }

    if args.check_token:
        try:
            client = WeChatClient(
                str(env.get("WECHAT_APP_ID", "")).strip(),
                str(env.get("WECHAT_APP_SECRET", "")).strip(),
            )
            token = client.access_token()
            report["checks"]["token_access"] = {
                "ok": True,
                "token_prefix": token[:8],
            }
        except (WeChatPublishError, ValueError, OSError) as exc:
            report["checks"]["token_access"] = {
                "ok": False,
                "error": str(exc),
            }
            report["validation"]["blocking_issues"].append("token_access_failed")
            report["recommended_next_step"] = "fix_blockers"

    if args.detect_ip:
        report["checks"]["public_ip"] = detect_public_ip()

    report["validation"]["blocking_issues"] = sorted(set(report["validation"]["blocking_issues"]))
    report["validation"]["publish_ready"] = not report["validation"]["blocking_issues"]
    if not report["validation"]["publish_ready"]:
        report["recommended_next_step"] = "fix_blockers"

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["recommended_next_step"] == "create_draft" else 1


if __name__ == "__main__":
    raise SystemExit(main())
