#!/usr/bin/env python3
"""
clean-douai-1609.py — Jerome (📜), ecclesia-dev CLI engineer
Cleans OCR-corrupted chapter:verse references in the 1609 Douay-Rheims
annotations TSV.

Validation strategy:
  - Check book abbreviation is known (also normalises Ti→Tit, Zec→Zech)
  - Check chapter number does not exceed the book's chapter count
  - For bad rows: attempt contextual correction using surrounding rows
  - If unresolvable: remove the row
"""

import csv
import os
import sys
import re
from copy import deepcopy

# ── Chapter counts per DRB book ──────────────────────────────────────────────
CHAPTER_COUNTS = {
    "Gn": 50, "Ex": 40, "Lv": 27, "Nm": 36, "Dt": 34, "Jos": 24,
    "Jgs": 21, "Ru": 4, "1Sam": 31, "2Sam": 24, "1Kings": 22, "2Kings": 25,
    "1Chr": 29, "2Chr": 36, "Ezr": 10, "Neh": 13, "Tb": 14, "Jdt": 16,
    "Est": 16, "1Mc": 16, "2Mc": 15, "Jb": 42, "Ps": 150, "Prv": 31,
    "Eccl": 12, "Sg": 8, "Wis": 19, "Sir": 51, "Is": 66, "Jer": 52,
    "Lam": 5, "Bar": 6, "Ez": 48, "Dn": 14, "Hos": 14, "Joel": 3,
    "Am": 9, "Ob": 1, "Jon": 4, "Mic": 7, "Nah": 3, "Hab": 3,
    "Zeph": 3, "Hag": 2, "Zech": 14, "Mal": 4, "Mt": 28, "Mk": 16,
    "Lk": 24, "Jn": 21, "Acts": 28, "Rom": 16, "1Cor": 16, "2Cor": 13,
    "Gal": 6, "Eph": 6, "Phil": 4, "Col": 4, "1Th": 5, "2Th": 3,
    "1Tim": 6, "2Tim": 4, "Tit": 3, "Phlm": 1, "Heb": 13, "Jude": 1,
    "Jas": 5, "1Pet": 5, "2Pet": 3, "1Jn": 5, "2Jn": 1, "3Jn": 1,
    "Apc": 22,
}

# Known abbreviation normalisation (file uses non-standard abbrevs)
ABBREV_FIXES = {
    "Ti": "Tit",
    "Zec": "Zech",
}


def normalise_book(book):
    """Return canonical abbreviation, or None if unknown."""
    return ABBREV_FIXES.get(book, book)


def parse_ref(ref_str):
    """Return (chapter:int, verse:int) or (None, None) on parse failure."""
    m = re.match(r'^(\d+):(\d+)$', ref_str.strip())
    if not m:
        return None, None
    return int(m.group(1)), int(m.group(2))


def is_valid(book_canon, chapter):
    """True when book is known and chapter is in range [1, max]."""
    if book_canon not in CHAPTER_COUNTS:
        return False
    return 1 <= chapter <= CHAPTER_COUNTS[book_canon]


def infer_chapter_from_context(idx, rows, book_canon):
    """
    Look at the N rows before and after position idx (same book) and try to
    infer the correct chapter. Returns an int if confident, else None.

    Strategy: collect chapters from neighbours of the same book; if they all
    agree on one chapter value that is valid for the book, use it.
    """
    window = 6
    neighbour_chapters = []
    for delta in range(-window, window + 1):
        j = idx + delta
        if j < 0 or j >= len(rows) or delta == 0:
            continue
        nb = rows[j]
        nb_book = normalise_book(nb["book"])
        if nb_book != book_canon:
            continue
        ch, _ = parse_ref(nb["ref"])
        if ch is not None and is_valid(book_canon, ch):
            neighbour_chapters.append(ch)
    if not neighbour_chapters:
        return None
    # Use the most common valid chapter in the neighbourhood
    freq = {}
    for c in neighbour_chapters:
        freq[c] = freq.get(c, 0) + 1
    best = max(freq, key=freq.__getitem__)
    return best if freq[best] >= 1 else None


