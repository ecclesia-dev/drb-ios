import SwiftUI

struct VerseCompareView: View {
    let verse: Verse

    @EnvironmentObject var bibleData: BibleDataManager
    @Environment(\.colorScheme) var colorScheme
    @Environment(\.dismiss) var dismiss

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 24) {
                    Text(verse.reference)
                        .font(Theme.serifBold(18))
                        .foregroundColor(Theme.accent(colorScheme))
                        .padding(.horizontal)

                    ForEach(translationRows, id: \.label) { row in
                        VStack(alignment: .leading, spacing: 6) {
                            Text(row.label)
                                .font(.system(size: 11, weight: .semibold))
                                .foregroundColor(.secondary)
                                .textCase(.uppercase)
                                .padding(.horizontal)
                            Text(row.text)
                                .font(Theme.serifBody(16))
                                .foregroundColor(Theme.textPrimary(colorScheme))
                                .padding(.horizontal)
                                .padding(.bottom, 4)
                                .fixedSize(horizontal: false, vertical: true)
                            Divider().padding(.horizontal)
                        }
                    }
                }
                .padding(.vertical)
            }
            .navigationTitle("Compare Translations")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button("Done") { dismiss() }
                        .foregroundColor(Theme.accent(colorScheme))
                }
            }
            .background(Theme.background(colorScheme))
        }
    }

    // MARK: - Translation rows

    private struct TranslationRow {
        let label: String
        let text: String
    }

    private var translationRows: [TranslationRow] {
        let translations: [(Translation, String)] = [
            (.vulgate,   "Clementine Vulgate (Latin)"),
            (.douai1609, "Douay 1609 / Rheims 1582"),
            (.challoner, "Douay-Rheims (Challoner)")
        ]
        return translations.compactMap { (translation, label) in
            let verses = bibleData.verses(for: verse.bookName, chapter: verse.chapter, translation: translation)
            guard let match = verses.first(where: { $0.verse == verse.verse }),
                  !match.text.isEmpty else { return nil }
            return TranslationRow(label: label, text: match.text)
        }
    }
}
