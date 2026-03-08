# QA Report — Lapide OT Addition (commit e3586ce)
**Agent:** Cyprian 🧪 (QA Engineer)  
**Date:** 2026-03-07  
**Commit:** `e3586ceb0487ef614577d7ed29905457c3be5e88`  
**Author:** Augustine [feat: add Lapide OT commentary — full Bible coverage (46 OT books)]  
**Security gate:** PASSED (Athanasius)

---

## Summary

**QA GATE: CONDITIONAL PASS** [Cyprian]

One functional blocker (chapter-level verse:0 entries inaccessible in UI) and one medium advisory (eager load memory pressure). Both must be addressed before next release, but neither causes a crash or data corruption.

---

## Check Results

### ✅ 1. TSV Format Consistency

All rows have exactly 3 columns (`Book\tVerse\tCommentary`).

```
Total errors: 0
```

**Result: PASS**

---

### ✅ 2. Book Abbreviations Match drb.tsv

All 54 unique abbreviations in `lapide.tsv` are present in `drb.tsv` column 2. No mismatches.

Books absent from lapide (expected — these are NT books Lapide did not comment on in this dataset):
`1Pt`, `2Pt`, `1Thes`, `2Thes`, `1Tm`, `2Tm`, `3Jn`, `Acts`, `Apc`, `Col`, `Eph`, `Heb`, `Jas`, `Jude`, `Phil`, `Phlm`, `Rom`, `Ti`

This is expected coverage, not a data error.

**Result: PASS**

---

### ⚠️ 3. Verse Format — BLOCKER FOUND

OT data introduces 404 entries using `Chapter:0` format (e.g. `Ps 1:0`, `Is 1:0`). These are **chapter-level introductory commentaries** — Lapide frequently opens a chapter with a thematic overview before commenting verse-by-verse.

**Distribution of verse:0 entries:**

| Book | Count |
|------|-------|
| Ps   | 122   |
| Is   | 66    |
| Jer  | 52    |
| Sir  | 51    |
| Ez   | 48    |
| Wis  | 19    |
| Dn   | 12    |
| Eccl | 11    |
| Bar  | 6     |
| Lam  | 5     |
| Minor prophets | 11 |
| **Total** | **404** |

**The problem:** `CommentaryManager.swift` builds lookup keys as `"Abbrev:Chapter:Verse"`. The app's UI triggers lookups using verse numbers from `drb.tsv`, where verses start at 1. A user viewing `Ps 1:1` will get key `Ps:1:1` — the chapter-level commentary at key `Ps:1:0` is **silently unreachable**.

NT data (existing) has no verse:0 entries — this is an OT-specific data pattern, new with this commit.

**Impact:** 404 commentary entries (5.2% of OT data) are inaccessible via normal verse browsing.

**Remediation options (Augustine to choose):**
1. **Remap to verse 1:** Change all `X:0` refs to `X:1` in the TSV so they attach to the chapter's first verse. Simple, no Swift changes needed.
2. **Chapter-level display:** Implement a chapter preamble lookup in `CommentaryManager` using a `:0` sentinel — display it at the top of the chapter view. Requires Swift changes.
3. **Keep as-is and document:** Accept that chapter introductions are not displayed. Not recommended — this silently drops significant content.

**Recommendation:** Option 1 (remap to verse 1) is the fastest fix for this release. Option 2 is the proper long-term solution.

**Result: CONDITIONAL — requires remediation**

---

### ⚠️ 4. Memory Loading (Athanasius's Flag — Confirmed)

`CommentaryManager.swift` loads Lapide **eagerly** in `init()`:

```swift
private init() {
    // Fix 1 + 4: Load only the small sources (Douai ~3k lines, Lapide ~7.8k lines — full Bible)
    // eagerly in the background. Haydock (13MB / ~36k lines) loads lazily on first access.
    Task {
        await loadSourceInBackground(.douai1609)
        await loadSourceInBackground(.lapide)
        isLoaded = true
    }
}
```

With the OT addition, `lapide.tsv` is now **7,830 rows / ~8MB** loaded at app startup on every launch. Haydock is lazy, but Lapide is not.

The in-code comment justifies it as "small," but 8MB eager load is no longer small — it's now 3× larger than the Douai source and only 1.6× smaller than Haydock.

**Flag: MED** — Memory pressure on older/low-RAM devices (iPhone SE 1st gen, iPad mini 2, etc.). Background task mitigates UI blocking but memory still allocated at startup.

**Recommendation:** Migrate Lapide to the same lazy-load pattern as Haydock. Trigger load on first `commentaries(for:)` call. The `ensureLoaded(_:)` helper already exists — just add `.lapide` to it.

**Result: ADVISORY (MED) — recommend fix before 1.0 release**

---

### ✅ 5. Row Count Sanity

```
7830 DouayRheims/lapide.tsv
```

Expected: 7830 (7829 data rows + 1 header). **Exact match.**

**Result: PASS**

---

### ✅ 6. Empty Commentary Rows

```
Empty commentary rows: 0
```

No empty commentary fields in the entire file.

**Result: PASS**

---

## Defect Log

| ID | Severity | Description | Owner |
|----|----------|-------------|-------|
| QA-001 | **HIGH** | 404 verse:0 entries (chapter-level commentary) unreachable via current UI verse lookup | Augustine |
| QA-002 | MED | Lapide loaded eagerly at startup (~8MB); recommend lazy load for older devices | Augustine |

---

## Final Verdict

**QA GATE: CONDITIONAL PASS** [Cyprian 🧪]

QA-001 must be resolved (or explicitly accepted with documented rationale) before the PR is merged. QA-002 is strongly recommended before 1.0 but not a hard blocker for the PR.

**Routing:**
- **QA-001 blocker** → route to **Augustine** for fix, then re-submit to QA
- Once Augustine resolves QA-001 → **Pius** (PR gate) → **Leo** (push)
- QA-002 can track as a follow-up issue if Augustine defers it

---

*Deo gratias. No regressions introduced. Data integrity is sound. Fix the verse:0 problem and this ships.*
