"""Render the complete public collection as one browsable README."""
import csv
import io
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

MAIN_SECTIONS = [
    ('Surveys and Perspectives', 'surveys-and-perspectives', '📚',
     'Field-level syntheses, perspectives, roadmaps, and historical accounts.'),
    ('Scientific Agents and Systems', 'scientific-agents-and-systems', '🤖',
     'Scientific agents and integrated systems, assigned once according to their primary contribution.'),
    ('Evaluation and Research Infrastructure', 'evaluation-and-research-infrastructure', '📊',
     'Benchmarks, datasets, environments, evaluation frameworks, and supporting research infrastructure.'),
]

FUNCTIONS = [
    ('Action Planning', 'action-planning', '🧭',
     'Formulating hypotheses, designing experiments, selecting actions, and planning scientific workflows.'),
    ('Observation Acquisition', 'observation-acquisition', '🔬',
     'Obtaining evidence through experiments, computation, data access, tool use, or knowledge retrieval.'),
    ('Claim Assessment', 'claim-assessment', '🔍',
     'Analyzing results, checking evidence, validating conclusions, and assessing scientific claims.'),
    ('Experience Reuse', 'experience-reuse', '♻️',
     'Retaining memory, updating knowledge or policies, and reusing experience to improve later studies.'),
]
FUNCTION_EMOJI = {name: icon for name, _, icon, _ in FUNCTIONS}

BENCHMARK_CATEGORIES = [
    ('Component competence', '🧩 Component Competence',
     '科研组件能力 · Coding, scientific knowledge, and multimodal interpretation.'),
    ('Research trajectories and replication', '🧭 Research Trajectories and Replication',
     '科研轨迹与复现 · Data-grounded workflows, hypothesis recovery, and paper replication.'),
    ('Experimental decisions', '🎯 Experimental Decisions',
     '实验决策 · Experiment selection and optimization under a resource budget.'),
    ('Interactive environments', '🌐 Interactive Environments',
     '交互环境 · Sequential scientific tasks in simulated worlds.'),
]


def write(name, content):
    path = ROOT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8', newline='\n') as stream:
        stream.write(content.rstrip() + '\n')


def escape(value):
    return str(value).replace('|', '\\|').replace('[', '\\[').replace(']', '\\]').replace('\n', ' ')


def public_url(record):
    official = record['publication_evidence'] if record['publication_status'] in {
        'PUBLISHED_VERIFIED', 'ACCEPTED_VERIFIED'} else ''
    return official or record['landing_url']


def link(record):
    return f"[{escape(record['title'])}]({public_url(record)})"


def status_tag(record):
    status = record['publication_status']
    if status == 'PREPRINT_CONTEMPORANEOUS':
        return ' 📝 *Preprint*'
    if status == 'PUBLICATION_PENDING_VERIFICATION':
        return ' ⏳ *Publication pending verification*'
    if status == 'ACCEPTED_VERIFIED':
        return ' ✅ *Accepted*'
    return ''


def contribution_note(record):
    contributions = record['function_contributions']
    if record['main_section'] == 'Scientific Agents and Systems':
        contributions = [item for item in contributions if item != record['primary_function']]
        prefix = ' · Other contributions: '
    else:
        prefix = ' · Functional coverage: '
    if not contributions:
        return ''
    return prefix + ' '.join(FUNCTION_EMOJI[item] for item in contributions)


def correction_relations(records):
    title_to_id = {record['title'].casefold(): record['id'] for record in records
                   if record['type'].casefold() != 'correction'}
    by_parent = defaultdict(list)
    unattached = []
    for record in records:
        if record['type'].casefold() != 'correction':
            continue
        base_title = re.sub(r'^Author Correction:\s*', '', record['title'], flags=re.I).casefold()
        parent = title_to_id.get(base_title)
        if parent:
            by_parent[parent].append(record)
        else:
            unattached.append(record)
    return by_parent, unattached


def paper_entry(record, corrections_by_parent):
    line = (f"- **{escape(record['title'])}** · `{escape(record['venue'])}` · "
            f"[Paper]({public_url(record)}){status_tag(record)}{contribution_note(record)}")
    for correction in corrections_by_parent.get(record['id'], []):
        line += (f"\n  - 🛠️ **{escape(correction['title'])}** · "
                 f"[Correction]({public_url(correction)})")
    return line


