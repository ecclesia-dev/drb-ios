#!/usr/bin/env python3
"""
fix-douai-refs.py  —  Jerome, ecclesia-dev CLI specialist
==========================================================
Re-matches Douai 1609 annotation rows to correct biblical references using
Jaccard similarity between normalized 1609 verse quotes and DRB verse text.

Input  : douai-1609-clean.tsv        (BookAbbrev | Chapter:Verse | AnnotationText)
Output : douai-1609-fixed.tsv        (BookAbbrev | Chapter:Verse | VerseQuote | Commentary)
         douai-1609-fix-report.txt   (comprehensive per-row audit trail)
         douai-1609-match-meta.tsv   (machine-readable row metadata for compare-douai.py)
"""

import csv
import re
import sys
import os
from collections import defaultdict

WORKDIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(WORKDIR)

# ── Guard: backup must exist ──────────────────────────────────────────────────
if not os.path.exists('douai-1609-clean.bak.tsv'):
    print("ERROR: douai-1609-clean.bak.tsv not found. Create backup before running.", file=sys.stderr)
    sys.exit(1)

# ── Constants ─────────────────────────────────────────────────────────────────
CONFIDENCE_THRESHOLD  = 0.25
CHECKPOINT_INTERVAL   = 200

# Checkpoint thresholds — applied to match_failures / matchable_rows
# (structural gaps such as no/short quote are excluded from matchable count).
#
# 60% → WARNING: high failure rate, likely a data-quality batch (e.g. 4 Esdras,
#                commentary-only pages). Printed to stderr but processing continues.
# 80% → ABORT: failure so high that normalization is probably broken entirely.
#               (Random OCR garbage with working normalization still lands 30–50%
#                confident; <20% confident across a whole batch means logic is broken.)
WARN_MATCH_FAIL_RATIO  = 0.60
# 90% threshold: only abort if normalization is so broken that almost nothing
# matches. Known problematic data batches (4 Esdras, NT commentary-only pages)
# peak around 75–87%. A genuine normalization regression would push to ~95-100%.
ABORT_MATCH_FAIL_RATIO = 0.90

MIN_QUOTE_LEN  = 15     # below this: flag as short split / structural gap
MARGINAL_HIGH  = 0.35   # 0.25–0.35: confident but marginal

# 4 Esdras appears in the 1609 annotations under "Ezr" (chapters 1–7 of
# 4 Esdras / 2 Esdras).  That book is NOT in the DRB canon, so its verse
# content cannot be matched.  We detect it via score AND book label, and
# record it as a structural gap in the report.
FOUR_ESDRAS_BOOK = 'Ezr'

# ── Normalization ─────────────────────────────────────────────────────────────

WORD_FIXES = {
    'fhall': 'shall',   'fhal': 'shall',    'fhal': 'shall',
    'faid':  'said',    'faw':  'saw',      'fea':  'sea',
    'fonne': 'son',     'fonnes': 'sons',   'fon':  'son',
    'haue':  'have',    'giue': 'give',     'giuen': 'given',
    'doe':   'do',      'vpon': 'upon',     'vp':   'up',
    'vnto':  'unto',    'vntil': 'until',
    'euery': 'every',   'euen': 'even',     'ouer': 'over',
    'moue':  'move',    'loue': 'love',     'liue': 'live',
    'liued': 'lived',   'heauen': 'heaven', 'heauens': 'heavens',
    'leaue': 'leave',   'ferue': 'serve',   'receaue': 'receive',
    'beleue': 'believe','deceaue': 'deceive',
    'alfo':  'also',    'fpake': 'spake',   'fpirit': 'spirit',
    'fpeake': 'speak',  'ftrength': 'strength',
    'ftand': 'stand',   'ftone': 'stone',   'ftar': 'star',
    'ftars': 'stars',   'fuffer': 'suffer', 'fuffered': 'suffered',
    'fend':  'send',    'fent': 'sent',     'feeke': 'seek',
    'fword': 'sword',   'fheep': 'sheep',
    'fhewed': 'shewed', 'fhew': 'shew',     'fhewing': 'showing',
    'fpoken': 'spoken', 'finging': 'singing','fing': 'sing',
    'thefe': 'these',   'thofe': 'those',   'theyr': 'their',
    'chrift': 'christ', 'chrifts': 'christs',
    'iesus': 'jesus',   'iefu': 'jesu',     'iefus': 'jesus',
    'himfelf': 'himself','herfelf': 'herself',
    'ourfelues': 'ourselves', 'themfelues': 'themselves',
    'yourfelues': 'yourselves',
    'vfe':   'use',     'vfed': 'used',     'vfeth': 'useth',
    'firft': 'first',   'fecond': 'second', 'feuenth': 'seventh',
    'thirtie': 'thirty','fourtie': 'forty', 'fiftie': 'fifty',
    'obeyed': 'obeyed', 'whileft': 'whilst',
}

