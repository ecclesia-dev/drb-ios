#!/usr/bin/env python3
"""
scrape-1609.py  —  saint-dismas source (Source #1)
Parse locally-mirrored saint-dismas PDFs into TSV.
Reads from: sources/saint-dismas/{OT,NT}/[Book]/chapter-NN.pdf
Output:     drb-1609-saint-dismas.tsv
            (BookAbbrev TAB Chapter TAB Verse TAB VerseText_1609)
Run mirror-sources.py first.
"""

import os
import re
import sys
import subprocess
from collections import Counter

HERE   = os.path.dirname(os.path.abspath(__file__))
SD_DIR = os.path.join(HERE, "sources", "saint-dismas")
OUTPUT = os.path.join(HERE, "drb-1609-saint-dismas.tsv")

# (abbrev, testament, folder_name, single_pdf_name_or_None)
BOOKS = [
    # OT
    ("Gn",     "OT", "Genesis",              None),
    ("Ex",     "OT", "Exodus",               None),
    ("Lv",     "OT", "Leviticus",            None),
    ("Nm",     "OT", "Numbers",              None),
    ("Dt",     "OT", "Deuteronomy",          None),
    ("Jos",    "OT", "Joshua",               None),
    ("Jgs",    "OT", "Judges",               None),
    ("Ru",     "OT", "Ruth",                 None),
    ("1Sam",   "OT", "One-Kings",            None),
    ("2Sam",   "OT", "Two-Kings",            None),
    ("1Kings", "OT", "Three-Kings",          None),
    ("2Kings", "OT", "Four-Kings",           None),
    ("1Chr",   "OT", "One-Paralipomenon",    None),
    ("2Chr",   "OT", "Two-Paralipomenon",    None),
    ("Ezr",    "OT", "One-Esdras",           None),
    ("Neh",    "OT", "Nehemias",             None),
    ("Tb",     "OT", "Tobias",               None),
    ("Jdt",    "OT", "Judith",               None),
    ("Est",    "OT", "Esther",               None),
    ("Jb",     "OT", "Job",                  None),
    ("Prv",    "OT", "Proverbs",             None),
    ("Eccl",   "OT", "Ecclesiastes",         None),
    ("Sg",     "OT", "Canticle",             None),
    ("Wis",    "OT", "Wisdom",               None),
    # NT
    ("Mt",     "NT", "Matthew",              None),
    ("Mk",     "NT", "Mark",                 None),
    ("Lk",     "NT", "Luke",                 None),
    ("Jn",     "NT", "John",                 None),
    ("Acts",   "NT", "Acts",                 None),
    ("Rom",    "NT", "Romans",               None),
    ("1Cor",   "NT", "One-Corinthians",      None),
    ("2Cor",   "NT", "Two-Corinthians",      None),
    ("Gal",    "NT", "Galatians",            None),
    ("Eph",    "NT", "Ephesians",            None),
    ("Phil",   "NT", "Philippians",          None),
    ("Col",    "NT", "Colossians",           None),
    ("1Thes",  "NT", "One-Thessalonians",    None),
    ("2Thes",  "NT", "Two-Thessalonians",    None),
    ("1Tim",   "NT", "One-Timothy",          None),
    ("2Tim",   "NT", "Two-Timothy",          None),
    ("Tit",    "NT", "Titus",                None),
    ("Phlm",   "NT", "Philemon",             "chapter.pdf"),
    ("Heb",    "NT", "Hebrews",              None),
    ("Jas",    "NT", "James",                None),
    ("1Pet",   "NT", "One-Peter",            None),
    ("2Pet",   "NT", "Two-Peter",            None),
    ("1Jn",    "NT", "One-John",             None),
    ("2Jn",    "NT", "Two-John",             "chapter.pdf"),
    ("3Jn",    "NT", "Three-John",           "chapter.pdf"),
    ("Jude",   "NT", "Jude",                 "chapter.pdf"),
    ("Rev",    "NT", "Apocalypse",           None),
]


def pdf_to_text(pdf_path):
    try:
        r = subprocess.run(['pdftotext', pdf_path, '-'],
                           capture_output=True, text=True, timeout=30)
        return r.stdout if r.returncode == 0 else ''
    except Exception:
        return ''


def clean_pdf_text(text):
    lines = text.split('\n')
    out = []
    for line in lines:
        s = line.strip()
        if re.match(r'^\d{1,4}$', s):          # page numbers
            continue
        if len(s) < 30:                          # short marginal refs
            if re.match(r'^([A-Z][a-z]{0,6}\.?\s+)*[\d,.\s]+\.?$', s):
                continue
            if re.match(r'^[A-Z][a-z]{0,5}\.?\s*\d*\.?$', s):
                continue
        out.append(s)
    return '\n'.join(out)


