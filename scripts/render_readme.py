"""Render the complete public collection as one browsable README."""
import csv
import io
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOPICS = [
    ('ROR', 'surveys', '📚', 'Surveys and Perspectives', 'Start with the broader landscape: scientific discovery, agentic workflows, and self-driving laboratories. This section preserves the original survey collection; topic-specific reviews also appear below.'),
    ('WP1', 'scientific-agents', '🤖', 'AI Scientists and Scientific Agents', 'Systems for research ideation, hypothesis generation, computational experimentation, and coordinated scientific workflows. Read each system in the context of its task, environment, and researcher involvement.'),
    ('WP2', 'autonomous-labs', '🧪', 'Autonomous Laboratories', 'Self-driving laboratories and embodied scientific systems in chemistry, materials, and the life sciences. For the A-Lab study, read the original article together with its author correction.'),
    ('WP3', 'scientific-evidence', '🔍', 'Scientific Reasoning and Verification', 'Scientific reasoning, evidence assessment, reproducibility, and validation. Ask which observation supports which claim, and whether the claim has been independently tested.'),
    ('WP4', 'experiment-design', '🎯', 'Active Learning and Experiment Design', 'Active learning, Bayesian optimization, and data-efficient experiment selection. Distinguish optimization within a study from improvement that transfers to subsequent scientific tasks.'),
    ('WP5', 'continual-learning', '🌱', 'Continual Learning and Agent Improvement', 'Scientific knowledge updates, memory, model and policy adaptation, and transferable capability improvement. Relevant background methods are included; their presence does not establish scientific-agent learning.'),
    ('WP6', 'benchmarks', '📊', 'Benchmarks and Scientific Evaluation', 'Evaluation of scientific knowledge, reasoning, tool use, and research workflows. Benchmarks measure different constructs and should be interpreted with their task definitions and scoring conditions.'),
]

def write(name, content):
    path = ROOT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8', newline='\n') as stream:
        stream.write(content.rstrip() + '\n')

def escape(value):
    return str(value).replace('|', '\\|').replace('[', '\\[').replace(']', '\\]').replace('\n', ' ')

def url(r):
    return (r['publication_evidence'] if r['publication_status'] in ('PUBLISHED_VERIFIED', 'ACCEPTED_VERIFIED') else '') or r['landing_url']

def link(r):
    return f"[{escape(r['title'])}]({url(r)})"

def entry(r):
    status = r['publication_status']
    tag = ' 📝 *Preprint*' if status == 'PREPRINT_CONTEMPORANEOUS' else (' ⏳ *Publication pending verification*' if status == 'PUBLICATION_PENDING_VERIFICATION' else (' ✅ *Accepted*' if status == 'ACCEPTED_VERIFIED' else ''))
    if r['type'].lower() == 'correction':
        tag += ' 🛠️ *Author correction*'
    return f"- **{escape(r['title'])}** · `{escape(r['venue'])}` · [Paper]({url(r)}){tag}"

