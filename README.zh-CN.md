# Awesome Scientific Agents · 科研智能体论文索引

[English](README.md) · [完整分类](README.md#contents) · [BibTeX](references.bib) · [CSV](data/papers.csv) · [JSON](data/papers.json)

围绕 **AI Scientist、自主实验室、可验证科学发现与持续学习** 的持续更新文献库，配套工作综述 *From Research Automation to Verifiable Scientific Discovery: Scientific Agency, Evidence, and Continual Learning*。

初始快照（2026-10-12）包含 **90 篇去重文献**：源目录标记 68 篇已核实发表，22 篇为同期预印本。分类保留跨专题归属，同一文献使用稳定的 `Mxxxx` ID。该集合来自定向检索工作库，覆盖范围仍可扩充；收录不代表能力主张已得到独立验证。

## 分类入口

| 分类 | 入口 |
| --- | --- |
| 综述与观点 | [Surveys](papers/surveys.md) |
| AI Scientist 与科研智能体 | [Scientific agents](papers/scientific-agents.md) |
| 自主实验室与具身科研 | [Autonomous labs](papers/autonomous-labs.md) |
| 科学推理、证据与验证 | [Scientific evidence](papers/scientific-evidence.md) |
| 主动学习、贝叶斯优化与实验决策 | [Experiment design](papers/experiment-design.md) |
| 持续学习与科研能力改进 | [Continual learning](papers/continual-learning.md) |
| Benchmark 与科学评价 | [Benchmarks](papers/benchmarks.md) |

## 如何使用

先读[阅读路线](docs/reading-guide.md)，再按专题浏览。论文条目链接到出版社、会议或预印本来源。正式发表与预印本分别列出；源库持有的 PDF 版本在数据字段中注明。A-Lab 原文 `M0026` 应与更正 `M0027` 一起阅读。

阅读时关注三个问题：**谁决定科研行动、哪些证据支持结论、系统实际学到了什么**。任务完成、科学知识更新与科研能力改进分别判断，不能仅凭自动化流程或结果提升混为一谈。

综述正文根据论证需要选择参考文献；本仓库可以持续收录相关工作。初始正文选用了 51 篇，完整库有 90 篇，具体见[综述配套说明](docs/review-companion.md)。期刊引用要求仍按投稿时指南执行。

## 维护与贡献

通过 [Issue](https://github.com/YuyangSunshine/awesome-scientific-agents/issues/new?template=paper.yml) 推荐论文，或按[贡献规范](CONTRIBUTING.md)提交 PR。提供原始来源、归属分类和版本信息。数据源是 `data/papers.json`；维护 BibTeX 后运行：

```bash
python scripts/build_catalog.py
python scripts/validate.py
```

源库有 79 篇全文、11 篇尚未获得全文，详见[来源与访问边界](docs/provenance.md)。此处的全文可用性描述源库快照，论文通过原始来源访问。仓库文本与整理采用 [CC BY 4.0](LICENSE-CONTENT.md)，维护脚本采用 [MIT](LICENSE)；论文保留各自许可。
