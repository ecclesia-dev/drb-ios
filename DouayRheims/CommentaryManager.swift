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
        case .douai1609: return "Douai"
        }
    }

    var description: String {
        switch self {
        case .haydock: return "Haydock Catholic Bible Commentary"
        case .lapide: return "Cornelius à Lapide (New Testament)"
        case .douai1609: return "Original Douai Annotations (1609)"
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
    // @Published so SwiftUI views reactively update when entries arrive (e.g. after lazy Haydock load)
    @Published private var entries: [String: [CommentaryEntry]] = [:]

    // Fix 4: Track which sources have been loaded (or are being loaded)
    private var loadedSources: Set<CommentarySource> = []
    private var loadingInProgress: Set<CommentarySource> = []

    @Published private(set) var isLoaded = false
    @Published private(set) var haydockLoaded = false

    private init() {
        // Fix 1 + 4: Load only the small sources (Douai ~3k lines, Lapide ~2.4k lines)
        // eagerly in the background. Haydock (13MB / ~36k lines) loads lazily on first access.
        Task {
            await loadSourceInBackground(.douai1609)
            await loadSourceInBackground(.lapide)
            isLoaded = true
        }
    }

    // MARK: - Background loading

    private func loadSourceInBackground(_ source: CommentarySource) async {
        guard !loadedSources.contains(source) && !loadingInProgress.contains(source) else { return }
        loadingInProgress.insert(source)

        let parsed = await Task.detached(priority: .utility) {
            CommentaryManager.parseSource(source)
        }.value

        // Back on @MainActor
        for (key, newEntries) in parsed {
            entries[key, default: []].append(contentsOf: newEntries)
        }
        loadedSources.insert(source)
        loadingInProgress.remove(source)
        if source == .haydock {
            haydockLoaded = true
        }
    }

    // Fix 4: Trigger Haydock/Lapide load on first access if not yet loaded
    private func ensureLoaded(_ source: CommentarySource) {
        guard !loadedSources.contains(source) && !loadingInProgress.contains(source) else { return }
        Task {
            await loadSourceInBackground(source)
        }
    }

    // MARK: - Background TSV parse (runs off main thread)

    nonisolated private static func parseSource(_ source: CommentarySource) -> [String: [CommentaryEntry]] {
        var result: [String: [CommentaryEntry]] = [:]

        guard let url = Bundle.main.url(forResource: source.filename, withExtension: "tsv"),
              let data = try? String(contentsOf: url, encoding: .utf8) else {
            return result
        }

        let lines = data.components(separatedBy: .newlines)
        for (index, line) in lines.enumerated() {
            let parts = line.components(separatedBy: "\t")
            guard parts.count >= 3 else { continue }

            let abbrev = parts[0]
            let verseRef = parts[1]
            let text = parts[2]

            // Skip header row
            if index == 0 && (abbrev.lowercased() == "book" || abbrev.lowercased() == "bookabbrev") {
                continue
            }

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
            result[key, default: []].append(entry)
        }

        return result
    }

    // MARK: - Public API

    /// Look up commentaries for a verse. Triggers lazy load of Haydock on first call.
    func commentaries(for abbreviation: String, chapter: Int, verse: Int) -> [CommentaryEntry] {
        // Fix 4: trigger Haydock load if not ready yet
        ensureLoaded(.haydock)
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

    /// Check if any commentary exists for a verse. Triggers lazy load of Haydock on first call.
    func hasCommentary(for abbreviation: String, chapter: Int, verse: Int) -> Bool {
        ensureLoaded(.haydock)
        let key = "\(abbreviation):\(chapter):\(verse)"
        return !(entries[key]?.isEmpty ?? true)
    }

    /// Available sources for a specific verse
    func availableSources(for abbreviation: String, chapter: Int, verse: Int) -> [CommentarySource] {
        commentariesBySource(for: abbreviation, chapter: chapter, verse: verse).map { $0.source }
    }
}
