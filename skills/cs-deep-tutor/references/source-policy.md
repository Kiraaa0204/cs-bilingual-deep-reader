# Source and PDF reliability policy

## Trust levels

- `reliable-text`: enough selectable text was extracted and no corruption signal fired.
- `layout-loss`: text exists, but a table, multi-column region, formula, or reading order may be damaged.
- `ocr-needed`: the page is image-heavy with too little extracted text.
- `unverified`: extraction failed or the page could not be inspected.

## Required behaviour

- Quote only characters present in the extracted page file.
- Keep the `PDF page` marker even when printed book numbering differs.
- Treat table rows, equations, superscripts, subscripts, and multi-column order as suspect until visually checked.
- Explicitly say “该页解析不可靠，暂不翻译这部分” when evidence is insufficient.
- Never silently repair truncated code, formulas, or prose.
- Distinguish the author’s claim from tutor inference and general CS background.

## Copyright-aware notes

Store short passages needed for bilingual alignment, plus original explanations and source locators. Do not reproduce whole chapters in the knowledge base. Extracted page files remain local derived data and must not be published.
