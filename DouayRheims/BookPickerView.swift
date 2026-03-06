import SwiftUI

struct BookPickerView: View {
    @EnvironmentObject var bibleData: BibleDataManager
    @Environment(\.colorScheme) var colorScheme
    @Environment(\.dismiss) var dismiss

    let onSelect: (Book, Int) -> Void

    @State private var selectedBook: Book?
    @State private var searchText = ""

    private var filteredBooks: [Book] {
        if searchText.isEmpty { return bibleData.books }
        let q = searchText.lowercased()
        return bibleData.books.filter {
            $0.name.lowercased().contains(q) || $0.abbreviation.lowercased().contains(q)
        }
    }

    var body: some View {
        NavigationStack {
            Group {
                if let book = selectedBook {
                    chapterGrid(book: book)
                } else {
                    bookList
                }
            }
            .navigationTitle(selectedBook?.name ?? "Select Book")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarLeading) {
                    if selectedBook != nil {
                        Button {
                            selectedBook = nil
                        } label: {
                            Label("Back", systemImage: "chevron.left")
                        }
                    }
                }
                ToolbarItem(placement: .topBarTrailing) {
                    Button("Done") { dismiss() }
                }
            }
            .background(Theme.background(colorScheme))
        }
    }

    // MARK: - Book List

    private var bookList: some View {
        List {
            ForEach(Testament.allCases, id: \.self) { testament in
                Section {
                    ForEach(filteredBooks.filter { $0.testament == testament }) { book in
                        Button {
                            selectedBook = book
                        } label: {
                            HStack {
                                VStack(alignment: .leading, spacing: 2) {
                                    Text(book.name)
                                        .font(Theme.serifBody(16))
                                        .foregroundColor(Theme.textPrimary(colorScheme))
                                    if Theme.deuterocanonical.contains(book.name) {
                                        Text("Deuterocanonical")
                                            .font(.caption2.weight(.medium))
                                            .foregroundColor(Theme.goldAccent(colorScheme))
                                    }
                                }
                                Spacer()
                                Text("\(book.chapters.count) ch.")
                                    .font(Theme.serifItalic(13))
                                    .foregroundColor(.secondary)
                                Image(systemName: "chevron.right")
                                    .font(.caption)
                                    .foregroundColor(.secondary)
                            }
                        }
                    }
                } header: {
                    Text(testament.rawValue)
                        .font(Theme.serifBold(12))
                        .foregroundColor(Theme.accent(colorScheme))
                        .textCase(nil)
                }
            }
        }
        .listStyle(.insetGrouped)
        .scrollContentBackground(.hidden)
        .searchable(text: $searchText, prompt: "Search books...")
    }

    // MARK: - Chapter Grid

    private func chapterGrid(book: Book) -> some View {
        ScrollView {
            LazyVGrid(columns: Array(repeating: GridItem(.flexible(), spacing: 12), count: 5), spacing: 12) {
                ForEach(book.chapters, id: \.self) { chapter in
                    Button {
                        onSelect(book, chapter)
                        dismiss()
                    } label: {
                        Text("\(chapter)")
                            .font(Theme.serifBody(16))
                            .frame(width: 56, height: 56)
                            .foregroundColor(Theme.textPrimary(colorScheme))
                            .background(
                                RoundedRectangle(cornerRadius: 10)
                                    .fill(Theme.accent(colorScheme).opacity(0.08))
                            )
                    }
                }
            }
            .padding(20)
        }
    }
}
