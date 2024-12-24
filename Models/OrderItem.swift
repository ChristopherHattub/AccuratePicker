struct OrderItem: Codable {
    let sku: String
    let name: String
    let quantity: Int
    var quantityPicked: Int = 0
    
    var isComplete: Bool {
        return quantityPicked >= quantity
    }
}