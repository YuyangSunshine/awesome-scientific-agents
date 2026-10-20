"""Check record/BibTeX consistency and local Markdown links without network requests."""
import csv
import json
import re
import struct
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
    anchors = set(re.findall(r'<a id="([^"]+)"', content))
    targets = re.findall(r'\[[^\]]*\]\(([^)]+)\)', content)
    targets += re.findall(r'(?:src|href)="([^"]+)"', content)
    for target in targets:
        if target.startswith('#'):
            assert target[1:] in anchors, f'Broken section anchor: {path.name}: {target}'
            continue
        if target.startswith(('http://', 'https://', 'mailto:')):
            continue
        local = unquote(target.split('#')[0].strip('<>'))
        assert (path.parent / local).exists(), f'Broken local link: {path.name}: {target}'
assert not list(ROOT.rglob('*.pdf')), 'Unexpected paper binary in repository'
readme = (ROOT / 'README.md').read_text(encoding='utf-8')
assert not re.search(r'\bM\d{4}\b', readme), 'Internal paper IDs displayed in README'
assert not list((ROOT / 'papers').glob('*.md')), 'Paper lists must live in the homepage'
for r in records:
    title = r['title'].replace('|', '\\|').replace('[', '\\[').replace(']', '\\]')
    assert f'**{title}**' in readme, f"Missing homepage entry: {r['id']}"
from render_readme import BENCHMARK_CATEGORIES, TOPICS
for _, slug, _, _, _ in TOPICS:
    section = readme.split(f'<a id="{slug}"></a>', 1)[1].split('\n---\n', 1)[0]
    years = [int(y) for y in re.findall(r'^### (\d{4})$', section, re.M)]
    assert years == sorted(set(years), reverse=True), f'Incorrect year grouping: {slug}'
resources = list(csv.DictReader((ROOT / 'data/benchmark_resources.csv').open(encoding='utf-8-sig')))
datasets = list(csv.DictReader((ROOT / 'data/dataset_roles.csv').open(encoding='utf-8-sig')))
scope = json.loads((ROOT / 'data/resource_review_scope.json').read_text(encoding='utf-8-sig'))
assert len(resources) == scope['resource_records']
assert len(datasets) == scope['dataset_families']
assert len({r['resource'] for r in resources}) == len(resources)
for resource in resources:
    assert resource['review_category'] in {c[0] for c in BENCHMARK_CATEGORIES}, 'Unclassified benchmark resource'
    assert resource['source_id'] in ids, 'Resource points to missing paper'
    assert urlsplit(resource['official_resource_url']).scheme == 'https'
    assert resource['official_resource_url'] in readme, 'Missing official resource link'
for dataset in datasets:
    assert set(dataset['source_ids'].split(';')) <= set(ids)
manifest = json.loads((ROOT / 'assets/review-figures.json').read_text(encoding='utf-8'))
for figure in manifest:
    assert set(figure['sources']) <= set(ids)
    assert (ROOT / 'assets' / figure['filename']).exists()
for name in ['logo.png', 'core_framework.png', 'fig05-learning-validation.png', 'fig07-benchmarks-datasets.png']:
    asset = (ROOT / 'assets' / name).read_bytes()
    assert asset[:8] == b'\x89PNG\r\n\x1a\n', f'Invalid PNG: {name}'
    assert min(struct.unpack('>II', asset[16:24])) >= 256
print(f'OK: {len(records)} unique records; all papers on the homepage; years, anchors, assets, CSV and BibTeX valid.')
