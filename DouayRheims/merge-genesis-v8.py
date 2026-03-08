#!/usr/bin/env python3
"""
merge-genesis-v8.py
Merges Genesis ch1-21 annotations into the main Douai 1609 TSV.
Author: Jerome [CLI agent]
"""

import csv
import os

GENESIS_FILE = os.path.join(os.path.dirname(__file__), "douai-1609-genesis-ch1-21.tsv")
V7_FILE = os.path.join(os.path.dirname(__file__), "douai-1609-fixed-v7.tsv")
V8_FILE = os.path.join(os.path.dirname(__file__), "douai-1609-fixed-v8.tsv")

V7_FIELDS = ["BookAbbrev", "Chapter:Verse", "VerseQuote", "Commentary", "Status"]


def parse_chapter(cv):
    """Return int chapter number from 'chapter:verse' string."""
    try:
        return int(cv.split(":")[0])
    except (ValueError, IndexError):
        return 0


def main():
    # --- Read genesis-ch1-21.tsv and convert to v7 schema ---
    genesis_rows = []
    with open(GENESIS_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            genesis_rows.append({
                "BookAbbrev": row["Book"],
                "Chapter:Verse": row["Verse"],
                "VerseQuote": row["Quote"],
                "Commentary": row["Commentary"],
                "Status": row["Status"],
            })

    print(f"Genesis ch1-21 rows read: {len(genesis_rows)}")

    # Collect the Chapter:Verse keys from genesis file (for overlap removal)
    genesis_cv_set = set(r["Chapter:Verse"] for r in genesis_rows)

    # --- Read douai-1609-fixed-v7.tsv ---
    v7_rows = []
    with open(V7_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            v7_rows.append(dict(row))

    print(f"v7 total rows: {len(v7_rows)}")

    # Separate Genesis rows from everything else
    v7_genesis = [r for r in v7_rows if r["BookAbbrev"] == "Gn"]
    v7_other = [r for r in v7_rows if r["BookAbbrev"] != "Gn"]

    print(f"v7 Genesis rows: {len(v7_genesis)}")
    print(f"v7 non-Genesis rows: {len(v7_other)}")

    # Remove overlapping Genesis rows (those covered by ch1-21 file)
    v7_genesis_non_overlap = [
        r for r in v7_genesis if r["Chapter:Verse"] not in genesis_cv_set
    ]
    removed = len(v7_genesis) - len(v7_genesis_non_overlap)
    print(f"v7 Genesis rows removed (overlap with ch1-21): {removed}")

    # Separate ch22+ Genesis rows (non-overlap)
    v7_genesis_ch22plus = [
        r for r in v7_genesis_non_overlap
        if parse_chapter(r["Chapter:Verse"]) >= 22
    ]
    # Also keep any non-overlap rows that might be ch1-21 but not in genesis file
    v7_genesis_remaining = [
        r for r in v7_genesis_non_overlap
        if parse_chapter(r["Chapter:Verse"]) < 22
    ]
    print(f"v7 Genesis ch22+ rows: {len(v7_genesis_ch22plus)}")
    print(f"v7 Genesis ch<22 non-overlap rows kept: {len(v7_genesis_remaining)}")

    # --- Build merged output ---
    # Order: genesis_rows (ch1-21) + v7_genesis_remaining (any extra ch<22) +
    #        v7_genesis_ch22plus (ch22+) + all other books in original order
    merged = genesis_rows + v7_genesis_remaining + v7_genesis_ch22plus + v7_other

    print(f"v8 total rows: {len(merged)}")

    # --- Write v8 ---
    with open(V8_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=V7_FIELDS, delimiter="\t")
        writer.writeheader()
        writer.writerows(merged)

    print(f"Written: {V8_FILE}")

    # --- Spot-checks ---
    gn_1_1 = [r for r in merged if r["BookAbbrev"] == "Gn" and r["Chapter:Verse"] == "1:1"]
    gn_22_13 = [r for r in merged if r["BookAbbrev"] == "Gn" and r["Chapter:Verse"] == "22:13"]
    print(f"\nSpot-check Gn 1:1  — {len(gn_1_1)} row(s) found {'✓' if gn_1_1 else '✗ MISSING'}")
    print(f"Spot-check Gn 22:13 — {len(gn_22_13)} row(s) found {'✓' if gn_22_13 else '✗ MISSING'}")

    # Genesis chapters present
    gn_chapters = sorted(set(parse_chapter(r["Chapter:Verse"]) for r in merged if r["BookAbbrev"] == "Gn"))
    print(f"\nGenesis chapters present: {gn_chapters}")


if __name__ == "__main__":
    main()
