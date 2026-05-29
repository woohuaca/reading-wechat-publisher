# WeChat Layout Guide

## Goal

Turn a strong note into a strong phone-reading article. The output stays as markdown, but it must already contain the metadata and image references needed for publishing.

## Structure

Use this pacing unless the material strongly argues otherwise:

1. Hook
2. Why this book matters now
3. Core framework
4. One or two high-value examples
5. Actionable takeaway
6. Closing line

## Cover Image Priority

1. Amazon listing cover
2. Publisher or author site
3. Open Library or public catalog record
4. A fallback image with explicit labeling

When using a fallback instead of the canonical cover, say so in the working notes.

## Image Plan

- Use one cover image.
- Use one knowledge card for the book's core framework when the idea benefits from compression.
- Add one or two inline images only if they reduce cognitive load or improve pacing.
- Prefer meaningful quote cards, matrices, timelines, and before/after diagrams over generic decorative art.

## Markdown Conventions

- Use YAML frontmatter for publish metadata.
- Use markdown image syntax: `![alt](./relative/path.png)` or `![alt](https://...)`.
- Keep remote image use deliberate. The publisher script will upload them to WeChat.
- Keep headings shallow. `#`, `##`, and `###` are usually enough.

## WeChat Style Notes

- Short paragraphs win.
- One big point per section.
- Avoid back-to-back long blockquotes.
- Let subheads carry meaning.
- End sections with a sentence that pulls the reader into the next one.
