#!/usr/bin/env python3

from __future__ import annotations

import html
import json
import mimetypes
import os
import re
import ssl
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

REQUIRED_ARTICLE_FIELDS = ("title", "book_title", "book_author", "digest", "cover_image")
SUPPORTED_WECHAT_IMAGE_FORMATS = {"png", "jpeg", "gif", "bmp"}

FRONTMATTER_ALIASES = {
    "title": "title",
    "标题": "title",
    "author": "author",
    "作者": "author",
    "book_title": "book_title",
    "书名": "book_title",
    "book_author": "book_author",
    "图书作者": "book_author",
    "core_phrase": "core_phrase",
    "核心词": "core_phrase",
    "digest": "digest",
    "摘要": "digest",
    "cover_image": "cover_image",
    "封面图": "cover_image",
    "content_source_url": "content_source_url",
    "原文链接": "content_source_url",
    "show_cover_pic": "show_cover_pic",
    "显示封面": "show_cover_pic",
    "need_open_comment": "need_open_comment",
    "开启评论": "need_open_comment",
    "only_fans_can_comment": "only_fans_can_comment",
    "仅粉丝评论": "only_fans_can_comment",
    "source_mode": "source_mode",
    "素材模式": "source_mode",
}

P_STYLE = (
    "margin: 0 0 1.05em; color: #1f2933; font-size: 16px; "
    "line-height: 1.9; letter-spacing: 0.01em;"
)
H1_STYLE = (
    "margin: 1.4em 0 0.7em; font-size: 28px; line-height: 1.22; "
    "color: #102a43;"
)
H2_STYLE = (
    "margin: 1.8em 0 0.7em; padding-left: 12px; border-left: 4px solid #0f766e; "
    "font-size: 23px; line-height: 1.35; color: #102a43;"
)
H3_STYLE = (
    "margin: 1.5em 0 0.65em; font-size: 19px; line-height: 1.4; color: #0f172a;"
)
QUOTE_STYLE = (
    "margin: 1.3em 0; padding: 0.9em 1em; background: #f7f9f7; "
    "border-left: 4px solid #0f766e; color: #334155;"
)
UL_STYLE = "margin: 0 0 1.2em 1.3em; padding: 0; color: #1f2933; line-height: 1.85;"
LI_STYLE = "margin: 0.2em 0;"
PRE_STYLE = (
    "margin: 1.2em 0; padding: 12px 14px; border-radius: 12px; background: #f8fafc; "
    "border: 1px solid #dbe2ea; overflow-x: auto; font-size: 14px; line-height: 1.7;"
)
HR_STYLE = "border: none; border-top: 1px solid #d9d0bf; margin: 2em 0;"
IMG_STYLE = (
    "display: block; width: 100%; max-width: 100%; margin: 1.1em auto; "
    "border-radius: 16px;"
)
CAPTION_STYLE = (
    "margin: 0.3em 0 1.2em; color: #66788a; font-size: 13px; text-align: center;"
)

PUBLISH_STATUS_LABELS = {
    0: "success",
    1: "publishing",
    2: "original-check-failed",
    3: "publish-failed",
    4: "audit-refused",
    5: "user-deleted-after-publish",
    6: "system-banned-after-publish",
}


class WeChatPublishError(RuntimeError):
    pass


def load_env_file(path: str | os.PathLike[str] | None) -> dict[str, str]:
    if not path:
        return {}
    env_path = Path(path)
    if not env_path.exists():
        raise FileNotFoundError(f"Env file not found: {env_path}")
    values: dict[str, str] = {}
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def normalize_bool(value: object, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "y", "on", "是"}:
        return True
    if text in {"0", "false", "no", "n", "off", "否"}:
        return False
    return default


def parse_scalar(value: str) -> object:
    stripped = value.strip()
    if not stripped:
        return ""
    if (
        (stripped.startswith('"') and stripped.endswith('"'))
        or (stripped.startswith("'") and stripped.endswith("'"))
    ) and len(stripped) >= 2:
        return stripped[1:-1]
    lowered = stripped.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    if re.fullmatch(r"-?\d+", stripped):
        try:
            return int(stripped)
        except ValueError:
            return stripped
    return stripped


