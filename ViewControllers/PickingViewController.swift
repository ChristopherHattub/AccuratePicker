import UIKit

class PickingViewController: UIViewController {
    private let scanner = BarcodeScanner()
    private let orderManager = OrderManager()
    
    private let scannerContainer: UIView = {
        let view = UIView()
        view.backgroundColor = .black
        return view
    }()
    
    private let tableView: UITableView = {
        let table = UITableView()
        table.backgroundColor = .clear
        table.separatorStyle = .none
        table.register(ItemCell.self, forCellReuseIdentifier: ItemCell.reuseIdentifier)
        return table
    }()
    
    private let completeButton: UIButton = {
        let button = UIButton(type: .system)
        button.setTitle("Complete Order", for: .normal)
        button.titleLabel?.font = .systemFont(ofSize: 18, weight: .bold)
        button.backgroundColor = .systemBlue
        button.tintColor = .white
        button.layer.cornerRadius = 12
        button.isEnabled = false
        return button
    }()
    
    private let statusLabel: UILabel = {
        let label = UILabel()
        label.font = .systemFont(ofSize: 18, weight: .medium)
        label.textAlignment = .center
        label.text = "Scan Order Barcode"
        return label
    }()
    
    override func viewDidLoad() {
        super.viewDidLoad()
        setupViews()
        setupDelegates()
    }
    
    private func setupViews() {
        view.backgroundColor = .systemBackground
        
        view.addSubview(scannerContainer)
        view.addSubview(statusLabel)
        view.addSubview(tableView)
        view.addSubview(completeButton)
        
        setupConstraints()
        completeButton.addTarget(self, action: #selector(completeButtonTapped), for: .touchUpInside)
        
        scanner.setupInView(scannerContainer)
    }
    
    private func setupConstraints() {
        scannerContainer.translatesAutoresizingMaskIntoConstraints = false
        statusLabel.translatesAutoresizingMaskIntoConstraints = false
        tableView.translatesAutoresizingMaskIntoConstraints = false
        completeButton.translatesAutoresizingMaskIntoConstraints = false
        
        NSLayoutConstraint.activate([
            scannerContainer.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor),
            scannerContainer.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            scannerContainer.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            scannerContainer.heightAnchor.constraint(equalToConstant: 200),
            
            statusLabel.topAnchor.constraint(equalTo: scannerContainer.bottomAnchor, constant: 16),
            statusLabel.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 16),
            statusLabel.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -16),
            
            tableView.topAnchor.constraint(equalTo: statusLabel.bottomAnchor, constant: 16),
            tableView.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            tableView.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            tableView.bottomAnchor.constraint(equalTo: completeButton.topAnchor, constant: -16),
            
            completeButton.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 16),
            completeButton.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -16),
            completeButton.bottomAnchor.constraint(equalTo: view.safeAreaLayoutGuide.bottomAnchor, constant: -16),
            completeButton.heightAnchor.constraint(equalToConstant: 50)
        ])
    }
    
    private func setupDelegates() {
        scanner.delegate = self
        orderManager.delegate = self
        tableView.dataSource = self
    }
    
    @objc private func completeButtonTapped() {
        let alert = UIAlertController(
            title: "Complete Order",
            message: "Are you sure you want to complete this order?",
            preferredStyle: .alert
        )
        
        alert.addAction(UIAlertAction(title: "Cancel", style: .cancel))
        alert.addAction(UIAlertAction(title: "Complete", style: .default) { [weak self] _ in
            self?.orderManager.completeOrder()
            self?.resetState()
        })
        
        present(alert, animated: true)
    }
    
    private func resetState() {
        statusLabel.text = "Scan Order Barcode"
        completeButton.isEnabled = false
        completeButton.backgroundColor = .systemBlue
        tableView.reloadData()
    }
}

// MARK: - BarcodeScannerDelegate
extension PickingViewController: BarcodeScannerDelegate {
    func didScanBarcode(_ code: String) {
        if orderManager.currentOrder == nil {
            orderManager.loadOrder(from: code)
        } else {
            if !orderManager.updateItem(sku: code) {
                showAlert(message: "Invalid item or already picked")
            }
        }
    }
    
    func didFailWithError(_ error: Error) {
        showAlert(message: error.localizedDescription)
    }
}

// MARK: - OrderManagerDelegate
extension PickingViewController: OrderManagerDelegate {
    func didUpdateOrder(_ order: Order) {
        statusLabel.text = "Order: \(order.orderId)"
        completeButton.isEnabled = true
        tableView.reloadData()
    }
    
    func didCompleteOrder(_ order: Order) {
        completeButton.backgroundColor = .systemGreen
    }
    
    func didFailWithError(_ error: Error) {
        showAlert(message: error.localizedDescription)
    }
}

// MARK: - UITableViewDataSource
extension PickingViewController: UITableViewDataSource {
    func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        return orderManager.currentOrder?.items.count ?? 0
    }
    
    func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell = tableView.dequeueReusableCell(withIdentifier: ItemCell.reuseIdentifier, for: indexPath) as! ItemCell
        if let item = orderManager.currentOrder?.items[indexPath.row] {
            cell.configure(with: item)
        }
        return cell
    }
}

// MARK: - Helper Methods
private extension PickingViewController {
    func showAlert(message: String) {
        let alert = UIAlertController(title: "Error", message: message, preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "OK", style: .default))
        present(alert, animated: true)
    }
}