def year_groups(records, corrections_by_parent, heading_level):
    if not records:
        return '*No records in this category.*\n\n'
    md = ''
    for year in sorted({int(record['year']) for record in records}, reverse=True):
        md += f"{'#' * heading_level} {year}\n\n"
        selected = sorted((record for record in records if int(record['year']) == year),
                          key=lambda item: item['title'].casefold())
        md += '\n'.join(paper_entry(record, corrections_by_parent) for record in selected) + '\n\n'
    return md


def benchmark_resource_map(records_by_id):
    resources = list(csv.DictReader(
        (ROOT / 'data/benchmark_resources.csv').open(encoding='utf-8-sig')))
    datasets = list(csv.DictReader(
        (ROOT / 'data/dataset_roles.csv').open(encoding='utf-8-sig')))
    md = '''### 🗺️ Benchmark and Dataset Resource Map

The expanded resource review organizes evaluation around four families: **component competence**, **research trajectories and replication**, **experimental decisions**, and **interactive environments**. Scientific data can fit a model, ground a claim, emulate a response, or evaluate capability; these roles require different provenance, splits and independence conditions.

<img src="assets/fig07-benchmarks-datasets.png" alt="Benchmark and dataset map: component competence, research trajectories, experimental decisions, interactive environments and four roles of scientific data" width="100%">

*Figure 7 from the working review. Named resources illustrate distinct evaluation constructs; screen traces and equipment are schematic. A benchmark score supports its evaluated construct rather than a universal measure of scientific discovery.*

The source resource review (2026-10-12) includes **11 resources: nine marked published and two contemporaneous preprints**, plus **four dataset families**. These resources link to papers already in this collection; they do not add 11 new unique publications. [Resource ledger](data/benchmark_resources.csv) · [Dataset roles](data/dataset_roles.csv) · [Review scope](data/resource_review_scope.json).

'''
    for category, heading, description in BENCHMARK_CATEGORIES:
        md += f'#### {heading}\n\n{description}\n\n'
        md += ('| Resource | Evaluated task | Paper | Official resource | Interpretation boundary |\n'
               '| --- | --- | --- | --- | --- |\n')
        for resource in resources:
            if resource['review_category'] != category:
                continue
            paper = records_by_id[resource['source_id']]
            label = resource['resource'] + (
                ' 📝' if paper['publication_status'] == 'PREPRINT_CONTEMPORANEOUS' else '')
            task = resource['family'].replace(' [preprint]', '')
            md += (f"| {label} | {escape(task)} | [Paper]({public_url(paper)}) | "
                   f"[Official resource]({resource['official_resource_url']}) | "
                   f"{escape(resource['scientific_boundary'])} |\n")
        if category == 'Experimental decisions':
            md += ('\nMeasured-response companion: [ALDE GB1/TrpB experimental data]'
                   '(https://zenodo.org/records/12196802). These landscapes support historical '
                   'experiment-selection replay; they are distinct from new wet-lab trials.\n')
        md += '\n'
    md += '''**Version-aware reading.** Keep revised splits, evaluator releases and original paper scales separate. For ScienceAgentBench, retain the verified-split distinction; for PaperBench, distinguish full replication from Code-Dev/code-only evaluation; for BixBench, record the question-set revision. For Olympus and ALDE, distinguish measured landscapes, fitted emulators, historical replay and new wet-lab experiments. Version details are inherited from the source resource ledger; this repository reports no new benchmark execution or performance ranking.

'''
    md += '''<details>
<summary>🗃️ Four dataset families and their use conditions</summary>

| Dataset family | Role | Conditions |
| --- | --- | --- |
'''
    for dataset in datasets:
        md += f"| {escape(dataset['family'])} | {escape(dataset['role'])} | {escape(dataset['conditions'])} |\n"
    md += '\n</details>\n\n'
    return md


