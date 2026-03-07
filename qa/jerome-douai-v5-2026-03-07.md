# Jerome — Douai 1609 v5 Fix Report
**Date:** 2026-03-07  
**Engineer:** Jerome ⚙️  
**Input:** `douai-1609-fixed-v4.tsv`  
**Output:** `douai-1609-fixed-v5.tsv`  
**Status:** READY FOR BELLARMINE RE-REVIEW — do not push

---

## Fix Summary

| Fix | Description | Changes |
|-----|-------------|---------|
| Fix 1 | Heb→Ex: Exodus ch2/3/6 rows misattributed as Hebrews | **12 rows** |
| Fix 2a | Isaiah impossible verse corrected (Is 99:3→36:3, Is 109:2→36:2) | **2 rows** |
| Fix 2b | Is 3:16 — already had [LOW_CONFIDENCE], no action needed | 0 |
| Fix 3 | Mk→Prv (Proverbs bleed audit) | **0 rows** — no matches found |
| Fix 4 | Lk→1Mc (1Maccabees bleed: Lk 1:21 Antiochus/Eupatour) | **1 row** |
| Fix 5 | Status column added (6th col) | All 2304 rows |

**Total data rows:** 2304 (unchanged from v4)  
**Status=APPROVED:** 1343  
**Status=LOW_CONFIDENCE:** 961  

---

## Fix 1 — Heb→Ex Detail

The awk audit matched ~20 rows total, but 8 were legitimate Hebrews ch.1 rows with
commentary cross-references to Moses. Only the 12 rows from Heb ch.2/3/6 with Exodus
content in the **verse quote** (VerseQuote field $3) were re-attributed. These are clearly
Exodus chapters 2, 3, and 6 that received the wrong book abbreviation during OCR processing.

Converted rows (selected):
- Ex 2:15 — "drowne al the male-children"
- Ex 2:19 — Hebrew women (midwives context in commentary)
- Ex 2:23 — "King of AEcypt died"
- Ex 2:1 — "Moyfes wifely confidering"
- Ex 2:21 — "fauour to ftinke before Pharao"
- Ex 3:20 — "Moyfes therfore tooke his wite"
- Ex 6:3, Ex 6:17 (×2) — Plague of blood / YHWH name passages

NOT changed: Heb 1:X rows (8 rows) — legitimate Epistle to the Hebrews ch.1 with
commentary mentioning Moses/law. Heb 2:6 ("What is man" — Ps 8:4 quote) also retained.

---

## Fix 2 — Isaiah Verse Corrections

- `Is 99:3` → `Is 36:3`: Content matches Is 36 Sennacherib/Rabshakeh passage ✓  
- `Is 109:2` → `Is 36:2`: Same passage context ✓  
- `Is 3:16`: Already tagged [LOW_CONFIDENCE] in v4, no change needed

---

## Fix 3 — Mk→Prv Audit

Searched all Mk rows for: "wise son", "glutton", "shameth his father",
"rich man seemeth", "poor man being prudent", "searcheth him"  
**Result: no matches.** No Proverbs bleed in Mk attribution.

---

## Fix 4 — Lk→1Mc Detail

One match at original line 1780:
- `Lk 1:21` → `1Mc 1:21`
- Content: "Yeaand of the batrels that perteyne to Antiochus the Noble, and his fonne Eupatour..."
- Clearly 2 Maccabees preface/prologue content (2Mc 2:20-21 region), misattributed as Luke.
  
**Note for Bellarmine:** The verse quote and commentary clearly describe Antiochus and Eupator,
matching the prologue of 2 Maccabees. Assigned 1Mc 1:21 per Fix 4 instructions; Bellarmine
may wish to review whether this should be `2Mc` instead.

---

## Fix 5 — Status Column

Added 6th column `Status` to all rows:
- `APPROVED` — row contains no [LOW_CONFIDENCE] tag in any field
- `LOW_CONFIDENCE` — row contains [LOW_CONFIDENCE] tag in VerseQuote or Commentary

The [LOW_CONFIDENCE] tags are preserved in their original fields; the Status column
provides a clean flag for UI suppression without removing data.

---

## Files

- `DouayRheims/douai-1609-fixed-v5.tsv` — production output
- `DouayRheims/apply_v5_fixes.py` — reproducible transform script (Jerome's work artifact)
- `qa/jerome-douai-v5-2026-03-07.md` — this report

**Commit:** `fix: Douai 1609 v5 — Bellarmine-directed attribution fixes [Jerome]`  
**Branch:** current working branch (not pushed — awaiting Bellarmine re-review)
