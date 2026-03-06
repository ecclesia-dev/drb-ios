import SwiftUI

struct CommentaryPanelContent: View {
    let resource: ResourceType
    let book: String
    let abbreviation: String
    let chapter: Int

    @EnvironmentObject var navigator: BibleNavigator
    @EnvironmentObject var database: DatabaseManager
    @EnvironmentObject var settings: SettingsManager
    @Environment(\.colorScheme) var colorScheme

    @State private var entries: [DatabaseManager.CommentaryRow] = []

    var body: some View {
        ScrollViewReader { proxy in
            ScrollView {
                VStack(alignment: .leading, spacing: 0) {
                    // Source header
                    HStack(spacing: 8) {
                        Image(systemName: resource.icon)
                            .font(.system(size: 14))
                            .foregroundColor(Theme.goldAccent(colorScheme))
                        Text(resource.rawValue)
                            .font(Theme.serifBold(15))
                            .foregroundColor(Theme.accent(colorScheme))
                    }
                    .padding(.bottom, 2)

                    Text(resource.description)
                        .font(.caption2)
                        .foregroundColor(.secondary)
                        .padding(.bottom, 16)

                    if entries.isEmpty {
                        emptyState
                    } else {
                        ForEach(Array(entries.enumerated()), id: \.offset) { index, entry in
                            CommentaryEntryRow(
                                entry: entry,
                                resource: resource,
                                isHighlighted: navigator.verse == entry.verse
                                    && navigator.book == book
                                    && navigator.chapter == chapter
                            )
                            .id(entry.verse)
                            .padding(.bottom, 10)
                        }
                    }

                    if let note = resource.spellingNote {
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
                        .padding(.top, 12)
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
        .onAppear { loadEntries() }
        .onChange(of: book) { loadEntries() }
        .onChange(of: chapter) { loadEntries() }
        .onChange(of: resource) { loadEntries() }
        .onChange(of: database.isReady) { loadEntries() }
    }

    private func loadEntries() {
        guard database.isReady else { return }
        entries = database.commentary(source: resource.dbSource, book: abbreviation, chapter: chapter)
    }

    private var emptyState: some View {
        VStack(spacing: 12) {
            Image(systemName: "text.page.slash")
                .font(.system(size: 32))
                .foregroundColor(.secondary.opacity(0.5))
            Text("No \(resource.shortName) commentary for \(book) \(chapter)")
                .font(Theme.serifItalic(14))
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
        }
        .frame(maxWidth: .infinity)
        .padding(.vertical, 40)
    }
}

struct CommentaryEntryRow: View {
    let entry: DatabaseManager.CommentaryRow
    let resource: ResourceType
    let isHighlighted: Bool

    @EnvironmentObject var settings: SettingsManager
    @Environment(\.colorScheme) var colorScheme

    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text("v.\(entry.verse)")
                .font(Theme.serifBold(CGFloat(settings.fontSize * 0.7)))
                .foregroundColor(Theme.goldAccent(colorScheme))

            Text(entry.text)
                .font(.custom("Georgia", size: CGFloat(settings.fontSize * 0.85)))
                .foregroundColor(Theme.textPrimary(colorScheme))
                .lineSpacing(CGFloat(settings.lineSpacing) * 0.8)
                .fixedSize(horizontal: false, vertical: true)
                .textSelection(.enabled)
        }
        .padding(.vertical, 6)
        .padding(.horizontal, 8)
        .background(
            RoundedRectangle(cornerRadius: 6)
                .fill(isHighlighted ? Theme.goldAccent(colorScheme).opacity(0.1) : Color.clear)
        )
    }
}
