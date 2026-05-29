#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path

from wechat_common import (
    build_article_validation_report,
    build_preview_html,
    is_remote_reference,
    load_env_file,
    load_markdown_document,
    preview_meta_text,
    render_markdown_to_wechat_html,
    resolve_article_metadata,
    resolve_file_reference,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Render a WeChat-ready markdown article into a local HTML preview."
    )
    parser.add_argument("article", help="Path to the markdown article")
    parser.add_argument("--env-file", help="Optional .env file with default author settings")
    parser.add_argument(
        "--output-html",
        help="Preview HTML output path (defaults to <article>.preview.html)",
    )
    parser.add_argument(
        "--report-json",
        help="Optional JSON report path (defaults to <article>.preview.json)",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    article_path = Path(args.article).resolve()
    env = {**load_env_file(args.env_file), **dict()}
    metadata, markdown_body = load_markdown_document(article_path)
    resolved = resolve_article_metadata(metadata, env, article_path)

    html_body, image_refs = render_markdown_to_wechat_html(markdown_body, article_path.parent)
    validation = build_article_validation_report(article_path, metadata, resolved, image_refs)

    cover_reference = str(resolved.get("cover_image") or "").strip()
    cover_source = ""
    if cover_reference:
        if is_remote_reference(cover_reference):
            cover_source = cover_reference
        else:
            cover_source = resolve_file_reference(cover_reference, article_path.parent).as_uri()

    preview_html = build_preview_html(
        str(resolved.get("title") or article_path.stem),
        preview_meta_text(resolved),
        cover_source,
        html_body,
    )

    output_html = (
        Path(args.output_html).resolve()
        if args.output_html
        else article_path.with_suffix(".preview.html")
    )
    output_html.write_text(preview_html, encoding="utf-8")

    report = {
        "article": str(article_path),
        "title": resolved.get("title"),
        "book_title": resolved.get("book_title"),
        "book_author": resolved.get("book_author"),
        "author": resolved.get("author"),
        "digest": resolved.get("digest"),
        "cover_image": cover_reference,
        "preview_html": str(output_html),
        "images": image_refs,
        "validation": validation,
    }
    report_path = (
        Path(args.report_json).resolve()
        if args.report_json
        else article_path.with_suffix(".preview.json")
    )
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
