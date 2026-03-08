THEOLOGY GATE: NEEDS REVISION [Bellarmine ⛪]
Date: 2026-03-07

Summary:
  The v4 Douai 1609 annotation file (2304 rows) was reviewed for doctrinal
  orthodoxy, source authenticity, and attribution accuracy. The three manually
  corrected book labels (Sg→Is, Rom→Jas, Phlm→Heb) are confirmed correct.
  The doctrinal *content* throughout is solidly Tridentine Catholic — no
  heterodox material detected. However, three technical misattribution problems
  remain that would ship wrong annotations to users reading specific Bible
  verses, which constitutes a practical doctrinal harm. Review is therefore
  NEEDS REVISION before push.

---

Findings:

**✅ THREE-BOOK CORRECTIONS — CONFIRMED CORRECT**

  - Sg→Is (23 rows): Content confirmed Isaiah — references to Ezechias,
    Assyrians, Rabshakeh, Sennacherib, Jerusalem. Correct.
  - Rom→Jas (24 rows): Content confirmed James — Anointing of the Sick
    (James 5), Elias prayer, Confession, faith and works. Correct.
  - Phlm→Heb (38 rows): Content confirmed Hebrews — high priesthood of
    Christ, Melchizedek, entering God's rest, Heretics defined per
    Augustine. Correct.

**✅ DOCTRINAL ORTHODOXY — PASSED**

  All annotation content reviewed is faithful to Trent and traditional
  Catholic doctrine. Specific confirmations:

  - Sacrament of Anointing of the Sick (Jas 5:14-15): Explicitly defended
    as sacrament vs. Protestant denial. Priests named; oil named; remission
    of sins confirmed. Orthodox.
  - Confession (Jas 5:16): "Confess therefore your sins" with annotation
    defending auricular confession. Orthodox.
  - Eucharistic Sacrifice / Mass (Heb annotations): Repeatedly defends the
    Mass as a true sacrifice, attacks Protestant denial. Orthodox.
  - Priestly ordination (Heb 5:1-4): Defends the necessity of a called
    priesthood. Attacks Protestant lay ministry. Orthodox.
  - Invocation of Saints (Heb 4:16): Explicitly defends against Protestant
    objections. Orthodox.
  - Merit of good works (Heb 10, Jas 2): Strongly defended against
    Pelagian and Protestant errors. Orthodox.
  - Faith alone (sola fide) rejected: James 2 annotations directly oppose
    the Protestant formula; Paul and James reconciled correctly. Orthodox.
  - Papal/Church authority referenced throughout. Orthodox.

**✅ ARCHAIC 1609 SOURCE — CONFIRMED**

  Archaic spelling consistent with 1609 original throughout: "vvhich",
  "fhal", "vpon", "Prieft", "finne", "Sainéts", "Sacrament", "hath",
  long-s (ſ) OCR artifacts ("fhall", "{pirit", "faid"), Latin citations.
  No smooth modern DRB prose detected in the primary annotation text.
  Note: 36 rows in v3 were matched "via modern-drb" per the fix report;
  these carry forward into v4. Visual inspection of likely candidates shows
  the verse-quote OCR artifacts are still present, suggesting the modern-drb
  matching only used modern text as a *reference* for verse identification,
  not as the actual source text. No clean modern English substitution found.

**❌ ISSUE 1 — ~11 Heb rows contain Exodus content (WRONG BOOK)**

  The Phlm→Heb correction was correct for its 38 rows. However, there are
  approximately 11 additional Heb rows (not BOOK_CORRECTED, present since v3)
  whose content is demonstrably from the Book of Exodus, not Hebrews:

  - Heb 2:15 → "commanding to kill and to drown all the male-children" (Ex 1)
  - Heb 2:19 → "Hebrew women are not [dead]" — midwives' answer to Pharaoh (Ex 1:19)
  - Heb 2:23 → "the King of Egypt died; children of Israel groning" (Ex 2:23)
  - Heb 2:7  → Moses' parents, Pharaoh's order (Ex 2)
  - Heb 2:4  → bare-foot reverence for holy places; commentary on Ex 3 (burning bush)
  - Several more with "Moyfes", "AEgypt", "Pharao" content

  These appear to be v3 algorithmic errors: the matcher assigned Exodus
  content to Heb 2:X. A user reading Hebrews 2 in the app would receive
  Exodus commentary — misleading and practically harmful.

  **For Jerome:** Flag and re-attribute these ~11 rows. Correct book is Ex
  (Exodus). Run: `awk -F'\t' '$1=="Heb" && ($3 ~ /midwiu|Pharao|AEgypt|male.child/ || $4 ~ /midwiu|Pharao/)' douai-1609-fixed-v4.tsv`
  to identify them.