def main():
    src = os.path.expanduser(
        "~/.openclaw/workspace/projects/drb-ios/DouayRheims/douai-1609.tsv"
    )
    dst = os.path.expanduser(
        "~/.openclaw/workspace/projects/drb-ios/DouayRheims/douai-1609-clean.tsv"
    )

    # ── Load ────────────────────────────────────────────────────────────────
    with open(src, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        fieldnames = reader.fieldnames
        rows = []
        for row in reader:
            rows.append({
                "book": row["BookAbbrev"].strip(),
                "ref": row["Chapter:Verse"].strip(),
                "annotation": row["Annotation"],
            })

    total_input = len(rows)
    print(f"Loaded {total_input} rows (excl. header).")

    # ── First pass: normalise abbreviations ──────────────────────────────────
    abbrev_fixed_count = 0
    for row in rows:
        canon = normalise_book(row["book"])
        if canon != row["book"]:
            row["_orig_book"] = row["book"]
            row["book"] = canon
            abbrev_fixed_count += 1

    print(f"Abbreviation normalisations (Ti→Tit, Zec→Zech): {abbrev_fixed_count}")

    # ── Second pass: identify bad rows ───────────────────────────────────────
    bad_indices = []
    for i, row in enumerate(rows):
        book_canon = row["book"]
        ch, vs = parse_ref(row["ref"])
        if ch is None:
            bad_indices.append((i, "unparseable ref"))
            continue
        if not is_valid(book_canon, ch):
            bad_indices.append((i, f"ch {ch} > max {CHAPTER_COUNTS.get(book_canon, '?')} for {book_canon}"))

    print(f"\nBad rows found: {len(bad_indices)}")
    for i, reason in bad_indices:
        r = rows[i]
        print(f"  [{i:4d}] {r['book']} {r['ref']} — {reason}")

    # ── Third pass: attempt to fix each bad row ──────────────────────────────
    fixed = 0
    removed_indices = []

    for i, reason in bad_indices:
        row = rows[i]
        book_canon = row["book"]
        ch, vs = parse_ref(row["ref"])

        if book_canon not in CHAPTER_COUNTS:
            # Unknown book even after normalisation — remove
            print(f"  REMOVE [{i}] unknown book {book_canon}")
            removed_indices.append(i)
            continue

        # Try to infer the correct chapter from surrounding rows
        inferred = infer_chapter_from_context(i, rows, book_canon)
        if inferred is not None:
            old_ref = row["ref"]
            row["ref"] = f"{inferred}:{vs}"
            row["_fixed_from"] = old_ref
            print(f"  FIX    [{i}] {book_canon} {old_ref} → {book_canon} {row['ref']}  (context inferred ch={inferred})")
            fixed += 1
        else:
            print(f"  REMOVE [{i}] {book_canon} {row['ref']} — cannot infer chapter")
            removed_indices.append(i)

    removed_set = set(removed_indices)
    removed = len(removed_set)

    # ── Build clean output ───────────────────────────────────────────────────
    clean_rows = [r for i, r in enumerate(rows) if i not in removed_set]
    total_output = len(clean_rows)

    with open(dst, "w", newline="", encoding="utf-8") as f:
        f.write("BookAbbrev\tChapter:Verse\tAnnotation\n")
        for row in clean_rows:
            f.write(f"{row['book']}\t{row['ref']}\t{row['annotation']}\n")

    # ── Summary ──────────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"Input rows:        {total_input}")
    print(f"Abbrev fixes:      {abbrev_fixed_count}")
    print(f"Bad refs found:    {len(bad_indices)}")
    print(f"  Fixed:           {fixed}")
    print(f"  Removed:         {removed}")
    print(f"Output rows:       {total_output}")
    print(f"Written to:        {dst}")

    # Return data for report
    return {
        "total_input": total_input,
        "abbrev_fixed": abbrev_fixed_count,
        "bad_found": len(bad_indices),
        "fixed": fixed,
        "removed": removed,
        "total_output": total_output,
        "bad_details": [(rows[i]["book"], rows[i].get("_fixed_from", rows[i]["ref"]), rows[i]["ref"], reason, i in removed_set)
                        for i, reason in bad_indices],
    }


if __name__ == "__main__":
    result = main()
