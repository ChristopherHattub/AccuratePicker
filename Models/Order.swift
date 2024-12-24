struct Order: Codable {
    let orderId: String
    let customer: String
    let date: String
    var items: [OrderItem]
    
    var isComplete: Bool {
        return items.allSatisfy { $0.isComplete }
    }
}