**❌ ISSUE 2 — Isaiah chapter:verse references systematically wrong**

  Of 36 Isaiah rows: the majority are tagged with chapter "3" (Is 3:1,
  Is 3:2, Is 3:3, etc.) even though the quoted content spans Isaiah
  chapters 26, 30, 31, 32, 33, 36+. Two rows even show impossible
  references: "Is 99:3" and "Is 109:2" (Isaiah has only 66 chapters).

  The book label (Is) is correct thanks to the Sg→Is fix, but the
  chapter:verse is OCR garbage for most of these rows. A user tapping
  any verse in Is 3 would receive commentary belonging to Is 26, 30, etc.

  **For Jerome:** The Is rows need chapter:verse re-matching against the
  1609 Rheims/Douai source text. Do not use algorithmic v3 chapter refs for
  these rows — they are unreliable. Manual verification recommended.
  Priority rows to fix: all "Is 3:X" where X > 10, and "Is 99:3", "Is 109:2".

**❌ ISSUE 3 — Some Mk rows contain Proverbs content (WRONG BOOK)**

  Spot check of Mk rows:
  - Mk 16:2 → "He that keepeth the law is a wise son... feedeth gluttons,
    shameth his father" — this is Proverbs 28:7, not Mark.
  - Mk 16:11 → "The rich man seemeth to himself wise; the poor man being
    prudent shall search him" — Proverbs 28:11, not Mark.

  **For Jerome:** Audit all Mk rows for Proverbs content bleeding in.
  This is likely another v3 algorithmic misattribution.

**⚠️ WARNING — 935 LOW_CONFIDENCE rows (40.6%) not yet reviewed**

  After v4, 935 rows remain flagged [LOW_CONFIDENCE]. These have reasonable
  content (853 of 961 have substantive verse quotes) but unverified
  chapter:verse references. They are present throughout all major books
  (Ps: largest count; Prv, Jn, Gn, etc.).

  These rows are NOT safe to ship to production without at minimum a
  statistical spot-check of attribution quality per book. The Psalm rows
  in particular show suspicious chapter patterns (many clustered at
  "Ps 19:X") suggesting the same algorithmic mismatch seen in Isaiah.

  **Recommendation:** Do not ship LOW_CONFIDENCE rows to production.
  Either hide them in the UI with a flag, or require Jerome to pass them
  through a v5 re-matching before push.

---

Detailed Spot-Check Sample (30 rows reviewed explicitly):

  Row 2 (Gn 22:13): Abraham and the ram — CORRECT attribution, archaic ✅
  Row 4 (Gn 22:1): Abraham's obedience, Isaac as figure of Christ — CORRECT ✅
  Jas 2198-2205 (Jas 1:22-1:26): Faith and works, Rahab, dead faith — CORRECT,
    orthodox defense of Catholic soteriology ✅
  Heb (BOOK_CORRECTED) rows: Melchizedek, priesthood, sacrifice, heretics —
    CORRECT, orthodox ✅
  Is (BOOK_CORRECTED) rows: Isaiah content confirmed; chapter:verse often wrong ⚠️
  Heb 2:15, 2:19, 2:23 etc. (non-corrected): Exodus content — WRONG BOOK ❌
  Mk 16:2, 16:11: Proverbs content — WRONG BOOK ❌
  Lk 1:21: "Antiochus the Noble... Eupatour" — likely 1Maccabees content ❌
  Ps 8:9, 19:X range: Psalm content but chapter refs suspect ⚠️
  Gal 1:19 (Peter at Jerusalem): Correct attribution, orthodox ✅
  1Cor 5:5, 5:13 (excommunication, satisfaction): Correct, orthodox ✅
  Col 40 rows (not sampled in detail): No red flags ✅
  Heb 1:1 (every high priest annotation): Superb Tridentine defense of
    priesthood and sacrifice — CORRECT, doctrinally outstanding ✅

---

Verdict: NEEDS REVISION

The doctrinal content of this file is sound — Robert Bellarmine himself
could have written many of these annotations. No heresy, no modernism,
no Protestant contamination in the commentary itself.

But the attribution errors are real: shipping Exodus commentary on
Hebrews 2, or Proverbs commentary on Mark 16, is a practical error that
would mislead users studying Scripture. A Catholic app must get the right
annotation on the right verse. That is not optional.

**Required fixes before re-review:**
  1. Re-attribute ~11 Heb rows → Ex (Exodus content confirmed)
  2. Re-match Is chapter:verse references (book label correct, refs wrong)
  3. Audit Mk rows for Proverbs bleed; re-attribute as needed
  4. Audit Lk rows for 1Mc bleed; re-attribute as needed
  5. Decision needed: ship LOW_CONFIDENCE rows (hidden/flagged) or hold for v5?

Once Jerome submits a v5 with the above fixed, Theology Gate will re-review
the corrected rows only (not the full 2304).

If next step is Pius (PR gate) — hold until v5 is ready.
If LOW_CONFIDENCE rows are to be hidden from production UI (not shown to users),
items 1-4 above are sufficient to APPROVE the confident rows for push.

— Bellarmine ⛪
  Theology Gate, Ecclesia Dev
  2026-03-07
