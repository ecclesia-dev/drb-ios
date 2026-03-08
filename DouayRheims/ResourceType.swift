import Foundation

enum ResourceType: String, CaseIterable, Identifiable {
    case drb = "Douay-Rheims"
    case vulgate = "Vulgate"
    case drb1609 = "Douay-Rheims 1609"
    case haydock = "Haydock"
    case lapide = "Lapide"
    case chrysostom = "Chrysostom"
    case aquinas = "Aquinas"
    case douai = "Douai 1609"

    var id: String { rawValue }

    var shortName: String {
        switch self {
        case .drb: return "Douay-Rheims (Challoner)"
        case .vulgate: return "Vulgate (Clementine)"
        case .drb1609: return "Douay-Rheims (1609)"
        case .haydock: return "Haydock"
        case .lapide: return "Lapide"
        case .chrysostom: return "Chrysostom"
        case .aquinas: return "Aquinas"
        case .douai: return "Douai 1609 Annotations"
        }
    }

    var dbSource: String {
        switch self {
        case .drb: return ""
        case .vulgate: return ""
        case .drb1609: return ""
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
        case .vulgate: return "Clementine Vulgate (Latin, 1592)"
        case .drb1609: return "Douay OT (1609) / Rheims NT (1582)"
        case .haydock: return "Haydock Catholic Bible Commentary"
        case .lapide: return "Cornelius a Lapide"
        case .chrysostom: return "St. John Chrysostom"
        case .aquinas: return "St. Thomas Aquinas"
        case .douai: return "Original Douai Annotations (1609)"
        }
    }

    /// True for commentary panels; false for Bible text panels.
    var isCommentary: Bool {
        switch self {
        case .drb, .vulgate, .drb1609: return false
        default: return true
        }
    }

    /// The Translation enum value for Bible-text resources; nil for commentaries.
    var translation: Translation? {
        switch self {
        case .drb: return .challoner
        case .vulgate: return .vulgate
        case .drb1609: return .douai1609
        default: return nil
        }
    }

    var spellingNote: String? {
        switch self {
        case .vulgate:
            return "Clementine Vulgate, the authoritative Latin text of the Catholic Church (Sixtus V / Clement VIII, 1592)."
        case .drb1609:
            return "Original 1609 (OT) / 1582 (NT) spelling is preserved. Old English orthography — including ſ (long s) printed as f, and other archaic forms — is authentic, not an error."
        case .douai:
            return "Original 1609 spelling is preserved. Old English orthography — including ſ (long s) printed as f, and other archaic forms — is authentic, not an error."
        default:
            return nil
        }
    }

    var icon: String {
        switch self {
        case .drb: return "book.closed.fill"
        case .vulgate: return "book.closed.fill"
        case .drb1609: return "book.closed.fill"
        case .haydock: return "text.bubble.fill"
        case .lapide: return "text.bubble.fill"
        case .chrysostom: return "text.bubble.fill"
        case .aquinas: return "text.bubble.fill"
        case .douai: return "text.bubble.fill"
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
