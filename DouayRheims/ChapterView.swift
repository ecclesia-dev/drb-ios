import SwiftUI

struct ChapterView: View {
    let book: Book
    let chapter: Int

    @EnvironmentObject var bibleData: BibleDataManager
    @EnvironmentObject var bookmarks: BookmarkManager
    @EnvironmentObject var settings: SettingsManager
    @EnvironmentObject var commentary: CommentaryManager
    @Environment(\.colorScheme) var colorScheme
    @Environment(\.horizontalSizeClass) var horizontalSizeClass
    @Environment(\.accessibilityReduceMotion) var reduceMotion

    @State private var selectedVerse: Verse?
    @State private var verseCompareVerse: Verse?

    private var isIPad: Bool {
        horizontalSizeClass == .regular
    }

    var body: some View {
        let verses = bibleData.verses(for: book.name, chapter: chapter)

        Group {
            if isIPad {
                iPadLayout(verses: verses)
            } else {
                iPhoneLayout(verses: verses)
            }
        }
        .navigationTitle("\(book.abbreviation) \(chapter)")
        .navigationBarTitleDisplayMode(.inline)
        .background(Theme.background(colorScheme))
        .sheet(item: $verseCompareVerse) { verse in
            VerseCompareView(verse: verse)
                .environmentObject(bibleData)
        }
    }

    // MARK: - iPhone Layout (sheet)

    @ViewBuilder
    private func iPhoneLayout(verses: [Verse]) -> some View {
        ScrollView {
            versesContent(verses: verses)
        }
        .sheet(item: $selectedVerse) { verse in
            CommentarySheet(verse: verse)
                .environmentObject(commentary)
                .environmentObject(settings)
        }
    }

    // MARK: - iPad Layout (side panel)

    @ViewBuilder
    private func iPadLayout(verses: [Verse]) -> some View {
        HStack(spacing: 0) {
            ScrollView {
                versesContent(verses: verses)
            }
            .frame(maxWidth: .infinity)

            if let verse = selectedVerse {
                Divider()

                CommentarySidePanel(verse: verse) {
                    if reduceMotion {
                        selectedVerse = nil
                    } else {
                        withAnimation(.easeInOut(duration: 0.25)) {
                            selectedVerse = nil
                        }
                    }
                }
                .environmentObject(commentary)
                .environmentObject(settings)
                .frame(width: 420)
                .transition(.move(edge: .trailing).combined(with: .opacity))
            }
        }
        .animation(reduceMotion ? nil : .easeInOut(duration: 0.25), value: selectedVerse?.id)
    }

    // MARK: - Shared verses content

    @ViewBuilder
    private func versesContent(verses: [Verse]) -> some View {
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

            // Verses — Fix 5: compute hasCommentary once per verse, not twice
            ForEach(verses) { verse in
                let verseHasCommentary = settings.showCommentary && commentary.hasCommentary(
                    for: verse.abbreviation, chapter: verse.chapter, verse: verse.verse
                )
                VerseRow(
                    verse: verse,
                    isSelected: selectedVerse?.id == verse.id,
                    hasCommentary: verseHasCommentary,
                    onTap: {
                        if verseHasCommentary {
                            if reduceMotion {
                                if selectedVerse?.id == verse.id {
                                    selectedVerse = nil
                                } else {
                                    selectedVerse = verse
                                }
                            } else {
                                withAnimation(.easeInOut(duration: 0.2)) {
                                    if selectedVerse?.id == verse.id {
                                        selectedVerse = nil
                                    } else {
                                        selectedVerse = verse
                                    }
                                }
                            }
                        }
                    },
                    onCompare: {
                        verseCompareVerse = verse
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
}

// MARK: - Verse Row

struct VerseRow: View {
    let verse: Verse
    var isSelected: Bool = false
    var hasCommentary: Bool = false
    var onTap: (() -> Void)? = nil
    var onCompare: (() -> Void)? = nil

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
        .padding(.vertical, 2)
        .padding(.horizontal, 4)
        .background(
            RoundedRectangle(cornerRadius: 6)
                .fill(isSelected ? Theme.accent(colorScheme).opacity(0.08) : Color.clear)
        )
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

            if let onCompare = onCompare {
                Divider()
                Button {
                    onCompare()
                } label: {
                    Label("Compare Translations", systemImage: "text.alignleft")
                }
            }
        }
        .overlay(alignment: .trailing) {
            HStack(spacing: 4) {
                if hasCommentary {
                    Image(systemName: "text.bubble")
                        .font(.system(size: 9))
                        .foregroundColor(Theme.goldAccent(colorScheme))
                        .offset(x: bookmarks.isBookmarked(verse.id) ? -8 : 4)
                        .accessibilityHidden(true)
                }
                if bookmarks.isBookmarked(verse.id) {
                    Image(systemName: "bookmark.fill")
                        .font(.system(size: 10))
                        .foregroundColor(Theme.accent(colorScheme))
                        .offset(x: 4)
                        .accessibilityHidden(true)
                }
            }
        }
        .accessibilityElement(children: .combine)
        .accessibilityLabel("\(verse.reference). \(verse.text)\(bookmarks.isBookmarked(verse.id) ? ". Bookmarked" : "")")
        .accessibilityHint(hasCommentary ? "Tap to view commentary" : "")
    }
}

// MARK: - Commentary Content (Fix 5 — shared between Sheet and SidePanel)

/// Shared source-tab selector + commentary text body.
/// Used by both CommentarySheet (iPhone) and CommentarySidePanel (iPad).
struct CommentaryContent: View {
    let verse: Verse
    @Binding var selectedSource: CommentarySource?
    let availableSources: [CommentarySource]
    /// Base font size multiplier — sheet uses larger sizes, panel uses smaller
    let fontScale: CGFloat

    @EnvironmentObject var commentary: CommentaryManager
    @EnvironmentObject var settings: SettingsManager
    @Environment(\.colorScheme) var colorScheme
    @Environment(\.accessibilityReduceMotion) var reduceMotion

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            sourceTabs
            commentaryBody
        }
    }

