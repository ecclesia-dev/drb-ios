#!/usr/bin/env python3
"""
merge-v9.py — Merge Douai 1609 v8 TSV with annotations TSVs into v9
Jerome [CLI agent]
"""

import csv
import os
from collections import defaultdict

# Canonical Catholic Bible book order (Douay-Rheims / Vulgate order)
BOOK_ORDER = [
    # Pentateuch
    "Gn", "Ex", "Lv", "Nm", "Dt",
    # Historical
    "Jos", "Jgs", "Ru", "1Sm", "2Sm", "1Kgs", "2Kgs",
    "1Chr", "2Chr", "Ezr", "Neh", "Tb", "Jdt", "Est", "1Mc", "2Mc",
    # Wisdom
    "Jb", "Ps", "Prv", "Eccl", "Sg", "Wis", "Sir",
    # Prophets
    "Is", "Jer", "Lam", "Bar", "Ez", "Dn",
    # Minor Prophets
    "Hos", "Jl", "Am", "Ob", "Jon", "Mi", "Na", "Hb", "Zep", "Hg", "Zec", "Mal",
    # NT
    "Mt", "Mk", "Lk", "Jn", "Acts", "Rom",
    "1Cor", "2Cor", "Gal", "Eph", "Phil", "Col",
    "1Thes", "2Thes", "1Tm", "2Tm", "Ti", "Phlm",
    "Heb", "Jas", "1Pt", "2Pt", "1Jn", "2Jn", "3Jn", "Jude", "Rv",
]

BOOK_INDEX = {book: i for i, book in enumerate(BOOK_ORDER)}

def book_sort_key(book_abbrev):
    return BOOK_INDEX.get(book_abbrev, 999)

def cv_sort_key(chapter_verse):
    """Parse 'Chapter:Verse' or 'Chapter' into sortable (chapter, verse) tuple."""
    try:
        parts = chapter_verse.split(":")
        ch = int(parts[0])
        vs = int(parts[1]) if len(parts) > 1 else 0
        return (ch, vs)
    except (ValueError, IndexError):
        return (9999, 9999)

def row_sort_key(row):
    return (book_sort_key(row["BookAbbrev"]), cv_sort_key(row["Chapter:Verse"]))

def load_v8(path):
    """Load v8 TSV. Returns dict keyed by (BookAbbrev, Chapter:Verse) -> list of rows."""
    rows = {}
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            key = (row["BookAbbrev"], row["Chapter:Verse"])
            if key not in rows:
                rows[key] = row
            # If duplicate key in v8, keep the first (already reviewed)
    print(f"Loaded v8: {len(rows)} unique keys from {path}")
    return rows

def load_annotations(path):
    """Load annotation TSV (BookAbbrev, Chapter:Verse, Annotation, Source)."""
    rows = {}
    if not os.path.exists(path):
        print(f"  SKIP (not found): {path}")
        return rows
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            key = (row["BookAbbrev"], row["Chapter:Verse"])
            if key not in rows:
                rows[key] = row
    print(f"  Loaded {len(rows)} unique keys from {os.path.basename(path)}")
    return rows

BASE = os.path.expanduser("~/projects")

V8_PATH = f"{BASE}/drb-ios/DouayRheims/douai-1609-fixed-v8.tsv"
V9_PATH = f"{BASE}/drb-ios/DouayRheims/douai-1609-fixed-v9.tsv"

ANNOTATION_TSVS = [
    f"{BASE}/drb/douai-1609-annotations.tsv",
    f"{BASE}/drb/douai-1609-pentateuch.tsv",
    f"{BASE}/drb/douai-1609-prophets.tsv",
    f"{BASE}/drb/douai-1609-wisdom.tsv",
    f"{BASE}/drb/douai-1609-historical.tsv",
    f"{BASE}/drb/douai-1609-minor-prophets.tsv",
]

print("=" * 60)
print("Douai 1609 v8 → v9 Merge")
print("=" * 60)

# 1. Load v8
v8_rows = load_v8(V8_PATH)

# 2. Load all annotation TSVs, merge by key (first-seen wins)
print("\nLoading annotation TSVs:")
all_annotations = {}
for tsv_path in ANNOTATION_TSVS:
    ann = load_annotations(tsv_path)
    for key, row in ann.items():
        if key not in all_annotations:
            all_annotations[key] = row

print(f"\nTotal unique annotation keys: {len(all_annotations)}")

# 3. Build merged output
# Start with v8 rows (all kept as-is)
merged = dict(v8_rows)  # key -> row dict with v8 schema

# Add annotation rows not in v8
added_count = 0
for key, ann_row in all_annotations.items():
    if key not in merged:
        merged[key] = {
            "BookAbbrev": ann_row["BookAbbrev"],
            "Chapter:Verse": ann_row["Chapter:Verse"],
            "VerseQuote": "",
            "Commentary": ann_row["Annotation"],
            "Status": "APPROVED",
        }
        added_count += 1

print(f"\nRows from v8 (kept as-is): {len(v8_rows)}")
print(f"Rows added from annotations (new keys only): {added_count}")
print(f"Total merged rows: {len(merged)}")

# 4. Sort
sorted_rows = sorted(merged.values(), key=row_sort_key)

# 5. Write v9
with open(V9_PATH, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["BookAbbrev", "Chapter:Verse", "VerseQuote", "Commentary", "Status"],
                            delimiter="\t", lineterminator="\n")
    writer.writeheader()
    writer.writerows(sorted_rows)

print(f"\nWrote v9: {V9_PATH}")

# 6. Stats: row count and unique chapter count per book
print("\n" + "=" * 60)
print("Row count and unique chapters per book:")
print("=" * 60)
book_chapters = defaultdict(set)
book_rows = defaultdict(int)
for row in sorted_rows:
    book = row["BookAbbrev"]
    cv = row["Chapter:Verse"]
    book_rows[book] += 1
    ch = cv.split(":")[0] if ":" in cv else cv
    book_chapters[book].add(ch)

# Print in canonical order
print(f"{'Book':<10} {'Rows':>6} {'Chapters':>10}")
print("-" * 30)
for book in BOOK_ORDER:
    if book in book_rows:
        print(f"{book:<10} {book_rows[book]:>6} {len(book_chapters[book]):>10}")

# Top 10 by chapter count
print("\nTop 10 books by chapter count:")
top10 = sorted(book_chapters.items(), key=lambda x: len(x[1]), reverse=True)[:10]
for i, (book, chaps) in enumerate(top10, 1):
    print(f"  {i:2}. {book:<8} {len(chaps)} chapters, {book_rows[book]} rows")

# 7. Spot-checks
print("\n" + "=" * 60)
print("Spot-checks:")
print("=" * 60)
spot_checks = [
    ("Is", "1:1"),
    ("Jer", "1:1"),
    ("Gn", "1:1"),
]
for book, cv in spot_checks:
    key = (book, cv)
    if key in merged:
        row = merged[key]
        commentary_preview = (row.get("Commentary") or "")[:80].replace("\n", " ")
        print(f"  ✓ {book} {cv}: {commentary_preview}...")
    else:
        print(f"  ✗ {book} {cv}: NOT FOUND")

print("\nDone.")
