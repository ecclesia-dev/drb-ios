import Foundation

// MARK: - Commentary Source

enum CommentarySource: String, CaseIterable, Identifiable {
    case haydock = "Haydock"
    case lapide = "Cornelius à Lapide"
    case douai1609 = "Douai 1609"

    var id: String { rawValue }

    var filename: String {
        switch self {
        case .haydock: return "haydock"
        case .lapide: return "lapide"
        case .douai1609: return "douai-1609"
        }
    }

    var shortName: String {
        switch self {
        case .haydock: return "Haydock"
        case .lapide: return "Lapide"
        case .douai1609: return "Douai 1609"
        }
    }
}

// MARK: - Commentary Entry

struct CommentaryEntry: Identifiable {
    let id = UUID()
    let source: CommentarySource
    let abbreviation: String
    let chapter: Int
    let verse: Int
    let text: String
}

// MARK: - Commentary Manager

@MainActor
final class CommentaryManager: ObservableObject {
    static let shared = CommentaryManager()

    // Key: "Abbrev:Chapter:Verse" -> [CommentaryEntry]
    private var entries: [String: [CommentaryEntry]] = [:]
    @Published private(set) var isLoaded = false

    private init() {
        loadAll()
    }

    private func loadAll() {
        for source in CommentarySource.allCases {
            loadSource(source)
        }
        isLoaded = true
    }

    private func loadSource(_ source: CommentarySource) {
        guard let url = Bundle.main.url(forResource: source.filename, withExtension: "tsv"),
              let data = try? String(contentsOf: url, encoding: .utf8) else {
            return
        }

        let lines = data.components(separatedBy: .newlines)
        for (index, line) in lines.enumerated() {
            let parts = line.components(separatedBy: "\t")
            guard parts.count >= 3 else { continue }

            let abbrev = parts[0]
            let verseRef = parts[1]
            let text = parts[2]

            // Skip header row
            if index == 0 && (abbrev == "Book" || abbrev == "book") { continue }

            // Parse "Chapter:Verse"
            let refParts = verseRef.components(separatedBy: ":")
            guard refParts.count == 2,
                  let chapter = Int(refParts[0]),
                  let verse = Int(refParts[1]) else { continue }

            let entry = CommentaryEntry(
                source: source,
                abbreviation: abbrev,
                chapter: chapter,
                verse: verse,
                text: text
            )

            let key = "\(abbrev):\(chapter):\(verse)"
            entries[key, default: []].append(entry)
        }
    }

    /// Look up commentaries for a verse by book abbreviation, chapter, and verse number
    func commentaries(for abbreviation: String, chapter: Int, verse: Int) -> [CommentaryEntry] {
        let key = "\(abbreviation):\(chapter):\(verse)"
        return entries[key] ?? []
    }

    /// Get commentaries grouped by source for a specific verse
    func commentariesBySource(for abbreviation: String, chapter: Int, verse: Int) -> [(source: CommentarySource, entries: [CommentaryEntry])] {
        let all = commentaries(for: abbreviation, chapter: chapter, verse: verse)
        var result: [(source: CommentarySource, entries: [CommentaryEntry])] = []
        for source in CommentarySource.allCases {
            let sourceEntries = all.filter { $0.source == source }
            if !sourceEntries.isEmpty {
                result.append((source: source, entries: sourceEntries))
            }
        }
        return result
    }

    /// Check if any commentary exists for a verse
    func hasCommentary(for abbreviation: String, chapter: Int, verse: Int) -> Bool {
        let key = "\(abbreviation):\(chapter):\(verse)"
        return entries[key] != nil && !(entries[key]!.isEmpty)
    }

    /// Available sources for a specific verse
    func availableSources(for abbreviation: String, chapter: Int, verse: Int) -> [CommentarySource] {
        commentariesBySource(for: abbreviation, chapter: chapter, verse: verse).map { $0.source }
    }
}
