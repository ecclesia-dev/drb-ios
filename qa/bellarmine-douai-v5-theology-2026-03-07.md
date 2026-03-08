# Bellarmine — Douai 1609 v5 Theology Review
**Date:** 2026-03-07  
**Reviewer:** Bellarmine ⛪ (Theology Gate)  
**File:** `douai-1609-fixed-v5.tsv`  
**Jerome's Report:** `jerome-douai-v5-2026-03-07.md`  
**Verdict:** ❌ NOT APPROVED — v6 required

---

## Executive Summary

Two of Jerome's five fixes contain attributable errors requiring correction before production
approval. Fixes 1, 3, and 5 are confirmed correct. Fixes 2 and 4 are wrong. Details below.

---

## Fix-by-Fix Verdict

### Fix 1 — 12 Heb→Ex rows ✅ CONFIRMED

**Status:** APPROVED

Spot-check confirmed Ex rows contain authentic Exodus content:
- Ex 5:17 — "Moyfes and Aaron... coming forth from Pharao" ✓
- Ex 8:11 — "land of AEgypt... Pharao... Moyfes" ✓
- Ex 9:6 — "Pharao... the children of Israel" ✓
- Ex 9:27 — "Pharao sent and called Moyfes and Aaron" ✓
- Ex 10:14 — "whole Land of AEgypt... Pharao... Moyfes" ✓
- Ex 11:10 — "Moyfes and Aaron... Pharao... children of Israel" ✓
- Ex 12:18/27 — Paschal Lamb / Passover narrative ✓

All 12 re-attributed rows contain genuine Exodus material. The decision to retain the 8
Heb ch.1 rows as Hebrews is also correct — those contain Epistle to the Hebrews content
with only commentary cross-references to Moses.

---

### Fix 2 — Isaiah impossible verses ❌ REJECTED

**Status:** NOT APPROVED — wrong target chapter assigned

Jerome moved `Is 99:3 → Is 36:3` and `Is 109:2 → Is 36:2`. The impossible chapter numbers
were fixed (Isaiah has 66 chapters), but the content was NOT verified against Isaiah 36
before assigning. Result: both rows now carry plausible-looking but wrong chapter refs.

**Evidence:**

