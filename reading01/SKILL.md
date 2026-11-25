---
name: paper-layout-reader
description: 将科研 PDF 的文字、跨栏版面、表格和公式解析为带页码和区块坐标的可核验结构。
---
先对每个实际 PDF 运行 pdftotext -bbox-layout paper.pdf /app/work/page.html（Poppler，缺失时用 PyMuPDF 的 page.get_text("dict")）。用 pdftoppm -f N -l N -scale-to 1400 -png paper.pdf /app/work/page 渲染疑难页，页号从 1 起。保留物理页号、印刷页码和每个块的 bbox，注明坐标原点与单位。
1. 依页按行的横向空隙寻找稳定栏沟。通栏标题、摘要或表格上下边缘把页面分成水平带，在各带内依原文书写方向逐栏从上往下读。用两栏末句与下一栏首句检查断词、标点和小节编号；续接文本保留两个原始定位。重复页眉页脚单列记录。
2. 按编号、字号和缩进构建章节树；标题、作者单位、图注、脚注与引用列表分别标记。逐块逐字输出，保留原始换行和单独的阅读顺序索引。对每个表格建带行列号的单元格阵列，记录合并跨度、层级表头、单位和脚注。续表先核对列名与单位再拼接。公式按编号和坐标切出局部图，对照上下标、负号、希腊字母与字体映射。
3. 无文字或替代字符异常的页先渲染 300 dpi，再以实际语言运行 tesseract page.png stdout -l eng tsv（中文需 chi_sim）。按图核验低置信词；无法分辨的符号保留裁图和 uncertain 标志。加密或缺页报告受影响范围。
4. 核查页数、各栏第一/末行、表格维度、图表题注配对及引用编号连续性。标明修正前后的具体错序块 ID。只对源页可见的结构赋值。
最小调用示例：输入一页双栏 PDF 和“提取方法节”。按上面流程得到示意块 {"id":"p1-b4","section":"Methods","page":1,"bbox":[45,130,260,178],"text":"…","next":"p1-b5"}；实际任务填原文和测得坐标。

## 运行与交付
读取 /input/case.json、task.md 及引用的实际材料，把每个 output_contract 字段映射到本次要生成的内容。以文件内容校正题签。中间文件留在 /app/work，先保存可核验的部分结果，再补全。最终写 /app/output/result.json，保留原 case_id 和契约要求的名称、层次、类型，另存案例要求的可编辑产物。Office 类产物需用可用的渲染器实际导出 PDF/PNG 供检查。
每条关键结果附文件名、页/节/行或图表号、最短可核对原文；推断与原文分开。缺失、未报告、材料冲突和工具失败分别标记，列出已完成范围、失败位置及下一步。记录实际变更与证据，不估算对照得分。检查 JSON 可解析、所有引用的文件存在、打开最终产物并抽核首尾及高风险项。运行 python3 /skills/weekly-skill/check.py /input/case.json /app/output/result.json 检查身份及标准 JSON Schema 的必需键；非标准契约逐项人工核对。依赖 Python 3.8+ 标准库。

## 首选版面提取入口
运行 python3 /skills/weekly-skill/layout.py paper.pdf /app/work/blocks.json（Python 3.8+、Poppler pdftotext）。输出每页物理尺寸、推定栏沟、按阅读顺序排列的区块及原文坐标。仅当左右两侧文字在纵向重叠且有足够空隙时，脚本才采用双栏顺序。通栏块作为分隔符。按 review 核对重叠区块与空文字层，对三栏、侧注、表格及右向左文字须按页图人工校正。该中间结果用于进一步结构识别和填写案例输出。

在 layout.py 后运行 python3 /skills/weekly-skill/structure.py blocks.json annotated.json。它根据跨页重复文本与顶部/底部几何位置识别页眉页脚候选，另标记章节起点与图表题注。输出保留全部原文、坐标和稳定 ID，可从排除页眉页脚的正文跳回原块。短标题、页边重复表头、连续公式编号可能误判；按渲染页确认，再用 section_anchor 组织层级。单页文件不以“重复”判断页眉。
