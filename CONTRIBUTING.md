# Contributing

Thank you for helping maintain the collection. Recommend papers through the paper suggestion issue form, or submit a pull request.

## Scope and sources

Include work that directly concerns scientific agents, autonomous experimentation, scientific reasoning and verification, experiment design, learning relevant to scientific workflows, or scientific evaluation. Explain the relevance of background methods. General office assistants and chat systems without a scientific task are outside the main scope.

Provide a primary source: publisher DOI, official conference proceedings, or a recognized preprint landing page. Add code and datasets only when verified as associated with the work; the current schema does not store unverified project URLs. Use a separate issue to propose such schema extensions.

## Add or update a record

1. Check for an existing title, DOI or arXiv ID in `data/papers.json`. Keep its stable ID for a version update. Allocate the next unused `Mxxxx` ID for a new work.
2. Fill the existing schema: title, authors, year, venue, type, domain, DOI and landing page, publication status and evidence, metadata source, topic membership, and source PDF version/access. Put multiple topic IDs in `wp_membership`, separated by `;`.
3. Verify published or accepted status against an official source. An unverified acceptance claim remains `PUBLICATION_PENDING_VERIFICATION`; an unaccepted preprint uses `PREPRINT_CONTEMPORANEOUS`. Publication status and claim validity are separate facts.
4. Link versions of the same work within a record; keep genuine follow-up studies and corrections separate. Mention related IDs in the PR. Read A-Lab `M0026` with correction `M0027`.
5. Add or update the matching `references.bib` entry with the same ID. Do not add local file paths or article binaries. Use source landing pages for access.
6. Run `python scripts/build_catalog.py` and `python scripts/validate.py`. Commit the updated generated Markdown and CSV. Topic lists and English README are generated; update their generator when changing shared prose.

`source_fulltext_available` records access in the source library, not whether a visitor can download a paper. For community additions without a source-library copy, use `false` and `pdf_version: "unavailable"`. Snapshot counts describe the initial import; current counts in the English README are regenerated. The Chinese introduction describes that initial snapshot explicitly.

## Evidence notes and errors

For a proposed scientific interpretation, provide a source location, claim type, supporting observation, and interpretation boundary. Distinguish independent validation reported by the source from a reproduction performed by the contributor. Do not add inferred autonomy or learning scores.

Report bibliographic mistakes, broken official links, changed publication status, and corrections with supporting primary sources. Automated checks verify local consistency; they do not establish scientific correctness or live availability of external pages.

By contributing original text or code, you agree to its respective repository license. Research papers retain their own licenses.
