#!/usr/bin/env python3
"""
compare-douai.py  —  Jerome, ecclesia-dev CLI specialist
=========================================================
Row-by-row comparison of douai-1609-clean.bak.tsv (original) against
douai-1609-fixed.tsv (re-matched output), using douai-1609-match-meta.tsv
for scores and split metadata.

Output: douai-1609-compare.txt

SECTION 1 — RESOLVED ISSUES      (ref changed, confident match)
SECTION 2 — UNCHANGED LOW CONF   (no confident match found)
SECTION 3 — POTENTIAL NEW ISSUES (ref changed but suspicious)
"""

import csv
import os
import sys

WORKDIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(WORKDIR)

for f in ('douai-1609-clean.bak.tsv', 'douai-1609-fixed.tsv', 'douai-1609-match-meta.tsv'):
    if not os.path.exists(f):
        print(f"ERROR: {f} not found. Run fix-douai-refs.py first.", file=sys.stderr)
        sys.exit(1)

# ── Biblical book order (for testament detection) ─────────────────────────────
OT_BOOKS = {
    'Gn','Ex','Lv','Nm','Dt','Jos','Jgs','Ru','1Sm','2Sm','1Kgs','2Kgs',
    '1Chr','2Chr','Ezr','Neh','Tb','Jdt','Est','1Mc','2Mc',
    'Jb','Ps','Prv','Eccl','Sg','Wis','Sir',
    'Is','Jer','Lam','Bar','Ez','Dn',
    'Hos','Jl','Am','Ob','Jon','Mi','Na','Hb','Zep','Hg','Zec','Mal',
}
NT_BOOKS = {
    'Mt','Mk','Lk','Jn','Acts','Rom','1Cor','2Cor','Gal','Eph','Php','Col',
    '1Thes','2Thes','1Tm','2Tm','Tit','Phlm','Heb','Jas','1Pt','2Pt',
    '1Jn','2Jn','3Jn','Jude','Rv',
}

def testament(book):
    if book in OT_BOOKS: return 'OT'
    if book in NT_BOOKS: return 'NT'
    return '??'

# ── Known problem pairs (orig book → expected match book) ─────────────────────
# Used to confirm whether a book change is a "known fix" or unexpected
KNOWN_MISATTRIBUTIONS = {
    ('Sg', 'Is'),    # OCR labeled Song of Songs rows as Isaiah content
    ('Rom', 'Jas'),  # Romans labeled rows are James 5
    ('Phlm', 'Heb'), # Philemon labeled rows are Hebrews
}

def is_known_fix(orig_book, new_book):
    return (orig_book, new_book) in KNOWN_MISATTRIBUTIONS

# ── Load original ─────────────────────────────────────────────────────────────
originals = []
with open('douai-1609-clean.bak.tsv', encoding='utf-8') as f:
    reader = csv.reader(f, delimiter='\t')
    next(reader)  # header
    for row in reader:
        originals.append({
            'book': row[0].strip() if len(row) > 0 else '',
            'ref':  row[1].strip() if len(row) > 1 else '',
            'text': row[2]         if len(row) > 2 else '',
        })

# ── Load fixed ────────────────────────────────────────────────────────────────
fixed = []
with open('douai-1609-fixed.tsv', encoding='utf-8') as f:
    reader = csv.reader(f, delimiter='\t')
    next(reader)  # header
    for row in reader:
        fixed.append({
            'book':    row[0].strip() if len(row) > 0 else '',
            'ref':     row[1].strip() if len(row) > 1 else '',
            'quote':   row[2]         if len(row) > 2 else '',
            'comment': row[3]         if len(row) > 3 else '',
        })

# ── Load metadata ─────────────────────────────────────────────────────────────
meta = []
with open('douai-1609-match-meta.tsv', encoding='utf-8') as f:
    reader = csv.reader(f, delimiter='\t')
    next(reader)  # header
    for row in reader:
        meta.append({
            'row_num':      int(row[0]) if len(row) > 0 else 0,
            'orig_book':    row[1].strip() if len(row) > 1 else '',
            'orig_ref':     row[2].strip() if len(row) > 2 else '',
            'matched_book': row[3].strip() if len(row) > 3 else '',
            'matched_ref':  row[4].strip() if len(row) > 4 else '',
            'score':        float(row[5])  if len(row) > 5 else 0.0,
            'split_method': row[6].strip() if len(row) > 6 else '',
            'quote_len':    int(row[7])    if len(row) > 7 else 0,
            'status':       row[8].strip() if len(row) > 8 else '',
        })