    // MARK: Source tabs

    @ViewBuilder
    private var sourceTabs: some View {
        if availableSources.count > 1 {
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 0) {
                    ForEach(availableSources) { source in
                        Button {
                            if reduceMotion {
                                selectedSource = source
                            } else {
                                withAnimation(.easeInOut(duration: 0.2)) {
                                    selectedSource = source
                                }
                            }
                        } label: {
                            Text(source.shortName)
                                .font(Theme.serifBody(14 * fontScale))
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
    }

    // MARK: Commentary body

    private var commentaryBody: some View {
        ScrollView {
            let activeSource = selectedSource ?? availableSources.first
            if let source = activeSource {
                let sourceEntries = commentary.commentariesBySource(
                    for: verse.abbreviation, chapter: verse.chapter, verse: verse.verse
                ).first(where: { $0.source == source })?.entries ?? []

                VStack(alignment: .leading, spacing: 12) {
                    // Source label with description
                    VStack(alignment: .leading, spacing: 2) {
                        Text(source.rawValue)
                            .font(Theme.serifBold(CGFloat(settings.fontSize) * 0.75 * fontScale))
                            .foregroundColor(Theme.goldAccent(colorScheme))
                        Text(source.description)
                            .font(.caption2)
                            .foregroundColor(.secondary)
                    }
                    .padding(.top, 4)

                    ForEach(sourceEntries) { entry in
                        Text(entry.text)
                            .font(.custom("Georgia", size: CGFloat(settings.fontSize) * 0.82 * fontScale))
                            .foregroundColor(Theme.textPrimary(colorScheme))
                            .lineSpacing(CGFloat(settings.lineSpacing) * 0.8)
                            .fixedSize(horizontal: false, vertical: true)
                            .textSelection(.enabled)
                    }

                    if let note = source.spellingNote {
                        HStack(alignment: .top, spacing: 6) {
                            Image(systemName: "info.circle")
                                .font(.system(size: 11))
                                .foregroundColor(.secondary)
                                .padding(.top, 1)
                            Text(note)
                                .font(.caption2)
                                .foregroundColor(.secondary)
                                .fixedSize(horizontal: false, vertical: true)
                        }
                        .padding(.top, 8)
                        .padding(.horizontal, 2)
                    }
                }
                .padding(.horizontal, 20)
                .padding(.vertical, 12)
            }
        }
    }
}

// MARK: - Commentary Sheet (iPhone)

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
                commentaryHeader
                Divider().padding(.horizontal, 20)
                // Fix 5: shared view handles source tabs + body
                CommentaryContent(
                    verse: verse,
                    selectedSource: $selectedSource,
                    availableSources: availableSources,
                    fontScale: 1.0
                )
                .environmentObject(commentary)
                .environmentObject(settings)
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
                    .accessibilityLabel("Close commentary")
                }
            }
        }
        .presentationDetents([.medium, .large])
        .presentationDragIndicator(.visible)
    }

    private var commentaryHeader: some View {
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
    }
}

// MARK: - Commentary Side Panel (iPad)

struct CommentarySidePanel: View {
    let verse: Verse
    let onDismiss: () -> Void

    @EnvironmentObject var commentary: CommentaryManager
    @EnvironmentObject var settings: SettingsManager
    @Environment(\.colorScheme) var colorScheme

    @State private var selectedSource: CommentarySource?

    private var availableSources: [CommentarySource] {
        commentary.availableSources(for: verse.abbreviation, chapter: verse.chapter, verse: verse.verse)
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            // Header with dismiss
            HStack {
                Text("Commentary")
                    .font(Theme.serifBold(16))
                    .foregroundColor(Theme.textPrimary(colorScheme))
                Spacer()
                Button(action: onDismiss) {
                    Image(systemName: "xmark.circle.fill")
                        .font(.system(size: 20))
                        .foregroundColor(.secondary)
                }
                .accessibilityLabel("Close commentary")
            }
            .padding(.horizontal, 16)
            .padding(.top, 12)
            .padding(.bottom, 8)

            Divider()

            // Verse reference
            VStack(alignment: .leading, spacing: 4) {
                Text(verse.reference)
                    .font(Theme.serifBold(CGFloat(settings.fontSize * 0.8)))
                    .foregroundColor(Theme.accent(colorScheme))

                Text(verse.text)
                    .font(.custom("Georgia-Italic", size: CGFloat(settings.fontSize * 0.78)))
                    .foregroundColor(Theme.textPrimary(colorScheme).opacity(0.8))
                    .lineSpacing(2)
                    .lineLimit(3)
            }
            .padding(.horizontal, 16)
            .padding(.vertical, 10)

            Divider()

            // Fix 5: shared view handles source tabs + body (slightly smaller scale for panel)
            CommentaryContent(
                verse: verse,
                selectedSource: $selectedSource,
                availableSources: availableSources,
                fontScale: 0.95
            )
            .environmentObject(commentary)
            .environmentObject(settings)
        }
        .background(Theme.background(colorScheme).opacity(0.98))
        .onChange(of: verse.id) {
            selectedSource = nil
        }
    }
}
