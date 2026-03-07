#!/usr/bin/env python3
"""
fix-douai-refs-v2.py
Re-match Douai 1609 annotation refs using 1609-spelling verse sources.

Source priority (per SOURCES.md):
  1. drb-1609-saint-dismas.tsv  — TeX PDFs, threshold 0.25
  2. drb-1609-originaldouay.tsv — HTML, threshold 0.25
  3. drb-1609-pdf.tsv           — OCR, threshold 0.22  (lower: OCR noise)
  4. drb.tsv                    — Modern DRB, threshold 0.20 — MATCH-ONLY, no text output

CRITICAL: drb.tsv text NEVER appears in output. Only used to identify book/ch/v.
          Output VerseQuote and Commentary are ALWAYS the annotation's own original text.

Inputs:  douai-1609-clean.tsv
Output:  douai-1609-fixed-v2.tsv  (BookAbbrev, Chapter:Verse, VerseQuote, Commentary)
         douai-1609-fix-report-v2.txt
"""

import re
import sys
import shutil
import os
from collections import defaultdict, Counter

HERE     = os.path.dirname(os.path.abspath(__file__))
INPUT    = os.path.join(HERE, "douai-1609-clean.tsv")
BAK      = os.path.join(HERE, "douai-1609-clean.bak.tsv")
OUTPUT   = os.path.join(HERE, "douai-1609-fixed-v2.tsv")
REPORT   = os.path.join(HERE, "douai-1609-fix-report-v2.txt")

SRC_SD   = os.path.join(HERE, "drb-1609-saint-dismas.tsv")   # Source 1
SRC_ODR  = os.path.join(HERE, "drb-1609-originaldouay.tsv")  # Source 2
SRC_PDF  = os.path.join(HERE, "drb-1609-pdf.tsv")            # Source 3
SRC_DRB  = os.path.join(HERE, "drb.tsv")                     # Source 4 — match only

THRESH_SD    = 0.25
THRESH_ODR   = 0.25
THRESH_PDF   = 0.22
THRESH_DRB   = 0.20

CHECKPOINT   = 200
ABORT_FRAC   = 0.60
QUOTE_MAX_W  = 30   # max words from annotation to use for matching


# ═══════════════════════════════════════════════════════════════════════════════
# Normalization
# ═══════════════════════════════════════════════════════════════════════════════

# Unicode long-s → s; other archaic ligatures
LONG_S = str.maketrans({
    'ſ': 's', '\u017f': 's', 'ꝉ': 'l', 'ꝛ': 'r',
})

SPELL_MAP = {
    # f→s (OCR of long-s in annotation source)
    'fhall': 'shall', 'fhal': 'shall', 'thal': 'shall', 'inal': 'shall',
    'fhould': 'should', 'fhew': 'shew', 'faid': 'said', 'faw': 'saw',
    'fonne': 'sonne', 'fome': 'some', 'fuch': 'such', 'felf': 'self',
    'felues': 'selues', 'fix': 'six', 'fince': 'since', 'firft': 'first',
    'fecond': 'second', 'ftand': 'stand', 'ftrong': 'strong',
    'ftrength': 'strength', 'ftone': 'stone', 'fword': 'sword',
    'fpirit': 'spirit', 'fpake': 'spake', 'fpoken': 'spoken',
    'fpeake': 'speake', 'fpread': 'spread', 'fruite': 'fruite',
    'fhore': 'shore', 'fhed': 'shed', 'fhepe': 'shepe', 'fhepe': 'sheepe',
    # v→u at word start (1609 orthography)
    'vp': 'up', 'vnto': 'unto', 'vpon': 'upon', 'vntil': 'until',
    'vnder': 'under', 'vfe': 'use', 'vs': 'us',
    # Common archaic forms — keep as-is for matching against 1609 source
    # (1609 source also has haue, giue, liue, doe, goe, wil, shal)
    # OCR-specific noise corrections
    'wil': 'wil', 'shal': 'shall',
    # "Apc" → "Rev" (annotation uses Apc for Apocalypse)
}

# Book abbreviation aliases (annotation uses different abbrevs in some cases)
BOOK_ALIAS = {
    'Apc': 'Rev',   # Apocalypse → Revelation
}


def normalize(text: str) -> list:
    """Lowercase, remove punctuation, apply spelling map. Return word list."""
    text = text.translate(LONG_S)
    text = text.lower()
    text = re.sub(r"[^\w\s']", ' ', text)
    text = re.sub(r'\b\d+\b', '', text)
    words = text.split()
    result = []
    for w in words:
        w = SPELL_MAP.get(w, w)
        if len(w) >= 2:
            result.append(w)
    return result


