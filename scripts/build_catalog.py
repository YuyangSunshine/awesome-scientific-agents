"""Build the public reading lists; Python 3.9+, standard library only."""
import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

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
    # OpenReview IDs and other functional parameters identify the source.
    query = [(key, value) for key, value in parse_qsl(parts.query, keep_blank_values=True)
             if not key.startswith('utm_') and key not in {'error', 'cookies_not_supported'}
             and not (parts.netloc.endswith('nature.com') and key == 'code')]
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))

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


def build():
    from render_readme import build as render
    render()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--import-from', type=Path, help='Optional private source-library directory')
    args = parser.parse_args()
    if args.import_from:
        import_library(args.import_from)
    build()
