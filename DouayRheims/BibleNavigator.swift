import Foundation
import Combine

@MainActor
final class BibleNavigator: ObservableObject {
    @Published var book: String = "Genesis"
    @Published var abbreviation: String = "Gn"
    @Published var chapter: Int = 1
    @Published var verse: Int? = nil

    func navigate(book: String, abbreviation: String, chapter: Int, verse: Int? = nil) {
        self.book = book
        self.abbreviation = abbreviation
        self.chapter = chapter
        self.verse = verse
    }

    func nextChapter(books: [Book]) {
        guard let currentBook = books.first(where: { $0.name == book }) else { return }
        if currentBook.chapters.contains(chapter + 1) {
            chapter += 1
            verse = nil
        } else {
            // Move to next book's chapter 1
            if let idx = books.firstIndex(where: { $0.name == book }), idx + 1 < books.count {
                let next = books[idx + 1]
                navigate(book: next.name, abbreviation: next.abbreviation, chapter: 1)
            }
        }
    }

    func previousChapter(books: [Book]) {
        if chapter > 1 {
            chapter -= 1
            verse = nil
        } else {
            // Move to previous book's last chapter
            guard let idx = books.firstIndex(where: { $0.name == book }), idx > 0 else { return }
            let prev = books[idx - 1]
            navigate(book: prev.name, abbreviation: prev.abbreviation, chapter: prev.chapters.last ?? 1)
        }
    }
}
