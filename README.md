# Douay-Rheims Bible for iOS

**The classic Catholic Bible on your iPhone and iPad.**

`73 Books · 3 Commentaries · Reading Plans · iPad Optimized`

A native iOS app for reading the Douay-Rheims Bible (Challoner revision) with the complete Catholic canon, Haydock commentary, Cornelius à Lapide, and 1609 Douai annotations. No account required. No subscriptions. No tracking.

---

## Features

- **Full Douay-Rheims text** — all 73 books, 35,805 verses, Vulgate order
- **Three commentary sources** — Haydock (full Bible, 35,000+ entries), Cornelius à Lapide (New Testament), and original 1609 Douai annotations
- **iPad layout** — NavigationSplitView with side-by-side commentary panel; tap a verse to open commentary without leaving the text
- **iPhone layout** — clean tab-based navigation with bottom-sheet commentary
- **Full-text search** — search across every verse instantly
- **Bookmarks** — long-press any verse to bookmark; share or copy with context menus
- **Reading plan** — "Bible in a Year" covering all 73 books in canonical order, with daily progress tracking
- **Customizable typography** — adjustable font size and line spacing using Georgia serif
- **Latin/English toggle** — switch prayer language where applicable
- **Dark mode** — full support with liturgical-inspired theming
- **Offline** — everything is bundled; no network connection needed

## iPad

On iPad, the app uses a three-column NavigationSplitView:

1. **Sidebar** — books, search, reading plan, bookmarks, settings
2. **Chapter list** — chapters for the selected book
3. **Reading pane** — verses with an inline commentary side panel (420pt)

Tap any verse to slide open the commentary panel without navigating away.

## Commentary

| Source | Coverage | Entries |
|--------|----------|---------|
| **Haydock** (Rev. George Leo Haydock, 1859) | Full Bible | 35,000+ |
| **Cornelius à Lapide** (English NT) | Gospels, Epistles | 2,400+ |
| **1609 Douai Annotations** | Original Douai notes | 3,100+ |

All commentary texts are public domain (pre-1928).

## Requirements

- iOS 17.0+
- iPadOS 17.0+
- Xcode 15+

## Build

```sh
git clone https://github.com/ecclesia-dev/drb-ios.git
cd drb-ios
open DouayRheims.xcodeproj
```

Build and run on simulator or device. No external dependencies.

## Related Projects

| Project | Description |
|---------|-------------|
| **[drb](https://github.com/ecclesia-dev/drb)** | Douay-Rheims Bible (terminal) |
| **[rosary-ios](https://github.com/ecclesia-dev/rosary-ios)** | Holy Rosary app for iOS |
| **[calendar-ios](https://github.com/ecclesia-dev/calendar-ios)** | 1962 Liturgical Calendar for iOS |

*Ad Maiorem Dei Gloriam.*

## Built by

Crafted by the [ecclesia-dev](https://github.com/ecclesia-dev) agent team.
