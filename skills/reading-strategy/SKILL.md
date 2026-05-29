---
name: reading-strategy
description: Use when the user wants a book turned into a structured reading note, framework map, chapter analysis, or WeChat-article source draft from a title, author, PDF, EPUB, highlights, excerpts, or spoken reflections.
---

# Reading Strategy

Use this skill to create the first source artifact in the workflow: a clean `.md` reading note that can later be redesigned for WeChat.

## Input Gate

- Prefer direct source material: `pdf`, `epub`, `txt`, highlights, chapter photos, or the user's own notes.
- If the user gives only a title and author, do not pretend the full book was read. Produce a clearly labeled `导读型笔记`.
- If the source quality is mixed, separate `书中明确内容` from `基于常识/公开信息的推断`.
- Apply the input promises in [references/reading-input-modes.md](./references/reading-input-modes.md) before drafting.
- Choose a framing lens from [references/reading-writing-modes.md](./references/reading-writing-modes.md) before drafting.

## Workflow

1. Identify the source mode.
   - `精读笔记`: source text or substantial highlights are available.
   - `导读笔记`: only title, author, reviews, or sparse inputs are available.
2. Identify the writing mode.
   - `结构导读`: default mode for clean explanation and framework capture.
   - `诊断模式`: use when the user wants the book turned into a reading of the times, a broken illusion, hidden mechanisms, and现实拷问.
   - `战略模式`: use when the user wants the book mapped directly to a business, product, policy, investment, or operating decision.
3. Extract one short `核心词`.
   - Use a phrase that helps name the file and captures the tension or promise of the book.
4. Create the output filename.
   - Format: `书名-作者-核心词.md`
   - Keep Chinese names when they are meaningful and readable.
5. Draft the note with the template in [references/reading-note-template.md](./references/reading-note-template.md).
6. Save the finished note as markdown.
7. End with a section that seeds the later WeChat article.
8. Make the confidence level visible.
   - `导读笔记` should not sound like a chapter-by-chapter close reading.
   - `精读笔记` should preserve page, chapter, quote, and evidence detail whenever available.

## Output Contract

- Always include a short metadata block at the top using YAML frontmatter.
- Always state `source_mode` as either `精读笔记` or `导读笔记`.
- Prefer adding `writing_mode` as one of `结构导读` / `诊断模式` / `战略模式`.
- Always include:
  - `一句话总述`
  - `这本书在解决什么问题`
  - `核心框架`
  - `关键洞见`
  - `反直觉点`
  - `行动建议`
  - `公众号改写线索`
- When chapter-level detail is available, add `章节拆解`.
- When only sparse inputs are available, replace fake certainty with `我目前能合理确认的范围`.
- In `诊断模式`, prefer sections such as `时代症候`, `它击穿了什么幻觉`, `隐藏机制`, `认知断层`, `现实拷问`.
- In `战略模式`, prefer sections such as `战略含义`, `决策映射`, `适用边界`, `下一步动作`.

## Quality Bar

- Prefer structural clarity over堆砌摘要.
- Prefer a clear problem the book is diagnosing over a flat list of points.
- Use original terminology from the book when it matters.
- Make disagreements visible instead of polishing them away.
- Preserve page numbers or chapter references whenever the source provides them.
- Never hide evidence gaps. The mode label is a promise to the reader.

## Resources

- Detailed note structure: [references/reading-note-template.md](./references/reading-note-template.md)
- Input-mode promises: [references/reading-input-modes.md](./references/reading-input-modes.md)
- Writing lenses: [references/reading-writing-modes.md](./references/reading-writing-modes.md)
- Copyable starter markdown: [assets/book-note-template.md](./assets/book-note-template.md)
