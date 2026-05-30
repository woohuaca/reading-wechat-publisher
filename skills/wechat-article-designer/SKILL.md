---
name: wechat-article-designer
description: Use when the user wants a reading note or long markdown article redesigned into a WeChat Official Account article with mobile-friendly pacing, cover art, knowledge cards, inline illustrations, and publish-ready metadata.
---

# Wechat Article Designer

Use this skill after the reading note exists. It reshapes the note into a mobile-first WeChat article and leaves a publish-ready markdown file with image references and frontmatter metadata.

When the user asks for stronger cover design, knowledge-card quality, Swiss/editorial layouts, WeChat cover pairs, or better social readability, route the visual package through `guizang-social-card-skill` at `/Users/woohuaca/.codex/skills/guizang-social-card-skill/SKILL.md`.

Knowledge-card default rule: from now on, treat `guizang-social-card-skill` as the standard path for article knowledge cards. Do not default to ad-hoc local card scripts for normal delivery. Local scripts are fallback-only when Guizang is unavailable, clearly blocked, or the user explicitly asks for a very fast rough draft.

## Workflow

1. Read the source note completely.
2. Define the article angle.
   - Pick one hook, one promise, and one emotional payoff.
3. Build a WeChat-friendly structure.
   - Strong opening
   - 3-5 main sections
   - clean transitions
   - short closing with one memorable line
4. Design the imagery plan.
   - Cover priority: Amazon listing cover first, then publisher site, then Open Library, then a clearly labeled fallback.
   - Default visual lane: if the user asks for higher design quality or the article is likely to be published, use `guizang-social-card-skill` to produce a coherent WeChat cover package and 1-2 stronger cards.
   - WeChat cover pair: prefer a `21:9` main cover plus `1:1` square cover preview package when using `guizang-social-card-skill`, even if only the main cover is uploaded to WeChat today.
   - Knowledge cards: use `guizang-social-card-skill` first and by default. Use `imagegen` only when the content specifically needs a generated diagram, matrix, timeline, or concept illustration.
   - Inline images: use only when they advance comprehension or rhythm.
   - If there are no usable images or screenshots, follow the one-shot intake branch from `guizang-social-card-skill`: ask once whether to use user-supplied images, web-sourced images, or AI-generated images.
5. Write a new markdown file using the template in [assets/wechat-article-template.md](./assets/wechat-article-template.md).
6. Run an editorial second pass with [references/wechat-editorial-checklist.md](./references/wechat-editorial-checklist.md).
7. Prefer local image paths for the final article.
   - Remote images are acceptable during drafting but should usually be localized before publishing.
8. Keep all publish metadata in frontmatter so the bundled scripts can use it directly.
9. Stop for user review before publishing.

## Output Contract

- Output filename should usually be `书名-作者-核心词-公众号.md`.
- Preserve or add these frontmatter keys:
  - `title`
  - `author`
  - `book_title`
  - `book_author`
  - `core_phrase`
  - `digest`
  - `cover_image`
  - `content_source_url`
  - `show_cover_pic`
  - `need_open_comment`
  - `only_fans_can_comment`
- Insert local or remote images with markdown image syntax: `![alt](path-or-url)`.
- Prefer local image paths for generated knowledge cards so the publisher script can upload them.

## Design Rules

- Optimize for phone reading, not desktop width.
- For WeChat longform, do not repeat the article title as the first body heading unless there is a deliberate design reason.
- Keep paragraphs short.
- Avoid more than one dense list in a row.
- Use subheads that carry meaning, not generic labels.
- Convert abstract ideas into one or two visual anchors.
- If the book is concept-heavy, add one knowledge card near the midpoint.
- Prefer one coherent visual system per article package instead of mixing unrelated cover and card styles.
- For stronger publish-ready output, prefer Guizang-style `Swiss` or `Editorial Magazine x E-ink` layouts over plain text-on-gradient cards.
- When visual evidence exists, make it part of the page argument; do not treat images as decoration.
- Favor large, legible display text and clean hierarchy over dense poster copy.
- If a knowledge card is included, assume it should come from Guizang unless the user says otherwise.

## Resources

- Layout and image checklist: [references/wechat-layout-guide.md](./references/wechat-layout-guide.md)
- Editorial second-pass checklist: [references/wechat-editorial-checklist.md](./references/wechat-editorial-checklist.md)
- Guizang integration guide: [references/guizang-integration.md](./references/guizang-integration.md)
- Publish-ready markdown starter: [assets/wechat-article-template.md](./assets/wechat-article-template.md)
