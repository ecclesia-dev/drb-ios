import SwiftUI

// MARK: - Loading View

struct LoadingView: View {
    @EnvironmentObject var database: DatabaseManager

    var body: some View {
        VStack(spacing: 12) {
            Spacer()
            ProgressView()
            Text("Preparing your Bible...")
                .font(.system(.body, design: .serif))
                .foregroundColor(.secondary)
            if !database.isReady {
                Text("Building study database (first launch only)")
                    .font(.caption)
                    .foregroundColor(.secondary.opacity(0.7))
            }
            Spacer()
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }
}

// MARK: - Root View

struct ContentView: View {
    @EnvironmentObject var bibleData: BibleDataManager
    @EnvironmentObject var database: DatabaseManager
    @Environment(\.horizontalSizeClass) var horizontalSizeClass
    @Environment(\.colorScheme) var colorScheme

    var body: some View {
        if !bibleData.isLoaded || !database.isReady {
            LoadingView()
        } else {
            MultiPaneView()
        }
    }
}
