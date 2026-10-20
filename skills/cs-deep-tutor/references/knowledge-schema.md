# Knowledge and state schema

Each imported book lives at `library/books/<book-id>/`.

| Path | Responsibility |
|---|---|
| `manifest.json` | Source identity, checksum, page count, extraction warnings |
| `structure.md` | PDF table of contents or page-level fallback outline |
| `pages/page-NNNN.md` | Page-grounded extracted evidence; never hand-edit |
| `progress.json` | Current position, mastery records, errors, review schedule |
| `sessions/` | One bilingual lesson note per session |
| `knowledge/00-map.md` | Concept dependency graph and chapter structure |
| `knowledge/glossary.md` | Chinese term, English term, definition, first source |
| `knowledge/formulas.md` | Formula, assumptions, derivation, units, edge cases |
| `knowledge/algorithms.md` | Goal, invariant, steps, correctness, complexity, trade-offs |
| `knowledge/code-patterns.md` | Pattern, execution trace, use/avoid guidance |
| `knowledge/pitfalls.md` | Misconceptions, counterexamples, diagnostic question |

Use stable concept names. Merge aliases into one entry. Every durable claim needs a source page or an explicit `Tutor inference` label.

The CLI owns `progress.json`. Markdown knowledge files are agent-maintained. Prefer small edits to rewriting whole files.
