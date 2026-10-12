"""Build the public reading lists; Python 3.9+, standard library only."""
import argparse
import csv
import io
import json
import re
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[1]
CATEGORIES = {
    'ROR': ('surveys', 'Surveys and perspectives', '综述与观点'),
    'WP1': ('scientific-agents', 'AI scientists and scientific agents', 'AI Scientist 与科研智能体'),
    'WP2': ('autonomous-labs', 'Self-driving laboratories and embodied science', '自主实验室与具身科研'),
    'WP3': ('scientific-evidence', 'Scientific reasoning, evidence and verification', '科学推理、证据与验证'),
    'WP4': ('experiment-design', 'Active learning and experimental design', '主动学习与实验决策'),
    'WP5': ('continual-learning', 'Continual learning and agent improvement', '持续学习与智能体能力改进'),
    'WP6': ('benchmarks', 'Benchmarks and scientific evaluation', 'Benchmark 与科学评价'),
}
FIELDS = ['id', 'title', 'authors', 'year', 'venue', 'type', 'domain', 'doi',
          'publication_doi', 'landing_url', 'arxiv_id', 'publication_status',
          'publication_evidence', 'wp_membership', 'pdf_version', 'metadata_source']

def write(name, content):
    path = ROOT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8', newline='\n') as stream:
        stream.write(content.rstrip() + '\n')

def clean_url(url):
    if not url:
        return ''
    parts = urlsplit(url)
    if parts.scheme not in ('https', 'http') or not parts.netloc:
        raise ValueError(f'Invalid public URL: {url}')
    return urlunsplit((parts.scheme, parts.netloc, parts.path, '', ''))

def import_library(source):
    raw = list(csv.DictReader((source / 'master_catalog.csv').open(encoding='utf-8-sig')))
    records = []
    for row in raw:
        rec = {field: ' '.join(row.get(field, '').split()) for field in FIELDS}
        rec['title'] = re.sub(r'^G\s+ryffin\s*:', 'Gryffin:', rec['title'])
        if not rec['metadata_source']:
            rec['metadata_source'] = 'Source working catalog; metadata provider unspecified'
        for field in ('landing_url', 'publication_evidence'):
            rec[field] = clean_url(rec[field])
        # Access information describes the source-library snapshot, not a public mirror.
        rec['source_fulltext_available'] = bool(row.get('local_file'))
        records.append(rec)
    write('data/papers.json', json.dumps(records, ensure_ascii=False, indent=2))
    bib = (source / 'references.bib').read_text(encoding='utf-8-sig')
    bib = re.sub(r'^\s*file\s*=.*\n', '', bib, flags=re.M)
    bib = re.sub(r'title = \{G\s+ryffin\s*:', 'title = {Gryffin:', bib)
    write('references.bib', bib)
    main = (source / 'latex_review/main.tex').read_text(encoding='utf-8')
    main = re.sub(r'(?<!\\)%[^\n]*', '', main)
    cited = sorted({key.strip() for group in re.findall(r'\\cite\w*\*?(?:\[[^\]]*\])*\{([^}]+)\}', main)
                    for key in group.split(',') if re.fullmatch(r'M\d{4}', key.strip())})
    snapshot = {
        'date': json.loads((source / '00_Project/library_summary.json').read_text(encoding='utf-8-sig'))['date'],
        'source': 'Curated 2026-agent-review working library; proposal v0.3',
        'records': len(records),
        'publication_status_counts': dict(Counter(r['publication_status'] for r in records)),
        'records_with_source_fulltext': sum(r['source_fulltext_available'] for r in records),
        'category_counts': {k: sum(k in r['wp_membership'].split(';') for r in records) for k in CATEGORIES},
        'manuscript_cited_ids': cited,
        'scope': 'Targeted working collection; not an exhaustive systematic review or an independent evidence audit.',
    }
    write('data/snapshot.json', json.dumps(snapshot, ensure_ascii=False, indent=2))

