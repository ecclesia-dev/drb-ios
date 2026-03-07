# Douai 1609 Annotation Matching — Reference Sources

## Purpose
Fix the douai-1609-clean.tsv: correct wrong book/chapter/verse labels using content
matching. The annotation text quotes the 1609 verse being commented on — match that
quote against 1609-spelling verse text to identify the correct reference.

## Sources (in priority order)

### 1. saint-dismas.com — TeX-typeset PDFs
- URL pattern (OT): `http://www.saint-dismas.com/ODRB/TeX/Old-Testament/[Book]/chapter-NN.pdf`
- URL pattern (NT): `http://www.saint-dismas.com/ODRB/TeX/New-Testament/[Book]/chapter-NN.pdf`
- Discover chapters per book: fetch `index.html` for each book, parse `chapter-NN.pdf` links
- Extract text: `pdftotext [file.pdf] -`
- Coverage: Genesis through Wisdom (OT) + all NT books. Missing: Psalms and prophets.
- Quality: highest — TeX-typeset, clean 1609 spelling
- Output: `drb-1609-saint-dismas.tsv`

### 2. originaldouayrheims.com — Hand-digitized HTML
- Base URL: `https://originaldouayrheims.com`
- OT path pattern: `/old/[bookname]` (lowercase)
- Some books use root `.html`: e.g. `https://originaldouayrheims.com/I%20Machabees.html`
- Coverage confirmed (books with actual content):
  - OT: genesis, ruth, psalms, wisdom, lamentations, baruch, daniel, jonas, sophonias
  - OT (.html at root): i machabees, ii machabees
  - NT: matthew, mark, luke, john, acts, romans, galatians, ephesians, philippians,
         colossians, titus, philemon, hebrews, james, jude, revelations,
         i/ii corinthians, i/ii thessalonians, i/ii timothee, i/ii/iii peter/john
- NOT available: Isaiah, Jeremiah, Ezekiel, and most minor prophets
- Quality: high — hand-digitized 1609 spelling, no OCR noise
- Output: `drb-1609-originaldouay.tsv`

### 3. THE HOLY BIBLE.pdf — Local PDF, Tesseract OCR
- Path: `<path-to-pdf>/THE HOLY BIBLE.pdf`
- 2,872 pages, 1635 Douay OT + 1582 Rheims NT, ABBYY FineReader scan (image-only)
- Render pages: `gs -dNOPAUSE -dBATCH -sDEVICE=png16m -r200 -dFirstPage=N -dLastPage=N -sOutputFile=/tmp/bible-pN.png "<path-to-pdf>/THE HOLY BIBLE.pdf"`
- OCR pages: `tesseract /tmp/bible-pN.png stdout 2>/dev/null`
- Known page ranges (approximate):
  - Isaiah: pages 1464–1545
  - Jeremiah: pages 1546–1660
- Parse: detect "CHAP." headers for chapter breaks; lines starting with digit = verse
- Use for: Isaiah and Jeremiah — not covered by sources 1 or 2
- Quality: medium — Tesseract OCR on 17th-century typeface, long-s artifacts
- Clean up: `rm /tmp/bible-p*.png` after each page to save disk
- Output: `drb-1609-pdf.tsv`

### 4. Modern DRB (drb.tsv) — Reference only
- Format: BookName TAB BookAbbrev TAB col3 TAB Chapter TAB Verse TAB VerseText
- Challoner revision (1749–52) — NOT 1609 text
- Use ONLY as matching aid to identify book/chapter/verse when sources 1–3 fail
- NEVER put modern DRB text into any output TSV column
- Output text in douai-1609-fixed-v2.tsv must always be the original 1609 annotation text

## Matching Rules
1. Try source 1 (saint-dismas) — Jaccard word overlap >= 0.25 → use match
2. Try source 2 (originaldouay) — Jaccard >= 0.25 → use match
3. Try source 3 (PDF OCR) — Jaccard >= 0.22 (lower threshold due to OCR noise) → use match
4. Try source 4 (modern DRB) — Jaccard >= 0.20 → correct ref only, never output text
5. No match → keep original ref, flag [LOW_CONFIDENCE]

## Checkpoint Rule
Every 200 rows: print progress. If >60% of last 200 rows are LOW_CONFIDENCE → ABORT.

## Output Files
- `drb-1609-saint-dismas.tsv` — scraped from source 1
- `drb-1609-originaldouay.tsv` — scraped from source 2
- `drb-1609-pdf.tsv` — OCR'd from source 3
- `douai-1609-fixed-v2.tsv` — corrected annotations (BookAbbrev, Chapter:Verse, VerseQuote, Commentary)
- `douai-1609-fix-report-v2.txt` — full audit trail
- `douai-1609-compare-v2.txt` — cross-comparison old vs new
- `douai-1609-clean.bak.tsv` — backup of original (do not modify)

## Hard Rules
- Never mix modern DRB text into output TSV
- VerseQuote = extracted from the annotation's own text, not substituted from any source
- Commentary = everything after the verse quote in the annotation
- Backup before touching anything
- Commit everything; do NOT push
