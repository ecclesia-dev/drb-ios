import Foundation

enum ResourceType: String, CaseIterable, Identifiable {
    case drb = "Douay-Rheims"
    case haydock = "Haydock"
    case lapide = "Lapide"
    case chrysostom = "Chrysostom"
    case aquinas = "Aquinas"
    case douai = "Douai 1609"

    var id: String { rawValue }

    var shortName: String {
        switch self {
        case .drb: return "DRB"
        case .haydock: return "Haydock"
        case .lapide: return "Lapide"
        case .chrysostom: return "Chrysostom"
        case .aquinas: return "Aquinas"
        case .douai: return "Douai"
        }
    }

    var dbSource: String {
        switch self {
        case .drb: return ""
        case .haydock: return "haydock"
        case .lapide: return "lapide"
        case .chrysostom: return "chrysostom"
        case .aquinas: return "aquinas"
        case .douai: return "douai"
        }
    }

    var description: String {
        switch self {
        case .drb: return "Douay-Rheims Bible"
        case .haydock: return "Haydock Catholic Bible Commentary"
        case .lapide: return "Cornelius a Lapide"
        case .chrysostom: return "St. John Chrysostom"
        case .aquinas: return "St. Thomas Aquinas"
        case .douai: return "Original Douai Annotations (1609)"
        }
    }

    var isCommentary: Bool {
        self != .drb
    }

    var spellingNote: String? {
        switch self {
        case .douai:
            return "Original 1609 spelling is preserved. Old English orthography — including ſ (long s) printed as f, and other archaic forms — is authentic, not an error."
        default:
            return nil
        }
    }

    var icon: String {
        switch self {
        case .drb: return "book.closed"
        case .haydock: return "text.book.closed"
        case .lapide: return "text.quote"
        case .chrysostom: return "person.text.rectangle"
        case .aquinas: return "graduationcap"
        case .douai: return "scroll"
        }
    }
}

struct Panel: Identifiable {
    let id = UUID()
    var resource: ResourceType
    var isLinked: Bool = true
    // Independent navigation for unlinked panels
    var independentBook: String = "Genesis"
    var independentAbbreviation: String = "Gn"
    var independentChapter: Int = 1
}
