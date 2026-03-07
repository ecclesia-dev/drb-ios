#!/usr/bin/env python3
"""
Jerome's Douai 1609 v5 fix script
Applies Bellarmine-directed corrections to douai-1609-fixed-v4.tsv
"""

import re

INPUT  = "douai-1609-fixed-v4.tsv"
OUTPUT = "douai-1609-fixed-v5.tsv"

# Counters
fix1_heb_to_ex   = 0
fix2_is_verse    = 0
fix2_is_lc_added = 0
fix3_mk_to_prv   = 0
fix4_lk_to_1mc   = 0
fix5_approved    = 0
fix5_lc          = 0

# Heb→Ex: only Exodus-chapter rows (ch 2, 3, 6) with Exodus content keywords
# These are lines 105-117 in the file (NR 105-117 in 1-indexed awk = 0-indexed python rows 104-116)
HEB_EXODUS_PATTERN = re.compile(
    r'[Pp]harao|AEgypt|AEcypt|Moyfes|midwi|male.child|male-child|drowning|drown',
    re.IGNORECASE
)
# Only target Heb chapters that correspond to Exodus (2, 3, 6) - Heb ch1 is real Hebrews
HEB_EXODUS_CHAPTERS = {'2', '3', '6'}

with open(INPUT, 'r', encoding='utf-8') as fin:
    lines = fin.readlines()

header = lines[0].rstrip('\n').rstrip('\t')
out_lines = []

# New header with Status column
out_lines.append(header + '\tStatus\n')

for i, line in enumerate(lines[1:], start=2):  # 1-indexed line number
    row = line.rstrip('\n').rstrip('\t')
    fields = row.split('\t')

    # Normalise to exactly 4 fields
    while len(fields) < 4:
        fields.append('')
    fields = fields[:4]  # drop any extra empty trailing cols

    book, chverse, quote, commentary = fields

    changed = False

    # --- Fix 1: Heb Exodus rows → Ex ---
    if book == 'Heb':
        chap = chverse.split(':')[0] if ':' in chverse else ''
        if chap in HEB_EXODUS_CHAPTERS:
            if (HEB_EXODUS_PATTERN.search(quote) or
                    HEB_EXODUS_PATTERN.search(commentary)):
                book = 'Ex'
                fix1_heb_to_ex += 1
                changed = True

    # --- Fix 2: Isaiah impossible chapter:verse ---
    if book == 'Is':
        if chverse == '99:3':
            chverse = '36:3'
            fix2_is_verse += 1
            changed = True
        elif chverse == '109:2':
            chverse = '36:2'
            fix2_is_verse += 1
            changed = True
        # Is 3:X where X>10 — flag LOW_CONFIDENCE if not already
        elif chverse.startswith('3:'):
            try:
                v = int(chverse.split(':')[1])
                if v > 10:
                    if '[LOW_CONFIDENCE]' not in quote and '[LOW_CONFIDENCE]' not in commentary:
                        commentary += ' [LOW_CONFIDENCE]'
                        fix2_is_lc_added += 1
                        changed = True
            except ValueError:
                pass

    # --- Fix 3: Mk rows with Proverbs bleed ---
    if book == 'Mk':
        PRV_PAT = re.compile(
            r'wise son|glutton|shameth his father|rich man seemeth|'
            r'poor man being prudent|searcheth him',
            re.IGNORECASE
        )
        if PRV_PAT.search(quote) or PRV_PAT.search(commentary):
            book = 'Prv'
            fix3_mk_to_prv += 1
            changed = True

    # --- Fix 4: Lk rows with 1Mc bleed ---
    if book == 'Lk':
        MC_PAT = re.compile(
            r'Antiochus|Eupatour|Maccab|Judas Machabeus',
            re.IGNORECASE
        )
        if MC_PAT.search(quote) or MC_PAT.search(commentary):
            book = '1Mc'
            fix4_lk_to_1mc += 1
            changed = True

    # --- Fix 5: Status column ---
    has_lc = (
        '[LOW_CONFIDENCE]' in quote or
        '[LOW_CONFIDENCE]' in commentary
    )
    if has_lc:
        status = 'LOW_CONFIDENCE'
        fix5_lc += 1
    else:
        status = 'APPROVED'
        fix5_approved += 1

    out_fields = [book, chverse, quote, commentary, status]
    out_lines.append('\t'.join(out_fields) + '\n')

with open(OUTPUT, 'w', encoding='utf-8') as fout:
    fout.writelines(out_lines)

print("=== Jerome v5 Fix Report ===")
print(f"Input rows (excl. header): {len(lines)-1}")
print(f"Output rows (excl. header): {len(out_lines)-1}")
print()
print(f"Fix 1 — Heb→Ex (Exodus ch2/3/6 misattributed): {fix1_heb_to_ex}")
print(f"Fix 2 — Isaiah impossible verse corrected:        {fix2_is_verse}")
print(f"Fix 2 — Isaiah Is 3:X>10 flagged LOW_CONFIDENCE: {fix2_is_lc_added}")
print(f"Fix 3 — Mk→Prv (Proverbs bleed):                 {fix3_mk_to_prv}")
print(f"Fix 4 — Lk→1Mc (1Maccabees bleed):               {fix4_lk_to_1mc}")
print(f"Fix 5 — Status=APPROVED:                          {fix5_approved}")
print(f"Fix 5 — Status=LOW_CONFIDENCE:                    {fix5_lc}")
print()
print(f"Output written: {OUTPUT}")
