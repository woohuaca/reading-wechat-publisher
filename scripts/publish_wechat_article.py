#!/usr/bin/env python3

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path

from wechat_common import (
    WeChatClient,
    WeChatPublishError,
    download_to_temp,
    is_remote_reference,
    load_env_file,
    load_markdown_document,
    preview_meta_text,
    render_markdown_to_wechat_html,
    resolve_article_metadata,
    resolve_file_reference,
    wait_for_publish,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Upload a WeChat-ready markdown article to WeChat Official Accounts."
    )
    parser.add_argument("article", help="Path to the markdown article")
    parser.add_argument("--env-file", help="Optional .env file with WeChat credentials")
    parser.add_argument(
        "--mode",
        choices=("draft", "publish"),
        default="draft",
        help="Create a draft or create-then-submit formal publish",
    )
    parser.add_argument(
        "--poll",
        action="store_true",
        help="Poll publish status after submitting formal publish",
    )
    parser.add_argument(
        "--skip-if-unchanged",
        action="store_true",
        help="For draft mode only, reuse the most recent successful draft if the article content is unchanged",
    )
    return parser


def materialize_media(reference: str, base_dir: Path, temp_paths: list[Path]) -> Path:
    if is_remote_reference(reference):
        path = download_to_temp(reference)
        temp_paths.append(path)
        return path
    return resolve_file_reference(reference, base_dir)


def article_state_path(article_path: Path) -> Path:
    return article_path.with_suffix(article_path.suffix + ".wechat-state.json")


def compute_article_sha256(article_path: Path) -> str:
    return hashlib.sha256(article_path.read_bytes()).hexdigest()


def load_article_state(article_path: Path) -> dict[str, object] | None:
    state_path = article_state_path(article_path)
    if not state_path.exists():
        return None
    try:
        return json.loads(state_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def write_article_state(article_path: Path, payload: dict[str, object]) -> None:
    state_path = article_state_path(article_path)
    state_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    args = build_parser().parse_args()
    article_path = Path(args.article).resolve()
    article_sha256 = compute_article_sha256(article_path)
    previous_state = load_article_state(article_path)
    env = {**load_env_file(args.env_file), **os.environ}
    metadata, markdown_body = load_markdown_document(article_path)
    resolved = resolve_article_metadata(metadata, env, article_path)

    if (
        args.mode == "draft"
        and args.skip_if_unchanged
        and previous_state
        and previous_state.get("article_sha256") == article_sha256
        and previous_state.get("latest_draft", {}).get("media_id")
    ):
        reused = {
            "mode": args.mode,
            "article": str(article_path),
            "title": resolved["title"],
            "meta": preview_meta_text(resolved),
            "reused_existing_draft": True,
            "state_path": str(article_state_path(article_path)),
            "media_id": previous_state["latest_draft"]["media_id"],
            "cover_media_id": previous_state["latest_draft"].get("cover_media_id", ""),
            "images_uploaded": previous_state["latest_draft"].get("images_uploaded", 0),
            "article_sha256": article_sha256,
        }
        print(json.dumps(reused, ensure_ascii=False, indent=2))
        return 0

    app_id = env.get("WECHAT_APP_ID", "").strip()
    app_secret = env.get("WECHAT_APP_SECRET", "").strip()
    client = WeChatClient(app_id, app_secret)

    temp_paths: list[Path] = []

    def upload_inline_image(reference: str, alt: str) -> str:
        image_path = materialize_media(reference, article_path.parent, temp_paths)
        upload_response = client.upload_inline_image(image_path)
        uploaded_url = str(upload_response.get("url") or "")
        if not uploaded_url:
            raise WeChatPublishError(f"Failed to upload inline image for {alt or reference}.")
        return uploaded_url

    try:
        html_body, image_refs = render_markdown_to_wechat_html(
            markdown_body,
            article_path.parent,
            image_resolver=upload_inline_image,
        )

        cover_reference = str(resolved.get("cover_image") or "").strip()
        if not cover_reference and image_refs:
            cover_reference = image_refs[0]["source"]
        if not cover_reference:
            raise WeChatPublishError("cover_image is required in frontmatter or as the first image.")

        cover_path = materialize_media(cover_reference, article_path.parent, temp_paths)
        cover_response = client.upload_cover_material(cover_path)
        thumb_media_id = str(cover_response.get("media_id") or "")
        if not thumb_media_id:
            raise WeChatPublishError("WeChat did not return thumb_media_id for the cover image.")

        article_payload = {
            "title": resolved["title"],
            "author": resolved.get("author", ""),
            "digest": resolved.get("digest", ""),
            "content": html_body,
            "content_source_url": resolved.get("content_source_url", ""),
            "thumb_media_id": thumb_media_id,
            "show_cover_pic": 1 if resolved.get("show_cover_pic") else 0,
            "need_open_comment": 1 if resolved.get("need_open_comment") else 0,
            "only_fans_can_comment": 1 if resolved.get("only_fans_can_comment") else 0,
        }

        draft_response = client.create_draft(article_payload)
        media_id = str(draft_response.get("media_id") or "")
        if not media_id:
            raise WeChatPublishError("WeChat did not return media_id after creating the draft.")

        result = {
            "mode": args.mode,
            "article": str(article_path),
            "title": resolved["title"],
            "meta": preview_meta_text(resolved),
            "media_id": media_id,
            "cover_media_id": thumb_media_id,
            "images_uploaded": len(image_refs),
            "article_sha256": article_sha256,
            "state_path": str(article_state_path(article_path)),
        }

        if args.mode == "publish":
            try:
                publish_response = client.submit_publish(media_id)
            except WeChatPublishError as exc:
                result["publish_error"] = str(exc)
                print(json.dumps(result, ensure_ascii=False, indent=2), file=sys.stderr)
                raise
            result["publish_response"] = publish_response
            publish_id = publish_response.get("publish_id")
            if publish_id is not None and args.poll:
                result["publish_status"] = wait_for_publish(client, publish_id)

        state_payload = {
            "article": str(article_path),
            "article_sha256": article_sha256,
            "updated_at_epoch": int(time.time()),
            "title": resolved["title"],
            "author": resolved.get("author", ""),
            "source_mode": metadata.get("source_mode", ""),
            "latest_draft": {
                "media_id": media_id,
                "cover_media_id": thumb_media_id,
                "images_uploaded": len(image_refs),
            },
        }
        if args.mode == "publish":
            state_payload["latest_publish_attempt"] = {
                "publish_response": result.get("publish_response"),
                "publish_status": result.get("publish_status"),
            }
        write_article_state(article_path, state_payload)

        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    finally:
        for path in temp_paths:
            try:
                path.unlink(missing_ok=True)
            except OSError:
                pass


if __name__ == "__main__":
    raise SystemExit(main())