def load_markdown_document(path: str | os.PathLike[str]) -> tuple[dict[str, object], str]:
    markdown_path = Path(path)
    content = markdown_path.read_text(encoding="utf-8")
    if not content.startswith("---\n"):
        return {}, content
    parts = content.split("\n---\n", 1)
    if len(parts) != 2:
        return {}, content
    _, rest = parts
    frontmatter_text = content[4 : len(content) - len(rest) - 5]
    metadata: dict[str, object] = {}
    for raw_line in frontmatter_text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, raw_value = line.split(":", 1)
        canonical = FRONTMATTER_ALIASES.get(key.strip(), key.strip())
        metadata[canonical] = parse_scalar(raw_value)
    return metadata, rest.lstrip("\n")


def resolve_article_metadata(
    metadata: dict[str, object],
    env: dict[str, str],
    source_path: str | os.PathLike[str],
) -> dict[str, object]:
    resolved = dict(metadata)
    path = Path(source_path)
    resolved["title"] = str(
        resolved.get("title")
        or resolved.get("book_title")
        or path.stem
    ).strip()
    resolved["book_title"] = str(
        resolved.get("book_title") or resolved["title"]
    ).strip()
    resolved["book_author"] = str(resolved.get("book_author") or "").strip()
    resolved["author"] = str(
        resolved.get("author") or env.get("WECHAT_DEFAULT_AUTHOR", "")
    ).strip()
    resolved["digest"] = str(resolved.get("digest") or "").strip()
    resolved["cover_image"] = str(resolved.get("cover_image") or "").strip()
    resolved["content_source_url"] = str(
        resolved.get("content_source_url")
        or env.get("WECHAT_DEFAULT_CONTENT_SOURCE_URL", "")
    ).strip()
    resolved["core_phrase"] = str(resolved.get("core_phrase") or "").strip()
    resolved["show_cover_pic"] = normalize_bool(resolved.get("show_cover_pic"), True)
    resolved["need_open_comment"] = normalize_bool(
        resolved.get("need_open_comment"),
        normalize_bool(env.get("WECHAT_OPEN_COMMENT"), True),
    )
    resolved["only_fans_can_comment"] = normalize_bool(
        resolved.get("only_fans_can_comment"),
        normalize_bool(env.get("WECHAT_ONLY_FANS_CAN_COMMENT"), False),
    )
    return resolved


def is_remote_reference(reference: str) -> bool:
    return reference.startswith("http://") or reference.startswith("https://")


def resolve_file_reference(reference: str, base_dir: str | os.PathLike[str]) -> Path:
    path = Path(reference).expanduser()
    if path.is_absolute():
        return path
    return (Path(base_dir) / path).resolve()


def inline_markup(text: str) -> str:
    rendered = html.escape(text, quote=False)
    rendered = re.sub(
        r"`([^`]+)`",
        lambda match: f"<code>{html.escape(match.group(1), quote=False)}</code>",
        rendered,
    )
    rendered = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", rendered)
    rendered = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", rendered)
    rendered = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        lambda match: (
            f'<a href="{html.escape(match.group(2), quote=True)}">'
            f"{match.group(1)}</a>"
        ),
        rendered,
    )
    return rendered


