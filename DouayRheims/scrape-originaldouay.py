#!/usr/bin/env python3
"""
scrape-originaldouay.py  —  originaldouayrheims.com source (Source #2)
Parse locally-mirrored HTML pages into TSV.
Reads from: sources/originaldouay/
Output:     drb-1609-originaldouay.tsv
"""

import os
import re
import sys
from collections import Counter

BASE_ODR = "https://originaldouayrheims.com"
HERE     = os.path.dirname(os.path.abspath(__file__))
ODR_DIR  = os.path.join(HERE, "sources", "originaldouay")
OUTPUT   = os.path.join(HERE, "drb-1609-originaldouay.tsv")

# (abbrev, odr_path)  — odr_path as used in mirror-sources.py ODR_BOOKS
BOOKS = [
    ("Gn",    "/old/genesis"),
    ("Ru",    "/old/ruth"),
    ("Ps",    "/old/psalms"),
    ("Wis",   "/old/wisdom"),
    ("Lam",   "/old/lamentations"),
    ("Bar",   "/old/baruch"),
    ("Dn",    "/old/daniel"),
    ("Jon",   "/old/jonas"),
    ("Zep",   "/old/sophonias"),
    ("Sir",   "/old/ecclesiasticus"),
    ("Mt",    "/matthew"),
    ("Mk",    "/mark"),
    ("Lk",    "/luke"),
    ("Jn",    "/john"),
    ("Acts",  "/acts"),
    ("Rom",   "/romans"),
    ("Gal",   "/galatians"),
    ("Eph",   "/ephesians"),
    ("Phil",  "/philippians"),
    ("Col",   "/colossians"),
    ("Tit",   "/titus"),
    ("Phlm",  "/philemon"),
    ("Heb",   "/hebrews"),
    ("Jas",   "/james"),
    ("Jude",  "/jude"),
    ("Rev",   "/revelations"),
    ("1Cor",  "/I Corinthians.html"),
    ("2Cor",  "/II Corinthians.html"),
    ("1Thes", "/I Thessalonians.html"),
    ("2Thes", "/II Thessalonians.html"),
    ("1Tim",  "/I Timothee.html"),
    ("2Tim",  "/II Timothee.html"),
    ("1Pet",  "/I Peter.html"),
    ("2Pet",  "/II Peter.html"),
    ("1Jn",   "/I John.html"),
    ("2Jn",   "/II John.html"),
    ("3Jn",   "/III John.html"),
]


def url_to_local_stem(url_path):
    """Convert URL path to local filename stem (mirrors mirror-sources.py logic)."""
    path = url_path.lstrip('/')
    path = path.replace('/', '--').replace(' ', '_').replace('.html', '')
    return path if path else 'index'


def path_to_index_stem(odr_path):
    """Return the stem used for the index file of a book."""
    # mirror-sources.py used (stem, path) where stem is the ODR_BOOKS[0] value
    # We need to reconstruct: for /old/genesis, stem = "old-genesis"
    # For /matthew, stem = "matthew"
    # For /I Corinthians.html, stem = "I-Corinthians"
    path = odr_path.lstrip('/')
    path = path.replace('.html', '')
    # Replace / with -
    path = path.replace('/', '-')
    # Replace spaces with -
    path = path.replace(' ', '-')
    return path


