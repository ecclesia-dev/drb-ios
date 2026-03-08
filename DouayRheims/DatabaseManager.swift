import Foundation
import SQLite3

@MainActor
final class DatabaseManager: ObservableObject {
    static let shared = DatabaseManager()

    @Published private(set) var isReady = false

    private var db: OpaquePointer?

    private init() {
        Task {
            await setupDatabase()
            isReady = true
        }
    }

    deinit {
        if let db = db {
            sqlite3_close(db)
        }
    }

    // MARK: - Setup

    private func setupDatabase() async {
        let dbURL = Self.databaseURL()
        let needsImport = !FileManager.default.fileExists(atPath: dbURL.path)

        guard sqlite3_open(dbURL.path, &db) == SQLITE_OK else { return }

        if needsImport {
            await Task.detached(priority: .userInitiated) { [db] in
                guard let db = db else { return }
                DatabaseManager.createTables(db)
                DatabaseManager.importAllTSVs(db)
            }.value
        }
    }

    private static func databaseURL() -> URL {
        let docs = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
        return docs.appendingPathComponent("drb_v2.sqlite")
    }

    nonisolated private static func createTables(_ db: OpaquePointer) {
        let sql = """
        CREATE TABLE IF NOT EXISTS verses (
            book TEXT NOT NULL,
            abbreviation TEXT NOT NULL,
            book_order INTEGER NOT NULL,
            chapter INTEGER NOT NULL,
            verse INTEGER NOT NULL,
            text TEXT NOT NULL,
            PRIMARY KEY (book, chapter, verse)
        );
        CREATE TABLE IF NOT EXISTS commentary (
            source TEXT NOT NULL,
            book TEXT NOT NULL,
            chapter INTEGER NOT NULL,
            verse INTEGER NOT NULL,
            text TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_commentary ON commentary(source, book, chapter);
        CREATE INDEX IF NOT EXISTS idx_verses_book ON verses(book, chapter);
        """
        sqlite3_exec(db, sql, nil, nil, nil)
    }

    // MARK: - TSV Import

    nonisolated private static func importAllTSVs(_ db: OpaquePointer) {
        sqlite3_exec(db, "BEGIN TRANSACTION", nil, nil, nil)
        importDRB(db)
        importCommentary3Col(db, resource: "haydock", source: "haydock", hasHeader: false)
        importCommentary3Col(db, resource: "lapide", source: "lapide", hasHeader: true)
        importCommentary3Col(db, resource: "douai-1609-clean", source: "douai", hasHeader: true)
        importChrysostom(db, resource: "chrysostom-matthew", source: "chrysostom")
        importChrysostom(db, resource: "chrysostom-john", source: "chrysostom")
        importChrysostom(db, resource: "chrysostom-epistles", source: "chrysostom")
        importAquinas(db, resource: "aquinas-psalms", source: "aquinas")
        importAquinas(db, resource: "aquinas-isaiah", source: "aquinas")
        sqlite3_exec(db, "COMMIT", nil, nil, nil)
    }

    nonisolated private static func importDRB(_ db: OpaquePointer) {
        guard let url = Bundle.main.url(forResource: "drb", withExtension: "tsv"),
              let data = try? String(contentsOf: url, encoding: .utf8) else { return }

        var stmt: OpaquePointer?
        let sql = "INSERT OR IGNORE INTO verses (book, abbreviation, book_order, chapter, verse, text) VALUES (?,?,?,?,?,?)"
        guard sqlite3_prepare_v2(db, sql, -1, &stmt, nil) == SQLITE_OK else { return }

        for line in data.components(separatedBy: .newlines) {
            let parts = line.components(separatedBy: "\t")
            guard parts.count >= 6 else { continue }
            let bookName = parts[0]
            let abbrev = parts[1]
            let order = Int32(parts[2]) ?? 0
            let chapter = Int32(parts[3]) ?? 0
            let verse = Int32(parts[4]) ?? 0
            let text = parts[5]

            sqlite3_bind_text(stmt, 1, (bookName as NSString).utf8String, -1, nil)
            sqlite3_bind_text(stmt, 2, (abbrev as NSString).utf8String, -1, nil)
            sqlite3_bind_int(stmt, 3, order)
            sqlite3_bind_int(stmt, 4, chapter)
            sqlite3_bind_int(stmt, 5, verse)
            sqlite3_bind_text(stmt, 6, (text as NSString).utf8String, -1, nil)
            sqlite3_step(stmt)
            sqlite3_reset(stmt)
        }
        sqlite3_finalize(stmt)
    }

