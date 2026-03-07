#!/usr/bin/env python3
"""
mirror-sources.py
Download all source material to local disk for offline processing.

Outputs:
  sources/saint-dismas/OT/[Book]/chapter-NN.pdf
  sources/saint-dismas/NT/[Book]/chapter-NN.pdf
  sources/originaldouay/[page].html
"""

import os
import re
import sys
import time
import subprocess
import urllib.request
from urllib.error import URLError, HTTPError

BASE_SD  = "http://www.saint-dismas.com"
BASE_ODR = "https://originaldouayrheims.com"
HERE     = os.path.dirname(os.path.abspath(__file__))
SD_DIR   = os.path.join(HERE, "sources", "saint-dismas")
ODR_DIR  = os.path.join(HERE, "sources", "originaldouay")

DELAY_SD  = 0.3
DELAY_ODR = 0.5

# ─── saint-dismas book list ───────────────────────────────────────────────────
SD_OT_BOOKS = [
    "Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy",
    "Joshua", "Judges", "Ruth",
    "One-Kings", "Two-Kings", "Three-Kings", "Four-Kings",
    "One-Paralipomenon", "Two-Paralipomenon",
    "One-Esdras", "Nehemias", "Tobias", "Judith", "Esther", "Job",
    "Proverbs", "Ecclesiastes", "Canticle", "Wisdom",
    # Psalmes and Isaias confirmed 0 standard chapters — skipped
]
SD_NT_BOOKS = [
    "Matthew", "Mark", "Luke", "John", "Acts", "Romans",
    "One-Corinthians", "Two-Corinthians", "Galatians", "Ephesians",
    "Philippians", "Colossians", "One-Thessalonians", "Two-Thessalonians",
    "One-Timothy", "Two-Timothy", "Titus", "Philemon", "Hebrews",
    "James", "One-Peter", "Two-Peter", "One-John", "Two-John", "Three-John",
    "Jude", "Apocalypse",
]

# ─── originaldouayrheims book list ───────────────────────────────────────────
# Each entry: (local_stem, remote_path_or_url)
ODR_BOOKS = [
    # OT /old/ paths — index page + chapter subpages discovered dynamically
    ("old-genesis",      "/old/genesis"),
    ("old-ruth",         "/old/ruth"),
    ("old-psalms",       "/old/psalms"),
    ("old-wisdom",       "/old/wisdom"),
    ("old-lamentations", "/old/lamentations"),
    ("old-baruch",       "/old/baruch"),
    ("old-daniel",       "/old/daniel"),
    ("old-jonas",        "/old/jonas"),
    ("old-sophonias",    "/old/sophonias"),
    ("old-ecclesiasticus","/old/ecclesiasticus"),
    # OT root .html
    ("I-Machabees",      "/I Machabees.html"),
    ("II-Machabees",     "/II Machabees.html"),
    # NT root paths
    ("matthew",    "/matthew"),
    ("mark",       "/mark"),
    ("luke",       "/luke"),
    ("john",       "/john"),
    ("acts",       "/acts"),
    ("romans",     "/romans"),
    ("galatians",  "/galatians"),
    ("ephesians",  "/ephesians"),
    ("philippians","/philippians"),
    ("colossians", "/colossians"),
    ("titus",      "/titus"),
    ("philemon",   "/philemon"),
    ("hebrews",    "/hebrews"),
    ("james",      "/james"),
    ("jude",       "/jude"),
    ("revelations","/revelations"),
    # NT root .html
    ("I-Corinthians",    "/I Corinthians.html"),
    ("II-Corinthians",   "/II Corinthians.html"),
    ("I-Thessalonians",  "/I Thessalonians.html"),
    ("II-Thessalonians", "/II Thessalonians.html"),
    ("I-Timothee",       "/I Timothee.html"),
    ("II-Timothee",      "/II Timothee.html"),
    ("I-Peter",          "/I Peter.html"),
    ("II-Peter",         "/II Peter.html"),
    ("I-John",           "/I John.html"),
    ("II-John",          "/II John.html"),
    ("III-John",         "/III John.html"),
]

