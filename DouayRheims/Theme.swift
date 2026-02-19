import SwiftUI

enum Theme {
    // MARK: - Colors
    static let parchment = Color(red: 0.96, green: 0.93, blue: 0.88)
    static let parchmentDark = Color(red: 0.12, green: 0.11, blue: 0.10)
    static let burgundy = Color(red: 0.545, green: 0.220, blue: 0.290)
    static let burgundyLight = Color(red: 0.690, green: 0.350, blue: 0.420)
    static let gold = Color(red: 0.72, green: 0.60, blue: 0.35)
    static let goldLight = Color(red: 0.85, green: 0.75, blue: 0.55)
    static let inkBrown = Color(red: 0.25, green: 0.20, blue: 0.15)
    static let inkLight = Color(red: 0.85, green: 0.82, blue: 0.78)

    // Deuterocanonical books
    static let deuterocanonical: Set<String> = [
        "Tobit", "Judith", "Wisdom", "Sirach", "Baruch",
        "1 Maccabees", "2 Maccabees"
    ]

    // MARK: - Fonts
    static func serifBody(_ size: CGFloat = 18) -> Font {
        .custom("Georgia", size: size)
    }

    static func serifBold(_ size: CGFloat = 18) -> Font {
        .custom("Georgia-Bold", size: size)
    }

    static func serifItalic(_ size: CGFloat = 16) -> Font {
        .custom("Georgia-Italic", size: size)
    }

    // MARK: - Adaptive colors
    static func background(_ colorScheme: ColorScheme) -> Color {
        colorScheme == .dark ? parchmentDark : parchment
    }

    static func textPrimary(_ colorScheme: ColorScheme) -> Color {
        colorScheme == .dark ? inkLight : inkBrown
    }

    static func accent(_ colorScheme: ColorScheme) -> Color {
        colorScheme == .dark ? burgundyLight : burgundy
    }

    static func goldAccent(_ colorScheme: ColorScheme) -> Color {
        colorScheme == .dark ? goldLight : gold
    }
}
