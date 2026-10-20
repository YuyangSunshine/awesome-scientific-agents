"""Check taxonomy, record/BibTeX consistency, and local links without network requests."""
import csv
import json
import re
import struct
from collections import Counter
from pathlib import Path
from urllib.parse import unquote, urlsplit

from render_readme import FUNCTIONS, MAIN_SECTIONS, correction_relations

ROOT = Path(__file__).resolve().parents[1]
records = json.loads((ROOT / 'data/papers.json').read_text(encoding='utf-8'))
snapshot = json.loads((ROOT / 'data/snapshot.json').read_text(encoding='utf-8'))

ids = [record['id'] for record in records]
assert len(ids) == len(set(ids)), 'Duplicate IDs'
assert all(re.fullmatch(r'M\d{4}', key) for key in ids), 'Invalid ID'
assert ids == [f'M{number:04d}' for number in range(1, len(records) + 1)], \
    'Records must be sorted and IDs contiguous'

required = {
    'id', 'title', 'authors', 'year', 'venue', 'type', 'domain', 'doi',
    'publication_doi', 'landing_url', 'arxiv_id', 'publication_status',
    'publication_evidence', 'main_section', 'primary_function',
    'function_contributions', 'legacy_wp_membership', 'pdf_version',
    'metadata_source', 'source_fulltext_available',
}
statuses = {
    'PUBLISHED_VERIFIED', 'ACCEPTED_VERIFIED', 'PREPRINT_CONTEMPORANEOUS',
    'PUBLICATION_PENDING_VERIFICATION',
}
main_sections = {item[0] for item in MAIN_SECTIONS}
functions = {item[0] for item in FUNCTIONS}
legacy_topics = {'ROR', 'WP1', 'WP2', 'WP3', 'WP4', 'WP5', 'WP6'}
doi_seen = set()

for record in records:
    assert set(record) == required, f"Schema mismatch: {record['id']}"
    assert all(record[key] for key in [
        'title', 'authors', 'year', 'venue', 'landing_url', 'metadata_source',
        'main_section', 'legacy_wp_membership']), f"Missing required value: {record['id']}"
    assert record['publication_status'] in statuses
    assert isinstance(record['source_fulltext_available'], bool)
    assert record['year'].isdigit()
    assert record['main_section'] in main_sections
    assert isinstance(record['function_contributions'], list)
    assert len(record['function_contributions']) == len(set(record['function_contributions']))
    assert set(record['function_contributions']) <= functions
    assert set(record['legacy_wp_membership'].split(';')) <= legacy_topics

    if record['main_section'] == 'Scientific Agents and Systems':
        assert record['primary_function'] in functions, \
            f"Missing primary function: {record['id']}"
        assert record['primary_function'] in record['function_contributions'], \
            f"Primary function absent from contribution list: {record['id']}"
    else:
        assert record['primary_function'] == '', \
            f"Primary function outside systems section: {record['id']}"

    if record['publication_status'] in {'PUBLISHED_VERIFIED', 'ACCEPTED_VERIFIED'}:
        assert record['publication_evidence'], f"Missing official evidence: {record['id']}"
    for field in ['landing_url', 'publication_evidence']:
        if record[field]:
            parts = urlsplit(record[field])
            assert parts.scheme in {'http', 'https'} and parts.netloc

    doi = (record['publication_doi'] or record['doi']).casefold()
    if doi:
        assert doi not in doi_seen, f'Duplicate DOI: {doi}'
        doi_seen.add(doi)

corrections_by_parent, unattached_corrections = correction_relations(records)
assert not unattached_corrections, 'Every correction must resolve to an original article title'
assert all(parent in ids for parent in corrections_by_parent)

bib = (ROOT / 'references.bib').read_text(encoding='utf-8')
bib_ids = re.findall(r'@\w+\s*\{\s*(M\d{4})\s*,', bib)
assert Counter(bib_ids) == Counter(ids), 'BibTeX ID mismatch'
assert not re.search(r'^\s*file\s*=', bib, re.M), 'Private file path in bibliography'

exported = list(csv.DictReader(
    (ROOT / 'data/papers.csv').open(encoding='utf-8', newline='')))
assert len(exported) == len(records)
for actual, record in zip(exported, records):
    expected = {key: str(value) for key, value in record.items()}
    expected['function_contributions'] = ';'.join(record['function_contributions'])
    assert actual == expected, f"CSV differs from JSON: {record['id']}"

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
for record in records:
    title = record['title'].replace('|', '\\|').replace('[', '\\[').replace(']', '\\]')
    assert f'**{title}**' in readme, f"Missing homepage entry: {record['id']}"
assert '\n- **Author Correction:' not in readme, 'Corrections must be nested beneath originals'

for _, slug, _, _ in MAIN_SECTIONS:
    assert f'<a id="{slug}"></a>' in readme, f'Missing main-section anchor: {slug}'
for _, slug, _, _ in FUNCTIONS:
    assert f'<a id="{slug}"></a>' in readme, f'Missing function anchor: {slug}'

assert snapshot['records'] == len(records)
assert snapshot['publication_status_counts'] == dict(Counter(
    record['publication_status'] for record in records))
assert snapshot['records_with_source_fulltext'] == sum(
    record['source_fulltext_available'] for record in records)
assert snapshot['main_section_counts'] == dict(Counter(
    record['main_section'] for record in records))
assert snapshot['primary_function_counts'] == dict(Counter(
    record['primary_function'] for record in records if record['primary_function']))
assert set(snapshot['manuscript_cited_ids']) <= set(ids)

resources = list(csv.DictReader(
    (ROOT / 'data/benchmark_resources.csv').open(encoding='utf-8-sig')))
datasets = list(csv.DictReader(
    (ROOT / 'data/dataset_roles.csv').open(encoding='utf-8-sig')))
scope = json.loads((ROOT / 'data/resource_review_scope.json').read_text(encoding='utf-8-sig'))
assert len(resources) == scope['resource_records']
assert len(datasets) == scope['dataset_families']
assert len({resource['resource'] for resource in resources}) == len(resources)
for resource in resources:
    assert resource['review_category'] in {category[0] for category in __import__(
        'render_readme').BENCHMARK_CATEGORIES}, 'Unclassified benchmark resource'
    assert resource['source_id'] in ids, 'Resource points to missing paper'
    assert urlsplit(resource['official_resource_url']).scheme == 'https'
    assert resource['official_resource_url'] in readme, 'Missing official resource link'
for dataset in datasets:
    assert set(dataset['source_ids'].split(';')) <= set(ids)

manifest = json.loads((ROOT / 'assets/review-figures.json').read_text(encoding='utf-8'))
for figure in manifest:
    assert set(figure['sources']) <= set(ids)
    assert (ROOT / 'assets' / figure['filename']).exists()
for name in ['logo.png', 'core_framework.png',
             'fig05-learning-validation.png', 'fig07-benchmarks-datasets.png']:
    asset = (ROOT / 'assets' / name).read_bytes()
    assert asset[:8] == b'\x89PNG\r\n\x1a\n', f'Invalid PNG: {name}'
    assert min(struct.unpack('>II', asset[16:24])) >= 256

print(f'OK: {len(records)} records; taxonomy, homepage, CSV, BibTeX, links, and assets valid.')
