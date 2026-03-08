# Douai 1609 — v6 QA Report
**Date:** 2026-03-07  
**Author:** Jerome ⚙️  
**Base:** `douai-1609-fixed-v5.tsv`  
**Output:** `douai-1609-fixed-v6.tsv`  
**Commit:** `9ee5f5b` — fix: Douai 1609 v6 — correct Is 51:3, Is 62:2, 2Mc 2:20 per Bellarmine [Jerome]

---

## Corrections Applied (3 total)

### Fix A — Isaiah Impossible Verses

Bellarmine rejected v5 assignments of `Is 36:3` and `Is 36:2` (duplicate). Correct chapters identified by verse content.

**A1 — Line 1689**
- v5: `Is	36:3`
- v6: `Is	51:3`
- Content confirms: *"For the fpiritual Sion, the Church of Chrift, shal receiue much grace..."* — Isaiah 51:3 (comfort Sion, Abraham your father)

**A2 — Line 1694**
- v5: `Is	36:2` (duplicate — Line 1677 is the genuine Is 36:2)
- v6: `Is	62:2`
- Content confirms: *"And the Gentilsfhal fee thy iuft one, and aj Kings thy nobly one..."* — Isaiah 62:2 (Gentils shall see thy just one, new name)

**Method (Python):**
```python
# A1
lines[1688] = line.replace('Is\t36:3\t', 'Is\t51:3\t', 1)
# A2
lines[1693] = line.replace('Is\t36:2\t', 'Is\t62:2\t', 1)
```

Equivalent sed (1-indexed, tab-literal):
```bash
sed -i '' '1689s/^Is\t36:3\t/Is\t51:3\t/' douai-1609-fixed-v6.tsv
sed -i '' '1694s/^Is\t36:2\t/Is\t62:2\t/' douai-1609-fixed-v6.tsv
```

---

### Fix B — 2 Maccabees Misattribution

Bellarmine confirms: Line 1780 contains the prologue to 2 Maccabees (Antiochus the Noble, Eupator, Jason the Cyrenean — 2Mc 2:20–24). In v5 it was mis-tagged `1Mc 1:21`.

**Line 1780**
- v5: `1Mc	1:21`
- v6: `2Mc	2:20`
- Content confirms: *"Yeaand of the batrels that perteyne to Antiochus the Noble, and his fonne Eupatour... and of the things which by lafon the Cyrenean are comprifed in fiue Books..."*

**Method (Python):**
```python
lines[1779] = line.replace('1Mc\t1:21\t', '2Mc\t2:20\t', 1)
```

Equivalent sed:
```bash
sed -i '' '1780s/^1Mc\t1:21\t/2Mc\t2:20\t/' douai-1609-fixed-v6.tsv
```

---

## Row Count Verification

| File | Lines | Data rows |
|------|-------|-----------|
| v5 (source) | 2305 | 2304 ✅ |
| v6 (output) | 2305 | 2304 ✅ |

Row count unchanged. No rows added or removed.

---

## Verification Commands

```bash
# Confirm Isaiah fixes
awk -F'\t' 'NR==1689 || NR==1694 {print NR": "$1" "$2}' douai-1609-fixed-v6.tsv
# Expected: 1689: Is 51:3 / 1694: Is 62:2

# Confirm 2Mc fix
awk -F'\t' 'NR==1780 {print NR": "$1" "$2}' douai-1609-fixed-v6.tsv
# Expected: 1780: 2Mc 2:20

# Confirm no residual impossible Isaiah verses
awk -F'\t' '$1=="Is" {split($2,a,":"); if(a[1]+0 > 66) print NR": "$1" "$2}' douai-1609-fixed-v6.tsv
# Expected: (no output)

# Row count
awk 'END{print NR-1" data rows"}' douai-1609-fixed-v6.tsv
# Expected: 2304 data rows
```

---

*Ad maiorem Dei gloriam.*