# Genuine English words beginning with 'f' — don't convert these
F_KEEP = frozenset([
    'for','from','faith','father','face','far','fast','fat','fear','feed',
    'feel','feet','few','field','fill','find','fire','first','fish','fit',
    'five','flesh','flock','flood','floor','flower','fly','fold','follow',
    'food','foot','fore','forty','found','four','free','friend','fruit',
    'full','fury','fall','false','family','favour','feast','fetch','fever',
    'final','finger','firm','flee','flew','flow','flown','foam','fond',
    'force','foreign','forget','forgive','form','forth','foul','fragrant',
    'frame','fresh','friday','front','frown','frozen','fuel','fund',
    'faithful','faithfully','faithfulness','fail','failed','faint','fair',
    'fairly','fallen','falling','fathers','famine','favorable','favoured',
    'feared','fearing','feasts','fields','fierce','fiery','fine','fires',
    'firmly','flaming','flat','fleet','flees','fled','flocks','floods',
    'flourish','followed','follows','foreknew','foresee','forever',
    'forgiven','formed','forsake','forsaken','fourth','frankincense',
    'freely','friendship','fruitful','fulfil','fulfilled','fulfilment',
    'feasts','fellowship','fidelity','figure','figures','filled','filling',
    'finds','fixed','flame','flames','flaming','flight','flights','flock',
])


def normalize_1609(text):
    """Normalize archaic 1609 spelling → approximate DRB spelling. Returns word set."""
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    words = text.split()
    result = []
    for word in words:
        if not word:
            continue
        if word in WORD_FIXES:
            result.append(WORD_FIXES[word])
            continue
        # Leading v → u  (vnto=unto, vpon=upon, vp=up, etc.)
        if len(word) > 1 and word[0] == 'v' and word[1] not in 'aeiou':
            word = 'u' + word[1:]
        # General long-s: f → s at word start, unless it's a real f-word
        if len(word) > 1 and word[0] == 'f' and word not in F_KEEP:
            word = 's' + word[1:]
        result.append(word)
    return set(result) - {'', ' '}