if not (len(originals) == len(fixed) == len(meta)):
    print(f"ERROR: row count mismatch — orig={len(originals)}, "
          f"fixed={len(fixed)}, meta={len(meta)}", file=sys.stderr)
    sys.exit(1)

total = len(originals)
print(f"Comparing {total} rows…", flush=True)

# ── Classify rows ─────────────────────────────────────────────────────────────
MARGINAL_THRESHOLD  = 0.35  # confident but borderline
SUSPICIOUS_SCORE    = 0.35  # book changed and score < this → flag
MIN_QUOTE_LEN       = 15

section1 = []   # RESOLVED ISSUES
section2 = []   # UNCHANGED LOW CONFIDENCE
section3 = []   # POTENTIAL NEW ISSUES

for i in range(total):
    orig = originals[i]
    fix  = fixed[i]
    m    = meta[i]
    rn   = i + 1

    orig_full  = f"{orig['book']} {orig['ref']}"
    new_full   = f"{fix['book']} {fix['ref']}"
    score      = m['score']
    status     = m['status']
    quote      = fix['quote']
    quote_len  = m['quote_len']
    split_meth = m['split_method']
    low_conf   = '[LOW_CONFIDENCE]' in fix['comment']
    ref_changed = (orig['book'] != fix['book']) or (orig['ref'] != fix['ref'])

    # ── SECTION 2: Unchanged low confidence ──────────────────────────────────
    if low_conf:
        # Determine reason from status field
        if status == 'STRUCTURAL_GAP':
            if not quote.strip() or quote_len < MIN_QUOTE_LEN:
                reason = f"structural gap — no usable verse quote (len={quote_len}, split={split_meth})"
            else:
                reason = f"structural gap — book not in DRB or zero candidate verses (score={score:.3f})"
        elif not quote.strip():
            reason = "verse quote empty"
        elif quote_len < MIN_QUOTE_LEN:
            reason = f"quote too short ({quote_len} chars)"
        elif split_meth == 'none':
            reason = "no split marker found in annotation text"
        else:
            reason = f"best match score {score:.3f} below threshold (0.25)"

        section2.append({
            'row': rn, 'orig': orig_full, 'score': score,
            'split': split_meth, 'quote': quote[:60],
            'reason': reason, 'status': status,
        })
        continue

    # ── SECTION 1 or 3: Ref changed, confident match ──────────────────────────
    if ref_changed:
        book_flipped   = orig['book'] != fix['book']
        testament_flip = testament(orig['book']) != testament(fix['book'])
        known          = is_known_fix(orig['book'], fix['book'])

        # Build a confirmation note for known fixes
        if known:
            confirm = f"Known misattribution corrected: {orig['book']}→{fix['book']}"
        elif book_flipped:
            confirm = f"Book changed: {orig['book']}→{fix['book']}"
        else:
            confirm = f"Ref corrected within {fix['book']}: {orig['ref']}→{fix['ref']}"

        entry = {
            'row': rn, 'orig': orig_full, 'new': new_full,
            'score': score, 'status': status, 'confirm': confirm,
            'quote': quote[:70], 'testament_flip': testament_flip,
            'book_flipped': book_flipped, 'known': known,
        }

        # Suspicious if:
        # (a) score is marginal (< SUSPICIOUS_SCORE), OR
        # (b) testament flipped without being a known fix, OR
        # (c) quote was very short (unreliable basis for matching)
        suspicious_reasons = []
        if score < SUSPICIOUS_SCORE:
            suspicious_reasons.append(f"marginal score ({score:.3f})")
        if testament_flip and not known:
            suspicious_reasons.append(
                f"unexpected testament flip {testament(orig['book'])}→{testament(fix['book'])}")
        if quote_len < MIN_QUOTE_LEN:
            suspicious_reasons.append(f"short quote ({quote_len} chars)")
        if split_meth == 'none':
            suspicious_reasons.append("no split marker — quote boundary uncertain")

        if suspicious_reasons:
            entry['suspicious_reasons'] = suspicious_reasons
            section3.append(entry)
        else:
            section1.append(entry)
    # ref unchanged, confident → no issue, skip


