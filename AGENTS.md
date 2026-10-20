# CS Bilingual Deep Reading Project

Use the project Skill at `skills/cs-deep-tutor/SKILL.md` whenever the user asks to import, read, explain, quiz, continue, track, or review a computer-science textbook.

Preserve all source textbooks. Treat `library/sources/` and any user-supplied PDF path as read-only. Write extracted content and learning state only below `library/books/`.

Run the deterministic CLI through `python3 skills/cs-deep-tutor/scripts/reader.py`. Never hand-edit `progress.json`; use CLI state commands. Do not claim that unreadable, scanned, or layout-damaged PDF text is source content.

Follow the repository's existing Band V quality rules: cohesive components, low coupling, single responsibilities, short functions, clear names, DRY code, and comprehensive tests across success and error partitions.