def render_markdown_to_wechat_html(
    markdown_text: str,
    base_dir: str | os.PathLike[str],
    image_resolver=None,
) -> tuple[str, list[dict[str, str]]]:
    lines = markdown_text.splitlines()
    blocks: list[str] = []
    image_refs: list[dict[str, str]] = []
    index = 0

    def resolve_image(reference: str, alt: str) -> str:
        if image_resolver is None:
            if is_remote_reference(reference):
                return reference
            return resolve_file_reference(reference, base_dir).as_uri()
        return image_resolver(reference, alt)

    while index < len(lines):
        line = lines[index].rstrip()
        stripped = line.strip()
        if not stripped:
            index += 1
            continue

        if stripped.startswith("```"):
            fence = stripped
            index += 1
            code_lines: list[str] = []
            while index < len(lines) and not lines[index].strip().startswith(fence):
                code_lines.append(lines[index])
                index += 1
            if index < len(lines):
                index += 1
            code_text = html.escape("\n".join(code_lines))
            blocks.append(f'<pre style="{PRE_STYLE}"><code>{code_text}</code></pre>')
            continue

        image_match = re.fullmatch(r"!\[(.*?)\]\((.+?)\)", stripped)
        if image_match:
            alt = image_match.group(1).strip() or "image"
            reference = image_match.group(2).strip()
            source = resolve_image(reference, alt)
            image_refs.append({"alt": alt, "source": reference, "resolved": source})
            blocks.append(
                f'<p style="margin: 1.2em 0 0.35em;"><img style="{IMG_STYLE}" '
                f'src="{html.escape(source, quote=True)}" alt="{html.escape(alt, quote=True)}" /></p>'
            )
            blocks.append(f'<p style="{CAPTION_STYLE}">{html.escape(alt)}</p>')
            index += 1
            continue

        heading_match = re.match(r"^(#{1,3})\s+(.*)$", stripped)
        if heading_match:
            level = len(heading_match.group(1))
            text = inline_markup(heading_match.group(2).strip())
            if level == 1:
                blocks.append(f'<h1 style="{H1_STYLE}">{text}</h1>')
            elif level == 2:
                blocks.append(f'<h2 style="{H2_STYLE}">{text}</h2>')
            else:
                blocks.append(f'<h3 style="{H3_STYLE}">{text}</h3>')
            index += 1
            continue

        if re.fullmatch(r"(-{3,}|\*{3,})", stripped):
            blocks.append(f'<hr style="{HR_STYLE}" />')
            index += 1
            continue

        if stripped.startswith(">"):
            quote_lines: list[str] = []
            while index < len(lines) and lines[index].strip().startswith(">"):
                quote_lines.append(lines[index].strip().lstrip(">").strip())
                index += 1
            quote_html = "<br />".join(inline_markup(item) for item in quote_lines if item)
            blocks.append(f'<blockquote style="{QUOTE_STYLE}">{quote_html}</blockquote>')
            continue

        unordered_match = re.match(r"^[-*]\s+(.*)$", stripped)
        ordered_match = re.match(r"^\d+\.\s+(.*)$", stripped)
        if unordered_match or ordered_match:
            is_ordered = ordered_match is not None
            items: list[str] = []
            while index < len(lines):
                current = lines[index].strip()
                if is_ordered:
                    current_match = re.match(r"^\d+\.\s+(.*)$", current)
                else:
                    current_match = re.match(r"^[-*]\s+(.*)$", current)
                if not current_match:
                    break
                items.append(current_match.group(1).strip())
                index += 1
            tag = "ol" if is_ordered else "ul"
            item_html = "".join(
                f'<li style="{LI_STYLE}">{inline_markup(item)}</li>' for item in items
            )
            blocks.append(f'<{tag} style="{UL_STYLE}">{item_html}</{tag}>')
            continue

        paragraph_lines: list[str] = [stripped]
        index += 1
        while index < len(lines):
            current = lines[index].rstrip()
            current_stripped = current.strip()
            if not current_stripped:
                index += 1
                break
            if re.match(r"^(#{1,3})\s+", current_stripped):
                break
            if current_stripped.startswith(">"):
                break
            if re.fullmatch(r"!\[(.*?)\]\((.+?)\)", current_stripped):
                break
            if re.match(r"^[-*]\s+", current_stripped):
                break
            if re.match(r"^\d+\.\s+", current_stripped):
                break
            if current_stripped.startswith("```"):
                break
            if re.fullmatch(r"(-{3,}|\*{3,})", current_stripped):
                break
            paragraph_lines.append(current_stripped)
            index += 1
        paragraph_text = inline_markup(" ".join(paragraph_lines))
        blocks.append(f'<p style="{P_STYLE}">{paragraph_text}</p>')

    return "\n".join(blocks), image_refs


def preview_meta_text(metadata: dict[str, object]) -> str:
    pieces = [str(metadata.get("book_title") or metadata.get("title") or "").strip()]
    if metadata.get("book_author"):
        pieces.append(f'作者: {metadata["book_author"]}')
    if metadata.get("core_phrase"):
        pieces.append(f'核心词: {metadata["core_phrase"]}')
    return " | ".join(piece for piece in pieces if piece)


