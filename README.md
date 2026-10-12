# Awesome Scientific Agents

A curated reading list on **AI scientists, autonomous laboratories, verifiable scientific discovery, and continual learning**.

[中文说明](README.zh-CN.md) · [Reading guide](docs/reading-guide.md) · [Taxonomy](docs/taxonomy.md) · [Contributing](CONTRIBUTING.md) · [BibTeX](references.bib) · [CSV](data/papers.csv) · [JSON](data/papers.json)

This living bibliography accompanies a working review, *From Research Automation to Verifiable Scientific Discovery: Scientific Agency, Evidence, and Continual Learning*. It connects research automation to three questions: **who controls scientific decisions, what evidence supports a claim, and what a system actually learns**.

**Library snapshot: 2026-10-12** — 90 unique records; 68 marked as verified publications in the source catalog; 22 preprints or records pending publication verification. These labels preserve the source-library assessment at the snapshot date. Classification is curated; inclusion is not endorsement or evidence of independent reproduction.

## Start here

- [Recommended reading route](docs/reading-guide.md): surveys → scientific systems → claim verification → learning → evaluation.
- [Complete paper lists](#contents): papers may appear in more than one topic; stable `Mxxxx` IDs identify unique records.
- [Review and library relationship](docs/review-companion.md): the manuscript selects references for its argument; this repository can expand continuously.
- [Snapshot and provenance](docs/provenance.md): targeted coverage, version distinctions, and unresolved full-text access.

## Contents

| Topic | Records | Reading list |
| --- | ---: | --- |
| Surveys and perspectives | 10 | [Browse](papers/surveys.md) |
| AI scientists and scientific agents | 15 | [Browse](papers/scientific-agents.md) |
| Self-driving laboratories and embodied science | 17 | [Browse](papers/autonomous-labs.md) |
| Scientific reasoning, evidence and verification | 14 | [Browse](papers/scientific-evidence.md) |
| Active learning and experimental design | 14 | [Browse](papers/experiment-design.md) |
| Continual learning and agent improvement | 15 | [Browse](papers/continual-learning.md) |
| Benchmarks and scientific evaluation | 17 | [Browse](papers/benchmarks.md) |

Topic counts overlap. Continual-learning entries include background methods; benchmarks span different task constructs and are not a common leaderboard.

## How to read this collection

**Scientific agency:** distinguish hypothesis generation, experiment selection, execution permission, verification, and acceptance of conclusions. **Evidence:** separate task completion, measurement, predictive accuracy, causal or mechanistic explanation, novelty, and generalization. **Learning:** distinguish accumulating records, updating scientific beliefs, changing a model or policy, and demonstrating transferable capability gains.

Published articles and preprints are listed separately. Corrections remain separate linked records; for A-Lab, read `M0026` with `M0027`. PDF-version and access fields in the dataset refer to the source-library snapshot. Article access is through official landing pages; bibliographic status does not establish the strength of a scientific claim.

## Contribute and maintain

Suggest a paper with the [paper suggestion form](https://github.com/YuyangSunshine/awesome-scientific-agents/issues/new?template=paper.yml), or submit a pull request following [CONTRIBUTING.md](CONTRIBUTING.md). Include a primary source, a topic, and version information. Update `data/papers.json` and `references.bib`, then run:

```bash
python scripts/build_catalog.py
python scripts/validate.py
```

The maintenance roadmap is to add verified code/dataset links, expand disciplinary coverage, and attach paper-level evidence notes after source review. No automatic capability ratings are assigned.

## Citation and license

Use the linked paper and its publication metadata when citing research. To cite the collection, use [CITATION.cff](CITATION.cff). Repository prose and curation are available under [CC BY 4.0](LICENSE-CONTENT.md); maintenance scripts are [MIT licensed](LICENSE). Linked papers retain their original licenses.
