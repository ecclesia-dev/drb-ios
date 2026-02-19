import SwiftUI

struct ChapterView: View {
    let book: Book
    let chapter: Int

    @EnvironmentObject var bibleData: BibleDataManager
    @EnvironmentObject var bookmarks: BookmarkManager
    @EnvironmentObject var settings: SettingsManager
    @EnvironmentObject var commentary: CommentaryManager
    @Environment(\.colorScheme) var colorScheme

    @State private var selectedVerse: Verse?

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
                    VerseRow(
                        verse: verse,
                        hasCommentary: settings.showCommentary && commentary.hasCommentary(
                            for: verse.abbreviation, chapter: verse.chapter, verse: verse.verse
                        ),
                        onTap: {
                            if settings.showCommentary && commentary.hasCommentary(
                                for: verse.abbreviation, chapter: verse.chapter, verse: verse.verse
                            ) {
                                selectedVerse = verse
                            }
                        }
                    )
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
        .sheet(item: $selectedVerse) { verse in
            CommentarySheet(verse: verse)
                .environmentObject(commentary)
                .environmentObject(settings)
        }
    }
}

// MARK: - Verse Row

struct VerseRow: View {
    let verse: Verse
    var hasCommentary: Bool = false
    var onTap: (() -> Void)? = nil

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
        .onTapGesture {
            onTap?()
        }
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
            HStack(spacing: 4) {
                if hasCommentary {
                    Image(systemName: "text.bubble")
                        .font(.system(size: 9))
                        .foregroundColor(Theme.goldAccent(colorScheme))
                        .offset(x: bookmarks.isBookmarked(verse.id) ? -8 : 4)
                }
                if bookmarks.isBookmarked(verse.id) {
                    Image(systemName: "bookmark.fill")
                        .font(.system(size: 10))
                        .foregroundColor(Theme.accent(colorScheme))
                        .offset(x: 4)
                }
            }
        }
    }
}

// MARK: - Commentary Sheet

struct CommentarySheet: View {
    let verse: Verse

    @EnvironmentObject var commentary: CommentaryManager
    @EnvironmentObject var settings: SettingsManager
    @Environment(\.colorScheme) var colorScheme
    @Environment(\.dismiss) var dismiss

    @State private var selectedSource: CommentarySource?

    private var availableSources: [CommentarySource] {
        commentary.availableSources(for: verse.abbreviation, chapter: verse.chapter, verse: verse.verse)
    }

    var body: some View {
        NavigationStack {
            VStack(alignment: .leading, spacing: 0) {
                // Verse text header
                VStack(alignment: .leading, spacing: 6) {
                    Text(verse.reference)
                        .font(Theme.serifBold(CGFloat(settings.fontSize * 0.85)))
                        .foregroundColor(Theme.accent(colorScheme))

                    Text(verse.text)
                        .font(.custom("Georgia-Italic", size: CGFloat(settings.fontSize * 0.85)))
                        .foregroundColor(Theme.textPrimary(colorScheme))
                        .lineSpacing(3)
                }
                .padding(.horizontal, 20)
                .padding(.top, 16)
                .padding(.bottom, 12)

                Divider()
                    .padding(.horizontal, 20)

                // Source tabs
                if availableSources.count > 1 {
                    ScrollView(.horizontal, showsIndicators: false) {
                        HStack(spacing: 0) {
                            ForEach(availableSources) { source in
                                Button {
                                    withAnimation(.easeInOut(duration: 0.2)) {
                                        selectedSource = source
                                    }
                                } label: {
                                    Text(source.shortName)
                                        .font(Theme.serifBody(14))
                                        .foregroundColor(
                                            (selectedSource ?? availableSources.first) == source
                                                ? Theme.accent(colorScheme)
                                                : .secondary
                                        )
                                        .padding(.horizontal, 16)
                                        .padding(.vertical, 10)
                                        .overlay(alignment: .bottom) {
                                            if (selectedSource ?? availableSources.first) == source {
                                                Rectangle()
                                                    .fill(Theme.accent(colorScheme))
                                                    .frame(height: 2)
                                            }
                                        }
                                }
                            }
                        }
                        .padding(.horizontal, 12)
                    }

                    Divider()
                }

                // Commentary text
                ScrollView {
                    let activeSource = selectedSource ?? availableSources.first
                    if let source = activeSource {
                        let entries = commentary.commentariesBySource(
                            for: verse.abbreviation, chapter: verse.chapter, verse: verse.verse
                        ).first(where: { $0.source == source })?.entries ?? []

                        VStack(alignment: .leading, spacing: 12) {
                            if availableSources.count == 1 {
                                Text(source.rawValue)
                                    .font(Theme.serifBold(CGFloat(settings.fontSize * 0.75)))
                                    .foregroundColor(Theme.goldAccent(colorScheme))
                                    .padding(.top, 4)
                            }

                            ForEach(entries) { entry in
                                Text(entry.text)
                                    .font(.custom("Georgia", size: CGFloat(settings.fontSize * 0.82)))
                                    .foregroundColor(Theme.textPrimary(colorScheme))
                                    .lineSpacing(CGFloat(settings.lineSpacing * 0.8))
                                    .fixedSize(horizontal: false, vertical: true)
                            }
                        }
                        .padding(.horizontal, 20)
                        .padding(.vertical, 12)
                    }
                }
            }
            .background(Theme.background(colorScheme))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button {
                        dismiss()
                    } label: {
                        Image(systemName: "xmark.circle.fill")
                            .foregroundColor(.secondary)
                    }
                }
            }
        }
        .presentationDetents([.medium, .large])
        .presentationDragIndicator(.visible)
    }
}