def default_preview_template_path() -> Path:
    return Path(__file__).resolve().parents[1] / "assets" / "wechat_preview_template.html"


def build_preview_html(
    title: str,
    meta_text: str,
    cover_source: str,
    body_html: str,
    template_path: str | os.PathLike[str] | None = None,
) -> str:
    template_file = Path(template_path) if template_path else default_preview_template_path()
    template = template_file.read_text(encoding="utf-8")
    cover_html = ""
    if cover_source:
        cover_html = (
            '<div class="cover">'
            f'<img src="{html.escape(cover_source, quote=True)}" alt="cover" />'
            "</div>"
        )
    return (
        template.replace("{{TITLE}}", html.escape(title))
        .replace("{{META}}", html.escape(meta_text))
        .replace("{{COVER}}", cover_html)
        .replace("{{BODY}}", body_html)
    )


def guess_content_type(path: str | os.PathLike[str]) -> str:
    guessed, _ = mimetypes.guess_type(str(path))
    return guessed or "application/octet-stream"


def sniff_image_format(path: str | os.PathLike[str]) -> str | None:
    file_path = Path(path)
    try:
        with file_path.open("rb") as handle:
            header = handle.read(16)
    except OSError:
        return None
    if header.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if header.startswith(b"\xff\xd8\xff"):
        return "jpeg"
    if header.startswith((b"GIF87a", b"GIF89a")):
        return "gif"
    if header.startswith(b"BM"):
        return "bmp"
    if header.startswith(b"RIFF") and len(header) >= 12 and header[8:12] == b"WEBP":
        return "webp"
    return None


def inspect_image_reference(
    reference: str,
    base_dir: str | os.PathLike[str],
    *,
    role: str,
    alt: str | None = None,
) -> dict[str, object]:
    report: dict[str, object] = {
        "role": role,
        "source": reference,
        "alt": alt or "",
        "is_remote": is_remote_reference(reference),
        "warnings": [],
        "blocking_issues": [],
    }
    if report["is_remote"]:
        report["publish_ready"] = False
        report["warnings"].append("remote_image_should_be_localized")
        return report

    resolved_path = resolve_file_reference(reference, base_dir)
    report["resolved_path"] = str(resolved_path)
    report["exists"] = resolved_path.exists()
    if not resolved_path.exists():
        report["publish_ready"] = False
        report["blocking_issues"].append("local_image_missing")
        return report

    report["size_bytes"] = resolved_path.stat().st_size
    report["mime_guess"] = guess_content_type(resolved_path)
    actual_format = sniff_image_format(resolved_path)
    report["actual_format"] = actual_format
    if actual_format is None:
        report["publish_ready"] = False
        report["blocking_issues"].append("image_format_unrecognized")
        return report
    if actual_format not in SUPPORTED_WECHAT_IMAGE_FORMATS:
        report["publish_ready"] = False
        report["blocking_issues"].append(f"unsupported_image_format:{actual_format}")
        return report

    expected_formats = set()
    suffix = resolved_path.suffix.lower()
    if suffix in {".jpg", ".jpeg"}:
        expected_formats.add("jpeg")
    elif suffix in {".png"}:
        expected_formats.add("png")
    elif suffix in {".gif"}:
        expected_formats.add("gif")
    elif suffix in {".bmp"}:
        expected_formats.add("bmp")
    if expected_formats and actual_format not in expected_formats:
        report["warnings"].append("extension_does_not_match_actual_format")

    report["publish_ready"] = True
    return report


