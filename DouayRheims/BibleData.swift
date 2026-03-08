import Foundation

// MARK: - Models

struct Verse: Identifiable, Hashable {
    let id: String  // "BookName:Chapter:Verse"
    let bookName: String
    let abbreviation: String
    let bookOrder: Int
    let chapter: Int
    let verse: Int
    let text: String
    let lowercasedText: String  // Fix 3: precomputed at parse time, zero alloc at search time

    var reference: String {
        "\(bookName) \(chapter):\(verse)"
    }

    var shortReference: String {
        "\(abbreviation) \(chapter):\(verse)"
    }
}

struct Book: Identifiable, Hashable {
    let id: String  // book name
    let name: String
    let abbreviation: String
    let order: Int
    let chapters: [Int]  // sorted chapter numbers
    let testament: Testament
}

enum Testament: String, CaseIterable {
    case oldTestament = "Old Testament"
    case newTestament = "New Testament"
}

// MARK: - Translation

enum Translation: String, CaseIterable {
    case challoner = "challoner"
    case vulgate   = "vulgate"
    case douai1609 = "douai1609"

    var displayName: String {
        switch self {
        case .challoner: return "Douay-Rheims (Challoner)"
        case .vulgate:   return "Clementine Vulgate"
        case .douai1609: return "Douay 1609 / Rheims 1582"
        }
    }
}

// MARK: - Bible Data Manager

@MainActor
final class BibleDataManager: ObservableObject {
    static let shared = BibleDataManager()

    @Published private(set) var books: [Book] = []
    @Published private(set) var isLoaded = false

    private var allVerses: [Verse] = []
    // Fix 2: Two-level index — O(1) chapter lookup instead of O(n) filter
    private var verseIndex: [String: [Int: [Verse]]] = [:]
    private var verseById: [String: Verse] = [:]

    // Parallel translation indexes (keyed by full book name, same as verseIndex)
    private var vulgateIndex: [String: [Int: [Verse]]] = [:]
    private var drb1609Index: [String: [Int: [Verse]]] = [:]

    // Flat verse arrays for search across non-Challoner translations
    private var vulgateVerses: [Verse] = []
    private var drb1609Verses: [Verse] = []

    private init() {
        // Fix 1: Load off the main thread — fire-and-forget Task on @MainActor,
        // actual CPU work runs in a detached Task on a background thread.
        Task {
            await loadDataAsync()
        }
    }

    // MARK: - Async Load (Fix 1)

    private func loadDataAsync() async {
        let result = await Task.detached(priority: .userInitiated) {
            BibleDataManager.parseData()
        }.value

        // Back on @MainActor — safe to publish
        self.allVerses = result.verses
        self.verseIndex = result.verseIndex
        self.verseById = result.verseById
        self.books = result.books
        self.vulgateIndex = result.vulgateIndex
        self.drb1609Index = result.drb1609Index
        self.vulgateVerses = result.vulgateVerses
        self.drb1609Verses = result.drb1609Verses
        self.isLoaded = true
    }

    // MARK: - Background parse (runs off main thread)

    private struct LoadResult {
        let verses: [Verse]
        let verseIndex: [String: [Int: [Verse]]]
        let verseById: [String: Verse]
        let books: [Book]
        let vulgateIndex: [String: [Int: [Verse]]]
        let drb1609Index: [String: [Int: [Verse]]]
        let vulgateVerses: [Verse]
        let drb1609Verses: [Verse]
    }

