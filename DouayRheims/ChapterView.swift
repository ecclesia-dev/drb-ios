import SwiftUI

struct ChapterView: View {
    let book: Book
    let chapter: Int

    @EnvironmentObject var bibleData: BibleDataManager
    @EnvironmentObject var bookmarks: BookmarkManager
    @EnvironmentObject var settings: SettingsManager
    @Environment(\.colorScheme) var colorScheme

    var body: some View {
        let verses = bibleData.verses(for: book.name, chapter: chapter)

        ScrollView {
            VStack(alignment: .leading, spacing: 0) {
                // Chapter header
                Text(book.name)
                    .font(settings.headerFont)
                    .foregroundColor(Theme.accent(colorScheme))
                    .padding(.bottom, 2)
                Text("Chapter \(chapter)")
                    .font(settings.subHeaderFont)
                    .foregroundColor(.secondary)
                    .padding(.bottom, 20)

                // Verses
                ForEach(verses) { verse in
                    VerseRow(verse: verse)
                        .padding(.bottom, 8)
                }

                // Prev/Next navigation
                HStack {
                    if chapter > 1 {
                        NavigationLink(destination: ChapterView(book: book, chapter: chapter - 1)) {
                            Label("Chapter \(chapter - 1)", systemImage: "chevron.left")
                                .font(Theme.serifBody(15))
                        }
                    }
                    Spacer()
                    if book.chapters.contains(chapter + 1) {
                        NavigationLink(destination: ChapterView(book: book, chapter: chapter + 1)) {
                            Label("Chapter \(chapter + 1)", systemImage: "chevron.right")
                                .font(Theme.serifBody(15))
                                .environment(\.layoutDirection, .rightToLeft)
                        }
                    }
                }
                .foregroundColor(Theme.accent(colorScheme))
                .padding(.top, 24)
                .padding(.bottom, 16)
            }
            .padding(.horizontal, 20)
            .padding(.vertical, 16)
        }
        .navigationTitle("\(book.abbreviation) \(chapter)")
        .navigationBarTitleDisplayMode(.inline)
        .background(Theme.background(colorScheme))
    }
}

struct VerseRow: View {
    let verse: Verse
    @EnvironmentObject var bookmarks: BookmarkManager
    @EnvironmentObject var settings: SettingsManager
    @Environment(\.colorScheme) var colorScheme

    var body: some View {
        HStack(alignment: .firstTextBaseline, spacing: 0) {
            Text("\(verse.verse) ")
                .font(settings.verseNumberFont)
                .foregroundColor(Theme.accent(colorScheme))
                .baselineOffset(4)

            Text(verse.text)
                .font(settings.bodyFont)
                .foregroundColor(Theme.textPrimary(colorScheme))
                .lineSpacing(CGFloat(settings.lineSpacing))
                .fixedSize(horizontal: false, vertical: true)

            Spacer(minLength: 0)
        }
        .contentShape(Rectangle())
        .contextMenu {
            Button {
                bookmarks.toggle(verse.id)
            } label: {
                Label(
                    bookmarks.isBookmarked(verse.id) ? "Remove Bookmark" : "Bookmark",
                    systemImage: bookmarks.isBookmarked(verse.id) ? "bookmark.slash" : "bookmark"
                )
            }

            Button {
                UIPasteboard.general.string = "\(verse.reference)\n\(verse.text)"
            } label: {
                Label("Copy", systemImage: "doc.on.doc")
            }

            ShareLink(item: "\(verse.reference)\n\(verse.text)") {
                Label("Share", systemImage: "square.and.arrow.up")
            }
        }
        .overlay(alignment: .trailing) {
            if bookmarks.isBookmarked(verse.id) {
                Image(systemName: "bookmark.fill")
                    .font(.system(size: 10))
                    .foregroundColor(Theme.accent(colorScheme))
                    .offset(x: 4)
            }
        }
    }
}