def build_article_validation_report(
    article_path: str | os.PathLike[str],
    metadata: dict[str, object],
    resolved: dict[str, object],
    image_refs: list[dict[str, str]],
) -> dict[str, object]:
    article_file = Path(article_path).resolve()
    required_missing = [
        field for field in REQUIRED_ARTICLE_FIELDS if not str(resolved.get(field) or "").strip()
    ]
    report: dict[str, object] = {
        "article": str(article_file),
        "source_mode": str(metadata.get("source_mode") or "").strip(),
        "required_fields_missing": required_missing,
        "blocking_issues": [],
        "warnings": [],
    }
    if required_missing:
        report["blocking_issues"].append("missing_required_frontmatter")

    cover_reference = str(resolved.get("cover_image") or "").strip()
    report["cover"] = (
        inspect_image_reference(cover_reference, article_file.parent, role="cover")
        if cover_reference
        else None
    )
    if report["cover"]:
        report["warnings"].extend(report["cover"]["warnings"])
        report["blocking_issues"].extend(report["cover"]["blocking_issues"])

    inline_reports: list[dict[str, object]] = []
    for image_ref in image_refs:
        inspected = inspect_image_reference(
            image_ref["source"],
            article_file.parent,
            role="inline",
            alt=image_ref.get("alt"),
        )
        inline_reports.append(inspected)
        report["warnings"].extend(inspected["warnings"])
        report["blocking_issues"].extend(inspected["blocking_issues"])
    report["inline_images"] = inline_reports

    if not str(resolved.get("author") or "").strip():
        report["warnings"].append("author_will_fall_back_to_empty_string")

    report["warnings"] = sorted(set(report["warnings"]))
    report["blocking_issues"] = sorted(set(report["blocking_issues"]))
    report["publish_ready"] = not report["blocking_issues"]
    report["recommended_mode"] = "draft"
    report["formal_publish_capability"] = "unknown_until_proven"
    return report


def detect_public_ip() -> dict[str, object]:
    endpoints = [
        ("https://api.ipify.org?format=json", "json"),
        ("https://ifconfig.me/ip", "text"),
    ]
    errors: list[str] = []
    for url, mode in endpoints:
        try:
            with urllib.request.urlopen(url, timeout=10) as response:
                raw = response.read().decode("utf-8").strip()
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{url}: {exc}")
            continue
        if mode == "json":
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError as exc:
                errors.append(f"{url}: invalid_json:{exc}")
                continue
            ip = str(payload.get("ip") or "").strip()
        else:
            ip = raw
        if ip:
            return {"ok": True, "ip": ip, "source": url}
    return {"ok": False, "errors": errors}


def download_to_temp(url: str) -> Path:
    response = urllib.request.urlopen(url, timeout=30)
    suffix = Path(urllib.parse.urlparse(url).path).suffix or ".bin"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as handle:
        handle.write(response.read())
        return Path(handle.name)


def encode_multipart_formdata(
    fields: dict[str, str] | None,
    files: dict[str, tuple[str, bytes, str]],
) -> tuple[str, bytes]:
    boundary = f"----CodexWeChat{uuid.uuid4().hex}"
    body = bytearray()
    if fields:
        for name, value in fields.items():
            body.extend(f"--{boundary}\r\n".encode("utf-8"))
            body.extend(
                f'Content-Disposition: form-data; name="{name}"\r\n\r\n{value}\r\n'.encode(
                    "utf-8"
                )
            )
    for field_name, (filename, content, content_type) in files.items():
        body.extend(f"--{boundary}\r\n".encode("utf-8"))
        disposition = (
            f'Content-Disposition: form-data; name="{field_name}"; filename="{filename}"\r\n'
        )
        body.extend(disposition.encode("utf-8"))
        body.extend(f"Content-Type: {content_type}\r\n\r\n".encode("utf-8"))
        body.extend(content)
        body.extend(b"\r\n")
    body.extend(f"--{boundary}--\r\n".encode("utf-8"))
    return boundary, bytes(body)