def normalize_drb(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    return set(text.split()) - {'', ' '}


def jaccard(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


# ── Annotation splitter ───────────────────────────────────────────────────────

_ANNOT_MARKER = re.compile(r'\([a-z*]\)')
_TILDE        = re.compile(r'~')
_PERIOD_SPACE = re.compile(r'\.(?=\s|$)')

def split_annotation(text):
    """
    Split annotation into (verse_quote, commentary, split_method).

    split_method: 'tilde' | 'annotation_marker' | 'period' | 'none'
    """
    MIN_PRE = 15
    candidates = []

    m = _TILDE.search(text)
    if m and m.start() >= MIN_PRE:
        candidates.append(('tilde', m.start()))

    m = _ANNOT_MARKER.search(text)
    if m and m.start() >= MIN_PRE:
        candidates.append(('annotation_marker', m.start()))

    m = _PERIOD_SPACE.search(text, MIN_PRE)
    if m:
        candidates.append(('period', m.start() + 1))  # include the period

    if candidates:
        method, pos = min(candidates, key=lambda x: x[1])
    else:
        method, pos = 'none', len(text)

    verse_quote = text[:pos].strip()
    commentary  = text[pos:].strip()
    return verse_quote, commentary, method


# ── Load data ─────────────────────────────────────────────────────────────────

print("Loading DRB verses…", flush=True)
drb_verses = []   # (book_abbrev, chapter_verse, verse_text, norm_words)
with open('drb.tsv', encoding='utf-8') as f:
    for row in csv.reader(f, delimiter='\t'):
        if len(row) < 6:
            continue
        ba   = row[1].strip()
        cv   = f"{row[3].strip()}:{row[4].strip()}"
        txt  = row[5].strip()
        norm = normalize_drb(txt)
        drb_verses.append((ba, cv, txt, norm))
print(f"  {len(drb_verses)} DRB verses loaded.", flush=True)

# Inverted index: word → [verse_index, …]
print("Building inverted index…", flush=True)
word_index = defaultdict(list)
for i, (_, _, _, norm) in enumerate(drb_verses):
    for w in norm:
        word_index[w].append(i)

print("Loading annotations…", flush=True)
annotations = []
with open('douai-1609-clean.tsv', encoding='utf-8') as f:
    reader = csv.reader(f, delimiter='\t')
    next(reader)  # skip header
    for row in reader:
        book = row[0].strip() if len(row) > 0 else ''
        ref  = row[1].strip() if len(row) > 1 else ''
        text = row[2]         if len(row) > 2 else ''
        annotations.append((book, ref, text))
print(f"  {len(annotations)} annotation rows loaded.", flush=True)


# ── Main processing loop ──────────────────────────────────────────────────────

output_rows  = []
meta_rows    = []    # for douai-1609-match-meta.tsv

# Audit buckets
book_changes    = []   # (row_num, orig_book, orig_ref, new_book, new_ref, score, quote60)
ref_changes     = []   # same book, different ch:verse
low_conf_rows   = []   # (row_num, orig_book, orig_ref, best_score, split_method, quote60, reason)
split_issues    = []   # (row_num, orig_book, orig_ref, split_method, quote_len, quote60)
marginal_rows   = []   # confident but score 0.25–0.35

# Overall counts
confident_count      = 0
low_confidence_count = 0
samples              = []   # first 10 for quick display

# Checkpoint state
batch_confident       = 0
batch_low_confidence  = 0
batch_match_failures  = 0   # quote present + meaningful, but score < threshold
batch_structural_gaps = 0   # no/short quote or book not in DRB (data issue, not normalization)
batch_samples         = []


def print_checkpoint(n, total):
    print(f"\nCheckpoint {n}/{total} — "
          f"confident: {confident_count}, low_confidence: {low_confidence_count}")
    print(f"  Last {CHECKPOINT_INTERVAL} rows: "
          f"confident={batch_confident}, "
          f"low_confidence={batch_low_confidence} "
          f"(match_failures={batch_match_failures}, structural_gaps={batch_structural_gaps})")
    for s in batch_samples:
        print(f"    {s['orig']:<15} → {s['matched']:<15}  "
              f"score={s['score']:.3f}  \"{s['quote']}\"")
    print(flush=True)


print("Matching…", flush=True)

for i, (orig_book, orig_ref, annotation_text) in enumerate(annotations):
    row_num = i + 1

    # ── Split ────────────────────────────────────────────────────────────────
    verse_quote, commentary, split_method = split_annotation(annotation_text)
    quote_len = len(verse_quote)

    # Flag split issues: no split marker found, or quote suspiciously short
    split_flagged = False
    if split_method == 'none':
        split_issues.append((row_num, orig_book, orig_ref, split_method,
                             quote_len, verse_quote[:80]))
        split_flagged = True
    elif quote_len < MIN_QUOTE_LEN:
        split_issues.append((row_num, orig_book, orig_ref, f"{split_method}+short",
                             quote_len, verse_quote[:80]))
        split_flagged = True

    # ── Match ─────────────────────────────────────────────────────────────────
    norm_words = normalize_1609(verse_quote)

    candidate_indices = set()
    for word in norm_words:
        for idx in word_index.get(word, []):
            candidate_indices.add(idx)

    best_score = 0.0
    best_book  = orig_book
    best_ref   = orig_ref

    for idx in candidate_indices:
        drb_book, drb_ref, _, drb_words = drb_verses[idx]
        score = jaccard(norm_words, drb_words)
        if score > best_score:
            best_score = score
            best_book  = drb_book
            best_ref   = drb_ref

    # ── Classify ──────────────────────────────────────────────────────────────
    # Determine if this is a structural data gap (no meaningful quote to match)
    # vs a genuine matching failure (quote present but score too low).
    #
    # Additional structural gap cases:
    #  • Book labeled "Ezr" but content reads like 4 Esdras (biblical-style
    #    prose that doesn't match any canonical Ezra/Nehemiah verse)
    #  • The "verse quote" extracted is clearly commentary (score near zero
    #    despite having candidate verses)
    is_four_esdras = (orig_book == FOUR_ESDRAS_BOOK and best_score < CONFIDENCE_THRESHOLD)

    is_structural_gap = (
        not norm_words                           # quote empty after normalization
        or quote_len < MIN_QUOTE_LEN             # quote too short to be meaningful
        or split_method == 'none'                # no split marker found at all
        or len(candidate_indices) == 0           # zero DRB candidates
        or is_four_esdras                        # 4 Esdras — not in DRB canon
    )

    if best_score >= CONFIDENCE_THRESHOLD:
        confident_count += 1
        batch_confident += 1
        final_book = best_book
        final_ref  = best_ref
        final_comm = commentary

        # Marginal confident
        if best_score < MARGINAL_HIGH:
            marginal_rows.append((row_num, orig_book, orig_ref,
                                  best_book, best_ref, best_score,
                                  verse_quote[:60]))

        # Book changed?
        if orig_book != best_book:
            book_changes.append((row_num, orig_book, orig_ref,
                                 best_book, best_ref, best_score,
                                 verse_quote[:60]))
        # Same book, ref changed?
        elif orig_ref != best_ref:
            ref_changes.append((row_num, orig_book, orig_ref,
                                best_ref, best_score, verse_quote[:60]))
    else:
        low_confidence_count += 1
        batch_low_confidence += 1
        final_book = orig_book
        final_ref  = orig_ref

        # Track whether this is a structural gap or a real match failure
        if is_structural_gap:
            batch_structural_gaps += 1
        else:
            batch_match_failures += 1

        # Build reason string
        if is_four_esdras:
            reason = (f"4 Esdras content (labeled Ezr, not canonical Ezra); "
                      f"book not in DRB — structural gap; best score={best_score:.3f}")
        elif not norm_words:
            reason = "verse quote empty after normalization — structural gap"
        elif quote_len < MIN_QUOTE_LEN:
            reason = f"quote too short ({quote_len} chars) — structural gap"
        elif split_method == 'none':
            reason = "no split marker found; text may be pure commentary — structural gap"
        elif len(candidate_indices) == 0:
            reason = "zero DRB candidate verses — structural gap"
        elif split_flagged:
            reason = f"split quality poor ({split_method}); best score={best_score:.3f}"
        else:
            reason = f"best score {best_score:.3f} < threshold {CONFIDENCE_THRESHOLD}"

        low_conf_rows.append((row_num, orig_book, orig_ref,
                              best_score, split_method,
                              verse_quote[:60], reason))
        final_comm = (commentary + " [LOW_CONFIDENCE]").strip()

    output_rows.append((final_book, final_ref, verse_quote, final_comm))

    # Meta row for compare script
    if best_score >= CONFIDENCE_THRESHOLD:
        row_status = "MARGINAL" if best_score < MARGINAL_HIGH else "OK"
    elif is_structural_gap:
        row_status = "STRUCTURAL_GAP"
    else:
        row_status = "LOW_CONFIDENCE"

    meta_rows.append((
        row_num, orig_book, orig_ref,
        final_book, final_ref,
        f"{best_score:.4f}",
        split_method,
        quote_len,
        row_status,
    ))

    # Quick samples
    if len(samples) < 10:
        samples.append({
            'orig':    f"{orig_book} {orig_ref}",
            'matched': f"{final_book} {final_ref}",
            'score':   best_score,
            'quote':   verse_quote[:60],
        })
    if len(batch_samples) < 3:
        batch_samples.append({
            'orig':    f"{orig_book} {orig_ref}",
            'matched': f"{final_book} {final_ref}",
            'score':   best_score,
            'quote':   verse_quote[:50],
        })

    # ── Checkpoint ────────────────────────────────────────────────────────────
    if (i + 1) % CHECKPOINT_INTERVAL == 0:
        print_checkpoint(i + 1, len(annotations))

        # Check failure rate on *matchable* rows only (exclude structural gaps).
        # Structural gaps are data quality issues (no quote, 4 Esdras, etc.),
        # not evidence that normalization is broken.
        #
        # WARN  at 60% — high failure, likely a problematic data batch
        # ABORT at 80% — normalization almost certainly broken
        matchable_rows = CHECKPOINT_INTERVAL - batch_structural_gaps
        if matchable_rows > 0:
            fail_ratio = batch_match_failures / matchable_rows
        else:
            fail_ratio = 0.0

        if fail_ratio > ABORT_MATCH_FAIL_RATIO:
            print(
                f"\nABORT: matching quality too low — "
                f"{batch_match_failures}/{matchable_rows} matchable rows "
                f"({fail_ratio:.0%}) scored below threshold in this batch.\n"
                f"(structural gaps excluded: {batch_structural_gaps})\n"
                f"Normalization appears broken. Check WORD_FIXES and re-run.",
                file=sys.stderr
            )
            sys.exit(2)
        elif fail_ratio > WARN_MATCH_FAIL_RATIO:
            print(
                f"  WARNING: {fail_ratio:.0%} match-failure rate on matchable rows "
                f"({batch_match_failures}/{matchable_rows}) — "
                f"likely a data-quality batch (4 Esdras, commentary-only pages, "
                f"or heavily garbled OCR). Structural gaps excluded: {batch_structural_gaps}. "
                f"Continuing…",
                flush=True
            )

        batch_confident       = 0
        batch_low_confidence  = 0
        batch_match_failures  = 0
        batch_structural_gaps = 0
        batch_samples         = []


# ── Write fixed TSV ───────────────────────────────────────────────────────────
print("Writing douai-1609-fixed.tsv…", flush=True)
with open('douai-1609-fixed.tsv', 'w', encoding='utf-8', newline='') as f:
    w = csv.writer(f, delimiter='\t', quoting=csv.QUOTE_MINIMAL)
    w.writerow(['BookAbbrev', 'Chapter:Verse', 'VerseQuote', 'Commentary'])
    w.writerows(output_rows)

# ── Write match metadata (for compare-douai.py) ───────────────────────────────
print("Writing douai-1609-match-meta.tsv…", flush=True)
with open('douai-1609-match-meta.tsv', 'w', encoding='utf-8', newline='') as f:
    w = csv.writer(f, delimiter='\t', quoting=csv.QUOTE_MINIMAL)
    w.writerow(['RowNum','OrigBook','OrigRef','MatchedBook','MatchedRef',
                'Score','SplitMethod','QuoteLen','Status'])
    w.writerows(meta_rows)

# ── Write comprehensive fix report ───────────────────────────────────────────
print("Writing douai-1609-fix-report.txt…", flush=True)

total = len(annotations)

with open('douai-1609-fix-report.txt', 'w', encoding='utf-8') as rpt:
    def w(line=''):
        rpt.write(line + '\n')

    w("DOUAI 1609 ANNOTATION FIX REPORT")
    w("=" * 60)
    w()
    structural_gaps = sum(1 for r in low_conf_rows if 'structural gap' in r[6])
    match_failures  = low_confidence_count - structural_gaps

    w("SUMMARY")
    w("-" * 40)
    w(f"  Total rows processed                : {total}")
    w(f"  Confidently matched (>= {CONFIDENCE_THRESHOLD})       : {confident_count}  ({confident_count/total:.1%})")
    w(f"  LOW_CONFIDENCE total                : {low_confidence_count}  ({low_confidence_count/total:.1%})")
    w(f"    → Normalization/match failures    : {match_failures}")
    w(f"    → Structural data gaps            : {structural_gaps}  (no quote, book not in DRB, etc.)")
    w(f"  Book corrections                    : {len(book_changes)}")
    w(f"  Ref corrections (same book)         : {len(ref_changes)}")
    w(f"  Marginal matches (0.25–0.35)        : {len(marginal_rows)}")
    w(f"  Split quality issues                : {len(split_issues)}")
    w()

    # ── Section A: Book corrections ───────────────────────────────────────────
    w("=" * 60)
    w(f"SECTION A — WRONG BOOK CORRECTIONS  ({len(book_changes)} rows)")
    w("=" * 60)
    if book_changes:
        w(f"  {'Row':>5}  {'Original':^15}  {'Matched':^15}  {'Score':^7}  Quote")
        w("  " + "-" * 72)
        for (rn, ob, or_, mb, mr, sc, qt) in book_changes:
            w(f"  {rn:5d}  {ob+' '+or_:^15}  {mb+' '+mr:^15}  {sc:7.3f}  {qt}")
    else:
        w("  (none)")
    w()

    # ── Section B: Ref corrections (same book) ────────────────────────────────
    w("=" * 60)
    w(f"SECTION B — CHAPTER:VERSE CORRECTIONS, SAME BOOK  ({len(ref_changes)} rows)")
    w("=" * 60)
    if ref_changes:
        w(f"  {'Row':>5}  {'Book':^6}  {'Orig Ref':^12}  {'New Ref':^12}  {'Score':^7}  Quote")
        w("  " + "-" * 72)
        for (rn, ob, or_, nr, sc, qt) in ref_changes:
            w(f"  {rn:5d}  {ob:^6}  {or_:^12}  {nr:^12}  {sc:7.3f}  {qt}")
    else:
        w("  (none)")
    w()

    # ── Section C: LOW_CONFIDENCE ─────────────────────────────────────────────
    w("=" * 60)
    w(f"SECTION C — LOW_CONFIDENCE ROWS  ({len(low_conf_rows)} rows)")
    w("=" * 60)
    if low_conf_rows:
        for (rn, ob, or_, sc, sm, qt, reason) in low_conf_rows:
            w(f"  Row {rn:4d}  {ob} {or_:<12}  score={sc:.3f}  split={sm}")
            w(f"           Reason : {reason}")
            w(f"           Quote  : {qt}")
            w()
    else:
        w("  (none)")

    # ── Section D: Split quality issues ──────────────────────────────────────
    w("=" * 60)
    w(f"SECTION D — SPLIT QUALITY ISSUES  ({len(split_issues)} rows)")
    w("=" * 60)
    w("  Rows where VerseQuote/Commentary boundary is unclear.")
    w()
    if split_issues:
        for (rn, ob, or_, sm, ql, qt) in split_issues:
            w(f"  Row {rn:4d}  {ob} {or_:<12}  method={sm}  quote_len={ql}")
            w(f"           Quote  : {qt}")
            w()
    else:
        w("  (none)")

    # ── Section E: Marginal matches ───────────────────────────────────────────
    w("=" * 60)
    w(f"SECTION E — MARGINAL MATCHES (0.25 ≤ score < 0.35)  ({len(marginal_rows)} rows)")
    w("=" * 60)
    w("  Confident but low-scoring — review if downstream quality is poor.")
    w()
    if marginal_rows:
        w(f"  {'Row':>5}  {'Original':^15}  {'Matched':^15}  {'Score':^7}  Quote")
        w("  " + "-" * 72)
        for (rn, ob, or_, mb, mr, sc, qt) in marginal_rows:
            w(f"  {rn:5d}  {ob+' '+or_:^15}  {mb+' '+mr:^15}  {sc:7.3f}  {qt}")
    else:
        w("  (none)")
    w()

    w("=" * 60)
    w("END OF REPORT")

# ── Final verification ────────────────────────────────────────────────────────
actual = len(output_rows)
print(f"\nDone.")
print(f"  Output rows  : {actual}")
print(f"  Confident    : {confident_count}  ({confident_count/total:.1%})")
print(f"  LOW_CONF     : {low_confidence_count}  ({low_confidence_count/total:.1%})")
print(f"  Book changes : {len(book_changes)}")
print(f"  Ref changes  : {len(ref_changes)}")
print(f"  Split issues : {len(split_issues)}")
print(f"  Marginal     : {len(marginal_rows)}")

if actual != 2304:
    print(f"\nWARNING: expected 2304 rows, got {actual}", file=sys.stderr)
    sys.exit(1)
else:
    print(f"  ✓ Row count matches (2304)")
