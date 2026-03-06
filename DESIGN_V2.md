# drb-ios v2.0 — Design Spec
## "Trad Catholic Logos"

**Owner:** Augustine (Engineering)  
**Priority:** P0 — Tim's explicit request  
**Goal:** Multi-pane synchronized Bible study interface with all commentary sources from the CLI

---

## Vision

Open multiple panels side by side. Each panel shows a different resource (DRB text, Haydock, Lapide, Chrysostom, Aquinas, Douai-1609). Navigate in one panel — all linked panels jump to the same passage. Like Logos Bible Software but stripped down, fast, and trad Catholic.

---

## Resources

All content must be loadable as panels:

| Resource | Source File | Coverage | Rows |
|---|---|---|---|
| DRB Bible | drb.tsv | Full OT+NT | ~31K |
| Haydock Commentary | haydock.tsv | Full Bible | ~35K |
| Cornelius à Lapide | lapide.tsv + lapide-ot/*.tsv | Growing OT | ~7K+ |
| Douai-1609 | douai-1609-clean.tsv | Partial OT | ~2.4K |
| Chrysostom | chrysostom-matthew.tsv + chrysostom-john.tsv + chrysostom-epistles.tsv | Mt, Jn, Rom, 1Cor, Phil | ~270 |
| Aquinas | aquinas-psalms.tsv + aquinas-isaiah.tsv | Psalms, Isaiah | ~104 |

TSV sources for Chrysostom and Aquinas are in the drb CLI project at:
`../drb/chrysostom-matthew.tsv` etc. — copy them into the iOS project.

---

## Architecture

### Data Layer — SQLite

Replace runtime TSV loading with SQLite for performance.

Schema:
```sql
CREATE TABLE verses (
    book TEXT NOT NULL,
    chapter INTEGER NOT NULL,
    verse INTEGER NOT NULL,
    text TEXT NOT NULL,
    PRIMARY KEY (book, chapter, verse)
);

CREATE TABLE commentary (
    source TEXT NOT NULL,      -- 'haydock', 'lapide', 'chrysostom', 'aquinas', 'douai'
    book TEXT NOT NULL,
    chapter INTEGER NOT NULL,
    verse INTEGER NOT NULL,
    text TEXT NOT NULL
);
CREATE INDEX idx_commentary ON commentary(source, book, chapter);
```

- Build SQLite DB at first launch from bundled TSV files
- Cache in app's Documents directory
- `DatabaseManager.swift` — singleton, handles all reads
- Async loading, no blocking main thread

### Navigation State

```swift
class BibleNavigator: ObservableObject {
    @Published var book: String = "Gn"
    @Published var chapter: Int = 1
    @Published var verse: Int? = nil
    
    // Navigate all linked panels
    func navigate(book: String, chapter: Int, verse: Int? = nil) {
        self.book = book
        self.chapter = chapter
        self.verse = verse
    }
}
```

Single `@StateObject` at the root view, passed via `@EnvironmentObject` to all panels.

### Panel System

```swift
enum ResourceType: String, CaseIterable, Identifiable {
    case drb = "Douay-Rheims"
    case haydock = "Haydock"
    case lapide = "Lapide"
    case chrysostom = "Chrysostom"
    case aquinas = "Aquinas"
    case douai = "Douai 1609"
    var id: String { rawValue }
}

struct Panel: Identifiable {
    let id = UUID()
    var resource: ResourceType
    var isLinked: Bool = true  // linked = follows BibleNavigator
}
```

---

## UI Design

### iPad Layout (Primary)

Horizontal split view, 2–4 panels side by side. Each panel:

```
┌─────────────────────────────────────────┐
│ [DRB ▼] [📌] [←] Genesis 1 [→]        │  ← Panel header
├─────────────────────────────────────────┤
│ 1. In the beginning God created heaven  │
│    and earth.                           │
│                                         │
│ 2. And the earth was void and empty...  │
│                                         │
│ [verse list, tappable]                  │
└─────────────────────────────────────────┘
```

Panel header elements:
- Resource picker dropdown (DRB / Haydock / Lapide / etc.)
- 📌 Link toggle — linked panels follow BibleNavigator; unlinked panels navigate independently
- ← → chapter navigation (broadcasts to all linked panels when linked)
- Book/chapter display (tappable = full navigator)

Add/remove panels:
- Toolbar button "+" → adds a new panel (default: Haydock, linked)
- Each panel has an "×" close button in header

### iPhone Layout

Tab bar with one panel per tab. Same navigation state syncs across tabs. Swipe between chapters.

### Panel Content

**DRB Panel:**
- Verse list: verse number + DRB text
- Tap verse → sets `navigator.verse` → commentary panels scroll to that verse
- Swipe left/right = next/previous chapter

**Commentary Panel (Haydock, Lapide, etc.):**
- Chapter-level view: show all commentary entries for current chapter
- Each entry shows: `v.N  [commentary text]`
- When `navigator.verse` is set, scroll to that verse entry + highlight it briefly
- If no commentary for current passage: show "No [source] commentary for this chapter"

**Source Attribution:**
- Each commentary panel shows source name + small info (i) → shows provenance note

---

## Navigation

### Book/Chapter Picker
- Tap book/chapter display in panel header → sheet with:
  - Scrollable book list (grouped: Pentateuch, Historical, Wisdom, Prophets, Gospels, Epistles, etc.)
  - Chapter grid per book
  - Confirms navigation → updates BibleNavigator

### Cross-References
- DRB text contains cross-refs (when available) — tappable
- Opens in linked panel or presents passage inline

---

## Implementation Plan for Augustine

### Phase 1 (Sprint 1 — Core Redesign)
1. Add `DatabaseManager.swift` — SQLite setup, TSV import at first launch, all 6 sources
2. Copy Chrysostom TSVs (chrysostom-matthew.tsv, chrysostom-john.tsv, chrysostom-epistles.tsv) and Aquinas TSVs (aquinas-psalms.tsv, aquinas-isaiah.tsv) into the Xcode project, add to target
3. Update `BibleNavigator.swift` — shared navigation state
4. Build `PanelView.swift` — generic panel container with header, resource picker, link toggle
5. Build `DRBPanelContent.swift` — DRB verse list with tap-to-select-verse
6. Build `CommentaryPanelContent.swift` — chapter commentary display, verse highlight on sync
7. Build `MultiPaneView.swift` — iPad horizontal split, iPhone tab bar
8. Replace current `ContentView.swift` with MultiPaneView
9. Book/chapter picker sheet

### Phase 2 (Sprint 2 — Polish)
- Full-text search across all resources
- Bookmarks that save resource+panel state
- Reading plans
- Verse highlighting/notes
- Export passage + commentary to text

---

## Constraints

- iOS 16+ deployment target
- SwiftUI only — no UIKit unless absolutely necessary
- No external dependencies — Swift Package Manager only if needed for SQLite (use SQLite.swift or raw sqlite3)
- Dark mode + light mode support (use existing Theme.swift)
- No Internet connection required — all data bundled
- Pre-push hook must pass — no system paths, no PII in code

---

## Files to Create/Modify

**New:**
- `DatabaseManager.swift`
- `BibleNavigator.swift` (replaces NavigationState)
- `PanelView.swift`
- `DRBPanelContent.swift`
- `CommentaryPanelContent.swift`
- `MultiPaneView.swift`
- `ResourceType.swift`
- `BookPickerView.swift`

**Modified:**
- `ContentView.swift` → replaced by MultiPaneView
- `CommentaryManager.swift` → replaced by DatabaseManager
- `BibleData.swift` → replaced by DatabaseManager

**New data files (copy from drb CLI project):**
- `chrysostom-matthew.tsv`
- `chrysostom-john.tsv`
- `chrysostom-epistles.tsv`
- `aquinas-psalms.tsv`
- `aquinas-isaiah.tsv`

---

## Commit Convention
`feat: [description] [Augustine]`

Notify on completion:
`openclaw system event --text "Done: drb-ios v2.0 multi-pane Logos-style redesign complete" --mode now`

---

## Polish & "Make It Awesome" Details

### Typography
- DRB text: use a proper serif for scripture. System serif (Georgia or New York) at 18pt minimum
- Commentary text: slightly smaller (16pt), same serif
- Verse numbers: small caps style, muted color, superscript or inline
- Chapter headings: bold, slightly larger

### Visual Aesthetic
- Dark mode first — deep navy/charcoal background (#1a1a2e or system dark)
- Light mode: warm parchment-ish white (not pure #FFFFFF — use #FAF8F2)
- Accent color: deep crimson for interactive elements
- Panel dividers: subtle, 1pt, slightly lighter than background
- Panel headers: slightly elevated (shadow or border-bottom), contains resource picker

### Verse Interaction
- Tap verse in DRB panel → verse number highlights (crimson underline), commentary panel scrolls and highlights matching entry
- Long press on verse → context menu: Copy Verse, Copy with Reference, Bookmark, Share
- Double-tap verse number → jump to cross-references (if available)

### Commentary Display
- Each commentary entry: verse number chip (small crimson pill badge) + commentary text
- When synced-verse is active: highlight entry with subtle background glow, scroll into view with animation
- "No commentary for this passage" state: graceful empty state with book/verse info, not just blank
- Patristic citations (Augustine, Jerome, Chrysostom mentions in Haydock/Lapide): render in italic or distinct style

### Navigation Feel
- Chapter swipe: horizontal swipe left/right on DRB panel advances/retreats chapters, smooth spring animation
- All linked panels follow with matching animation
- Chapter transition: brief fade or slide — not jarring
- Book picker: searchable, shows book abbreviation + full name, canonical Catholic ordering (Pentateuch → Historical → Wisdom → Prophets → NT)

### Panel Management (iPad)
- Drag panel dividers to resize
- Minimum panel width: ~300pt
- Panel close button: appears on hover/tap of panel header area
- "+" button in toolbar → panel picker sheet (choose resource, link state)
- Up to 4 panels on iPad Pro, 2 on standard iPad

### Toolbar (top-level)
- Left: app name / logo area
- Center: current passage reference (e.g. "Genesis 1") — tappable = book picker
- Right: Search (magnifying glass), Bookmarks, Settings

### Loading Performance
- SQLite import runs once at first launch, shows progress bar
- After that: instant (SQLite indexed reads)
- Lazy load verse text — don't load all 31K verses into memory
- Commentary for current chapter only — paginate by chapter

### Empty States
- First launch: brief welcome screen showing available resources with icons
- No commentary: "Lapide has no commentary for Judges 7 yet — the translation is ongoing"
- Search no results: helpful empty state

### Accessibility
- Dynamic Type support on all text
- VoiceOver labels on all interactive elements
- High contrast mode support
- Reduce Motion: disable chapter transition animations

