# Computer Science Bilingual Deep Reading System

`阅读cs相关书籍使用skills，纯自用`

这是一套以 Codex 对话为主、本地 Markdown 为长期记忆的计算机教材中英双语精读系统。原始 PDF 始终只读；逐页证据、知识库、进度、错题与复习计划保存在 `library/books/`。

## 一次性准备

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --only-binary=:all: \
  'setuptools>=75' 'PyMuPDF>=1.24,<2' 'pytest>=8,<10' 'PyYAML>=6,<7'
.venv/bin/python -m pip install --no-build-isolation --no-deps -e .
.venv/bin/python -m pytest
```

如果不激活虚拟环境，直接把下文的 `python3` 换成 `.venv/bin/python`。

## 导入第一本教材

可将 PDF 放进 `library/sources/`，也可以保留在任何本地目录。系统只记录绝对路径和 SHA-256，不会移动或修改原文件。

```bash
.venv/bin/python skills/cs-deep-tutor/scripts/reader.py import-book \
  "/绝对路径/Computer Systems A Programmer's Perspective.pdf" \
  --title "Computer Systems: A Programmer's Perspective" \
  --book-id "csapp"
```

导入会生成：

- `library/books/csapp/pages/`：逐页原文证据和可靠性警告
- `library/books/csapp/structure.md`：PDF 目录结构
- `library/books/csapp/knowledge/`：可长期维护的知识库
- `library/books/csapp/progress.json`：当前位置、掌握度、错题和复习日期

看到 `ocr-needed`、`unverified` 或 `layout-loss` 时，Codex 会明确停止猜测。扫描版 OCR 不会被静默启用。

## 在 Codex 中使用

导入后可以直接说：

- “开始阅读 csapp，从第 1 章开始。”
- “继续上一节。”
- “把第 36 页这段中英对照讲清楚，详细解释底层原理。”
- “用一个具体输入跟踪这段代码。”
- “考考我；在我回答前不要给答案。”
- “复习薄弱知识。”
- “整理本章的术语、算法、公式和易错点。”

Skill 会按短段落给出英文原文与紧邻的简体中文翻译，保留 English technical terms，并用 What / Why / How / Trade-offs / Edge Cases 深讲。每次只在你完成回忆与迁移检查后记录掌握。

## 继续上次进度

对 Codex 说“继续上一节”，或先自行检查：

```bash
.venv/bin/python skills/cs-deep-tutor/scripts/reader.py list-books
.venv/bin/python skills/cs-deep-tutor/scripts/reader.py status --book csapp
```

当前位置只代表“最后完整讨论的位置”，不代表已经掌握。掌握度必须有问答证据。

## 复习

对 Codex 说“复习薄弱知识”，它会先主动回忆、再纠错。也可以查看队列：

```bash
.venv/bin/python skills/cs-deep-tutor/scripts/reader.py due --book csapp --include-weak
```

评分 0–2 的概念次日重试；评分 3–5 按 1、3、7、14、30、60 天逐步延长。只有能够正确解释并迁移应用，才会进入 `mastered`。

## 设计边界

- 当前只支持 PDF；解析以页码和可验证原文为核心。
- 自动提取不等于视觉还原。表格、公式、上下标和多栏顺序出现警告时，需要检查 PDF 页面。
- 翻译和深度讲解由 Codex 在阅读会话中完成，避免用未经检查的机器批处理污染长期笔记。
- 知识库随章节精读或“整理全书重点”任务持续更新，不复制整章受版权保护的原文。

## License

本项目使用 [MIT License](LICENSE)。原始教材及其提取内容不属于本项目开源授权范围，请勿上传或再分发受版权保护的教材。