    nonisolated private static func parseData() -> LoadResult {
        // ── 1. Load Challoner (drb.tsv) ──────────────────────────────────────
        guard let drbURL = Bundle.main.url(forResource: "drb", withExtension: "tsv"),
              let drbData = try? String(contentsOf: drbURL, encoding: .utf8) else {
            return LoadResult(verses: [], verseIndex: [:], verseById: [:], books: [],
                              vulgateIndex: [:], drb1609Index: [:])
        }

        var verses: [Verse] = []
        var bookChapters: [String: (abbrev: String, order: Int, chapters: Set<Int>)] = [:]
        var abbrevToName: [String: String] = [:]

        let drbLines = drbData.components(separatedBy: .newlines)
        for line in drbLines {
            let parts = line.components(separatedBy: "\t")
            guard parts.count >= 6 else { continue }

            let bookName = parts[0]
            let abbrev = parts[1]
            let bookOrder = Int(parts[2]) ?? 0
            let chapter = Int(parts[3]) ?? 0
            let verseNum = Int(parts[4]) ?? 0
            let text = parts[5]

            let verse = Verse(
                id: "\(bookName):\(chapter):\(verseNum)",
                bookName: bookName,
                abbreviation: abbrev,
                bookOrder: bookOrder,
                chapter: chapter,
                verse: verseNum,
                text: text,
                lowercasedText: text.lowercased()
            )
            verses.append(verse)

            if var info = bookChapters[bookName] {
                info.chapters.insert(chapter)
                bookChapters[bookName] = info
            } else {
                bookChapters[bookName] = (abbrev, bookOrder, [chapter])
                abbrevToName[abbrev] = bookName
            }
        }

        // Build verse index and id map for Challoner
        var verseIndex: [String: [Int: [Verse]]] = [:]
        var verseById: [String: Verse] = [:]
        for verse in verses {
            verseIndex[verse.bookName, default: [:]][verse.chapter, default: []].append(verse)
            verseById[verse.id] = verse
        }
        for bookName in verseIndex.keys {
            for chapter in verseIndex[bookName]!.keys {
                verseIndex[bookName]![chapter]!.sort { $0.verse < $1.verse }
            }
        }

        let books = bookChapters.map { name, info in
            Book(
                id: name,
                name: name,
                abbreviation: info.abbrev,
                order: info.order,
                chapters: info.chapters.sorted(),
                testament: info.order >= 47 ? .newTestament : .oldTestament
            )
        }.sorted { $0.order < $1.order }

        // ── 2. Load Clementine Vulgate (vulgate-clementine.tsv) ──────────────
        // Schema: FullBookName(0) BookAbbrev(1) BookNum(2) Chapter(3) Verse(4) Text(5)
        var vulgateIndex: [String: [Int: [Verse]]] = [:]
        var vulgateVerses: [Verse] = []
        if let vulURL = Bundle.main.url(forResource: "vulgate-clementine", withExtension: "tsv"),
           let vulData = try? String(contentsOf: vulURL, encoding: .utf8) {
            let vulLines = vulData.components(separatedBy: .newlines)
            for line in vulLines {
                let parts = line.components(separatedBy: "\t")
                guard parts.count >= 6 else { continue }
                let bookName = parts[0]
                let abbrev = parts[1]
                let bookOrder = Int(parts[2]) ?? 0
                let chapter = Int(parts[3]) ?? 0
                let verseNum = Int(parts[4]) ?? 0
                let text = parts[5]
                guard !bookName.isEmpty, chapter > 0, verseNum > 0 else { continue }

                let verse = Verse(
                    id: "vul:\(bookName):\(chapter):\(verseNum)",
                    bookName: bookName,
                    abbreviation: abbrev,
                    bookOrder: bookOrder,
                    chapter: chapter,
                    verse: verseNum,
                    text: text,
                    lowercasedText: text.lowercased()
                )
                vulgateIndex[bookName, default: [:]][chapter, default: []].append(verse)
                vulgateVerses.append(verse)
            }
            for bookName in vulgateIndex.keys {
                for chapter in vulgateIndex[bookName]!.keys {
                    vulgateIndex[bookName]![chapter]!.sort { $0.verse < $1.verse }
                }
            }
        }

        // ── 3. Load Douay-Rheims 1609 (drb-1609.tsv) ─────────────────────────
        // Schema: header row + BookAbbrev(0) Chapter(1) Verse(2) Text(3)
        var drb1609Index: [String: [Int: [Verse]]] = [:]
        var drb1609Verses: [Verse] = []
        if let d1609URL = Bundle.main.url(forResource: "drb-1609", withExtension: "tsv"),
           let d1609Data = try? String(contentsOf: d1609URL, encoding: .utf8) {
            let d1609Lines = d1609Data.components(separatedBy: .newlines)
            var skipHeader = true
            for line in d1609Lines {
                if skipHeader { skipHeader = false; continue }  // skip header row
                let parts = line.components(separatedBy: "\t")
                guard parts.count >= 4 else { continue }
                let abbrev = parts[0]
                let chapter = Int(parts[1]) ?? 0
                let verseNum = Int(parts[2]) ?? 0
                let text = parts[3]
                guard !abbrev.isEmpty, chapter > 0, verseNum > 0 else { continue }

                // Map abbreviation → full book name using DRB data
                let bookName = abbrevToName[abbrev] ?? abbrev
                let bookOrder = bookChapters[bookName]?.order ?? 0

                let verse = Verse(
                    id: "1609:\(bookName):\(chapter):\(verseNum)",
                    bookName: bookName,
                    abbreviation: abbrev,
                    bookOrder: bookOrder,
                    chapter: chapter,
                    verse: verseNum,
                    text: text,
                    lowercasedText: text.lowercased()
                )
                drb1609Index[bookName, default: [:]][chapter, default: []].append(verse)
                drb1609Verses.append(verse)
            }
            for bookName in drb1609Index.keys {
                for chapter in drb1609Index[bookName]!.keys {
                    drb1609Index[bookName]![chapter]!.sort { $0.verse < $1.verse }
                }
            }
        }

        return LoadResult(
            verses: verses,
            verseIndex: verseIndex,
            verseById: verseById,
            books: books,
            vulgateIndex: vulgateIndex,
            drb1609Index: drb1609Index,
            vulgateVerses: vulgateVerses,
            drb1609Verses: drb1609Verses
        )
    }

