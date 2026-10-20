"""Build the public reading lists; Python 3.9+, standard library only."""
import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[1]
MAIN_SECTIONS = (
    'Surveys and Perspectives',
    'Scientific Agents and Systems',
    'Evaluation and Research Infrastructure',
)
FUNCTIONS = (
    'Action Planning',
    'Observation Acquisition',
    'Claim Assessment',
    'Experience Reuse',
)
FIELDS = [
    'id', 'title', 'authors', 'year', 'venue', 'type', 'domain', 'doi',
    'publication_doi', 'landing_url', 'arxiv_id', 'publication_status',
    'publication_evidence', 'main_section', 'primary_function',
    'function_contributions', 'legacy_wp_membership', 'pdf_version',
    'metadata_source', 'source_fulltext_available',
]


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
    query = [(key, value) for key, value in parse_qsl(parts.query, keep_blank_values=True)
             if not key.startswith('utm_') and key not in {'error', 'cookies_not_supported'}
             and not (parts.netloc.endswith('nature.com') and key == 'code')]
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))


def import_library(source):
    """Import a source catalog that already follows the review-aligned schema."""
    raw = list(csv.DictReader((source / 'master_catalog.csv').open(encoding='utf-8-sig')))
    records = []
    for row in raw:
        missing = [field for field in FIELDS if field not in row
                   and field != 'source_fulltext_available']
        if missing:
            raise ValueError('Source catalog uses the legacy schema; migrate it before import: '
                             + ', '.join(missing))
        rec = {field: ' '.join(row.get(field, '').split()) for field in FIELDS
               if field != 'source_fulltext_available'}
        rec['function_contributions'] = [item.strip() for item in
                                         rec['function_contributions'].split(';') if item.strip()]
        for field in ('landing_url', 'publication_evidence'):
            rec[field] = clean_url(rec[field])
        rec['source_fulltext_available'] = bool(row.get('local_file'))
        records.append(rec)
    write('data/papers.json', json.dumps(records, ensure_ascii=False, indent=2))

    bib = (source / 'references.bib').read_text(encoding='utf-8-sig')
    bib = re.sub(r'^\s*file\s*=.*\n', '', bib, flags=re.M)
    write('references.bib', bib)

    main = (source / 'latex_review/main.tex').read_text(encoding='utf-8')
    main = re.sub(r'(?<!\\)%[^\n]*', '', main)
    cited = sorted({key.strip() for group in re.findall(
        r'\\cite\w*\*?(?:\[[^\]]*\])*\{([^}]+)\}', main)
                    for key in group.split(',') if re.fullmatch(r'M\d{4}', key.strip())})
    snapshot = {
        'date': json.loads((source / '00_Project/library_summary.json').read_text(
            encoding='utf-8-sig'))['date'],
        'source': 'Review-aligned scientific-agent working library',
        'records': len(records),
        'publication_status_counts': dict(Counter(r['publication_status'] for r in records)),
        'records_with_source_fulltext': sum(r['source_fulltext_available'] for r in records),
        'main_section_counts': dict(Counter(r['main_section'] for r in records)),
        'primary_function_counts': dict(Counter(
            r['primary_function'] for r in records if r['primary_function'])),
        'manuscript_cited_ids': cited,
        'scope': ('Targeted working collection; not an exhaustive systematic review or an '
                  'independent evidence audit.'),
    }
    write('data/snapshot.json', json.dumps(snapshot, ensure_ascii=False, indent=2))


def build():
    from render_readme import build as render
    render()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--import-from', type=Path,
                        help='Optional review-aligned private source-library directory')
    args = parser.parse_args()
    if args.import_from:
        import_library(args.import_from)
    build()
