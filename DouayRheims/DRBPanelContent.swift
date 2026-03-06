import SwiftUI

struct DRBPanelContent: View {
    let book: String
    let abbreviation: String
    let chapter: Int

    @EnvironmentObject var bibleData: BibleDataManager
    @EnvironmentObject var navigator: BibleNavigator
    @EnvironmentObject var bookmarks: BookmarkManager
    @EnvironmentObject var settings: SettingsManager
    @EnvironmentObject var database: DatabaseManager
    @Environment(\.colorScheme) var colorScheme

    var body: some View {
        let verses = bibleData.verses(for: book, chapter: chapter)

        ScrollViewReader { proxy in
            ScrollView {
                VStack(alignment: .leading, spacing: 0) {
                    // Chapter header
                    Text(book)
                        .font(settings.headerFont)
                        .foregroundColor(Theme.accent(colorScheme))
                        .padding(.bottom, 2)
                    Text("Chapter \(chapter)")
                        .font(settings.subHeaderFont)
                        .foregroundColor(.secondary)
                        .padding(.bottom, 20)

                    ForEach(verses) { verse in
                        let isHighlighted = navigator.verse == verse.verse
                            && navigator.book == book
                            && navigator.chapter == chapter

                        DRBVerseRow(
                            verse: verse,
                            isHighlighted: isHighlighted,
                            onTap: {
                                navigator.verse = verse.verse
                            }
                        )
                        .id(verse.verse)
                        .padding(.bottom, 6)
                    }
                }
                .padding(.horizontal, 16)
                .padding(.vertical, 12)
            }
            .onChange(of: navigator.verse) {
                if let v = navigator.verse,
                   navigator.book == book,
                   navigator.chapter == chapter {
                    withAnimation(.easeInOut(duration: 0.3)) {
                        proxy.scrollTo(v, anchor: .top)
                    }
                }
            }
        }
    }
}

struct DRBVerseRow: View {
    let verse: Verse
    let isHighlighted: Bool
    let onTap: () -> Void

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
        .padding(.vertical, 3)
        .padding(.horizontal, 6)
        .background(
            RoundedRectangle(cornerRadius: 6)
                .fill(isHighlighted ? Theme.accent(colorScheme).opacity(0.12) : Color.clear)
        )
        .contentShape(Rectangle())
        .onTapGesture { onTap() }
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
