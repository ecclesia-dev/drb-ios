import SwiftUI

struct SettingsView: View {
    @EnvironmentObject var settings: SettingsManager
    @Environment(\.colorScheme) var colorScheme

    var body: some View {
        List {
            Section("Text Size") {
                VStack(alignment: .leading, spacing: 12) {
                    HStack {
                        Text("A")
                            .font(.custom("Georgia", size: 14))
                            .foregroundColor(.secondary)
                        Slider(value: $settings.fontSize, in: 14...28, step: 1)
                            .tint(Theme.accent(colorScheme))
                        Text("A")
                            .font(.custom("Georgia", size: 28))
                            .foregroundColor(.secondary)
                    }

                    // Preview
                    VStack(alignment: .leading, spacing: 4) {
                        Text("1 ")
                            .font(.custom("Georgia-Bold", size: CGFloat(settings.fontSize * 0.67)))
                            .foregroundColor(Theme.accent(colorScheme))
                        +
                        Text("In the beginning God created heaven, and earth.")
                            .font(.custom("Georgia", size: CGFloat(settings.fontSize)))
                            .foregroundColor(Theme.textPrimary(colorScheme))
                    }
                    .lineSpacing(CGFloat(settings.lineSpacing))
                    .padding(12)
                    .background(
                        RoundedRectangle(cornerRadius: 8)
                            .fill(Theme.background(colorScheme).opacity(0.5))
                    )
                }
                .padding(.vertical, 8)
            }

            Section("Line Spacing") {
                HStack {
                    Image(systemName: "text.alignleft")
                        .foregroundColor(.secondary)
                    Slider(value: $settings.lineSpacing, in: 2...12, step: 1)
                        .tint(Theme.accent(colorScheme))
                    Image(systemName: "line.3.horizontal")
                        .foregroundColor(.secondary)
                }
            }

            Section("About") {
                VStack(alignment: .leading, spacing: 8) {
                    Text("Douay-Rheims Bible")
                        .font(Theme.serifBold(17))
                        .foregroundColor(Theme.textPrimary(colorScheme))
                    Text("The Douay-Rheims Bible is an English translation of the Latin Vulgate, originally published by the English College at Douay (OT, 1609) and Rheims (NT, 1582). It includes all 73 books of the Catholic canon, including the Deuterocanonical books.")
                        .font(Theme.serifBody(14))
                        .foregroundColor(.secondary)
                        .lineSpacing(3)
                }
                .padding(.vertical, 4)
            }
        }
        .listStyle(.insetGrouped)
        .scrollContentBackground(.hidden)
        .background(Theme.background(colorScheme))
        .navigationTitle("Settings")
    }
}
