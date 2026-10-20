# Third-party evaluation

评估日期：2026-10-20。结论是**借鉴设计，不直接集成代码或安装脚本**。这样可以避免未知依赖、许可证不明、Claude/Windows 路径耦合和不必要的本地模型服务。

| 项目 | 可借鉴部分 | 不直接集成的原因 | 决策 |
|---|---|---|---|
| [radawaysp/codex-book-to-skill](https://github.com/radawaysp/codex-book-to-skill) | 章节级渐进加载、术语表、patterns、cheatsheet | 主要目标是把书压缩成新 Skill；流程含 PowerShell/Windows 路径，并非持续教学和掌握度跟踪 | 本地实现章节结构与知识分类，不复制源码 |
| [noahnan-max/book-to-skill](https://github.com/noahnan-max/book-to-skill) | 来源追踪、evidence gates、知识合并 | 仓库明确说明尚未选择开源许可证；不应复制或改编代码 | 仅采用“来源锚点/证据门”思想 |
| [AdkinsHan/en2zh](https://github.com/AdkinsHan/en2zh) | 每个英文段落后立即放中文、代码不翻译、术语保留英文 | 路径和操作说明面向 Claude；只解决翻译，不处理教材理解、测验和状态 | 在教学协议中重新实现格式规则 |
| [xixiaofinland/agent-skills book-tutor](https://github.com/xixiaofinland/agent-skills/tree/main/skills/book-tutor) | Socratic probe、理解检查、durable notes、no guessing | 依赖 `CLAUDE.md` 契约且没有 PDF 可靠性层和间隔调度实现 | 将教学循环改写为 Codex 项目 Skill |
| [AI-Engineer-Skool/booktutor-ai](https://github.com/AI-Engineer-Skool/booktutor-ai) | PDF→RAG tutor 的基本方向 | 需要 Docling、LM Studio、向量库和本地模型；复杂度与当前对话优先目标不匹配，且为 AGPL-3.0 | 不集成 |

本项目只声明 PyMuPDF 与 pytest 两个 PyPI 依赖，使用受限版本范围；未运行上述仓库的脚本，也未复制其代码。