def build():
    records = json.loads((ROOT / 'data/papers.json').read_text(encoding='utf-8'))
    snapshot = json.loads((ROOT / 'data/snapshot.json').read_text(encoding='utf-8'))
    buf = io.StringIO(newline='')
    writer = csv.DictWriter(buf, fieldnames=list(records[0]), lineterminator='\n')
    writer.writeheader()
    writer.writerows(records)
    write('data/papers.csv', buf.getvalue())
    counts = Counter(r['publication_status'] for r in records)
    by_id = {r['id']: r for r in records}
    base = 'https://github.com/YuyangSunshine/awesome-scientific-agents'
    md = f'''<p align="center">
  <img src="assets/logo.png" alt="Awesome Scientific Agents logo: scientific knowledge, experimentation, and verification" width="150">
</p>

# 🔬 Awesome Scientific Agents

### From Research Automation to Verifiable Scientific Discovery

<p>
  <a href="{base}/actions/workflows/catalog.yml"><img src="https://github.com/YuyangSunshine/awesome-scientific-agents/actions/workflows/catalog.yml/badge.svg" alt="Catalog validation"></a>
  <a href="{base}/commits/main"><img src="https://img.shields.io/github/last-commit/YuyangSunshine/awesome-scientific-agents?color=168c91" alt="Last update"></a>
  <a href="#contents"><img src="https://img.shields.io/badge/Papers-{len(records)}-168c91" alt="{len(records)} papers"></a>
  <a href="LICENSE-CONTENT.md"><img src="https://img.shields.io/badge/Content-CC_BY_4.0-405678" alt="Content license CC BY 4.0"></a>
  <a href="{base}/issues"><img src="https://img.shields.io/badge/PRs-welcome-e78970" alt="Contributions welcome"></a>
</p>

**[📌 Browse papers](#contents) · [🧭 Reading route](#reading-route) · [📥 BibTeX](references.bib) · [CSV](data/papers.csv) · [JSON](data/papers.json) · [🤝 Contribute](#contribute)**

<a id="introduction"></a>
## 👀 Why This Awesome List?

AI scientists and autonomous laboratories are bringing more of the research process into computational and experimental workflows—from asking questions and proposing hypotheses to selecting experiments and interpreting results. Yet a completed workflow leaves crucial questions open: who made the scientific decisions, which evidence supports the conclusion, and did the system become better at doing science?

This collection brings together research on **scientific agency, verifiable evidence, and continual learning** across the life sciences, chemistry, materials, and computational science. It accompanies our working review, *From Research Automation to Verifiable Scientific Discovery: Scientific Agency, Evidence, and Continual Learning*, and provides a living reading map that can grow alongside the field. The aim is to help readers connect systems to their scientific claims, understand what evaluations measure, and identify the experiments needed to establish progress.

> 🇨🇳 **为什么建立这个文献库？** 科研智能体与自主实验室正在连接问题提出、假设生成、实验执行与结果分析。我们希望沿着“谁决定科研行动、证据支持什么结论、系统如何获得能力改进”三条主线，把相关论文整理成便于阅读和持续补充的研究地图。

<p align="center">
  <img src="assets/review-overview-v2.png" alt="Review framework: research operations; agency, evidence and learning as cross-cutting analytical axes; separate scientific knowledge and agent capability update pathways; benchmark interpretation" width="100%">
</p>

*Read the map from research operations to their assessment: three analytical axes apply across the workflow; scientific knowledge revision and agent capability improvement follow distinct update pathways; benchmark interpretation depends on the evaluated unit and construct.*

**How the framework fits together.** Research operations produce questions, protocols, measurements, and conclusions. Agency locates decision authority and verification responsibility; evidence analysis traces each claim to the observations that support it; learning analysis identifies what changed and tests whether the change improved later performance. Knowledge revision can guide the next experiment, while a claim of transferable agent improvement needs a separate controlled comparison. Benchmark scores must be interpreted against the task and unit actually evaluated.

| 🤖 Agency | 🔍 Verification | 🌱 Learning |
| --- | --- | --- |
| Who proposes, selects, authorizes, and accepts scientific decisions? | What observation supports the claim, and how is it checked? | What changes, over what time scale, and does it improve later scientific tasks? |

**Collection snapshot: {snapshot['date']}** · **{len(records)} unique papers** · {counts['PUBLISHED_VERIFIED']} marked as verified publications in the source catalog · {len(records) - counts['PUBLISHED_VERIFIED']} preprints or records awaiting publication verification.

<a id="contents"></a>
## 📌 Table of Contents

- [🧭 Suggested Reading Route](#reading-route)
'''
    for _, slug, icon, title, _ in TOPICS:
        md += f'- [{icon} {title}](#{slug})\n'
    md += '''- [🗂️ About the Collection](#about)
- [🤝 Contribute](#contribute)
- [💬 Citation and Credits](#citation)

**Within each topic, papers are grouped by year, newest first.** 📝 marks preprints; ⏳ marks unresolved publication status; 🛠️ marks corrections. Other entries are marked published in the source catalog. Cross-topic listings are intentional and do not add to the unique-paper count.

<a id="reading-route"></a>
## 🧭 Suggested Reading Route

'''
    route = [
        ('📚 Establish the landscape', ['M0001', 'M0002', 'M0023'], 'Compare existing coverage and definitions before evaluating a new framework.'),
        ('🤖 Read scientific systems', ['M0015', 'M0011', 'M0016', 'M0021'], 'Compare tasks, execution environments, researcher control, and the supported scientific endpoints.'),
        ('🧪 Follow an experiment to its evidence', ['M0026', 'M0027', 'M0053'], 'Read A-Lab with its correction; distinguish synthesis, identification, novelty, and within-study optimization.'),
    ]
    for name, keys, guidance in route:
        md += f'**{name}.** {guidance}\n\n' + '\n'.join('- ' + link(by_id[k]) for k in keys) + '\n\n'
    md += '''Then explore [🌱 continual learning](#continual-learning) and [📊 benchmarks](#benchmarks). For learning, look for a frozen-versus-updated comparison, matched budgets, and tests on later tasks. For a benchmark, identify its task unit, tools, intervention rules, and scoring construct.

---

'''
    for code, slug, icon, title, description in TOPICS:
        selected = [r for r in records if code in r['wp_membership'].split(';')]
        md += f'<a id="{slug}"></a>\n## {icon} {title}\n\n{description}\n\n'
        for year in sorted({int(r['year']) for r in selected}, reverse=True):
            md += f'### {year}\n\n'
            md += '\n'.join(entry(r) for r in sorted(selected, key=lambda x: x['title'].casefold()) if int(r['year']) == year) + '\n\n'
        md += '[↑ Back to contents](#contents)\n\n---\n\n'
    unavailable = [r for r in records if not r['source_fulltext_available']]
    md += f'''<a id="about"></a>
## 🗂️ About the Collection

This is a targeted, curated working collection exported from our review library. It is open to expansion and does not claim exhaustive field coverage. Publication status and version metadata preserve the source-catalog assessment; inclusion does not establish a scientific claim or independent reproduction. Continual-learning entries include methodological background, and benchmark entries span distinct evaluation tasks.

The initial source snapshot contained {snapshot['records']} unique records; its working main text cited {len(snapshot['manuscript_cited_ids'])} of them. This repository can continue growing as the manuscript selects the references needed for its argument. Journal reference requirements continue to apply to the manuscript.

Papers are accessed through their original publication or preprint pages. Related versions of a work should be connected; genuine follow-up studies and corrections remain distinct. Read the A-Lab article alongside its author correction rather than carrying forward an earlier result without its update.

<details>
<summary>📂 Source-library access and metadata</summary>

The source snapshot had full text for {snapshot['records_with_source_fulltext']} unique records and lacked full text for {snapshot['records'] - snapshot['records_with_source_fulltext']}. These are source-library access counts. Full-text availability does not establish complete evidence coding or independent validation.

The dataset preserves publication evidence, metadata sources, topic membership, and the PDF version held by the source library. Bibliographic record keys remain in the downloadable datasets for maintenance and BibTeX matching.

**Full text unavailable in the current source-library export:**

'''
    md += '\n'.join('- ' + link(r) for r in unavailable)
    md += f'''

</details>

<a id="contribute"></a>
## 🤝 Contribute

Missing a relevant paper, a correction, or a newer publication version? [Suggest a paper]({base}/issues/new?template=paper.yml) or open a pull request. Include the primary source, scientific relevance, topic, and version information. See [CONTRIBUTING.md](CONTRIBUTING.md) for the data format and maintenance steps.

We welcome broader disciplinary coverage, verified code and dataset links, and evidence notes grounded in specific source locations. Keep scientific claims tied to observations and interpretation limits.

<details>
<summary>🛠️ Regenerate the catalog</summary>

Update `data/papers.json` and `references.bib`, then run:

```bash
python scripts/build_catalog.py
python scripts/validate.py
```

These commands regenerate this single-page README and CSV export. The maintainer can refresh from the private working library with `python scripts/build_catalog.py --import-from /path/to/2026-agent-review`; reconcile community additions before importing.

</details>

<a id="citation"></a>
## 💬 Citation and Credits

Cite the original paper for a research claim. To cite the collection itself, use [CITATION.cff](CITATION.cff).

The reading-list presentation draws inspiration from [Awesome-Agent-Papers](https://github.com/luo-junyu/Awesome-Agent-Papers), [Awesome-LLM-Scientific-Discovery](https://github.com/HKUST-KnowComp/Awesome-LLM-Scientific-Discovery), and [awesome-llm-agents](https://github.com/kaushikb11/awesome-llm-agents). The introduction, organization around our review questions, logo, and overview illustration were created for this collection.

Original repository content and curation: [CC BY 4.0](LICENSE-CONTENT.md). Maintenance scripts: [MIT](LICENSE). Linked papers retain their original licenses. The two illustrations were generated with OpenAI's built-in image generation tool; the [prompts](assets/prompts.json) document their intended design. The overview is conceptual and reports no experimental findings.

[↑ Back to contents](#contents)
'''
    write('README.md', md)