def jaccard(a: list, b: list) -> float:
    if not a or not b:
        return 0.0
    sa, sb = set(a), set(b)
    inter = len(sa & sb)
    union = len(sa | sb)
    return inter / union if union else 0.0


# ═══════════════════════════════════════════════════════════════════════════════
# Verse loading
# ═══════════════════════════════════════════════════════════════════════════════

def load_1609_tsv(path) -> dict:
    """Load 1609 TSV → {(abbrev,ch,v): (raw_text, norm_words)}"""
    verses = {}
    if not os.path.exists(path):
        print(f"  SKIP: {os.path.basename(path)} not found", file=sys.stderr)
        return verses
    with open(path, encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i == 0:
                continue
            parts = line.rstrip('\n').split('\t')
            if len(parts) < 4:
                continue
            abbrev, ch_s, v_s, text = parts[0], parts[1], parts[2], parts[3]
            try:
                ch, v = int(ch_s), int(v_s)
            except ValueError:
                continue
            key = (abbrev, ch, v)
            if key not in verses:
                verses[key] = (text, normalize(text))
    return verses


def load_modern_drb(path) -> dict:
    """Load modern DRB → {(abbrev,ch,v): norm_words}  — NO raw text stored."""
    verses = {}
    if not os.path.exists(path):
        print(f"  SKIP: {os.path.basename(path)} not found", file=sys.stderr)
        return verses
    with open(path, encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i == 0:
                continue
            parts = line.rstrip('\n').split('\t')
            if len(parts) < 6:
                continue
            abbrev, ch_s, v_s, text = parts[1], parts[3], parts[4], parts[5]
            try:
                ch, v = int(ch_s), int(v_s)
            except ValueError:
                continue
            key = (abbrev, ch, v)
            if key not in verses:
                verses[key] = normalize(text)  # norm_words only
    return verses


def build_index(verses: dict) -> dict:
    """word → frozenset of verse keys (inverted index)."""
    idx = defaultdict(set)
    for key, val in verses.items():
        words = val[1] if isinstance(val, tuple) else val
        for w in set(words):
            idx[w].add(key)
    return idx


def best_match(query_words, verses, index, threshold):
    """Return (best_key, best_score) or (None, 0.0)."""
    if not query_words:
        return None, 0.0
    candidates = Counter()
    for w in set(query_words):
        for key in index.get(w, ()):
            candidates[key] += 1
    if not candidates:
        return None, 0.0
    best_key, best_score = None, 0.0
    for key, _ in candidates.most_common(300):
        val = verses[key]
        v_words = val[1] if isinstance(val, tuple) else val
        score = jaccard(query_words, v_words)
        if score > best_score:
            best_score, best_key = score, key
    return (best_key, best_score) if best_score >= threshold else (None, 0.0)


# ═══════════════════════════════════════════════════════════════════════════════
# Annotation splitting
# ═══════════════════════════════════════════════════════════════════════════════

SPLIT_RE = re.compile(
    r'(?<=[.!?])\s+(?=[A-Z])'       # sentence end + capital
    r'|~'                             # tilde separator
    r'|(?=\([a-z]\))'                 # (a)(b) annotation markers
    r'|\bANNOTATION[S]?\b'           # "ANNOTATIONS" header
    r'|\bANNOT[AIO]+N\b',
    re.IGNORECASE
)


def split_annotation(text: str):
    """Split into (verse_quote, commentary) using first available boundary."""
    m = SPLIT_RE.search(text, 2)
    if m:
        return text[:m.start()].strip(), text[m.end():].strip()
    # Fallback: first '. ' after 20 chars
    fp = text.find('. ', 20)
    if fp > 0:
        return text[:fp+1].strip(), text[fp+2:].strip()
    return text[:120].strip(), text[120:].strip()


def match_words_from(quote, full_text):
    words = normalize(quote)
    if len(words) < 5:
        words = normalize(full_text)[:QUOTE_MAX_W]
    return words[:QUOTE_MAX_W]


def parse_ref(ref_str):
    m = re.match(r'(\d+):(\d+)', ref_str.strip())
    return (int(m.group(1)), int(m.group(2))) if m else (None, None)


# ═══════════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    # Backup
    if not os.path.exists(BAK):
        shutil.copy2(INPUT, BAK)
        print(f"Backup created: {os.path.basename(BAK)}")
    else:
        print(f"Backup exists:  {os.path.basename(BAK)}")

    # Load sources
    print("\nLoading verse sources...")
    verses_sd  = load_1609_tsv(SRC_SD)
    verses_odr = load_1609_tsv(SRC_ODR)
    verses_pdf = load_1609_tsv(SRC_PDF)
    verses_drb = load_modern_drb(SRC_DRB)
    print(f"  Source 1 (saint-dismas): {len(verses_sd):6d} verses  threshold={THRESH_SD}")
    print(f"  Source 2 (originaldouay):{len(verses_odr):6d} verses  threshold={THRESH_ODR}")
    print(f"  Source 3 (PDF OCR):      {len(verses_pdf):6d} verses  threshold={THRESH_PDF}")
    print(f"  Source 4 (modern DRB):   {len(verses_drb):6d} verses  threshold={THRESH_DRB} [match-only]")

    # Build indices
    print("\nBuilding inverted indices...")
    idx_sd  = build_index(verses_sd)
    idx_odr = build_index(verses_odr)
    idx_pdf = build_index(verses_pdf)
    idx_drb = build_index(verses_drb)

    # Load annotations
    print(f"\nReading {os.path.basename(INPUT)}...")
    with open(INPUT, encoding='utf-8') as f:
        raw_lines = f.readlines()
    ann_rows = []
    for line in raw_lines[1:]:
        parts = line.rstrip('\n').split('\t')
        if len(parts) >= 3:
            ann_rows.append(parts)
    total = len(ann_rows)
    print(f"  {total} annotation rows to process")

    # Process
    out_rows    = []
    book_changes = []
    ref_changes  = []
    low_conf     = []
    bad_splits   = []
    stats        = Counter()
    chk_lc       = 0

    print(f"\nMatching {total} annotations...\n")

    for i, parts in enumerate(ann_rows):
        orig_book = parts[0].strip()
        orig_ref  = parts[1].strip() if len(parts) > 1 else ''
        anno_text = parts[2].strip() if len(parts) > 2 else ''

        # Normalise book alias (Apc → Rev)
        lookup_book = BOOK_ALIAS.get(orig_book, orig_book)

        orig_ch, orig_v = parse_ref(orig_ref)

        # Split annotation
        quote, commentary = split_annotation(anno_text)
        if not quote or len(quote) < 5:
            bad_splits.append((i+1, orig_ref, 'quote too short'))
        if not commentary:
            bad_splits.append((i+1, orig_ref, 'no commentary'))

        q_words = match_words_from(quote, anno_text)

        # Try sources in order
        match_key, score, via = None, 0.0, ''

        k, s = best_match(q_words, verses_sd,  idx_sd,  THRESH_SD)
        if k:
            match_key, score, via = k, s, 'saint-dismas'

        if not match_key:
            k, s = best_match(q_words, verses_odr, idx_odr, THRESH_ODR)
            if k:
                match_key, score, via = k, s, 'originaldouay'

        if not match_key:
            k, s = best_match(q_words, verses_pdf, idx_pdf, THRESH_PDF)
            if k:
                match_key, score, via = k, s, 'pdf-ocr'

        if not match_key:
            k, s = best_match(q_words, verses_drb, idx_drb, THRESH_DRB)
            if k:
                match_key, score, via = k, s, 'modern-drb'

        # Determine output
        if match_key:
            new_book, new_ch, new_v = match_key
            stats[f'via_{via}'] += 1
            new_ref = f"{new_ch}:{new_v}"
            lc_flag = ''

            # Restore original book alias in output if matched via alias
            if orig_book in BOOK_ALIAS and BOOK_ALIAS[orig_book] == new_book:
                new_book = orig_book  # keep original alias

            if new_book != orig_book:
                book_changes.append((i+1, orig_book, new_book, orig_ref, new_ref, score, via))
                stats['book_changed'] += 1
            elif new_ref != orig_ref:
                ref_changes.append((i+1, orig_book, orig_ref, new_ref, score, via))
                stats['ref_changed'] += 1
            else:
                stats['unchanged'] += 1

            final_book, final_ref = new_book, new_ref
        else:
            # LOW_CONFIDENCE — keep original
            final_book = orig_book
            final_ref  = orig_ref
            lc_flag    = ' [LOW_CONFIDENCE]'
            stats['low_conf'] += 1
            chk_lc += 1
            low_conf.append((i+1, orig_book, orig_ref,
                             f'best scores: sd={score:.3f}'))

        out_rows.append([
            final_book, final_ref,
            quote.replace('\t', ' '),
            (commentary + lc_flag).replace('\t', ' '),
        ])

        # Checkpoint
        if (i + 1) % CHECKPOINT == 0:
            lc_frac = chk_lc / CHECKPOINT
            conf = (i + 1) - stats['low_conf']
            print(f"  Checkpoint {i+1:4d}/{total} — "
                  f"confident: {conf}, low_conf: {stats['low_conf']}, "
                  f"window_lc: {chk_lc}/{CHECKPOINT} ({lc_frac:.0%})")
            if lc_frac > ABORT_FRAC:
                print(f"\nABORT: matching quality too low — {chk_lc}/{CHECKPOINT} "
                      f"in last window were LOW_CONFIDENCE. Check normalization.")
                sys.exit(1)
            chk_lc = 0

    # Summary
    print(f"\n{'='*60}")
    print(f"RESULTS  (total={total})")
    for k in sorted(stats.keys()):
        print(f"  {k}: {stats[k]}")

    # Write output TSV
    print(f"\nWriting {os.path.basename(OUTPUT)} ...")
    with open(OUTPUT, 'w', encoding='utf-8') as f:
        f.write("BookAbbrev\tChapter:Verse\tVerseQuote\tCommentary\n")
        for row in out_rows:
            f.write('\t'.join(row) + '\n')

    # Write report
    print(f"Writing {os.path.basename(REPORT)} ...")
    with open(REPORT, 'w', encoding='utf-8') as f:
        w = f.write
        w("=" * 70 + "\n")
        w("DOUAI 1609 ANNOTATION FIX REPORT v2\n")
        w("=" * 70 + "\n\n")
        w("SUMMARY\n" + "-"*40 + "\n")
        w(f"Total annotation rows:          {total}\n")
        via_total = sum(v for k,v in stats.items() if k.startswith('via_'))
        w(f"Matched (confident):            {via_total} ({via_total/total*100:.1f}%)\n")
        for src in ('saint-dismas','originaldouay','pdf-ocr','modern-drb'):
            n = stats.get(f'via_{src}', 0)
            w(f"  via {src:20s}: {n}\n")
        w(f"LOW_CONFIDENCE (kept):          {stats['low_conf']} ({stats['low_conf']/total*100:.1f}%)\n")
        w(f"Book changed:                   {stats['book_changed']}\n")
        w(f"Ref changed (same book):        {stats['ref_changed']}\n")
        w(f"Ref unchanged:                  {stats['unchanged']}\n")
        w(f"\nThresholds: SD={THRESH_SD} ODR={THRESH_ODR} PDF={THRESH_PDF} DRB={THRESH_DRB}\n")
        w(f"\nHard rule: modern DRB text NEVER appears in output TSV.\n")
        w(f"  VerseQuote = annotation's own original text (split from annotation).\n")
        w(f"  Commentary = annotation's own original text (remainder after split).\n")

        w("\n" + "="*70 + "\n")
        w("SECTION A: BOOK-LEVEL CORRECTIONS\n")
        w("="*70 + "\n")
        w(f"({len(book_changes)} rows where book changed)\n\n")
        for row_i, ob, nb, or_, nr, sc, via in book_changes:
            w(f"  Row {row_i:4d}: {ob:6s} {or_:8s} → {nb:6s} {nr:8s}  [score={sc:.3f} via={via}]\n")

        w("\n" + "="*70 + "\n")
        w("SECTION B: CHAPTER/VERSE CORRECTIONS (SAME BOOK)\n")
        w("="*70 + "\n")
        w(f"({len(ref_changes)} rows)\n\n")
        for row_i, ob, or_, nr, sc, via in ref_changes:
            w(f"  Row {row_i:4d}: {ob:6s} {or_:8s} → {nr:8s}  [score={sc:.3f} via={via}]\n")

        w("\n" + "="*70 + "\n")
        w("SECTION C: LOW_CONFIDENCE ROWS (original ref kept)\n")
        w("="*70 + "\n")
        w(f"({len(low_conf)} rows)\n\n")
        for row_i, ob, or_, reason in low_conf:
            w(f"  Row {row_i:4d}: {ob:6s} {or_:12s} — {reason}\n")

        w("\n" + "="*70 + "\n")
        w("SECTION D: SPLIT ISSUES\n")
        w("="*70 + "\n")
        w(f"({len(bad_splits)} flags)\n\n")
        for row_i, or_, reason in bad_splits:
            w(f"  Row {row_i:4d}: {or_:12s} — {reason}\n")

    print(f"\nDone.")
    print(f"  Output:  {OUTPUT}")
    print(f"  Report:  {REPORT}")


if __name__ == '__main__':
    main()
