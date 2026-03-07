#!/usr/bin/env python3
"""
compare-douai-v3.py
Compare douai-1609-clean.bak.tsv (original) against douai-1609-fixed-v3.tsv (v3 output).
Outputs: douai-1609-compare-v3.txt

Columns compared:
  BookAbbrev, Chapter:Verse (from bak)
  vs
  BookAbbrev, Chapter:Verse (from v3)

Also compares VerseQuote split quality.
"""

import os
import sys

HERE    = os.path.dirname(os.path.abspath(__file__))
BAK     = os.path.join(HERE, "douai-1609-clean.bak.tsv")
V3      = os.path.join(HERE, "douai-1609-fixed-v3.tsv")
OUT     = os.path.join(HERE, "douai-1609-compare-v3.txt")


def load_bak(path):
    rows = []
    with open(path, encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i == 0:
                continue
            parts = line.rstrip('\n').split('\t')
            if len(parts) >= 2:
                rows.append({
                    'book': parts[0].strip(),
                    'ref':  parts[1].strip(),
                    'text': parts[2].strip() if len(parts) > 2 else '',
                })
    return rows


def load_v3(path):
    rows = []
    with open(path, encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i == 0:
                continue
            parts = line.rstrip('\n').split('\t')
            if len(parts) >= 2:
                rows.append({
                    'book':  parts[0].strip(),
                    'ref':   parts[1].strip(),
                    'quote': parts[2].strip() if len(parts) > 2 else '',
                    'comm':  parts[3].strip() if len(parts) > 3 else '',
                })
    return rows


def main():
    if not os.path.exists(BAK):
        print(f"ERROR: {BAK} not found", file=sys.stderr)
        sys.exit(1)
    if not os.path.exists(V3):
        print(f"ERROR: {V3} not found", file=sys.stderr)
        sys.exit(1)

    bak_rows = load_bak(BAK)
    v3_rows  = load_v3(V3)

    if len(bak_rows) != len(v3_rows):
        print(f"WARNING: row count mismatch — bak={len(bak_rows)}, v3={len(v3_rows)}", file=sys.stderr)

    total        = min(len(bak_rows), len(v3_rows))
    book_changes = []
    ref_changes  = []
    low_conf     = []
    unchanged    = []

    for i in range(total):
        b = bak_rows[i]
        v = v3_rows[i]
        is_lc = '[LOW_CONFIDENCE]' in v.get('comm', '')

        if b['book'] != v['book']:
            book_changes.append((i+1, b['book'], b['ref'], v['book'], v['ref'], is_lc))
        elif b['ref'] != v['ref']:
            ref_changes.append((i+1, b['book'], b['ref'], v['ref'], is_lc))
        else:
            if is_lc:
                low_conf.append((i+1, b['book'], b['ref']))
            else:
                unchanged.append((i+1, b['book'], b['ref']))

    with open(OUT, 'w', encoding='utf-8') as f:
        w = f.write
        w("=" * 70 + "\n")
        w("DOUAI 1609 COMPARE: bak → v3\n")
        w("=" * 70 + "\n\n")
        w(f"Total rows compared:    {total}\n")
        w(f"Book changed:           {len(book_changes)}\n")
        w(f"  of which LOW_CONF:    {sum(1 for *_, lc in book_changes if lc)}\n")
        w(f"Ref changed (same bk):  {len(ref_changes)}\n")
        w(f"  of which LOW_CONF:    {sum(1 for *_, lc in ref_changes if lc)}\n")
        w(f"Unchanged (confident):  {len(unchanged)}\n")
        w(f"Unchanged (LOW_CONF):   {len(low_conf)}\n\n")

        w("=" * 70 + "\n")
        w("BOOK-LEVEL CHANGES\n")
        w("=" * 70 + "\n")
        w(f"({len(book_changes)} rows)\n\n")
        for row_i, ob, or_, nb, nr, lc in book_changes:
            flag = ' [LOW_CONF]' if lc else ''
            w(f"  Row {row_i:4d}: {ob:8s} {or_:8s} → {nb:8s} {nr:8s}{flag}\n")

        w("\n" + "=" * 70 + "\n")
        w("CHAPTER/VERSE CHANGES (SAME BOOK)\n")
        w("=" * 70 + "\n")
        w(f"({len(ref_changes)} rows)\n\n")
        for row_i, ob, or_, nr, lc in ref_changes:
            flag = ' [LOW_CONF]' if lc else ''
            w(f"  Row {row_i:4d}: {ob:8s} {or_:8s} → {nr:8s}{flag}\n")

        w("\n" + "=" * 70 + "\n")
        w("UNCHANGED / LOW_CONFIDENCE\n")
        w("=" * 70 + "\n")
        w(f"({len(low_conf)} rows kept at original ref due to LOW_CONFIDENCE)\n\n")
        for row_i, ob, or_ in low_conf:
            w(f"  Row {row_i:4d}: {ob:8s} {or_:8s}\n")

    print(f"Written: {OUT}")
    print(f"  Book changes:          {len(book_changes)}")
    print(f"  Ref changes (same bk): {len(ref_changes)}")
    print(f"  Unchanged confident:   {len(unchanged)}")
    print(f"  Unchanged LOW_CONF:    {len(low_conf)}")


if __name__ == '__main__':
    main()
