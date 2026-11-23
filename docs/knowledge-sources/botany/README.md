# Botanical knowledge sources

This directory records the approved source materials for Mirage's first closed-domain specialist: introductory botany.

## Current source policy

- Mirage has no network access at runtime.
- Source acquisition is an offline maintainer task. A human downloads and reviews each source before it is admitted.
- Preserve the original file unchanged; record its version, retrieval date, checksum, license, and provenance.
- Do not treat a source statement as automatically true. Extract claims with page/section citations and mark conflicts for review.
- Do not train model weights on a source unless its license and any additional terms explicitly permit that use.

## Approved candidate sources

1. **Botany (Melissa Ha, Maria Morrow, and Kammy Algiers)** — primary botany textbook. The LibreTexts book page provides a full-book PDF download control. Licensed CC BY-NC 4.0 except where an individual page says otherwise.
   - Book: https://bio.libretexts.org/Bookshelves/Botany/Botany_(Ha_Morrow_and_Algiers)
   - Authors/institutional provenance and license are stated on the book itself.
2. **The Science of Plants: Understanding Plants and How They Grow** — supporting plant-science text developed by faculty and staff at the University of Minnesota Department of Horticultural Science for HORT 1001/6001. The publisher provides PDF/EPUB offline downloads. Licensed CC BY-NC 4.0 except where otherwise noted.
   - Book: https://open.lib.umn.edu/horticulture/
   - Publication record: https://publishing.lib.umn.edu/publication/the-science-of-plants/

## Important exclusion: OpenStax Biology 2e

OpenStax Biology 2e is a useful general biology textbook, but its current licensing notice explicitly says it may not be ingested into large language models or generative AI offerings without prior written permission. Therefore it is **not approved for Mirage's knowledge ingestion or model training** unless written permission is obtained. See:
https://openstax.org/books/biology-2e/pages/index

## Local source-file layout

After downloading the books manually from their official publisher pages, place the untouched files here:

```
data/source_materials/originals/
  ha-morrow-algiers-botany.pdf
  umn-the-science-of-plants.pdf
```

Do not commit the PDFs to Git. Keep large source files out of version control; this repository stores provenance and processing metadata. Keep local copies backed up separately and do not redistribute them beyond the applicable license.

## Admission workflow

1. Download only from the official publisher/book page linked above.
2. Record the exact edition/version and download date in `sources.yaml`.
3. Calculate SHA-256 for each local file (`sha256sum data/source_materials/originals/*.pdf`).
4. Inspect the table of contents and license notices, including page-specific exceptions.
5. Extract text locally; retain page numbers and section headings.
6. Review extracted claims against the source pages before adding them to Mirage's curated knowledge base.
7. Keep source assertions, verified claims, disagreements, and unknowns distinct.

No source has yet been ingested into Mirage's knowledge base. This directory establishes provenance and the admission process only.
