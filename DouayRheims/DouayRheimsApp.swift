import SwiftUI

@main
struct DouayRheimsApp: App {
    @StateObject private var bibleData = BibleDataManager.shared
    @StateObject private var bookmarks = BookmarkManager.shared
    @StateObject private var settings = SettingsManager.shared
    @StateObject private var commentary = CommentaryManager.shared

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(bibleData)
                .environmentObject(bookmarks)
                .environmentObject(settings)
                .environmentObject(commentary)
        }
    }
}
