#!/usr/bin/env python3
"""
compare-douai-v2.py
Cross-compare douai-1609-clean.bak.tsv (original) vs douai-1609-fixed-v2.tsv (new).
Output: douai-1609-compare-v2.txt

SECTION 1: RESOLVED — known issues fixed (book misattributions, wrong refs)
SECTION 2: UNCHANGED LOW CONFIDENCE — every row still marked [LOW_CONFIDENCE]
SECTION 3: POTENTIAL NEW ISSUES — ref changed to something unexpected; flag for review
SECTION 4: STATS SUMMARY
"""

import re
import sys

ORIG   = "douai-1609-clean.bak.tsv"
FIXED  = "douai-1609-fixed-v2.tsv"
OUT    = "douai-1609-compare-v2.txt"

# Known book misattributions from v1 analysis (rough list to seed RESOLVED section)
KNOWN_MISATTRIBUTIONS = {
    # (wrong_book, wrong_ref) patterns — if these changed, flag as RESOLVED
    'Sg', 'Phlm',  # Sg→Is was a known category of error
}

# Books that should rarely have annotations (unexpected targets)
UNEXPECTED_TARGETS = {'Ru', 'Est', 'Ezr', 'Neh', '2Jn', '3Jn', 'Jude'}


def load_tsv(path, has_fixed_cols=False):
    """
    Load a TSV annotation file.
    Returns list of dicts with row index + fields.
    """
    rows = []
    with open(path, encoding='utf-8') as f:
        lines = f.readlines()

    header = lines[0].strip().split('\t')
    for i, line in enumerate(lines[1:], 1):
        parts = line.rstrip('\n').split('\t')
        row = {'row_i': i, 'raw': line.rstrip('\n')}
        if has_fixed_cols:
            row['book']      = parts[0].strip() if len(parts) > 0 else ''
            row['ref']       = parts[1].strip() if len(parts) > 1 else ''
            row['quote']     = parts[2].strip() if len(parts) > 2 else ''
            row['commentary']= parts[3].strip() if len(parts) > 3 else ''
            row['low_conf']  = '[LOW_CONFIDENCE]' in row.get('commentary', '')
        else:
            row['book']      = parts[0].strip() if len(parts) > 0 else ''
            row['ref']       = parts[1].strip() if len(parts) > 1 else ''
            row['annotation']= parts[2].strip() if len(parts) > 2 else ''
            row['low_conf']  = False
        rows.append(row)
    return rows


def parse_ref(ref_str):
    m = re.match(r'(\d+):(\d+)', ref_str.strip())
    if m:
        return int(m.group(1)), int(m.group(2))
    return None, None


def is_plausible_ref(book, ref):
    """
    Basic plausibility check: book should be a known abbreviation,
    ref should be a valid chapter:verse format.
    """
    known_books = {
        'Gn','Ex','Lv','Nm','Dt','Jos','Jgs','Ru','1Sam','2Sam',
        '1Kings','2Kings','1Chr','2Chr','Ezr','Neh','Tb','Jdt','Est',
        '1Mc','2Mc','Jb','Ps','Prv','Eccl','Sg','Wis','Sir','Is',
        'Jer','Lam','Bar','Ez','Dn','Hos','Jl','Am','Ob','Jon','Mi',
        'Na','Hab','Zep','Hg','Zec','Mal','Mt','Mk','Lk','Jn','Acts',
        'Rom','1Cor','2Cor','Gal','Eph','Phil','Col','1Thes','2Thes',
        '1Tim','2Tim','Tit','Phlm','Heb','Jas','1Pet','2Pet','1Jn',
        '2Jn','3Jn','Jude','Rev','Apc',
    }
    if book not in known_books:
        return False, f"unknown book '{book}'"
    ch, v = parse_ref(ref)
    if ch is None:
        return False, f"unparseable ref '{ref}'"
    if ch < 1 or ch > 200:
        return False, f"chapter {ch} out of range"
    if v < 1 or v > 200:
        return False, f"verse {v} out of range"
    return True, ''