def load_chapter_pages(odr_path):
    """
    Return ordered list of (chap_num, html_content) for all chapters of a book.
    """
    index_url = BASE_ODR + odr_path
    index_stem = path_to_index_stem(odr_path)
    index_file = os.path.join(ODR_DIR, f"{index_stem}--index.html")

    if not os.path.exists(index_file):
        print(f"  WARN: missing {index_file}", file=sys.stderr)
        return []

    with open(index_file, encoding='utf-8', errors='replace') as f:
        index_html = f.read()

    # Find chapter links from h3 block
    h3_m = re.search(r'<h3>(.*?)</h3>', index_html, re.DOTALL | re.IGNORECASE)
    if not h3_m:
        # Single-page book (no h3 chapter nav)
        return [(1, index_html)]

    hrefs = re.findall(r'href=["\']([^"\']+)["\']', h3_m.group(1), re.IGNORECASE)
    chapter_hrefs = []
    for href in hrefs:
        href = href.strip()
        if not href or href.startswith('#') or href.startswith('javascript'):
            continue
        if re.search(r'(sum|arg|intro)\b', href, re.IGNORECASE):
            continue
        chapter_hrefs.append(href)

    if not chapter_hrefs:
        return [(1, index_html)]

    pages = []
    for chap_idx, href in enumerate(chapter_hrefs):
        chap_num = chap_idx + 1

        # Resolve href → full URL path
        if href.startswith('http'):
            full_path = href.replace(BASE_ODR, '')
        elif href.startswith('/'):
            full_path = href
        else:
            # Relative — resolve against index URL's directory
            base_dir = odr_path.rsplit('/', 1)[0]
            full_path = base_dir + '/' + href

        # Check if this is the index URL itself
        full_path_clean = full_path.split('?')[0]  # strip query
        if full_path_clean == odr_path or full_path_clean == odr_path.rstrip('/'):
            # This chapter IS the index page
            pages.append((chap_num, index_html))
            continue

        # Map to local file
        local_stem = url_to_local_stem(full_path_clean)
        local_file = os.path.join(ODR_DIR, f"{local_stem}.html")

        if not os.path.exists(local_file):
            # Try alternate: the file might be stored differently
            # e.g., old/genesis/genesis2 → "old--genesis--genesis2"
            # already handled by url_to_local_stem, but double-check
            print(f"  WARN: missing {local_file} (href={href})", file=sys.stderr)
            continue

        with open(local_file, encoding='utf-8', errors='replace') as f:
            pages.append((chap_num, f.read()))

    return pages


def strip_tags(html_frag):
    text = re.sub(r'<[^>]+>', ' ', html_frag)
    for ent, rep in [('&nbsp;', ' '), ('&amp;', '&'), ('&lt;', '<'),
                     ('&gt;', '>'), ('&apos;', "'"), ('&quot;', '"')]:
        text = text.replace(ent, rep)
    text = re.sub(r'&[a-zA-Z#0-9]+;', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()


def parse_chapter_html(html):
    """Extract (verse_num, verse_text) from chapter page HTML."""
    body_m = re.search(r'<body[^>]*>(.*)', html, re.DOTALL | re.IGNORECASE)
    body = body_m.group(1) if body_m else html
    body = re.sub(r'<nav\b.*?</nav>', '', body, flags=re.DOTALL | re.IGNORECASE)

    # Verse tags: <b>N. </b> or <b>N </b> or <b>N.</b>
    verse_re = re.compile(r'<b>\s*(\d{1,3})\.?\s*</b>', re.IGNORECASE)
    matches = list(verse_re.finditer(body))
    if not matches:
        return []

    verses = []
    for i, m in enumerate(matches):
        vnum = int(m.group(1))
        if not (1 <= vnum <= 200):
            continue
        start = m.end()
        end = matches[i+1].start() if i+1 < len(matches) else len(body)
        text = strip_tags(body[start:end]).strip()
        text = re.sub(r'^\d+\.?\s*', '', text)
        if len(text) > 2:
            verses.append((vnum, text))
    return verses


def scrape_book(abbrev, odr_path):
    pages = load_chapter_pages(odr_path)
    if not pages:
        return []

    rows = []
    for chap_num, html in pages:
        verses = parse_chapter_html(html)
        for vnum, vtxt in verses:
            vtxt = vtxt.replace('\t', ' ').replace('\n', ' ').strip()
            if vtxt:
                rows.append((abbrev, chap_num, vnum, vtxt))
    return rows


def main():
    all_rows = []
    for abbrev, odr_path in BOOKS:
        rows = scrape_book(abbrev, odr_path)
        all_rows.extend(rows)
        print(f"  {abbrev:6s}: {len(rows):5d} verses")

    # Deduplicate
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
    for abbrev, _ in BOOKS:
        if counts.get(abbrev, 0):
            print(f"  {abbrev:8s}: {counts[abbrev]}")
    print("Done.")


if __name__ == '__main__':
    main()