def build():
    records = json.loads((ROOT / 'data/papers.json').read_text(encoding='utf-8'))
    snapshot = json.loads((ROOT / 'data/snapshot.json').read_text(encoding='utf-8'))
    records_by_id = {record['id']: record for record in records}
    corrections_by_parent, unattached_corrections = correction_relations(records)

    # Export list-valued functional contributions as a compact semicolon-separated CSV field.
    buf = io.StringIO(newline='')
    writer = csv.DictWriter(buf, fieldnames=list(records[0]), lineterminator='\n')
    writer.writeheader()
    for record in records:
        exported = dict(record)
        exported['function_contributions'] = ';'.join(record['function_contributions'])
        writer.writerow(exported)
    write('data/papers.csv', buf.getvalue())

    counts = Counter(record['publication_status'] for record in records)
    research_work_count = sum(record['type'].casefold() != 'correction' for record in records)
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
</p>

**[📌 Browse papers](#contents) · [🧭 Reading route](#reading-route) · [📥 BibTeX](references.bib) · [CSV](data/papers.csv) · [JSON](data/papers.json) · [🤝 Contribute](#contribute)**

<a id="introduction"></a>
## 👀 Why This Awesome List?

AI scientists and autonomous laboratories are bringing more of the research process into computational and experimental workflows—from asking questions and proposing hypotheses to selecting experiments and interpreting results. Yet a completed workflow leaves crucial questions open: who made the scientific decisions, which evidence supports the conclusion, and did the system become better at doing science?

This collection brings together research on **scientific agency, verifiable evidence, and continual learning** across the life sciences, chemistry, materials, and computational science. It accompanies our working review, *From Research Automation to Verifiable Scientific Discovery: Scientific Agency, Evidence, and Continual Learning*, and provides a living reading map that can grow alongside the field. The aim is to help readers connect systems to their scientific claims, understand what evaluations measure, and identify the experiments needed to establish progress.

> 🇨🇳 **为什么建立这个文献库？** 科研智能体与自主实验室正在连接问题提出、假设生成、实验执行与结果分析。我们希望沿着“谁决定科研行动、证据支持什么结论、系统如何获得能力改进”三条主线，把相关论文整理成便于阅读和持续补充的研究地图。

<p align="center">
  <img src="assets/core_framework.png" alt="Figure 1: action planning, observation acquisition, claim assessment, and experience reuse connected by evidence-linked experimental traces" width="100%">
</p>

*Figure 1. Scientific functions and the basis of discovery. Workflow completion, supported claims and learning benefits require distinct assessments. Actions shape available observations, evidence assessments connect results to claims, and retained experience informs later research. E²T is proposed to preserve the relationships needed for inspection and revision.*

**How the framework fits together.** Research operations produce questions, protocols, measurements, and conclusions. Agency locates decision authority and verification responsibility; evidence analysis traces each claim to the observations that support it; learning analysis identifies what changed and tests whether the change improved later performance. Knowledge revision can guide the next experiment, while a claim of transferable agent improvement needs a separate controlled comparison. Benchmark scores must be interpreted against the task and unit actually evaluated.

| 🤖 Agency | 🔍 Verification | 🌱 Learning |
| --- | --- | --- |
| Who proposes, selects, authorizes, and accepts scientific decisions? | What observation supports the claim, and how is it checked? | What changes, over what time scale, and does it improve later scientific tasks? |

### Functional contribution legend

| Emoji | Function | Scope |
| --- | --- | --- |
'''
    for name, _, icon, description in FUNCTIONS:
        md += f'| {icon} | **{name}** | {description} |\n'
    md += f'''

**Collection snapshot: {snapshot['date']}** · **{len(records)} unique records** · {counts.get('PUBLISHED_VERIFIED', 0)} marked as verified publications in the source catalog · {len(records) - counts.get('PUBLISHED_VERIFIED', 0)} preprints or records awaiting publication verification.

<a id="contents"></a>
## 📌 Table of Contents

- [🧭 Suggested Reading Route](#reading-route)
- [📚 Surveys and Perspectives](#surveys-and-perspectives)
- [🤖 Scientific Agents and Systems](#scientific-agents-and-systems)
  - [🧭 Action Planning](#action-planning)
  - [🔬 Observation Acquisition](#observation-acquisition)
  - [🔍 Claim Assessment](#claim-assessment)
  - [♻️ Experience Reuse](#experience-reuse)
- [📊 Evaluation and Research Infrastructure](#evaluation-and-research-infrastructure)
- [🗂️ About the Collection](#about)
- [🤝 Contribute](#contribute)
- [💬 Citation and Credits](#citation)

**Within each category, records are grouped by year, newest first.** 📝 marks preprints; ⏳ marks unresolved publication status; 🛠️ marks a correction linked to its original article.

<a id="reading-route"></a>
## 🧭 Suggested Reading Route

'''
    route = [
        ('📚 Establish the landscape', ['M0001', 'M0002', 'M0023'],
         'Compare existing coverage and definitions before evaluating a new framework.'),
        ('🤖 Read scientific systems', ['M0015', 'M0011', 'M0016', 'M0021'],
         'Compare tasks, execution environments, researcher control, and the supported scientific endpoints.'),
        ('🧪 Follow an experiment to its evidence', ['M0026', 'M0027', 'M0053'],
         'Read A-Lab with its correction; distinguish synthesis, identification, novelty, and within-study optimization.'),
    ]
    for name, keys, guidance in route:
        md += f'**{name}.** {guidance}\n\n' + '\n'.join(
            '- ' + link(records_by_id[key]) for key in keys) + '\n\n'
    md += '''Then explore [♻️ experience reuse](#experience-reuse) and [📊 evaluation and research infrastructure](#evaluation-and-research-infrastructure). For learning, look for a frozen-versus-updated comparison, matched budgets, and tests on later tasks. For a benchmark, identify its task unit, tools, intervention rules, and scoring construct.

---

'''

    surveys = [record for record in records
               if record['main_section'] == 'Surveys and Perspectives'
               and record['type'].casefold() != 'correction']
    md += '''<a id="surveys-and-perspectives"></a>
## 📚 Surveys and Perspectives

Field-level syntheses, perspectives, roadmaps, and historical accounts. These records frame the field rather than representing one functional stage of a scientific system.

'''
    md += year_groups(surveys, corrections_by_parent, 3)
    md += '[↑ Back to contents](#contents)\n\n---\n\n'

    md += '''<a id="scientific-agents-and-systems"></a>
## 🤖 Scientific Agents and Systems

Integrated scientific agents and systems appear once under their **primary contribution**. Emojis after an entry show additional functional contributions.

'''
    for function, slug, icon, description in FUNCTIONS:
        selected = [record for record in records
                    if record['main_section'] == 'Scientific Agents and Systems'
                    and record['primary_function'] == function
                    and record['type'].casefold() != 'correction']
        md += f'<a id="{slug}"></a>\n### {icon} {function}\n\n{description}\n\n'
        if function == 'Experience Reuse':
            md += '''<details>
<summary>🖼️ Review figure: testing whether experience improves the next study</summary>

<img src="assets/fig05-learning-validation.png" alt="Learning validation: compare frozen and updated capabilities on independent later tasks under matched conditions" width="100%">

*Figure 5 from the working review. Distinguish data/memory, scientific beliefs, predictive models, decision policies and reusable capabilities. Test a versioned update on later independent tasks against a frozen baseline with matched model, data access, task selection and budgets; assess performance, cost, calibration and retention. This is a proposed evaluation design, not a measured learning effect.*

</details>

'''
        md += year_groups(selected, corrections_by_parent, 4)
    md += '[↑ Back to contents](#contents)\n\n---\n\n'

    evaluation = [record for record in records
                  if record['main_section'] == 'Evaluation and Research Infrastructure'
                  and record['type'].casefold() != 'correction']
    md += '''<a id="evaluation-and-research-infrastructure"></a>
## 📊 Evaluation and Research Infrastructure

Benchmarks, datasets, environments, evaluation frameworks, and infrastructure for measuring or supporting scientific-agent capabilities. Functional emojis indicate the stages covered by an evaluation rather than a primary system classification.

'''
    md += benchmark_resource_map(records_by_id)
    md += '### 📚 Papers by Year\n\n'
    md += year_groups(evaluation, corrections_by_parent, 4)
    if unattached_corrections:
        md += '### 🛠️ Unattached corrections\n\n'
        md += '\n'.join(paper_entry(record, corrections_by_parent)
                        for record in unattached_corrections) + '\n\n'
    unavailable = [record for record in records if not record['source_fulltext_available']]
    md += f'''[↑ Back to contents](#contents)

---

<a id="about"></a>
## 🗂️ About the Collection

This is a targeted, curated working collection exported from our review library. It is open to expansion and does not claim exhaustive field coverage. Publication status and version metadata preserve the source-catalog assessment; inclusion does not establish a scientific claim or independent reproduction. Continual-learning entries include methodological background, and benchmark entries span distinct evaluation tasks.

The source snapshot contains {snapshot['records']} unique records; its working main text cited {len(snapshot['manuscript_cited_ids'])} of them. The remaining {snapshot['retained_repository_records']} records were retained from the earlier repository so the collection can continue growing beyond the manuscript bibliography. Journal reference requirements continue to apply to the manuscript.

Papers are accessed through their original publication or preprint pages. Related versions of a work should be connected; genuine follow-up studies and corrections remain distinct. Read the A-Lab article alongside its author correction rather than carrying forward an earlier result without its update.

<details>
<summary>📂 Source-library access and metadata</summary>

The source snapshot had full text for {snapshot['records_with_source_fulltext']} unique records and lacked full text for {snapshot['records'] - snapshot['records_with_source_fulltext']}. These are source-library access counts. Full-text availability does not establish complete evidence coding or independent validation.

The dataset preserves publication evidence, metadata sources, section membership, primary functional assignment, additional functional contributions, and the PDF version held by the source library. The previous `wp_membership` values remain as `legacy_wp_membership` for migration traceability. Bibliographic record keys remain in the downloadable datasets for maintenance and BibTeX matching.

**Full text unavailable in the current source-library export:**

'''
    md += '\n'.join(f"- [{escape(record['title'])}]({public_url(record)})" for record in unavailable)
    md += f'''

</details>

<a id="contribute"></a>
## 🤝 Contribute

Missing a relevant paper, a correction, or a newer publication version? [Suggest a paper]({base}/issues/new?template=paper.yml) or open a pull request. Include the primary source, scientific relevance, main section, primary function where applicable, and version information. See [CONTRIBUTING.md](CONTRIBUTING.md) for the data format and maintenance steps.

We welcome broader disciplinary coverage, verified code and dataset links, and evidence notes grounded in specific source locations. Keep scientific claims tied to observations and interpretation limits.

<details>
<summary>🛠️ Regenerate the catalog</summary>

Update `data/papers.json` and `references.bib`, then run:

```bash
python scripts/build_catalog.py
python scripts/validate.py
```

These commands regenerate this single-page README and CSV export. The maintainer can refresh from a review-aligned private working library with `python scripts/build_catalog.py --import-from /path/to/2026-agent-review`; reconcile community additions before importing.

</details>

<a id="citation"></a>
## 💬 Citation and Credits

Cite the original paper for a research claim. To cite the collection itself, use [CITATION.cff](CITATION.cff).

The reading-list presentation draws inspiration from [Awesome-Agent-Papers](https://github.com/luo-junyu/Awesome-Agent-Papers), [Awesome-LLM-Scientific-Discovery](https://github.com/HKUST-KnowComp/Awesome-LLM-Scientific-Discovery), and [awesome-llm-agents](https://github.com/kaushikb11/awesome-llm-agents). The introduction, organization around our review questions, and logo were created for this collection.

Original repository content and curation: [CC BY 4.0](LICENSE-CONTENT.md). Maintenance scripts: [MIT](LICENSE). Linked papers retain their original licenses. The logo and earlier repository overview drafts were generated with OpenAI's built-in image generation tool; the [prompts](assets/prompts.json) preserve their design history.

Figures 1, 5 and 7 are reproduced from the working review's existing figure collection. Their [source manifest](assets/review-figures.json) preserves the source-paper anchors, original filenames, and qualitative interpretation. They illustrate scientific workflows, evaluation designs and resource constructs rather than report new experimental results.

[↑ Back to contents](#contents)
'''
    write('README.md', md)


if __name__ == '__main__':
    build()
