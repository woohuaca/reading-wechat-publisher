# Guizang Integration Guide

Use this note when `wechat-article-designer` needs higher visual quality.

## When To Route Through Guizang

Prefer `guizang-social-card-skill` when any of the following is true:

- the user explicitly asks for stronger排版、插图设计、封面质感、社交卡质量
- the article is likely to be published to WeChat and should look less like a plain markdown export
- the content benefits from a `Swiss` or `Editorial Magazine x E-ink` visual system
- the article needs a proper WeChat cover pair: `21:9` main cover plus `1:1` square cover
- the article includes screenshots, data views, concept cards, or should feel more magazine-like

## What To Produce

For WeChat-oriented article packages, the preferred output is:

1. One `21:9` main cover for publication.
2. One `1:1` square cover for visual checking and cross-platform reuse.
3. One to two knowledge cards that carry a real argument, not decorative filler.

## Decision Rule

- `Swiss`: use for systems, frameworks, AI, strategy, product, data, and sharper analytical pieces.
- `Editorial Magazine x E-ink`: use for slower essays, social diagnosis, book-commentary pieces, historical or geopolitical writing, and long-form feature tone.

## Image Intake Rule

If there are no usable screenshots or photos, ask once:

`这篇我需要 1-2 张图。三种走法：`

- `A. 你自己有照片 / 截图，传给我（推荐）`
- `B. 我去 Pexels / Unsplash / Flickr 帮你找`
- `C. 用 AI 生成`

Do not keep re-asking later. Accept the user's choice and proceed.

## Practical Constraints In This Workflow

- Today, the WeChat publisher script still uploads one main cover image. The `1:1` square cover is kept for review, reuse, and future channels.
- Keep all generated assets local so the publisher script can upload them.
- Use one coherent visual system across cover and cards; avoid a magazine cover with unrelated plain cards.
