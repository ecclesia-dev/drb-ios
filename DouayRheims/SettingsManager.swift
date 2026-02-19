import Foundation
import SwiftUI

@MainActor
final class SettingsManager: ObservableObject {
    static let shared = SettingsManager()

    @AppStorage("fontSize") var fontSize: Double = 18.0
    @AppStorage("lineSpacing") var lineSpacing: Double = 5.0
    @AppStorage("showCommentary") var showCommentary: Bool = true

    private init() {}

    var bodyFont: Font {
        .custom("Georgia", size: CGFloat(fontSize))
    }

    var verseNumberFont: Font {
        .custom("Georgia-Bold", size: CGFloat(fontSize * 0.67))
    }

    var headerFont: Font {
        .custom("Georgia-Bold", size: CGFloat(fontSize * 1.33))
    }

    var subHeaderFont: Font {
        .custom("Georgia-Italic", size: CGFloat(fontSize))
    }
}
