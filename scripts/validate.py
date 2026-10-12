"""Check record/BibTeX consistency and local Markdown links without network requests."""
import csv
import json
import re
from collections import Counter
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
records = json.loads((ROOT / 'data/papers.json').read_text(encoding='utf-8'))
ids = [r['id'] for r in records]
assert len(ids) == len(set(ids)), 'Duplicate IDs'
assert all(re.fullmatch(r'M\d{4}', key) for key in ids), 'Invalid ID'
required = {'id', 'title', 'authors', 'year', 'venue', 'type', 'domain', 'doi', 'publication_doi',
            'landing_url', 'arxiv_id', 'publication_status', 'publication_evidence', 'wp_membership',
            'pdf_version', 'metadata_source', 'source_fulltext_available'}
statuses = {'PUBLISHED_VERIFIED', 'ACCEPTED_VERIFIED', 'PREPRINT_CONTEMPORANEOUS', 'PUBLICATION_PENDING_VERIFICATION'}
doi_seen = set()
for r in records:
    assert set(r) == required, f"Schema mismatch: {r['id']}"
    assert all(r[k] for k in ['title', 'authors', 'year', 'venue', 'landing_url', 'metadata_source'])
    assert r['publication_status'] in statuses
    assert isinstance(r['source_fulltext_available'], bool)
    assert r['year'].isdigit()
    assert set(r['wp_membership'].split(';')) <= {'ROR', 'WP1', 'WP2', 'WP3', 'WP4', 'WP5', 'WP6'}
    assert r['wp_membership']
    if r['publication_status'] in {'PUBLISHED_VERIFIED', 'ACCEPTED_VERIFIED'}:
        assert r['publication_evidence'], f"Missing official evidence: {r['id']}"
    for field in ['landing_url', 'publication_evidence']:
        if r[field]:
            parts = urlsplit(r[field])
            assert parts.scheme in {'http', 'https'} and parts.netloc
    doi = (r['publication_doi'] or r['doi']).casefold()
    if doi:
        assert doi not in doi_seen, f'Duplicate DOI: {doi}'
        doi_seen.add(doi)
bib = (ROOT / 'references.bib').read_text(encoding='utf-8')
bib_ids = re.findall(r'@\w+\s*\{\s*(M\d{4})\s*,', bib)
assert Counter(bib_ids) == Counter(ids), 'BibTeX ID mismatch'
assert not re.search(r'^\s*file\s*=', bib, re.M), 'Private file path in bibliography'
exported = list(csv.DictReader((ROOT / 'data/papers.csv').open(encoding='utf-8', newline='')))
assert len(exported) == len(records)
for actual, expected in zip(exported, records):
    assert actual == {key: str(value) for key, value in expected.items()}, 'CSV differs from JSON'
for path in ROOT.rglob('*.md'):
    if '.git' in path.parts:
        continue
    content = path.read_text(encoding='utf-8')
    assert not re.search(r'\b[A-Z]:[\\/]', content), f'Local absolute path in {path.name}'
    for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)', content):
        if target.startswith(('http://', 'https://', '#', 'mailto:')):
            continue
        local = unquote(target.split('#')[0].strip('<>'))
        assert (path.parent / local).exists(), f'Broken local link: {path.name}: {target}'
assert not list(ROOT.rglob('*.pdf')), 'Unexpected paper binary in repository'
print(f'OK: {len(records)} unique records; matching BibTeX and CSV; local Markdown links valid.')
