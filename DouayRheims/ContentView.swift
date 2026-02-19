import SwiftUI

struct ContentView: View {
    @Environment(\.colorScheme) var colorScheme

    var body: some View {
        TabView {
            NavigationStack {
                BookListView()
            }
            .tabItem {
                Label("Bible", systemImage: "book.closed")
            }

            NavigationStack {
                SearchView()
            }
            .tabItem {
                Label("Search", systemImage: "magnifyingglass")
            }

            NavigationStack {
                ReadingPlanView()
            }
            .tabItem {
                Label("Plan", systemImage: "calendar")
            }

            NavigationStack {
                BookmarksView()
            }
            .tabItem {
                Label("Bookmarks", systemImage: "bookmark")
            }

            NavigationStack {
                SettingsView()
            }
            .tabItem {
                Label("Settings", systemImage: "textformat.size")
            }
        }
        .tint(Theme.accent(colorScheme))
    }
}