    /// Import 3-column commentary TSV: BookAbbrev\tChapter:Verse\tText
    nonisolated private static func importCommentary3Col(_ db: OpaquePointer, resource: String, source: String, hasHeader: Bool) {
        guard let url = Bundle.main.url(forResource: resource, withExtension: "tsv"),
              let data = try? String(contentsOf: url, encoding: .utf8) else { return }

        var stmt: OpaquePointer?
        let sql = "INSERT INTO commentary (source, book, chapter, verse, text) VALUES (?,?,?,?,?)"
        guard sqlite3_prepare_v2(db, sql, -1, &stmt, nil) == SQLITE_OK else { return }

        for (index, line) in data.components(separatedBy: .newlines).enumerated() {
            let parts = line.components(separatedBy: "\t")
            guard parts.count >= 3 else { continue }
            if hasHeader && index == 0 {
                let first = parts[0].lowercased()
                if first == "book" || first == "bookabbrev" { continue }
            }

            let abbrev = parts[0]
            let verseRef = parts[1]
            let text = parts[2]

            let refParts = verseRef.components(separatedBy: ":")
            guard refParts.count == 2,
                  let chapter = Int32(refParts[0]),
                  let verse = Int32(refParts[1]) else { continue }

            sqlite3_bind_text(stmt, 1, (source as NSString).utf8String, -1, nil)
            sqlite3_bind_text(stmt, 2, (abbrev as NSString).utf8String, -1, nil)
            sqlite3_bind_int(stmt, 3, chapter)
            sqlite3_bind_int(stmt, 4, verse)
            sqlite3_bind_text(stmt, 5, (text as NSString).utf8String, -1, nil)
            sqlite3_step(stmt)
            sqlite3_reset(stmt)
        }
        sqlite3_finalize(stmt)
    }

    /// Import 4-column Chrysostom TSV: book\tchapter\tverse\tcommentary (with header)
    nonisolated private static func importChrysostom(_ db: OpaquePointer, resource: String, source: String) {
        guard let url = Bundle.main.url(forResource: resource, withExtension: "tsv"),
              let data = try? String(contentsOf: url, encoding: .utf8) else { return }

        var stmt: OpaquePointer?
        let sql = "INSERT INTO commentary (source, book, chapter, verse, text) VALUES (?,?,?,?,?)"
        guard sqlite3_prepare_v2(db, sql, -1, &stmt, nil) == SQLITE_OK else { return }

        for (index, line) in data.components(separatedBy: .newlines).enumerated() {
            if index == 0 { continue } // skip header
            let parts = line.components(separatedBy: "\t")
            guard parts.count >= 4 else { continue }
            let abbrev = parts[0]
            let chapter = Int32(parts[1]) ?? 0
            let verse = Int32(parts[2]) ?? 0
            let text = parts[3]

            sqlite3_bind_text(stmt, 1, (source as NSString).utf8String, -1, nil)
            sqlite3_bind_text(stmt, 2, (abbrev as NSString).utf8String, -1, nil)
            sqlite3_bind_int(stmt, 3, chapter)
            sqlite3_bind_int(stmt, 4, verse)
            sqlite3_bind_text(stmt, 5, (text as NSString).utf8String, -1, nil)
            sqlite3_step(stmt)
            sqlite3_reset(stmt)
        }
        sqlite3_finalize(stmt)
    }

    /// Import 5-column Aquinas TSV: book\tchapter\tverse\tlatin_incipit\tenglish_translation (with header)
    nonisolated private static func importAquinas(_ db: OpaquePointer, resource: String, source: String) {
        guard let url = Bundle.main.url(forResource: resource, withExtension: "tsv"),
              let data = try? String(contentsOf: url, encoding: .utf8) else { return }

        var stmt: OpaquePointer?
        let sql = "INSERT INTO commentary (source, book, chapter, verse, text) VALUES (?,?,?,?,?)"
        guard sqlite3_prepare_v2(db, sql, -1, &stmt, nil) == SQLITE_OK else { return }

        for (index, line) in data.components(separatedBy: .newlines).enumerated() {
            if index == 0 { continue } // skip header
            let parts = line.components(separatedBy: "\t")
            guard parts.count >= 5 else { continue }
            let abbrev = parts[0]
            let chapter = Int32(parts[1]) ?? 0
            let verse = Int32(parts[2]) ?? 0
            let text = parts[4] // english_translation is column 5

            sqlite3_bind_text(stmt, 1, (source as NSString).utf8String, -1, nil)
            sqlite3_bind_text(stmt, 2, (abbrev as NSString).utf8String, -1, nil)
            sqlite3_bind_int(stmt, 3, chapter)
            sqlite3_bind_int(stmt, 4, verse)
            sqlite3_bind_text(stmt, 5, (text as NSString).utf8String, -1, nil)
            sqlite3_step(stmt)
            sqlite3_reset(stmt)
        }
        sqlite3_finalize(stmt)
    }

    // MARK: - Query API

