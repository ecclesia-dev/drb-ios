# Augustine QA Fix Report — Lapide :0 Verse Entries
**Date:** 2026-03-07  
**Agent:** Augustine 🔨 (Lead iOS Engineer)  
**Ticket:** QA-001

---

## Summary

Remapped 404 `Chapter:0` verse keys in `lapide.tsv` to `Chapter:1`. These were chapter-level
introductory commentaries from Cornelius à Lapide that were silently unreachable because
`CommentaryManager` builds lookup keys from `drb.tsv` verse numbers starting at `:1`.

---

## Changes

### `DouayRheims/lapide.tsv`
- **Before:** 404 rows with verse format `Book Chapter:0` (e.g. `Ps 1:0`, `Is 1:0`)
- **After:** All remapped to `Chapter:1` — verified 0 `:0` entries remain
- These introductory commentaries now resolve correctly against the verse key index

### `DouayRheims/CommentaryManager.swift`
- Removed stale label calling Lapide a "small" source (it is ~7.8k rows, not small)
- Updated comment to accurately reflect row counts: Douai ~3k, Lapide ~7.8k
- Added `TODO (QA-002/Cyprian)` comment flagging Lapide for lazy-load migration to reduce
  startup memory pressure (same pattern already in use for Haydock)

---

## Commit

```
a6988f8  fix: remap Lapide :0 verse entries to :1, update size comments [Augustine]
```

Files changed: `lapide.tsv`, `CommentaryManager.swift`  
**NOT pushed — awaiting Pius PR gate → Leo merge.**

---

## Verification

```
Before fix:  404 :0 rows
After fix:     0 :0 rows  ✅
```

---

## Open Items

- **QA-002 (Cyprian):** Lapide lazy-load — TODO comment added in `CommentaryManager.swift`;
  implementation deferred to a follow-up task. Lapide at ~7.8k rows loads eagerly on startup
  which adds unnecessary memory pressure on first launch. Should mirror Haydock's lazy pattern.

---

*Ad maiorem Dei gloriam.*
