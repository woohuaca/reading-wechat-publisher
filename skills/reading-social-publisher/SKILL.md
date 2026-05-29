---
name: reading-social-publisher
description: Use when the user wants one orchestrated workflow that turns a book or reading note into a multi-channel social package, including WeChat Official Account articles, Guizang-style covers/cards, and Xiaohongshu or Rednote draft-ready image posts.
---

# Reading Social Publisher

Use this skill as the top-level coordinator when the user wants the full path from source material to social distribution.

This skill does not replace the existing specialist skills. It decides which lane to run, keeps the assets coherent, and stops at the safest publish boundary for each platform.

## What This Skill Owns

- Source-mode honesty
- Cross-channel angle selection
- Visual package consistency
- Review-first publishing
- Platform-specific stop rules

## Orchestration Sequence

1. Establish the source lane.
   - If the user only provides a title and author, treat it as `导读笔记`.
   - If the user provides the book file, highlights, notes, or transcript, treat it as `精读笔记`.
   - Use `$reading-strategy` to create or update the structured note.

2. Decide the output lanes.
   - `WeChat longform`: use `$wechat-article-designer`.
   - `Xiaohongshu / Rednote image post`: produce a short caption plus a card set.
   - If the user wants both, keep one core angle and express it differently by channel.

3. Route the visual layer through Guizang when quality matters.
   - Use `guizang-social-card-skill` for:
     - WeChat `21:9` main cover
     - WeChat `1:1` square cover
     - 1-2 knowledge cards for longform
     - 9-15 Xiaohongshu cards when the user wants a carousel-style post
   - Keep all generated assets local.

4. Prepare review artifacts before any publish action.
   - For WeChat: produce the publish-ready markdown plus local preview.
   - For Xiaohongshu: produce the image folder, a title, a caption, and suggested hashtags.

5. Publish by the safest lane.
   - `WeChat`: use `$wechat-publisher` and default to `draft-only`.
   - `Xiaohongshu / Rednote`: default to `draft-only` in the browser.

## Xiaohongshu / Rednote Rules

- Use Browser on the creator page after the user logs in.
- The in-app browser currently cannot upload files directly.
- Ask the user to perform the file-upload step from the prepared local folder.
- After upload, fill title, caption, and hashtags automatically when possible.
- Prefer saving a draft over formal publish.
- If the platform uses a non-standard custom publish bar that resists DOM automation, pause and let the user click the final `暂存离开` or equivalent draft button.

## WeChat Rules

- Keep WeChat as a separate, explicit confirmation step.
- Run preview and preflight first.
- Draft creation is the normal finish state.
- Formal publish should remain opt-in and capability-gated.

## Output Contract

When this skill is used successfully, leave behind:

- One structured source note
- One WeChat-ready markdown article when WeChat is in scope
- One coherent local visual package
- One Xiaohongshu-ready title/caption package when Rednote is in scope
- Draft identifiers or platform status notes when a draft is created

## Companion Skills

- Source analysis: [../reading-strategy/SKILL.md](../reading-strategy/SKILL.md)
- WeChat article shaping: [../wechat-article-designer/SKILL.md](../wechat-article-designer/SKILL.md)
- WeChat draft publishing: [../wechat-publisher/SKILL.md](../wechat-publisher/SKILL.md)
- Guizang visual system: `/Users/woohuaca/.codex/skills/guizang-social-card-skill/SKILL.md`