# ── Write comparison report ───────────────────────────────────────────────────
print("Writing douai-1609-compare.txt…", flush=True)

resolved_count   = len(section1)
unchanged_count  = len(section2)
new_issues_count = len(section3)

with open('douai-1609-compare.txt', 'w', encoding='utf-8') as rpt:
    def w(line=''):
        rpt.write(line + '\n')

    w("DOUAI 1609 COMPARISON REPORT")
    w("=" * 70)
    w("Original: douai-1609-clean.bak.tsv")
    w("Fixed   : douai-1609-fixed.tsv")
    w()
    structural_gap_count = sum(1 for e in section2 if e.get('status') == 'STRUCTURAL_GAP')
    true_low_conf_count  = unchanged_count - structural_gap_count

    w("SUMMARY")
    w("-" * 40)
    w(f"  Total rows            : {total}")
    w(f"  Resolved issues       : {resolved_count}  "
      f"(ref/book changed, confident match)")
    w(f"  Unchanged low conf.   : {unchanged_count}  "
      f"(no confident match — kept original)")
    w(f"    → Match failures    : {true_low_conf_count}  "
      f"(quote present but score too low)")
    w(f"    → Structural gaps   : {structural_gap_count}  "
      f"(no quote / book not in DRB)")
    w(f"  Potential new issues  : {new_issues_count}  "
      f"(ref changed but suspicious — review)")
    w(f"  Unchanged + confident : {total - resolved_count - unchanged_count - new_issues_count}  "
      f"(original ref confirmed correct)")
    w()

    # ── SECTION 1 ─────────────────────────────────────────────────────────────
    w("=" * 70)
    w(f"SECTION 1 — RESOLVED ISSUES  ({resolved_count} rows)")
    w("=" * 70)
    w("  Rows where book or ref changed to a confidently matched DRB verse.")
    w()
    if section1:
        for e in section1:
            tag = " [KNOWN FIX]" if e['known'] else ""
            w(f"  Row {e['row']:4d}  {e['orig']:<16} → {e['new']:<16}  "
              f"score={e['score']:.3f}  status={e['status']}{tag}")
            w(f"           {e['confirm']}")
            w(f"           Quote: {e['quote']}")
            w()
    else:
        w("  (none)")
    w()

    # ── SECTION 2 ─────────────────────────────────────────────────────────────
    w("=" * 70)
    w(f"SECTION 2 — UNCHANGED (LOW CONFIDENCE)  ({unchanged_count} rows)")
    w("=" * 70)
    w("  No confident match found; original ref kept; [LOW_CONFIDENCE] tagged.")
    w()
    if section2:
        for e in section2:
            tag = "  [STRUCTURAL GAP]" if e.get('status') == 'STRUCTURAL_GAP' else ""
            w(f"  Row {e['row']:4d}  {e['orig']:<16}  score={e['score']:.3f}  "
              f"split={e['split']}{tag}")
            w(f"           Reason : {e['reason']}")
            w(f"           Quote  : {e['quote']}")
            w()
    else:
        w("  (none)")

    # ── SECTION 3 ─────────────────────────────────────────────────────────────
    w("=" * 70)
    w(f"SECTION 3 — POTENTIAL NEW ISSUES  ({new_issues_count} rows)")
    w("=" * 70)
    w("  Ref changed but match looks suspicious. Human review recommended.")
    w()
    if section3:
        for e in section3:
            w(f"  Row {e['row']:4d}  {e['orig']:<16} → {e['new']:<16}  "
              f"score={e['score']:.3f}  status={e['status']}")
            w(f"           Flags  : {'; '.join(e['suspicious_reasons'])}")
            w(f"           Quote  : {e['quote']}")
            w()
    else:
        w("  (none — all ref changes look clean)")
    w()

    w("=" * 70)
    w("END OF COMPARISON REPORT")

print(f"\nDone.")
print(f"  Section 1 (resolved)     : {resolved_count}")
print(f"  Section 2 (low conf)     : {unchanged_count}")
print(f"  Section 3 (new issues)   : {new_issues_count}")
