# 科研阅读 Skills

五套可独立使用的科研阅读工作流。打开对应目录的 SKILL.md，按案例准备真实材料和输出约定。Python 辅助工具可从各目录直接运行。在 Playground 外使用时，将文中 /skills/weekly-skill 替换为该 Skill 的安装目录。

| 目录 | 用途 | 辅助工具 |
|---|---|---|
| [reading01](reading01) | 科研 PDF 解析 | Poppler 提取坐标、双栏顺序、页眉和题注候选 |
| [reading02](reading02) | 文献翻译 | 原文与译文对齐、术语与数字差异检查 |
| [reading03](reading03) | 结构化阅读笔记 | 校验引文定位、按原章节输出笔记和检索索引 |
| [reading04](reading04) | Nanopublication | 将带来源断言导出为 JSON-LD 命名图 |
| [reading05](reading05) | 文献知识图谱 | 实体别名消歧与带逐边证据的有向路径查询 |

Python 辅助工具使用标准库；PDF 解析的 pdftotext 与渲染命令由 Poppler 提供。各目录提供最小调用示例、输入输出和已知限制。
