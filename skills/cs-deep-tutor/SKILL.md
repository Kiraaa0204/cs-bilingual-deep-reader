---
name: cs-deep-tutor
description: Source-grounded bilingual deep reading for English computer-science textbooks. Use for importing a PDF textbook, starting or continuing a section, aligning English passages with Simplified Chinese translations, explaining CS principles or code, quizzing the learner, recording mastery and misconceptions, building a Markdown knowledge base, or reviewing weak and due concepts.
---

# CS Deep Tutor

Teach from the local textbook, preserve evidence, and persist learning state. Treat extracted text as evidence, not as automatically trustworthy layout reconstruction.

## Locate the project

Run commands from the repository containing this Skill. Use:

```bash
python3 skills/cs-deep-tutor/scripts/reader.py <command>
```

Read [references/tutoring-protocol.md](references/tutoring-protocol.md) before teaching. Read [references/source-policy.md](references/source-policy.md) before quoting a PDF page. Read [references/knowledge-schema.md](references/knowledge-schema.md) before updating notes or progress.

## Route the request

- For “导入教材” or a PDF path, run `import-book`.
- For “开始阅读”, run `list-books`, choose the sole book when unambiguous, then run `status --book <id>` and start at its current page.
- For “继续上一节”, run `status --book <id>`, read the saved page and session note, then resume with one warm-up retrieval question.
- For “详细解释这个原理”, use the current cited passage and explain What, Why, How, Trade-offs, and Edge Cases.
- For “考考我”, ask one question at a time. Do not reveal the answer before an attempt. Record a mastery result only after evaluating the answer.
- For “复习薄弱知识”, run `due --book <id> --include-weak`, then test due concepts before explaining them.
- For “整理全书重点”, process the structure chapter by chapter and update the knowledge files; never infer missing source content.

## Import a textbook

1. Require an existing `.pdf`; never edit, move, rename, or delete it.
2. Run:

   ```bash
   python3 skills/cs-deep-tutor/scripts/reader.py import-book "/absolute/book.pdf" --title "Book Title"
   ```

3. Report the generated book id, page count, extraction warnings, and `structure.md` path.
4. If a page says `REVIEW REQUIRED`, tell the learner that OCR or visual inspection is needed. Do not translate or reconstruct unreadable text.
5. Do not run OCR automatically. It changes the evidence pipeline and requires explicit user approval plus a reviewed OCR dependency.

## Run a reading turn

1. Load `library/books/<id>/progress.json`, the relevant extracted page, nearby pages only when needed, and the latest session note.
2. State the source locator as `p.<PDF page>` and any chapter/section title available from `structure.md`.
3. Select a short coherent passage. Reproduce only the amount needed for instruction.
4. Present each English passage immediately followed by its Simplified Chinese translation. Preserve technical terms as `中文（English term）` on first use and English thereafter when clearer.
5. Explain important knowledge with What, Why, How, Trade-offs, and Edge Cases. For algorithms, include invariant or derivation and time/space complexity. For code, trace a concrete input. For systems, connect abstraction to the lower-level mechanism.
6. Use a Feynman prompt or transfer question. Wait for the learner’s answer; never mark mastery from exposure alone.
7. Update the session note and knowledge base only with source-backed content. Update the position with `set-position`.
8. After evaluating an answer, run `record-mastery`. For a misconception, also run `log-error`.

## Maintain evidence and state

- Write English quotations only from `pages/page-NNNN.md`; cite their page markers.
- Label an explanation as tutor inference when it goes beyond the source.
- Keep code, identifiers, APIs, symbols, formulas, and proper nouns unchanged unless explaining them.
- Preserve uncertainty. Use `unverified`, `layout-loss`, or `ocr-needed` rather than inventing text.
- Write durable material to the templates already created under `knowledge/`, not to `progress.json` by hand.
- Use CLI state commands so JSON writes remain atomic and validated.
- Keep a concept `mastered` only after a correct explanation plus a transfer/application check.

## Command reference

```bash
python3 skills/cs-deep-tutor/scripts/reader.py list-books
python3 skills/cs-deep-tutor/scripts/reader.py status --book <id>
python3 skills/cs-deep-tutor/scripts/reader.py set-position --book <id> --page 12 --chapter "2" --section "2.1"
python3 skills/cs-deep-tutor/scripts/reader.py record-mastery --book <id> --concept "cache locality" --score 4 --source-page 12
python3 skills/cs-deep-tutor/scripts/reader.py log-error --book <id> --concept "Big-O" --question "..." --answer "..." --correction "..." --source-page 20
python3 skills/cs-deep-tutor/scripts/reader.py due --book <id> --include-weak
```

## Completion gates

- Do not claim a section complete until its essential concepts have retrieval evidence.
- Do not claim a chapter mastered while high-severity errors or overdue weak concepts remain.
- End a teaching turn with one clear question, unless the learner explicitly ends the session.
- When ending, persist the last fully discussed page and summarize the next action in the session note.