def extract_verse_region(text):
    ann = re.search(r'\n\s*Annotations?\s*\n', text, re.IGNORECASE)
    if ann:
        text = text[:ann.start()]
    # Remove running chapter headers
    text = re.sub(r'(?:Chapter|Psalme)\s+\d+\s*\n', '\n', text, flags=re.IGNORECASE)
    return text


def parse_verses(content):
    content = re.sub(r'[♪♦†‡§¶⋮⊕✟\u2666\u266a\u2022\u25aa\u00b6]', '', content)
    content = re.sub(r'\b[a-z]\)', '', content)
    content = re.sub(r'\s+', ' ', content).strip()
    # Long-s normalization not needed here — keep raw 1609 text for output
    verse_positions = []
    for m in re.finditer(r'(?<![.,\d])(?<!\w)(\d{1,3})(?!\d)(?![.,])\s+', content):
        n = int(m.group(1))
        if 1 <= n <= 200:
            rest = m.end()
            if rest < len(content) and content[rest].isalpha():
                verse_positions.append((m.start(), m.end(), n))

    if not verse_positions:
        return [(1, content.strip())]

    results = []
    first_vnum = verse_positions[0][2]
    pre_text = content[:verse_positions[0][0]].strip()

    if first_vnum > 1 and pre_text:
        pre_text = re.sub(r'^([A-Z])\s+([a-z])', r'\1\2', pre_text)
        results.append((1, pre_text))

    for i, (start, end, vnum) in enumerate(verse_positions):
        next_start = verse_positions[i+1][0] if i+1 < len(verse_positions) else len(content)
        vtxt = content[end:next_start].strip()
        if vtxt:
            results.append((vnum, vtxt))

    return results


def get_chapter_pdfs(book_dir, single_pdf):
    """Return sorted list of (chapter_num, pdf_path)."""
    if single_pdf:
        p = os.path.join(book_dir, single_pdf)
        return [(1, p)] if os.path.exists(p) else []

    entries = []
    if not os.path.isdir(book_dir):
        return entries
    for fname in os.listdir(book_dir):
        if not fname.endswith('.pdf'):
            continue
        m = re.search(r'(\d+)', fname)
        if m:
            entries.append((int(m.group(1)), os.path.join(book_dir, fname)))
    entries.sort()
    return entries


def main():
    all_rows = []
    total_books = len(BOOKS)

    for bi, (abbrev, testament, folder, single_pdf) in enumerate(BOOKS):
        book_dir = os.path.join(SD_DIR, testament, folder)
        chapters = get_chapter_pdfs(book_dir, single_pdf)

        if not chapters:
            print(f"[{bi+1}/{total_books}] {abbrev:6s} ({folder}): NO PDFS", file=sys.stderr)
            continue

        book_rows = []
        for chap_num, pdf_path in chapters:
            raw = pdf_to_text(pdf_path)
            if not raw.strip():
                continue
            cleaned = clean_pdf_text(raw)
            region  = extract_verse_region(cleaned)
            stream  = re.sub(r'\n', ' ', region)
            stream  = re.sub(r'\s+', ' ', stream).strip()
            verses  = parse_verses(stream)
            for vnum, vtxt in verses:
                vtxt = vtxt.replace('\t', ' ').strip()
                if vtxt:
                    book_rows.append((abbrev, chap_num, vnum, vtxt))

        all_rows.extend(book_rows)
        print(f"[{bi+1}/{total_books}] {abbrev:6s}: {len(chapters):3d} ch → {len(book_rows):5d} verses")

    # Deduplicate (keep first occurrence per key)
    seen, final = set(), []
    for row in all_rows:
        key = (row[0], row[1], row[2])
        if key not in seen:
            seen.add(key)
            final.append(row)

    print(f"\nTotal unique verses: {len(final)}")
    print(f"Writing {OUTPUT} ...")
    with open(OUTPUT, 'w', encoding='utf-8') as f:
        f.write("BookAbbrev\tChapter\tVerse\tVerseText_1609\n")
        for abbrev, ch, v, txt in final:
            f.write(f"{abbrev}\t{ch}\t{v}\t{txt}\n")

    counts = Counter(r[0] for r in final)
    print("\nVerses per book:")
    for abbrev, _, _, _ in BOOKS:
        if counts.get(abbrev, 0):
            print(f"  {abbrev:8s}: {counts[abbrev]}")
    print("Done.")


if __name__ == '__main__':
    main()