    // MARK: - Public API

    // O(1) chapter lookup for any translation
    func verses(for book: String, chapter: Int, translation: Translation = .challoner) -> [Verse] {
        switch translation {
        case .challoner:
            return verseIndex[book]?[chapter] ?? []
        case .vulgate:
            return vulgateIndex[book]?[chapter] ?? []
        case .douai1609:
            return drb1609Index[book]?[chapter] ?? []
        }
    }

    // Convenience overload — uses the user's chosen primary translation.
    // Callers that don't pass an explicit translation automatically follow the setting.
    func verses(for book: String, chapter: Int) -> [Verse] {
        verses(for: book, chapter: chapter, translation: SettingsManager.shared.primaryTranslation)
    }

    // Fix 3: Use precomputed lowercasedText — no per-search String allocation.
    // Searches the specified translation; defaults to the user's primary translation.
    func search(_ query: String, translation: Translation, limit: Int = 100) -> [Verse] {
        guard !query.isEmpty else { return [] }
        let lowered = query.lowercased()
        let sourceVerses: [Verse]
        switch translation {
        case .challoner: sourceVerses = allVerses
        case .vulgate:   sourceVerses = vulgateVerses
        case .douai1609: sourceVerses = drb1609Verses
        }
        var results: [Verse] = []
        for verse in sourceVerses {
            if verse.lowercasedText.contains(lowered) ||
               verse.bookName.lowercased().contains(lowered) {
                results.append(verse)
                if results.count >= limit { break }
            }
        }
        return results
    }

    // Convenience overload — searches using the user's primary translation
    func search(_ query: String, limit: Int = 100) -> [Verse] {
        search(query, translation: SettingsManager.shared.primaryTranslation, limit: limit)
    }

    // Fix 2: O(1) bookmark lookup — was allVerses.first { $0.id == id }
    func verse(for id: String) -> Verse? {
        verseById[id]
    }
}