`Is 36:3` (Jerome's correction of Is 99:3) contains:
> "For the fpiritual Sion, the Church of Chrift… Attend to Abraham your father… Our Lord
> therefore wil comfort Sion, and wil comfort al the ruines therof…"

This is **Isaiah 51:3** (RSV: "For the LORD will comfort Zion…") and Isaiah 51:1-2 (attending
to Abraham). Not Isaiah 36. Isaiah 36 is the Sennacherib/Rabshakeh campaign at Jerusalem —
completely different content.

`Is 36:2` (Jerome's correction of Is 109:2) — there are NOW TWO rows at Is 36:2:
- First: "And the King of the Affyrians-fent Rabfaces from Lachis to lerufalem" → this IS
  legitimate Isaiah 36:2 (Sennacherib at the water conduit). This row is correct. ✓
- Second (Jerome's correction): "And the Gentils shal fee thy iuft one, and aj Kings thy
  nobly onc: and chou fhalt be called by a new name… Thou shalt no more be called Forsaken"
  → this is **Isaiah 62:2-4** (RSV: "The nations shall see your vindication… you shall be
  called by a new name"). Not Isaiah 36.

**Required corrections for v6:**

| Current (wrong) | Correct | Evidence |
|-----------------|---------|----------|
| `Is 36:3` | `Is 51:3` | Content = "Our Lord will comfort Sion / look to Abraham your father" = Is 51:1-3 |
| `Is 36:2` (second row) | `Is 62:2` | Content = "Gentils shall see thy just one / called by a new name" = Is 62:2 |

Note: The OCR corruptions `99` and `109` were likely garbled from `51` and `62` respectively.
This is a plausible OCR error pattern (`51 → 5l → ...99`; `62 → 6z → ...109`).

---

### Fix 3 — Mk→Prv audit ✅ CONFIRMED

**Status:** APPROVED (no action required)

Jerome found zero Proverbs bleed in Mark attributions. No objection.

---

### Fix 4 — Lk→1Mc ❌ REJECTED

**Status:** NOT APPROVED — wrong book (1Mc vs 2Mc)

Jerome correctly identified the row was misattributed as Luke, and correctly identified the
content as Maccabees. However, he assigned `1Mc 1:21` when the content is demonstrably from
**2 Maccabees**.

**Evidence:**

The row at 1Mc 1:21 (the converted row) reads:
> "Yeaand of the batrels that perteyne to Antiochus the Noble, and his fonne Eupatour; 22.
> and of the apparitions that were made from heauen to them… 24. Also the things which by
> Iafon the Cyrenean are comprifed in fiue Books, we haue attempted to abridge in one volume…
> 27. The veritie certes concerning every particular leauing to the auctours…"

This is the **prologue of 2 Maccabees** (2Mc 2:20-32). The specific markers:
- "Antiochus the Noble, and his son Eupator" = 2Mc 2:20 ✓
- "apparitions from heaven" = 2Mc 2:21 ✓
- "Jason the Cyrenean… five Books… abridge in one volume" = 2Mc 2:23-24 ✓ (this is the
  explicit preface of 2 Maccabees, not present in 1 Maccabees)

Jerome himself flagged this uncertainty in his report. He was right to doubt. The correct
attribution is `2Mc 2:20` (or `2Mc 2:21` if the VerseQuote anchor is on that verse).

Note: There is also a legitimate `1Mc 1:21` row with Antiochus-entering-Jerusalem content
("And Antiochus turned, after he strucke egypt… entered the Sanctuarie"). That row is correct
and should not be disturbed.

**Required correction for v6:**
- Row currently at `1Mc 1:21` (Eupator/Jason-of-Cyrene content): rebook to `2Mc 2:20`
- Status may remain LOW_CONFIDENCE given verse uncertainty, but book must be corrected

---

### Fix 5 — Status column ✅ CONFIRMED (with minor doc note)

**Status:** APPROVED

Column structure confirmed correct:
- Total rows: 2304 (excluding header) ✓
- Status=APPROVED: 1343 ✓
- Status=LOW_CONFIDENCE: 961 ✓
- All rows have uniform 5-column structure ✓

**Minor documentation error in Jerome's report:** His report states "6th column" but Status
is actually the **5th column** (BookAbbrev, Chapter:Verse, VerseQuote, Commentary, Status).
The original file had 4 columns; Jerome added Status as the 5th. Data is correct; report has
wrong column number. Jerome should correct the report in v6.

---

### LOW_CONFIDENCE approach — ✅ ACCEPTABLE

961 rows with uncertain verse attribution remaining as LOW_CONFIDENCE, suppressed in app UI
pending a v6 re-matching pass — this is acceptable for production. The content is real Douai
1609 text; only the verse ref is uncertain. Users are not harmed by suppression. This approach
preserves the data for future correction without polluting the UI.

---

## Jerome's v6 Mandatory Corrections

| Priority | Fix | Action Required |
|----------|-----|-----------------|
| **HIGH** | Fix 2a | Change `Is 36:3` → `Is 51:3` (Isaiah 51 content confirmed) |
| **HIGH** | Fix 2b | Change second `Is 36:2` → `Is 62:2` (Isaiah 62 content confirmed) |
| **HIGH** | Fix 4 | Change `1Mc 1:21` (Eupator/Jason row) → `2Mc 2:20` |
| **LOW** | Fix 5 doc | Correct report to say Status is 5th column, not 6th |

After v6 corrections, submit to Bellarmine for spot-check re-review (Fix 2 and Fix 4 rows only).

---

## Pipeline Status

```
Jerome v5 → Bellarmine REJECTED → Jerome v6 required
```

Next after v6 approval: Pius (PR gate) → Leo pushes drb-ios.

---

_Ad maiorem Dei gloriam._  
_Bellarmine ⛪ — Theology Gate, Ecclesia Dev_
