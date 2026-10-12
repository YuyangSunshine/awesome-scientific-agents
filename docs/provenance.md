# Snapshot and provenance

[← Home](../README.md)

The initial public snapshot was exported on 2026-10-12 from the local `2026-agent-review` library, using the deduplicated master catalog and its BibTeX bibliography. It contains 90 stable records. Category membership comes from the original six work packages plus the survey collection.

The source collection had full text for 79 unique records and lacked full text for 11. This is a source-library access measure, not the number of PDFs hosted here. Publication and PDF-version labels are inherited metadata, not a new audit performed for this repository. Source downloads, raw internal notes, manuscript drafts, and local filesystem paths are not part of the public export.

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

- **M0005** · 2026 · NatRevChem · [The past, present and future of self-driving laboratories](https://doi.org/10.1038/s41570-026-00847-2) · `Published`
- **M0007** · 2026 · NatBiotechnol · [Agentic AI and the rise of in silico team science in biomedical research](https://doi.org/10.1038/s41587-026-03035-1) · `Published`
- **M0089** · 2026 · TPAMI · [The Hitchhiker’s Guide to Autonomous Research: A Survey of Scientific Agents](https://doi.org/10.1109/tpami.2026.3721500) · `Published`
- **M0022** · 2023 · NatSynth · [The rise of self-driving labs in chemical and materials sciences](https://doi.org/10.1038/s44160-022-00231-0) · `Published`
- **M0024** · 2025 · NatRevChem · [Steering towards safe self-driving laboratories](https://doi.org/10.1038/s41570-025-00747-x) · `Published`
- **M0033** · 2023 · DigitDiscov · [What is missing in autonomous discovery: open challenges for the community](https://doi.org/10.1039/d3dd00143a) · `Published`
- **M0035** · 2024 · DigitDiscov · [Review of low-cost self-driving laboratories in chemistry and materials science: the “frugal twin” concept](https://doi.org/10.1039/d3dd00223c) · `Published`
- **M0036** · 2025 · RSOS · [Autonomous ‘self-driving’ laboratories: a review of technology and policy implications](https://doi.org/10.1098/rsos.250646) · `Published`
- **M0043** · 2024 · NatMethods · [Guiding questions to avoid data leakage in biological machine learning applications](https://doi.org/10.1038/s41592-024-02362-y) · `Published`
- **M0065** · 2025 · bioRxiv · [OriGene: A Self-Evolving Virtual Disease Biologist Automating Therapeutic Target Discovery](https://doi.org/10.1101/2025.06.03.657658) · `Preprint / pending verification`
- **M0070** · 2023 · ReactChemEng · [Equipping data-driven experiment planning for Self-driving Laboratories with semantic memory: case studies of transfer learning in chemical reaction optimization](https://doi.org/10.1039/d3re00008g) · `Published`

## Updating from the private source library

The maintainer can refresh the public export with `python scripts/build_catalog.py --import-from /path/to/2026-agent-review`. This replaces the public metadata snapshot; reconcile community additions before importing. Edit the snapshot date when taking a later snapshot. Public regeneration without `--import-from` requires only the files in this repository.
