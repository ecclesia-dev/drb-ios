import SwiftUI

// A simple "Bible in a Year" reading plan: ~3-4 chapters per day across 365 days
// Covers all 73 books in canonical order

struct ReadingPlanView: View {
    @EnvironmentObject var bibleData: BibleDataManager
    @Environment(\.colorScheme) var colorScheme
    @AppStorage("readingPlanStartDate") private var startDateString: String = ""
    @AppStorage("readingPlanCompletedDays") private var completedDaysData: Data = Data()

    private var completedDays: Set<Int> {
        (try? JSONDecoder().decode(Set<Int>.self, from: completedDaysData)) ?? []
    }

    private var startDate: Date? {
        guard !startDateString.isEmpty else { return nil }
        return ISO8601DateFormatter().date(from: startDateString)
    }

    private var currentDayNumber: Int {
        guard let start = startDate else { return 1 }
        let days = Calendar.current.dateComponents([.day], from: start, to: Date()).day ?? 0
        return min(max(days + 1, 1), 365)
    }

    var body: some View {
        Group {
            if startDate == nil {
                startPlanView
            } else {
                planProgressView
            }
        }
        .navigationTitle("Reading Plan")
        .background(Theme.background(colorScheme))
    }

    private var startPlanView: some View {
        VStack(spacing: 24) {
            Spacer()
            Image(systemName: "calendar.badge.clock")
                .font(.system(size: 56))
                .foregroundColor(Theme.accent(colorScheme).opacity(0.6))

            Text("Read the Bible in a Year")
                .font(Theme.serifBold(22))
                .foregroundColor(Theme.textPrimary(colorScheme))

            Text("A daily reading plan covering all 73 books of the Douay-Rheims Bible in canonical order.")
                .font(Theme.serifItalic(16))
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
                .padding(.horizontal, 32)

            Button {
                startDateString = ISO8601DateFormatter().string(from: Date())
            } label: {
                Text("Begin Today")
                    .font(Theme.serifBold(18))
                    .foregroundColor(.white)
                    .padding(.horizontal, 32)
                    .padding(.vertical, 14)
                    .background(Theme.accent(colorScheme))
                    .clipShape(RoundedRectangle(cornerRadius: 12))
            }
            Spacer()
        }
    }

    private var planProgressView: some View {
        List {
            Section {
                VStack(alignment: .leading, spacing: 8) {
                    Text("Day \(currentDayNumber) of 365")
                        .font(Theme.serifBold(20))
                        .foregroundColor(Theme.textPrimary(colorScheme))

                    ProgressView(value: Double(completedDays.count), total: 365)
                        .tint(Theme.accent(colorScheme))

                    Text("\(completedDays.count) of 365 days completed")
                        .font(Theme.serifItalic(14))
                        .foregroundColor(.secondary)
                }
                .padding(.vertical, 8)
            }

            // Today's reading highlighted
            let todayReading = ReadingPlan.readings[currentDayNumber - 1]
            Section {
                VStack(alignment: .leading, spacing: 8) {
                    HStack {
                        Text("Today's Reading")
                            .font(Theme.serifBold(16))
                            .foregroundColor(Theme.accent(colorScheme))
                        Spacer()
                        if completedDays.contains(currentDayNumber) {
                            Image(systemName: "checkmark.circle.fill")
                                .foregroundColor(.green)
                        }
                    }

                    ForEach(todayReading.passages, id: \.self) { passage in
                        NavigationLink(destination: chapterDestination(passage)) {
                            Text(passage)
                                .font(Theme.serifBody(16))
                                .foregroundColor(Theme.textPrimary(colorScheme))
                        }
                    }

                    if !completedDays.contains(currentDayNumber) {
                        Button {
                            markCompleted(currentDayNumber)
                        } label: {
                            Text("Mark as Read")
                                .font(Theme.serifBold(15))
                                .frame(maxWidth: .infinity)
                                .padding(.vertical, 10)
                                .background(Theme.accent(colorScheme).opacity(0.15))
                                .foregroundColor(Theme.accent(colorScheme))
                                .clipShape(RoundedRectangle(cornerRadius: 8))
                        }
                        .buttonStyle(.plain)
                    }
                }
                .padding(.vertical, 4)
            }

            // Upcoming readings
            Section("Upcoming") {
                ForEach(upcomingDays(), id: \.day) { item in
                    VStack(alignment: .leading, spacing: 4) {
                        HStack {
                            Text("Day \(item.day)")
                                .font(Theme.serifBold(14))
                                .foregroundColor(Theme.accent(colorScheme))
                            Spacer()
                            if completedDays.contains(item.day) {
                                Image(systemName: "checkmark.circle.fill")
                                    .font(.system(size: 14))
                                    .foregroundColor(.green)
                            }
                        }
                        Text(item.passages.joined(separator: ", "))
                            .font(Theme.serifBody(14))
                            .foregroundColor(Theme.textPrimary(colorScheme))
                            .lineLimit(2)
                    }
                    .padding(.vertical, 2)
                }
            }

            Section {
                Button(role: .destructive) {
                    startDateString = ""
                    completedDaysData = Data()
                } label: {
                    Text("Reset Reading Plan")
                        .font(Theme.serifBody(15))
                }
            }
        }
        .listStyle(.insetGrouped)
        .scrollContentBackground(.hidden)
    }

