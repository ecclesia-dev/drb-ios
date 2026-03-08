# Jerome QA Report — Douai 1609 v7
**Date:** 2026-03-07  
**File:** `DouayRheims/douai-1609-fixed-v7.tsv`  
**Commit:** `69fe28e`

## Problem
v6 introduced a duplicate `2Mc 2:20` reference. Two rows shared the same book/verse key:
1. Row about "Iudas Machabeus and purification of the great temple" — misidentified as 2:20, actually 2:19 content
2. Corrected row (added in v6) about Antiochus/Eupator/Jason the Cyrenean — correctly 2:20, but Status was `LOW_CONFIDENCE`

## Fixes Applied

| Row | Change |
|-----|--------|
| "Iudas Machabeus… purification of the great temple" | Verse `2:20` → `2:19` |
| Antiochus/Eupator/Jason the Cyrenean row | Status `LOW_CONFIDENCE` → `APPROVED` |

## Verification

- `2Mc 2:19` rows: **1** ✅
- `2Mc 2:20` rows: **1** ✅ (no duplicate)
- Total data rows: **2304** ✅ (unchanged from v6)

## Commit

```
69fe28e fix: Douai 1609 v7 — resolve 2Mc 2:19/2:20 collision, approve corrected row [Jerome]
```

— ⚙️ Jerome
