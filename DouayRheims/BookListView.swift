import SwiftUI

struct BookListView: View {
    @EnvironmentObject var bibleData: BibleDataManager
    @Environment(\.colorScheme) var colorScheme

    var body: some View {
        List {
            ForEach(Testament.allCases, id: \.self) { testament in
                Section {
                    ForEach(bibleData.books.filter { $0.testament == testament }) { book in
                        NavigationLink(destination: ChapterListView(book: book)) {
                            HStack {
                                VStack(alignment: .leading, spacing: 2) {
                                    Text(book.name)
                                        .font(Theme.serifBody(17))
                                        .foregroundColor(Theme.textPrimary(colorScheme))
                                    if Theme.deuterocanonical.contains(book.name) {
                                        Text("Deuterocanonical")
                                            .font(.system(size: 11, weight: .medium))
                                            .foregroundColor(Theme.goldAccent(colorScheme))
                                    }
                                }
                                Spacer()
                                Text("\(book.chapters.count)")
                                    .font(Theme.serifItalic(14))
                                    .foregroundColor(.secondary)
                            }
                        }
                    }
                } header: {
                    Text(testament.rawValue)
                        .font(Theme.serifBold(13))
                        .foregroundColor(Theme.accent(colorScheme))
                        .textCase(nil)
                }
            }
        }
        .listStyle(.insetGrouped)
        .navigationTitle("Douay-Rheims Bible")
        .scrollContentBackground(.hidden)
        .background(Theme.background(colorScheme))
    }
}