    private func upcomingDays() -> [DailyReading] {
        let start = currentDayNumber
        let end = min(start + 6, 365)
        guard start < end else { return [] }
        return (start..<end).map { ReadingPlan.readings[$0] } // days after today
    }

    private func markCompleted(_ day: Int) {
        var days = completedDays
        days.insert(day)
        completedDaysData = (try? JSONEncoder().encode(days)) ?? Data()
    }

    @ViewBuilder
    private func chapterDestination(_ passage: String) -> some View {
        // Parse "Genesis 1-3" or "Genesis 1" into a chapter view
        let parsed = ReadingPlan.parsePassage(passage, books: bibleData.books)
        if let book = parsed.book {
            ChapterView(book: book, chapter: parsed.startChapter)
        } else {
            Text(passage)
        }
    }
}

// MARK: - Reading Plan Data

struct DailyReading: Identifiable {
    let day: Int
    let passages: [String]
    var id: Int { day }
}

enum ReadingPlan {
    // Generate a 365-day plan covering all chapters
    static let readings: [DailyReading] = generatePlan()

    struct ParsedPassage {
        let book: Book?
        let startChapter: Int
    }

    static func parsePassage(_ passage: String, books: [Book]) -> ParsedPassage {
        // "Genesis 1" or "Genesis 1-3"
        let parts = passage.components(separatedBy: " ")
        guard parts.count >= 2 else { return ParsedPassage(book: nil, startChapter: 1) }

        let chapterPart = parts.last!
        let bookName = parts.dropLast().joined(separator: " ")
        let chapter = Int(chapterPart.components(separatedBy: "-").first ?? "1") ?? 1
        let book = books.first { $0.name == bookName }
        return ParsedPassage(book: book, startChapter: chapter)
    }

    private static func generatePlan() -> [DailyReading] {
        // All 73 books with chapter counts in canonical order
        let bookChapters: [(String, Int)] = [
            ("Genesis", 50), ("Exodus", 40), ("Leviticus", 27), ("Numbers", 36),
            ("Deuteronomy", 34), ("Joshua", 24), ("Judges", 21), ("Ruth", 4),
            ("1 Samuel", 31), ("2 Samuel", 24), ("1 Kings", 22), ("2 Kings", 25),
            ("1 Chronicles", 29), ("2 Chronicles", 36), ("Ezra", 10), ("Nehemiah", 13),
            ("Tobit", 14), ("Judith", 16), ("Esther", 16), ("Job", 42),
            ("Psalms", 150), ("Proverbs", 31), ("Ecclesiastes", 12), ("Song of Solomon", 8),
            ("Wisdom", 19), ("Sirach", 51), ("Isaiah", 66), ("Jeremiah", 52),
            ("Lamentations", 5), ("Baruch", 6), ("Ezekiel", 48), ("Daniel", 14),
            ("Hosea", 14), ("Joel", 3), ("Amos", 9), ("Obadiah", 1),
            ("Jonah", 4), ("Micah", 7), ("Nahum", 3), ("Habakkuk", 3),
            ("Zephaniah", 3), ("Haggai", 2), ("Zechariah", 14), ("Malachi", 4),
            ("1 Maccabees", 16), ("2 Maccabees", 15),
            ("Matthew", 28), ("Mark", 16), ("Luke", 24), ("John", 21),
            ("Acts", 28), ("Romans", 16), ("1 Corinthians", 16), ("2 Corinthians", 13),
            ("Galatians", 6), ("Ephesians", 6), ("Philippians", 4), ("Colossians", 4),
            ("1 Thessalonians", 5), ("2 Thessalonians", 3), ("1 Timothy", 6), ("2 Timothy", 4),
            ("Titus", 3), ("Philemon", 1), ("Hebrews", 13), ("James", 5),
            ("1 Peter", 5), ("2 Peter", 3), ("1 John", 5), ("2 John", 1),
            ("3 John", 1), ("Jude", 1), ("Apocalypse", 22),
        ]

        // Flatten all chapters
        var allChapters: [(book: String, chapter: Int)] = []
        for (book, count) in bookChapters {
            for ch in 1...count {
                allChapters.append((book, ch))
            }
        }

        // Total chapters: ~1334. Distribute across 365 days (~3-4 per day)
        let totalChapters = allChapters.count
        var readings: [DailyReading] = []
        var idx = 0

        for day in 1...365 {
            let remaining = totalChapters - idx
            let remainingDays = 366 - day
            let todayCount = max(1, (remaining + remainingDays - 1) / remainingDays)
            let endIdx = min(idx + todayCount, totalChapters)

            var passages: [String] = []
            var i = idx
            while i < endIdx {
                let book = allChapters[i].book
                let startCh = allChapters[i].chapter
                // Group consecutive chapters of same book
                var endCh = startCh
                while i + 1 < endIdx && allChapters[i + 1].book == book && allChapters[i + 1].chapter == endCh + 1 {
                    i += 1
                    endCh = allChapters[i].chapter
                }
                if startCh == endCh {
                    passages.append("\(book) \(startCh)")
                } else {
                    passages.append("\(book) \(startCh)-\(endCh)")
                }
                i += 1
            }

            readings.append(DailyReading(day: day, passages: passages))
            idx = endIdx
        }

        return readings
    }
}