class WeChatClient:
    def __init__(self, app_id: str, app_secret: str):
        if not app_id or not app_secret:
            raise WeChatPublishError("WECHAT_APP_ID and WECHAT_APP_SECRET are required.")
        self.app_id = app_id
        self.app_secret = app_secret
        self._access_token: str | None = None
        self._expires_at = 0.0
        self._https_opener = self._build_https_opener()

    @staticmethod
    def _build_https_opener() -> urllib.request.OpenerDirector:
        # Pin WeChat API calls to TLS 1.2. In some Python runtimes the default
        # negotiation path intermittently fails here, while curl/openssl succeed
        # with TLS 1.2 against the same endpoint.
        context = ssl.create_default_context()
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        context.maximum_version = ssl.TLSVersion.TLSv1_2
        return urllib.request.build_opener(urllib.request.HTTPSHandler(context=context))

    def _request_json(
        self,
        url: str,
        *,
        method: str = "GET",
        payload: dict | None = None,
        data: bytes | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict:
        request_headers = dict(headers or {})
        body = data
        if payload is not None:
            request_headers["Content-Type"] = "application/json"
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        request = urllib.request.Request(url, data=body, headers=request_headers, method=method)
        raw = ""
        for attempt in range(3):
            try:
                with self._https_opener.open(request, timeout=30) as response:
                    raw = response.read().decode("utf-8")
                break
            except urllib.error.HTTPError as exc:
                detail = exc.read().decode("utf-8", errors="replace")
                raise WeChatPublishError(f"HTTP {exc.code} for {url}: {detail}") from exc
            except (urllib.error.URLError, ssl.SSLError) as exc:
                if attempt == 2:
                    raise WeChatPublishError(f"Network error for {url}: {exc}") from exc
                time.sleep(1.2 * (attempt + 1))
        payload_data = json.loads(raw)
        if payload_data.get("errcode") not in (None, 0):
            raise WeChatPublishError(
                f"WeChat API error {payload_data.get('errcode')}: {payload_data.get('errmsg')}"
            )
        return payload_data

    def access_token(self) -> str:
        now = time.time()
        if self._access_token and now < self._expires_at:
            return self._access_token
        query = urllib.parse.urlencode(
            {
                "grant_type": "client_credential",
                "appid": self.app_id,
                "secret": self.app_secret,
            }
        )
        payload = self._request_json(f"https://api.weixin.qq.com/cgi-bin/token?{query}")
        token = payload.get("access_token")
        if not token:
            raise WeChatPublishError("No access_token returned from WeChat.")
        self._access_token = str(token)
        expires_in = int(payload.get("expires_in", 7200))
        self._expires_at = now + max(expires_in - 120, 60)
        return self._access_token

    def _upload_file(self, endpoint: str, file_path: Path) -> dict:
        token = self.access_token()
        url = f"https://api.weixin.qq.com{endpoint}{'&' if '?' in endpoint else '?'}access_token={token}"
        file_bytes = file_path.read_bytes()
        boundary, body = encode_multipart_formdata(
            None,
            {
                "media": (
                    file_path.name,
                    file_bytes,
                    guess_content_type(file_path),
                )
            },
        )
        return self._request_json(
            url,
            method="POST",
            data=body,
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        )

    def upload_cover_material(self, file_path: Path) -> dict:
        return self._upload_file("/cgi-bin/material/add_material?type=image", file_path)

    def upload_inline_image(self, file_path: Path) -> dict:
        return self._upload_file("/cgi-bin/media/uploadimg", file_path)

    def create_draft(self, article_payload: dict) -> dict:
        token = self.access_token()
        return self._request_json(
            f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}",
            method="POST",
            payload={"articles": [article_payload]},
        )

    def submit_publish(self, media_id: str) -> dict:
        token = self.access_token()
        return self._request_json(
            f"https://api.weixin.qq.com/cgi-bin/freepublish/submit?access_token={token}",
            method="POST",
            payload={"media_id": media_id},
        )

    def get_publish_status(self, publish_id: int | str) -> dict:
        token = self.access_token()
        return self._request_json(
            f"https://api.weixin.qq.com/cgi-bin/freepublish/get?access_token={token}",
            method="POST",
            payload={"publish_id": int(publish_id)},
        )


def wait_for_publish(
    client: WeChatClient,
    publish_id: int | str,
    *,
    timeout_seconds: int = 180,
    interval_seconds: int = 5,
) -> dict:
    started = time.time()
    latest_status: dict | None = None
    while time.time() - started <= timeout_seconds:
        latest_status = client.get_publish_status(publish_id)
        status_code = int(latest_status.get("publish_status", -1))
        if status_code != 1:
            latest_status["publish_status_label"] = PUBLISH_STATUS_LABELS.get(
                status_code, "unknown"
            )
            return latest_status
        time.sleep(interval_seconds)
    if latest_status is None:
        latest_status = {"publish_id": publish_id, "publish_status": 1}
    latest_status["publish_status_label"] = "timeout"
    return latest_status