    struct VerseRow {
        let book: String
        let abbreviation: String
        let bookOrder: Int
        let chapter: Int
        let verse: Int
        let text: String
    }

    struct CommentaryRow {
        let source: String
        let book: String
        let chapter: Int
        let verse: Int
        let text: String
    }

    func verses(book: String, chapter: Int) -> [VerseRow] {
        guard let db = db else { return [] }
        var results: [VerseRow] = []
        var stmt: OpaquePointer?
        let sql = "SELECT book, abbreviation, book_order, chapter, verse, text FROM verses WHERE book = ? AND chapter = ? ORDER BY verse"
        guard sqlite3_prepare_v2(db, sql, -1, &stmt, nil) == SQLITE_OK else { return [] }
        sqlite3_bind_text(stmt, 1, (book as NSString).utf8String, -1, nil)
        sqlite3_bind_int(stmt, 2, Int32(chapter))
        while sqlite3_step(stmt) == SQLITE_ROW {
            results.append(VerseRow(
                book: String(cString: sqlite3_column_text(stmt, 0)),
                abbreviation: String(cString: sqlite3_column_text(stmt, 1)),
                bookOrder: Int(sqlite3_column_int(stmt, 2)),
                chapter: Int(sqlite3_column_int(stmt, 3)),
                verse: Int(sqlite3_column_int(stmt, 4)),
                text: String(cString: sqlite3_column_text(stmt, 5))
            ))
        }
        sqlite3_finalize(stmt)
        return results
    }

    func commentary(source: String, book: String, chapter: Int) -> [CommentaryRow] {
        guard let db = db else { return [] }
        var results: [CommentaryRow] = []
        var stmt: OpaquePointer?
        let sql = "SELECT source, book, chapter, verse, text FROM commentary WHERE source = ? AND book = ? AND chapter = ? ORDER BY verse"
        guard sqlite3_prepare_v2(db, sql, -1, &stmt, nil) == SQLITE_OK else { return [] }
        sqlite3_bind_text(stmt, 1, (source as NSString).utf8String, -1, nil)
        sqlite3_bind_text(stmt, 2, (book as NSString).utf8String, -1, nil)
        sqlite3_bind_int(stmt, 3, Int32(chapter))
        while sqlite3_step(stmt) == SQLITE_ROW {
            results.append(CommentaryRow(
                source: String(cString: sqlite3_column_text(stmt, 0)),
                book: String(cString: sqlite3_column_text(stmt, 1)),
                chapter: Int(sqlite3_column_int(stmt, 2)),
                verse: Int(sqlite3_column_int(stmt, 3)),
                text: String(cString: sqlite3_column_text(stmt, 4))
            ))
        }
        sqlite3_finalize(stmt)
        return results
    }

    func searchVerses(_ query: String, limit: Int = 100) -> [VerseRow] {
        guard let db = db, !query.isEmpty else { return [] }
        var results: [VerseRow] = []
        var stmt: OpaquePointer?
        let sql = "SELECT book, abbreviation, book_order, chapter, verse, text FROM verses WHERE text LIKE ? ORDER BY book_order, chapter, verse LIMIT ?"
        guard sqlite3_prepare_v2(db, sql, -1, &stmt, nil) == SQLITE_OK else { return [] }
        let pattern = "%\(query)%"
        sqlite3_bind_text(stmt, 1, (pattern as NSString).utf8String, -1, nil)
        sqlite3_bind_int(stmt, 2, Int32(limit))
        while sqlite3_step(stmt) == SQLITE_ROW {
            results.append(VerseRow(
                book: String(cString: sqlite3_column_text(stmt, 0)),
                abbreviation: String(cString: sqlite3_column_text(stmt, 1)),
                bookOrder: Int(sqlite3_column_int(stmt, 2)),
                chapter: Int(sqlite3_column_int(stmt, 3)),
                verse: Int(sqlite3_column_int(stmt, 4)),
                text: String(cString: sqlite3_column_text(stmt, 5))
            ))
        }
        sqlite3_finalize(stmt)
        return results
    }

    func hasCommentary(source: String, book: String, chapter: Int) -> Bool {
        guard let db = db else { return false }
        var stmt: OpaquePointer?
        let sql = "SELECT 1 FROM commentary WHERE source = ? AND book = ? AND chapter = ? LIMIT 1"
        guard sqlite3_prepare_v2(db, sql, -1, &stmt, nil) == SQLITE_OK else { return false }
        sqlite3_bind_text(stmt, 1, (source as NSString).utf8String, -1, nil)
        sqlite3_bind_text(stmt, 2, (book as NSString).utf8String, -1, nil)
        sqlite3_bind_int(stmt, 3, Int32(chapter))
        let found = sqlite3_step(stmt) == SQLITE_ROW
        sqlite3_finalize(stmt)
        return found
    }
}
