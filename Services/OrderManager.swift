import Foundation

protocol OrderManagerDelegate: AnyObject {
    func didUpdateOrder(_ order: Order)
    func didCompleteOrder(_ order: Order)
    func didFailWithError(_ error: Error)
}

class OrderManager {
    private(set) var currentOrder: Order?
    weak var delegate: OrderManagerDelegate?
    
    private let fileManager = FileManager.default
    private let documentsPath = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
    
    func loadOrder(from barcode: String) {
        do {
            if let data = barcode.data(using: .utf8),
               let order = try? JSONDecoder().decode(Order.self, from: data) {
                self.currentOrder = order
                delegate?.didUpdateOrder(order)
                return
            }
            
            let orderPath = documentsPath.appendingPathComponent("\(barcode).json")
            let data = try Data(contentsOf: orderPath)
            let order = try JSONDecoder().decode(Order.self, from: data)
            self.currentOrder = order
            delegate?.didUpdateOrder(order)
        } catch {
            delegate?.didFailWithError(error)
        }
    }
    
    func updateItem(sku: String) -> Bool {
        guard var order = currentOrder,
              let itemIndex = order.items.firstIndex(where: { $0.sku == sku }) else {
            return false
        }
        
        if order.items[itemIndex].isComplete {
            return false
        }
        
        order.items[itemIndex].quantityPicked += 1
        currentOrder = order
        delegate?.didUpdateOrder(order)
        
        if order.isComplete {
            delegate?.didCompleteOrder(order)
        }
        
        return true
    }
    
    func completeOrder() {
        guard let order = currentOrder else { return }
        
        do {
            let completion = OrderCompletion(order: order, completedAt: Date())
            let encoder = JSONEncoder()
            encoder.dateEncodingStrategy = .iso8601
            
            let data = try encoder.encode(completion)
            let fileName = "completed_\(order.orderId)_\(Int(Date().timeIntervalSince1970)).json"
            let fileURL = documentsPath.appendingPathComponent(fileName)
            
            try data.write(to: fileURL)
            currentOrder = nil
            
        } catch {
            delegate?.didFailWithError(error)
        }
    }
}

struct OrderCompletion: Codable {
    let order: Order
    let completedAt: Date
}