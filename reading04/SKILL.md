---
name: grounded-nanopublications
description: 将科研材料拆为独立可核验的断言，绑定最小充分证据、原始来源和发布信息，导出机器可读记录。
---
逐篇建立来源记录，包括实际标题、作者、年份、版本、DOI 或文件标识、物理页和印刷页对应。缺 DOI 使用本地文献标识。阅读实物，定位问题指定段落及解释所需图表。每个并列谓词分别判断真假，拆成独立记录，同时保留共享的样本、条件、比较对象、方向、量纲、否定和可能性。区分作者结果、引用他人成果、设想和由多段证据推断的关系。
每条记录建三个层次：
- assertion：稳定本地 ID、主语、谓词、宾语、约束、极性与原文模态。连续量明确测量对象与参照。
- provenance：逐字短引及精确文件/页/段/图表行列；需要跨句消解代词时同时附前句；间接推理列出中间前提和缺口。明确每个引文实际支撑哪条边。
- publication-info：此记录的生成方式和来源版本，将论文作者与断言整理者区分。以来源 ID、锚点及段内序号生成确定性本地 ID，保留版本差异。
输出案例规定的 JSON/JSON-LD 或 RDF。需标准 nanopub 时用 TriG，head 图以 np:hasAssertion、np:hasProvenance、np:hasPublicationInfo 指向三个独立命名图；provenance 图用 prov:wasDerivedFrom 关联 assertion 图与文献，pubinfo 图描述 nanopub。无真实持久 ID 则使用 urn:local: 标识。RDF 用 rdflib.Dataset().parse(path,format="trig") 重读验证，可用 JSON 时优先用标准库重读。逐条核对方向、限定、证据是否足以推出断言；置信度以“原文直接陈述/需跨句/仅间接”及理由表述。
示例：输入“在氮气下，A 的损耗低于 B，但寿命未测量”。调用本 Skill 提取比较。示意断言 A/lowerLossThan/B，condition=氮气，证据定位=示例段1；寿命记未测量，不能生成寿命优于边。

## 运行与交付
读取 /input/case.json、task.md 及引用的实际材料，把每个 output_contract 字段映射到本次要生成的内容。以文件内容校正题签。中间文件留在 /app/work，先保存可核验的部分结果，再补全。最终写 /app/output/result.json，保留原 case_id 和契约要求的名称、层次、类型，另存案例要求的可编辑产物。Office 类产物需用可用的渲染器实际导出 PDF/PNG 供检查。
每条关键结果附文件名、页/节/行或图表号、最短可核对原文；推断与原文分开。缺失、未报告、材料冲突和工具失败分别标记，列出已完成范围、失败位置及下一步。记录实际变更与证据，不估算对照得分。检查 JSON 可解析、所有引用的文件存在、打开最终产物并抽核首尾及高风险项。运行 python3 /skills/weekly-skill/check.py /input/case.json /app/output/result.json 检查身份及标准 JSON Schema 的必需键；非标准契约逐项人工核对。依赖 Python 3.8+ 标准库。

需要命名图时，先把核实过的断言写入 records.json 数组，再运行 python3 /skills/weekly-skill/serialize.py records.json claims.jsonld。每项含 doc、version、anchor、id（该锚点内稳定序号，以字符串表示）、subject、predicate、object、evidence（原文）、basis（证据性质及理由）；condition、polarity、modality 用文本保留范围，author/year/doi 按实物补齐。版本未知用明确的本地输入文件哈希标识，不推测官方版本。输出使用 JSON-LD 展开的 IRI 与 head/assertion/provenance/pubinfo 四张命名图。一条记录只有一个独立主谓宾陈述。数值比较的分母、单位与参照对象应连同陈述记录。回查 provenance 中的引文是否在原文 anchor 出现，再做蕴含核验。相同源/版本/锚点/序号的重复记录会报错，修正序号前先检查是否重复抽取。