# ─── Network helpers ──────────────────────────────────────────────────────────
def fetch_bytes(url, timeout=30):
    encoded = url.replace(' ', '%20')
    req = urllib.request.Request(
        encoded,
        headers={'User-Agent': 'Mozilla/5.0 (compatible; DRB-mirror/1.0)'}
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read()
    except (HTTPError, URLError) as e:
        print(f"  WARN fetch {url}: {e}", file=sys.stderr)
        return None


def fetch_text(url):
    data = fetch_bytes(url)
    if data is None:
        return None
    try:
        return data.decode('utf-8')
    except UnicodeDecodeError:
        return data.decode('latin-1')


def save_file(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as f:
        f.write(data if isinstance(data, bytes) else data.encode('utf-8'))


def curl_download(url, dest):
    """Use curl for binary downloads (PDFs) — more reliable."""
    result = subprocess.run(
        ['curl', '-s', '-L', '--max-time', '30',
         '--retry', '2', '--retry-delay', '2',
         '-o', dest, url.replace(' ', '%20')],
        capture_output=True
    )
    return result.returncode == 0 and os.path.exists(dest) and os.path.getsize(dest) > 200


# ─── saint-dismas mirror ──────────────────────────────────────────────────────
def get_sd_chapter_pdfs(book_path, testament):
    """
    Fetch the book's index.html, extract chapter PDF filenames.
    Returns list of (chapter_num, filename, url).
    """
    url = f"{BASE_SD}/ODRB/TeX/{testament}/{book_path}/index.html"
    html = fetch_text(url)
    if not html:
        return []

    hrefs = re.findall(r'href="(/ODRB/TeX/[^"]+\.pdf)"', html)
    chapters = []
    for href in hrefs:
        fname = href.split('/')[-1]
        if re.search(r'(argument|introduction|interpretation|preface|summe)', fname, re.I):
            continue
        m = re.search(r'(\d+)', fname)
        if m:
            chap_num = int(m.group(1))
            chapters.append((chap_num, fname, BASE_SD + href))
    chapters.sort(key=lambda x: x[0])
    return chapters


def mirror_saint_dismas():
    pdf_count = 0
    skipped   = 0

    for testament, books in [("Old-Testament", SD_OT_BOOKS), ("New-Testament", SD_NT_BOOKS)]:
        short_t = "OT" if testament.startswith("Old") else "NT"
        print(f"\n── {testament} ({len(books)} books) ──")

        for book in books:
            book_dir = os.path.join(SD_DIR, short_t, book)
            os.makedirs(book_dir, exist_ok=True)

            chapters = get_sd_chapter_pdfs(book, testament)
            if not chapters:
                print(f"  {book}: no chapters found", file=sys.stderr)
                time.sleep(DELAY_SD)
                continue

            sys.stdout.write(f"  {book:30s} {len(chapters):3d} ch  ")
            sys.stdout.flush()

            book_new = 0
            for chap_num, fname, url in chapters:
                dest = os.path.join(book_dir, fname)
                if os.path.exists(dest) and os.path.getsize(dest) > 200:
                    skipped += 1
                    continue

                if curl_download(url, dest):
                    pdf_count += 1
                    book_new += 1
                else:
                    print(f"\n  WARN: failed {url}", file=sys.stderr)
                time.sleep(DELAY_SD)

            print(f"downloaded {book_new}, skipped {len(chapters)-book_new}")

    return pdf_count, skipped


# ─── originaldouayrheims mirror ───────────────────────────────────────────────
def get_odr_chapter_links(html, index_url):
    """Extract chapter page hrefs from index page h3 nav block."""
    h3_m = re.search(r'<h3>(.*?)</h3>', html, re.DOTALL | re.IGNORECASE)
    if not h3_m:
        return []
    block = h3_m.group(1)
    hrefs = re.findall(r'href=["\']([^"\']+)["\']', block, re.IGNORECASE)
    seen, links = set(), []
    for href in hrefs:
        href = href.strip()
        if not href or href.startswith('#') or href.startswith('javascript'):
            continue
        if re.search(r'(sum|arg|intro)\b', href, re.IGNORECASE):
            continue
        if href.startswith('http'):
            full = href
        elif href.startswith('/'):
            full = BASE_ODR + href
        else:
            base_dir = index_url.rsplit('/', 1)[0]
            full = base_dir.replace('%20', ' ') + '/' + href
        if full not in seen:
            seen.add(full)
            links.append(full)
    return links


def url_to_local_stem(url):
    """Convert an ODR URL to a safe local filename stem."""
    path = url.replace(BASE_ODR, '').lstrip('/')
    path = path.replace('/', '--').replace(' ', '_').replace('.html', '')
    return path if path else 'index'


def mirror_originaldouay():
    html_count = 0
    skipped    = 0

    print(f"\n── originaldouayrheims.com ({len(ODR_BOOKS)} books) ──")

    for stem, path in ODR_BOOKS:
        index_url = BASE_ODR + path

        # Fetch index (or single-page) HTML
        index_local = os.path.join(ODR_DIR, f"{stem}--index.html")
        if os.path.exists(index_local):
            with open(index_local, encoding='utf-8', errors='replace') as f:
                html = f.read()
            skipped += 1
        else:
            html = fetch_text(index_url)
            if html:
                save_file(index_local, html.encode('utf-8'))
                html_count += 1
            else:
                print(f"  WARN: could not fetch {index_url}", file=sys.stderr)
                time.sleep(DELAY_ODR)
                continue
            time.sleep(DELAY_ODR)

        # Discover chapter subpages
        chapter_urls = get_odr_chapter_links(html, index_url)
        if not chapter_urls:
            # Single-page book — already saved above
            print(f"  {stem:30s}  1 page (single-chapter)")
            continue

        sys.stdout.write(f"  {stem:30s} {len(chapter_urls):3d} ch  ")
        sys.stdout.flush()

        book_new = 0
        for chap_url in chapter_urls:
            local_stem = url_to_local_stem(chap_url)
            chap_local = os.path.join(ODR_DIR, f"{local_stem}.html")

            if os.path.exists(chap_local):
                skipped += 1
                continue

            chap_html = fetch_text(chap_url)
            if chap_html:
                save_file(chap_local, chap_html.encode('utf-8'))
                html_count += 1
                book_new += 1
            else:
                print(f"\n  WARN: failed {chap_url}", file=sys.stderr)
            time.sleep(DELAY_ODR)

        print(f"downloaded {book_new}, skipped {len(chapter_urls)-book_new}")

    return html_count, skipped


# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("Mirroring sources to local disk")
    print("=" * 60)

    print("\n[1/2] saint-dismas.com PDFs")
    pdf_new, pdf_skip = mirror_saint_dismas()

    print("\n[2/2] originaldouayrheims.com HTML")
    html_new, html_skip = mirror_originaldouay()

    print("\n" + "=" * 60)
    print("MIRROR COMPLETE")
    print(f"  saint-dismas PDFs:   {pdf_new} downloaded, {pdf_skip} already existed")
    print(f"  originaldouay HTML:  {html_new} downloaded, {html_skip} already existed")
    print(f"  saint-dismas dir:    {SD_DIR}")
    print(f"  originaldouay dir:   {ODR_DIR}")
    print("=" * 60)


if __name__ == '__main__':
    main()
