import SwiftUI

struct PanelView: View {
    @Binding var panel: Panel
    let onClose: (() -> Void)?

    @EnvironmentObject var navigator: BibleNavigator
    @EnvironmentObject var bibleData: BibleDataManager
    @Environment(\.colorScheme) var colorScheme

    @State private var showBookPicker = false
    @State private var showResourcePicker = false

    private var currentBook: String {
        panel.isLinked ? navigator.book : panel.independentBook
    }

    private var currentAbbreviation: String {
        panel.isLinked ? navigator.abbreviation : panel.independentAbbreviation
    }

    private var currentChapter: Int {
        panel.isLinked ? navigator.chapter : panel.independentChapter
    }

    var body: some View {
        VStack(spacing: 0) {
            panelHeader
            Divider()
            panelContent
        }
        .background(Theme.background(colorScheme))
        .clipShape(RoundedRectangle(cornerRadius: 0))
        .sheet(isPresented: $showBookPicker) {
            BookPickerView { book, chapter in
                navigateTo(book: book.name, abbreviation: book.abbreviation, chapter: chapter)
            }
            .environmentObject(bibleData)
        }
    }

    // MARK: - Header

    private var panelHeader: some View {
        VStack(spacing: 6) {
            HStack(spacing: 8) {
                // Resource picker
                Menu {
                    ForEach(ResourceType.allCases) { res in
                        Button {
                            panel.resource = res
                        } label: {
                            Label(res.rawValue, systemImage: res.icon)
                        }
                    }
                } label: {
                    HStack(spacing: 4) {
                        Image(systemName: panel.resource.icon)
                            .font(.system(size: 12))
                        Text(panel.resource.shortName)
                            .font(Theme.serifBold(13))
                        Image(systemName: "chevron.down")
                            .font(.system(size: 8, weight: .bold))
                    }
                    .foregroundColor(Theme.accent(colorScheme))
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background(
                        RoundedRectangle(cornerRadius: 6)
                            .fill(Theme.accent(colorScheme).opacity(0.08))
                    )
                }

                // Link toggle
                Button {
                    if panel.isLinked {
                        // Becoming unlinked — copy current nav state
                        panel.independentBook = navigator.book
                        panel.independentAbbreviation = navigator.abbreviation
                        panel.independentChapter = navigator.chapter
                    }
                    panel.isLinked.toggle()
                } label: {
                    Image(systemName: panel.isLinked ? "link" : "link.badge.plus")
                        .font(.system(size: 13))
                        .foregroundColor(panel.isLinked ? Theme.goldAccent(colorScheme) : .secondary)
                }
                .accessibilityLabel(panel.isLinked ? "Linked" : "Unlinked")

                Spacer()

                // Close button (if closeable)
                if let onClose = onClose {
                    Button(action: onClose) {
                        Image(systemName: "xmark")
                            .font(.system(size: 11, weight: .semibold))
                            .foregroundColor(.secondary)
                    }
                }
            }

            // Navigation row
            HStack(spacing: 12) {
                Button {
                    goToPreviousChapter()
                } label: {
                    Image(systemName: "chevron.left")
                        .font(.system(size: 12, weight: .semibold))
                        .foregroundColor(Theme.accent(colorScheme))
                }

                Button {
                    showBookPicker = true
                } label: {
                    Text("\(currentBook) \(currentChapter)")
                        .font(Theme.serifBody(14))
                        .foregroundColor(Theme.textPrimary(colorScheme))
                        .lineLimit(1)
                }

                Button {
                    goToNextChapter()
                } label: {
                    Image(systemName: "chevron.right")
                        .font(.system(size: 12, weight: .semibold))
                        .foregroundColor(Theme.accent(colorScheme))
                }

                Spacer()
            }
        }
        .padding(.horizontal, 12)
        .padding(.vertical, 8)
        .background(Theme.background(colorScheme))
    }

    // MARK: - Content

    @ViewBuilder
    private var panelContent: some View {
        if panel.resource == .drb {
            DRBPanelContent(
                book: currentBook,
                abbreviation: currentAbbreviation,
                chapter: currentChapter
            )
        } else {
            CommentaryPanelContent(
                resource: panel.resource,
                book: currentBook,
                abbreviation: currentAbbreviation,
                chapter: currentChapter
            )
        }
    }

    // MARK: - Navigation

    private func navigateTo(book: String, abbreviation: String, chapter: Int) {
        if panel.isLinked {
            navigator.navigate(book: book, abbreviation: abbreviation, chapter: chapter)
        } else {
            panel.independentBook = book
            panel.independentAbbreviation = abbreviation
            panel.independentChapter = chapter
        }
    }

    private func goToNextChapter() {
        if panel.isLinked {
            navigator.nextChapter(books: bibleData.books)
        } else {
            guard let currentBookObj = bibleData.books.first(where: { $0.name == panel.independentBook }) else { return }
            if currentBookObj.chapters.contains(panel.independentChapter + 1) {
                panel.independentChapter += 1
            } else if let idx = bibleData.books.firstIndex(where: { $0.name == panel.independentBook }), idx + 1 < bibleData.books.count {
                let next = bibleData.books[idx + 1]
                panel.independentBook = next.name
                panel.independentAbbreviation = next.abbreviation
                panel.independentChapter = 1
            }
        }
    }

    private func goToPreviousChapter() {
        if panel.isLinked {
            navigator.previousChapter(books: bibleData.books)
        } else {
            if panel.independentChapter > 1 {
                panel.independentChapter -= 1
            } else if let idx = bibleData.books.firstIndex(where: { $0.name == panel.independentBook }), idx > 0 {
                let prev = bibleData.books[idx - 1]
                panel.independentBook = prev.name
                panel.independentAbbreviation = prev.abbreviation
                panel.independentChapter = prev.chapters.last ?? 1
            }
        }
    }
}
