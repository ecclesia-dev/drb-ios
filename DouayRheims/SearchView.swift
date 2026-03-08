import SwiftUI

struct SearchView: View {
    @EnvironmentObject var bibleData: BibleDataManager
    @EnvironmentObject var bookmarks: BookmarkManager
    @EnvironmentObject var settings: SettingsManager
    @Environment(\.colorScheme) var colorScheme

    @State private var query = ""
    @State private var results: [Verse] = []
    @State private var hasSearched = false

    var body: some View {
        List {
            if !hasSearched {
                Section {
                    Text("Search across all verses of the \(settings.primaryTranslation.displayName).")
                        .font(Theme.serifItalic(16))
                        .foregroundColor(.secondary)
                        .listRowBackground(Color.clear)
                }
            } else if results.isEmpty {
                Section {
                    Text("No verses found for \"\(query)\"")
                        .font(Theme.serifItalic(16))
                        .foregroundColor(.secondary)
                        .listRowBackground(Color.clear)
                }
            } else {
                Section {
                    Text("\(results.count)\(results.count >= 100 ? "+" : "") results")
                        .font(Theme.serifItalic(14))
                        .foregroundColor(.secondary)
                }

                ForEach(results) { verse in
                    VStack(alignment: .leading, spacing: 4) {
                        Text(verse.reference)
                            .font(Theme.serifBold(14))
                            .foregroundColor(Theme.accent(colorScheme))

                        Text(verse.text)
                            .font(Theme.serifBody(16))
                            .foregroundColor(Theme.textPrimary(colorScheme))
                            .lineSpacing(3)
                            .lineLimit(3)
                    }
                    .padding(.vertical, 4)
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
                    }
                }
            }
        }
        .listStyle(.insetGrouped)
        .scrollContentBackground(.hidden)
        .background(Theme.background(colorScheme))
        .navigationTitle("Search")
        .searchable(text: $query, prompt: "Search verses...")
        .onSubmit(of: .search) {
            performSearch()
        }
        .onChange(of: query) { _, newValue in
            if newValue.isEmpty {
                results = []
                hasSearched = false
            }
        }
    }

    private func performSearch() {
        hasSearched = true
        results = bibleData.search(query, translation: settings.primaryTranslation)
    }
}