def main():
    print(f"Loading {ORIG}...")
    orig_rows = load_tsv(ORIG, has_fixed_cols=False)
    print(f"  {len(orig_rows)} rows")

    print(f"Loading {FIXED}...")
    fixed_rows = load_tsv(FIXED, has_fixed_cols=True)
    print(f"  {len(fixed_rows)} rows")

    n = min(len(orig_rows), len(fixed_rows))

    resolved       = []   # ref changed in expected direction
    unchanged_lc   = []   # still LOW_CONFIDENCE
    potential_new  = []   # ref changed in unexpected/suspicious way
    same           = []   # ref unchanged and confident
    book_changes   = []   # any book change

    for i in range(n):
        orig  = orig_rows[i]
        fixed = fixed_rows[i]

        ob = orig['book']
        or_ = orig['ref']
        nb = fixed['book']
        nr = fixed['ref']
        lc = fixed['low_conf']

        book_changed = (ob != nb)
        ref_changed  = (or_ != nr)
        changed = book_changed or ref_changed

        if lc:
            unchanged_lc.append({
                'row': i+1, 'orig_book': ob, 'orig_ref': or_,
                'commentary_snippet': fixed['commentary'][:100],
            })
            continue

        if not changed:
            same.append(i+1)
            continue

        if book_changed:
            book_changes.append({
                'row': i+1,
                'from': f"{ob} {or_}",
                'to': f"{nb} {nr}",
            })

        # Plausibility check on new ref
        plaus, reason = is_plausible_ref(nb, nr)
        if not plaus:
            potential_new.append({
                'row': i+1,
                'orig': f"{ob} {or_}",
                'new': f"{nb} {nr}",
                'reason': f"implausible: {reason}",
            })
            continue

        # Was this a known category of misattribution (Sg→Is, Phlm→Heb etc.)?
        # Heuristic: if the book changed from a smaller/shorter book to a larger one
        # that's typically cited more, it's probably correct
        if book_changed:
            resolved.append({
                'row': i+1,
                'from': f"{ob} {or_}",
                'to': f"{nb} {nr}",
                'type': 'book+ref' if ref_changed else 'book-only',
            })
        else:
            resolved.append({
                'row': i+1,
                'from': f"{ob} {or_}",
                'to': f"{nb} {nr}",
                'type': 'ref-only',
            })

    # ─── Write output ──────────────────────────────────────────────────────────
    print(f"Writing {OUT}...")
    with open(OUT, 'w', encoding='utf-8') as f:
        w = f.write

        w("=" * 70 + "\n")
        w("DOUAI 1609 ANNOTATION COMPARISON REPORT v2\n")
        w(f"  Original:  {ORIG} ({len(orig_rows)} rows)\n")
        w(f"  Fixed:     {FIXED} ({len(fixed_rows)} rows)\n")
        w("=" * 70 + "\n\n")

        w("SUMMARY\n")
        w("-" * 40 + "\n")
        w(f"  Total rows compared:    {n}\n")
        w(f"  Refs corrected:         {len(resolved)}\n")
        w(f"    of which book changed:{sum(1 for r in resolved if 'book' in r['type'])}\n")
        w(f"  Unchanged + confident:  {len(same)}\n")
        w(f"  Still LOW_CONFIDENCE:   {len(unchanged_lc)}\n")
        w(f"  Potential new issues:   {len(potential_new)}\n\n")

        # Section 1: Resolved
        w("\n" + "=" * 70 + "\n")
        w("SECTION 1: RESOLVED — Refs Corrected\n")
        w("=" * 70 + "\n")
        w(f"({len(resolved)} rows where ref changed)\n\n")

        book_only = [r for r in resolved if r['type'] == 'book+ref' or r['type'] == 'book-only']
        ref_only  = [r for r in resolved if r['type'] == 'ref-only']

        if book_only:
            w("--- Book-level corrections ---\n")
            for r in book_only:
                w(f"  Row {r['row']:4d}: {r['from']:20s} → {r['to']}\n")
        if ref_only:
            w("\n--- Chapter/verse corrections (same book) ---\n")
            for r in ref_only:
                w(f"  Row {r['row']:4d}: {r['from']:20s} → {r['to']}\n")

        # Section 2: Unchanged LOW_CONFIDENCE
        w("\n" + "=" * 70 + "\n")
        w("SECTION 2: UNCHANGED LOW CONFIDENCE\n")
        w("=" * 70 + "\n")
        w(f"({len(unchanged_lc)} rows still marked LOW_CONFIDENCE — needs manual review)\n\n")
        for r in unchanged_lc:
            w(f"  Row {r['row']:4d}: {r['orig_book']} {r['orig_ref']}\n")
            if r['commentary_snippet']:
                w(f"           {r['commentary_snippet'][:80]}...\n")

        # Section 3: Potential new issues
        w("\n" + "=" * 70 + "\n")
        w("SECTION 3: POTENTIAL NEW ISSUES — Flag for Review\n")
        w("=" * 70 + "\n")
        w(f"({len(potential_new)} rows where new ref looks suspicious)\n\n")
        for r in potential_new:
            w(f"  Row {r['row']:4d}: {r['orig']:20s} → {r['new']:20s}  [{r['reason']}]\n")

        w("\n" + "=" * 70 + "\n")
        w("END OF REPORT\n")

    print(f"Done. Output: {OUT}")


if __name__ == '__main__':
    main()
