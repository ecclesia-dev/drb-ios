# Jerome QA Report: Douai 1609 Genesis Ch. 1–21 Extraction
**Date:** 2026-03-07  
**Agent:** Jerome (⚙️)  
**Source:** https://originaldouayrheims.com/old/genesis (chapters 1–21)  
**Output:** `DouayRheims/douai-1609-genesis-ch1-21.tsv`

---

## Executive Summary

**Critical Finding:** originaldouayrheims.com has only digitized annotations for **Genesis Chapter 1**. Chapters 2–21 have verse text present but **no annotation commentary whatsoever**.

The task premise ("chapters 1–21 confirmed present") referred to verse text presence, not annotation presence. Annotations (commentary) have only been hand-digitized for Ch. 1 on this site.

---

## Annotations Extracted Per Chapter

| Chapter | Annotations | Notes |
|---------|-------------|-------|
| 1 | **6** | ✅ Fully digitized on site |
| 2 | 0 | Verse text only — no commentary |
| 3 | 0 | Verse text only (Gn 3:15 Protoevangelium note absent) |
| 4 | 0 | Verse text only |
| 5 | 0 | Verse text only |
| 6 | 0 | Verse text only |
| 7 | 0 | Verse text only |
| 8 | 0 | Verse text only |
| 9 | 0 | Verse text only |
| 10 | 0 | Verse text only |
| 11 | 0 | Verse text only |
| 12 | 0 | Verse text only |
| 13 | 0 | Verse text only |
| 14 | 0 | Verse text only |
| 15 | 0 | Verse text only |
| 16 | 0 | Verse text only |
| 17 | 0 | Verse text only |
| 18 | 0 | Verse text only |
| 19 | 0 | Verse text only |
| 20 | 0 | Verse text only |
| 21 | 0 | Verse text only |
| **TOTAL** | **6** | |

---

## Chapter 1 Annotations Detail

All 6 annotations are `APPROVED` status — extracted directly from structured HTML with clear `VERSE. <i>Quote</i>] Commentary` markup.

| Verse | Quote | Commentary Summary |
|-------|-------|--------------------|
| 1:1 | "In the beginning." | Church Traditions vs. Scripture — pre-Scripture era, authority of Tradition (2,439 chars) |
| 1:1 | "In the beginning God made heauen and earth." | Difficulty of Scripture — Origen, Augustine, Basil, three spiritual senses (3,015 chars) |
| 1:2 | "The Spirite of God." | Baptism prefigured in waters, Tertullian on Christians as fish (955 chars) |
| 1:16 | "Tvvo great lights, and starres." | Light as accident, Eucharist — accidents remaining without subject (1,380 chars) |
| 1:26 | "Let vs make man to our Image." | Ten prerogatives of man in creation — detailed enumeration (3,249 chars) |
| 1:28 | "Increase and multiplie." | God's blessings effectual, Eucharist, precept of multiplication (1,253 chars) |

---

## HTML Structure Notes

The site uses two distinct HTML patterns that look similar:

1. **Actual annotations** (Ch. 1 only): `<span id="Annotations">ANNOTATIONS. Chap. I.</span>` header followed by `<span id="Annotations2">VERSE. <i>Quote</i>] Commentary</span>` blocks

2. **Verse text indentation** (Chs. 4, 6, 9, 11–13, 15, 18 etc.): `<span id="Annotations2">` used as CSS styling vehicle for indented verse text — **no commentary content**

The presence of `Annotations2` spans was not a reliable indicator of actual annotation content. Reliable detection required the `ANNOTATIONS. Chap.` header *and* the `]` character after an italic quote.

---

## Recommendation for Chs. 2–21

The 1610 Douai Old Testament is on Archive.org. The annotations for Genesis 2–21 must be sourced from there. Suggested approach:

- Primary source: [Archive.org Douai 1609-10 OT scan](https://archive.org/details/holybible00douauoft) — pages 1–80 cover Genesis
- Method: PDF extraction with OCR correction (similar to existing `drb-1609-pdf.tsv` pipeline)
- Note: Genesis 3:15 annotation (Protoevangelium / Immaculate Conception connection) is particularly important to capture

This site alone cannot fill the Genesis 1–21 gap. Ch. 1 is captured; the rest requires archive.org.

---

## Output File

**Path:** `DouayRheims/douai-1609-genesis-ch1-21.tsv`  
**Rows:** 6 (header + 6 data rows)  
**Columns:** `Book`, `Verse`, `Quote`, `Commentary`, `BOOK_CORRECTED`, `Status`  
**All rows:** `Book=Gn`, `BOOK_CORRECTED=` (empty), `Status=APPROVED`

**Do NOT commit** — awaiting Bellarmine review.