def esc(value):
    return str(value).replace('|', '\\|').replace('[', '\\[').replace(']', '\\]').replace('\n', ' ')

def paper_line(r):
    link = (r['publication_evidence'] if r['publication_status'] in ('PUBLISHED_VERIFIED', 'ACCEPTED_VERIFIED') else '') or r['landing_url'] or ('https://doi.org/' + (r['publication_doi'] or r['doi']))
    status = 'Published' if r['publication_status'] == 'PUBLISHED_VERIFIED' else ('Accepted' if r['publication_status'] == 'ACCEPTED_VERIFIED' else 'Preprint / pending verification')
    extra = ' · **Correction**' if r['type'].lower() == 'correction' else ''
    return f"- **{r['id']}** · {r['year']} · {esc(r['venue'])} · [{esc(r['title'])}]({link}) · `{status}`{extra}"

def build():
    records = json.loads((ROOT / 'data/papers.json').read_text(encoding='utf-8'))
    snapshot = json.loads((ROOT / 'data/snapshot.json').read_text(encoding='utf-8'))
    fields = FIELDS + ['source_fulltext_available']
    buf = io.StringIO(newline='')
    writer = csv.DictWriter(buf, fieldnames=fields, lineterminator='\n')
    writer.writeheader()
    writer.writerows(records)
    write('data/papers.csv', buf.getvalue())
    counts = Counter(r['publication_status'] for r in records)
    date = snapshot['date']
    intro = f'''# Awesome Scientific Agents

A curated reading list on **AI scientists, autonomous laboratories, verifiable scientific discovery, and continual learning**.

[中文说明](README.zh-CN.md) · [Reading guide](docs/reading-guide.md) · [Taxonomy](docs/taxonomy.md) · [Contributing](CONTRIBUTING.md) · [BibTeX](references.bib) · [CSV](data/papers.csv) · [JSON](data/papers.json)

This living bibliography accompanies a working review, *From Research Automation to Verifiable Scientific Discovery: Scientific Agency, Evidence, and Continual Learning*. It connects research automation to three questions: **who controls scientific decisions, what evidence supports a claim, and what a system actually learns**.

**Library snapshot: {date}** — {len(records)} unique records; {counts['PUBLISHED_VERIFIED']} marked as verified publications in the source catalog; {len(records)-counts['PUBLISHED_VERIFIED']} preprints or records pending publication verification. These labels preserve the source-library assessment at the snapshot date. Classification is curated; inclusion is not endorsement or evidence of independent reproduction.

## Start here

- [Recommended reading route](docs/reading-guide.md): surveys → scientific systems → claim verification → learning → evaluation.
- [Complete paper lists](#contents): papers may appear in more than one topic; stable `Mxxxx` IDs identify unique records.
- [Review and library relationship](docs/review-companion.md): the manuscript selects references for its argument; this repository can expand continuously.
- [Snapshot and provenance](docs/provenance.md): targeted coverage, version distinctions, and unresolved full-text access.

## Contents

| Topic | Records | Reading list |
| --- | ---: | --- |'''
    for key, (slug, title, _) in CATEGORIES.items():
        selected = [r for r in records if key in r['wp_membership'].split(';')]
        intro += f'\n| {title} | {len(selected)} | [Browse](papers/{slug}.md) |'
        lines = [f'# {title}', '', '[← All topics](../README.md) · [Reading guide](../docs/reading-guide.md)', '',
                 f'Snapshot: {date}. {len(selected)} records; cross-topic memberships are retained.', '', '## Published / verified accepted']
        published = [r for r in selected if r['publication_status'] in ('PUBLISHED_VERIFIED', 'ACCEPTED_VERIFIED')]
        preprints = [r for r in selected if r not in published]
        for label, items in [('Published', published), ('Preprints / publication pending verification', preprints)]:
            if label != 'Published':
                lines += ['', '## ' + label]
            lines += ['', *[paper_line(r) for r in sorted(items, key=lambda x: (-int(x['year']), x['title'].casefold()))]]
        write(f'papers/{slug}.md', '\n'.join(lines))
    intro += '''

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
'''
    write('README.md', intro)
    by_id = {r['id']: r for r in records}
    access = [r for r in records if not r['source_fulltext_available']]
    provenance = f'''# Snapshot and provenance

[← Home](../README.md)

The initial public snapshot was exported on {date} from the local `2026-agent-review` library, using the deduplicated master catalog and its BibTeX bibliography. It contains {len(records)} stable records. Category membership comes from the original six work packages plus the survey collection.

The source collection had full text for {sum(r['source_fulltext_available'] for r in records)} unique records and lacked full text for {len(access)}. This is a source-library access measure, not the number of PDFs hosted here. Publication and PDF-version labels are inherited metadata, not a new audit performed for this repository. Source downloads, raw internal notes, manuscript drafts, and local filesystem paths are not part of the public export.

This is a targeted working collection, not an exhaustive search, a completed systematic review, or an independent reproduction study. Counts are descriptive inventory counts. The snapshot date is not a guarantee that every entry was newly verified on that day.

## Publication and version fields

- `PUBLISHED_VERIFIED`: publication marked verified by the source catalog; consult `publication_evidence` and `metadata_source`.
- `ACCEPTED_VERIFIED`: reserved for acceptance supported by an official record.
- `PREPRINT_CONTEMPORANEOUS`: contemporaneous preprint, kept separately from published work.
- `PUBLICATION_PENDING_VERIFICATION`: publication status remains unresolved.
- `pdf_version`: version held by the source library, including published article, author manuscript, preprint, or unavailable.
- `source_fulltext_available`: whether the source snapshot had a local full-text file; it does not establish full evidence coding or independent validation.
- `wp_membership`: semicolon-separated topic IDs; multi-topic assignment does not create extra unique papers.

Related versions should share a record where they represent the same work. Follow-up studies and corrections remain distinct. Keep the stable IDs when updating metadata; allocate a new unused ID for a new work.

## Full text unavailable in the initial source snapshot

'''
    provenance += '\n'.join(paper_line(r) for r in access)
    provenance += '\n\n## Updating from the private source library\n\nThe maintainer can refresh the public export with `python scripts/build_catalog.py --import-from /path/to/2026-agent-review`. This replaces the public metadata snapshot; reconcile community additions before importing. Edit the snapshot date when taking a later snapshot. Public regeneration without `--import-from` requires only the files in this repository.\n'
    write('docs/provenance.md', provenance)
    cited = snapshot['manuscript_cited_ids']
    write('docs/review-companion.md', f'''# Review companion

[← Home](../README.md)

The working review is titled *From Research Automation to Verifiable Scientific Discovery: Scientific Agency, Evidence, and Continual Learning*. Its current scope connects scientific agents and autonomous laboratories across life sciences, chemistry, materials, and computational science.

The seven-part narrative covers introduction, scientific systems, decision control, claims and evidence, demonstrated learning, benchmark constructs, and future research. Its three analytical threads are claim–evidence alignment, scientific decision authority and verification responsibility, and demonstrated learning with appropriate controls.

The collection is a living bibliography; manuscript references are selected to support the argument. A repository entry is not a substitute for citing a source that supports a claim in a paper. Any journal reference limit applies to the manuscript under its current author guidelines; repository inclusion does not change that requirement.

At the {date} snapshot the source bibliography contained {len(records)} records and the working main text cited {len(cited)} unique IDs. The list below records that working selection, not a final accepted manuscript or a ranking of the field. The repository has room for papers beyond that selection and beyond future manuscript reference budgets.

## Working main-text selection

''' + '\n'.join(paper_line(by_id[key]) for key in cited))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--import-from', type=Path, help='Optional private source-library directory')
    args = parser.parse_args()
    if args.import_from:
        import_library(args.import_from)
    build()
