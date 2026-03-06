# SCREENSHOT_SPECS.md — App Store Screenshots
## Douay-Rheims Bible (drb-ios)

> Art Director: Giotto 🖌️  
> Date: 2026-03-04  
> Device: iPhone 15 Pro Max (6.7" display, 2796×1290 px @ 460ppi)  
> Target user: Traditional Catholic seeking a serious Scripture study tool  
> Status: Ready for design production

---

### Design Notes (All Screenshots)

**Color mode:** Light mode is primary (parchment background is warmer and more inviting in app store context). Include 1–2 dark mode variants as alternates if budget allows.

**Typography on frames:** Use Georgia or a close editorial serif for caption text. Burgundy (`#8B3849`) or gold (`#B89A59`) on cream/white backgrounds.

**Status bar:** Use a clean mock (9:41 AM, full signal, full battery). Do not show notification badges.

**Screen chrome:** Show the iPhone 15 Pro Max frame (natural titanium). Keep bezels minimal; content should dominate.

**Caption placement:** Bottom third of the device frame, below the screen area, in a colored band. Not overlaid on the screenshot itself — the UI speaks for itself.

---

## Screenshot 1 — The Full Catholic Bible

**Screen shown:** `BookListView` — the main book list, scrolled to show both Testaments

**Content to display:**
- Old Testament section visible, starting with Genesis
- Scroll position: show the **Deuterocanonical books labeled in gold** — specifically Tobit, Judith, Wisdom visible in list
- Each book row shows: book name (Georgia serif, burgundy accent for deuterocanonical label), chapter count on right
- Bottom tab bar visible with "Bible" tab selected

**Specific data to show:**
```
Old Testament
  Genesis          50 chapters
  Exodus           40 chapters
  ...
  Tobit            14 chapters  [Deuterocanonical — gold label]
  Judith           16 chapters  [Deuterocanonical — gold label]
  ...
```

**Why this is compelling:**
Traditional Catholics know immediately this is a *real* Catholic Bible. Seeing "Deuterocanonical" labeled in gold on Tobit and Judith signals fidelity to the full 73-book canon — something Protestants removed. This is a differentiation screenshot.

**Caption text (below device frame):**
> **All 73 Books**  
> The complete Catholic canon — deuterocanonical books included.

---

## Screenshot 2 — Reading Scripture in Beauty

**Screen shown:** `ChapterView` — reading a chapter, mid-scroll

**Content to display:**
- Book: **John**, Chapter 1
- Show verses 1–14 ("In the beginning was the Word...")
- Verse numbers in burgundy, verse text in Georgia serif on parchment
- Font size: large (setting at ~20pt to fill the screen beautifully)
- Line spacing: generous
- Navigation header: "Jn 1" centered, back chevron

**Specific verse text visible:**
```
1  In the beginning was the Word, and the Word was with 
   God, and the Word was God.
2  The same was in the beginning with God.
3  All things were made by him: and without him was made 
   nothing that was made.
...
14 And the Word was made flesh, and dwelt among us...
```

**Why this is compelling:**
The Douay-Rheims prose is unmistakably beautiful and distinctly Catholic. Any trad Catholic will recognize "And the Word was made flesh" from the Last Gospel of the Mass. This screenshot sells the reading experience: clean, typographically excellent, parchment-warm.

**Caption text:**
> **Sacred Scripture in the Challoner Revision**  
> The Douay-Rheims — as it has always been read.

---

## Screenshot 3 — Commentary Side by Side

**Screen shown:** `ChapterView` (iPhone) with `CommentarySheet` open at `.large` detent

**Content to display:**
- Background: John 1:1 visible (highlighted/selected, faint burgundy wash)
- Commentary sheet pulled up, showing:
  - Verse reference: **John 1:1** in burgundy
  - Verse text in italic Georgia
  - Source tab: **Haydock** selected
  - Source subtitle: "Bishop Haydock's Catholic Family Bible, 1811"
  - Commentary body: 3–4 lines of Haydock's actual commentary text

**Sample commentary text to show (approximate Haydock on Jn 1:1):**
```
In the beginning. Before all time, or from eternity. The 
Word: the Son of God, the second Person of the 
Blessed Trinity, called the Word, because eternally 
begotten of the Father...
```

- Second source tab visible: **Cornelius** (not selected, greyed)

**Why this is compelling:**
This is the killer feature. No other free app gives you Haydock *and* Cornelius à Lapide on the same verse. Traditional Catholics know these names — Haydock is a staple of Catholic homes. Showing commentary open beside the text proves the app is for serious study, not casual reading.

**Caption text:**
> **Three Classic Commentaries**  
> Haydock · Cornelius à Lapide · Original Annotations — tap any verse.

---

## Screenshot 4 — Full-Text Search Across 35,805 Verses

**Screen shown:** `SearchView` — active search with results displayed

**Content to display:**
- Search bar at top with query: **"Blood of the New Testament"** (a distinctly Catholic phrase from the Mass)
- Results count: "3+ results"
- First 3 results visible, each showing:
  - Reference in burgundy (e.g., "Mt 26:28")
  - Verse text in Georgia: "For this is my blood of the new testament, which shall be shed for many unto remission of sins."
  - Second result: Mk 14:24
  - Third result: Lk 22:20

**Why this is compelling:**
The search query is liturgically loaded — traditional Catholics will immediately recognize it from the Canon of the Mass. Showing that the search works across the entire Bible for this phrase communicates both the depth of the text and that the app understands its audience. It also showcases the beauty of the Douay-Rheims language compared to modern translations.

**Caption text:**
> **Search Every Verse**  
> Find any word or phrase across all 35,805 verses instantly.

---

## Screenshot 5 — Bible in a Year Reading Plan

**Screen shown:** `ReadingPlanView` — plan in progress view

**Content to display:**
- Day header: **"Day 47 of 365"** (in progress, not day 1)
- Progress bar: ~13% filled, burgundy tint
- Subtext: "47 of 365 days completed"
- "Today's Reading" section:
  - Passages: "Exodus 16–18" with a NavigationLink arrow
  - "Mark as Read" button in burgundy (not yet tapped)
- "Upcoming" section showing next 3 days:
  ```
  Day 48   Exodus 19-21
  Day 49   Exodus 22-24
  Day 50   Exodus 25-27
  ```

**Why this is compelling:**
A Bible-in-a-Year plan covering all 73 books is something many Catholics attempt but few apps make easy with the Douay-Rheims specifically. Showing a plan in-progress (not at Day 1) makes it feel real and achievable. The presence of Exodus suggests Old Testament coverage — which many reading plans skip or rush.

**Caption text:**
> **Read the Bible in a Year**  
> All 73 books — a plan you can actually finish.

---

## Production Notes

- All screenshots should be captured or mocked at **2796×1290 px** (iPhone 15 Pro Max native)
- App Store requires this size for the 6.7" slot
- Submit in order: 1 → 5 (first screenshot is highest-impact; App Store shows it in search results without tapping)
- If possible, capture screenshots on a device with parchment light mode and a fresh font size setting of 19pt
- Dark mode variants (screenshots 2 and 3) would be strong alternates for the "More screenshots" section

*Ad maiorem Dei gloriam.*
