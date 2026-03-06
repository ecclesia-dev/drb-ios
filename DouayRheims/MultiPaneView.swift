import SwiftUI

struct MultiPaneView: View {
    @EnvironmentObject var bibleData: BibleDataManager
    @EnvironmentObject var navigator: BibleNavigator
    @EnvironmentObject var database: DatabaseManager
    @EnvironmentObject var bookmarks: BookmarkManager
    @EnvironmentObject var settings: SettingsManager
    @Environment(\.horizontalSizeClass) var horizontalSizeClass
    @Environment(\.colorScheme) var colorScheme

    @State private var panels: [Panel] = [
        Panel(resource: .drb),
        Panel(resource: .haydock)
    ]

    @State private var showSearch = false
    @State private var showBookmarks = false
    @State private var showSettings = false
    @State private var showReadingPlan = false
    @State private var selectedTab = 0

    private var isIPad: Bool {
        horizontalSizeClass == .regular
    }

    var body: some View {
        Group {
            if isIPad {
                iPadLayout
            } else {
                iPhoneLayout
            }
        }
        .sheet(isPresented: $showSearch) {
            NavigationStack { SearchView() }
                .environmentObject(bibleData)
                .environmentObject(bookmarks)
                .environmentObject(settings)
        }
        .sheet(isPresented: $showBookmarks) {
            NavigationStack { BookmarksView() }
                .environmentObject(bibleData)
                .environmentObject(bookmarks)
                .environmentObject(settings)
        }
        .sheet(isPresented: $showSettings) {
            NavigationStack { SettingsView() }
                .environmentObject(settings)
        }
        .sheet(isPresented: $showReadingPlan) {
            NavigationStack { ReadingPlanView() }
                .environmentObject(bibleData)
                .environmentObject(settings)
        }
    }

    // MARK: - iPad Layout (HStack of panels)

    private var iPadLayout: some View {
        VStack(spacing: 0) {
            // Toolbar
            iPadToolbar
            Divider()

            // Panels
            HStack(spacing: 0) {
                ForEach(panels.indices, id: \.self) { index in
                    if index > 0 {
                        Divider()
                    }
                    PanelView(
                        panel: $panels[index],
                        onClose: panels.count > 1 ? { removePanel(at: index) } : nil
                    )
                }
            }
        }
        .background(Theme.background(colorScheme))
    }

    private var iPadToolbar: some View {
        HStack(spacing: 16) {
            Text("Douay-Rheims")
                .font(Theme.serifBold(18))
                .foregroundColor(Theme.accent(colorScheme))

            Spacer()

            // Add panel
            if panels.count < maxPanels {
                Button {
                    addPanel()
                } label: {
                    Label("Add Panel", systemImage: "plus.rectangle.on.rectangle")
                        .font(.system(size: 14))
                        .foregroundColor(Theme.accent(colorScheme))
                }
            }

            Button {
                showSearch = true
            } label: {
                Image(systemName: "magnifyingglass")
                    .font(.system(size: 15))
                    .foregroundColor(Theme.accent(colorScheme))
            }

            Button {
                showReadingPlan = true
            } label: {
                Image(systemName: "calendar")
                    .font(.system(size: 15))
                    .foregroundColor(Theme.accent(colorScheme))
            }

            Button {
                showBookmarks = true
            } label: {
                Image(systemName: "bookmark")
                    .font(.system(size: 15))
                    .foregroundColor(Theme.accent(colorScheme))
            }

            Button {
                showSettings = true
            } label: {
                Image(systemName: "textformat.size")
                    .font(.system(size: 15))
                    .foregroundColor(Theme.accent(colorScheme))
            }
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 10)
        .background(Theme.background(colorScheme))
    }

    // MARK: - iPhone Layout (TabView of panels)

    private var iPhoneLayout: some View {
        TabView(selection: $selectedTab) {
            ForEach(panels.indices, id: \.self) { index in
                NavigationStack {
                    VStack(spacing: 0) {
                        PanelView(
                            panel: $panels[index],
                            onClose: panels.count > 1 ? { removePanel(at: index) } : nil
                        )
                    }
                    .toolbar {
                        ToolbarItemGroup(placement: .topBarTrailing) {
                            if panels.count < maxPanels {
                                Button {
                                    addPanel()
                                } label: {
                                    Image(systemName: "plus.rectangle.on.rectangle")
                                }
                            }
                        }
                    }
                    .navigationBarTitleDisplayMode(.inline)
                }
                .tabItem {
                    Label(panels[index].resource.shortName, systemImage: panels[index].resource.icon)
                }
                .tag(index)
            }

            NavigationStack { SearchView() }
                .tabItem {
                    Label("Search", systemImage: "magnifyingglass")
                }
                .tag(100)

            NavigationStack { ReadingPlanView() }
                .tabItem {
                    Label("Plan", systemImage: "calendar")
                }
                .tag(101)

            NavigationStack { BookmarksView() }
                .tabItem {
                    Label("Bookmarks", systemImage: "bookmark")
                }
                .tag(102)

            NavigationStack { SettingsView() }
                .tabItem {
                    Label("Settings", systemImage: "textformat.size")
                }
                .tag(103)
        }
        .tint(Theme.accent(colorScheme))
    }

    // MARK: - Panel Management

    private var maxPanels: Int {
        isIPad ? 4 : 2
    }

    private func addPanel() {
        guard panels.count < maxPanels else { return }
        let newResource: ResourceType = {
            let used = Set(panels.map(\.resource))
            for r in ResourceType.allCases where r.isCommentary && !used.contains(r) {
                return r
            }
            return .haydock
        }()
        panels.append(Panel(resource: newResource))
    }

    private func removePanel(at index: Int) {
        guard panels.count > 1 else { return }
        panels.remove(at: index)
        if selectedTab >= panels.count {
            selectedTab = panels.count - 1
        }
    }
}
