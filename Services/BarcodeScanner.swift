import AVFoundation

protocol BarcodeScannerDelegate: AnyObject {
    func didScanBarcode(_ code: String)
    func didFailWithError(_ error: Error)
}

class BarcodeScanner: NSObject {
    private var captureSession: AVCaptureSession?
    private var previewLayer: AVCaptureVideoPreviewLayer?
    weak var delegate: BarcodeScannerDelegate?
    
    override init() {
        super.init()
        checkCameraPermissions()
    }
    
    private func checkCameraPermissions() {
        switch AVCaptureDevice.authorizationStatus(for: .video) {
        case .authorized:
            break
        case .notDetermined:
            AVCaptureDevice.requestAccess(for: .video) { [weak self] granted in
                if granted {
                    DispatchQueue.main.async {
                        self?.setupScanner()
                    }
                }
            }
        default:
            delegate?.didFailWithError(ScannerError.noCameraAccess)
        }
    }
    
    func setupInView(_ view: UIView) {
        guard let captureSession = self.captureSession else {
            setupScanner()
            return
        }
        
        previewLayer = AVCaptureVideoPreviewLayer(session: captureSession)
        previewLayer?.frame = view.layer.bounds
        previewLayer?.videoGravity = .resizeAspectFill
        
        if let previewLayer = previewLayer {
            view.layer.addSublayer(previewLayer)
        }
        
        startScanning()
    }
    
    private func setupScanner() {
        let session = AVCaptureSession()
        
        guard let videoCaptureDevice = AVCaptureDevice.default(for: .video),
              let videoInput = try? AVCaptureDeviceInput(device: videoCaptureDevice) else {
            delegate?.didFailWithError(ScannerError.deviceNotFound)
            return
        }
        
        let metadataOutput = AVCaptureMetadataOutput()
        
        if session.canAddInput(videoInput) && session.canAddOutput(metadataOutput) {
            session.addInput(videoInput)
            session.addOutput(metadataOutput)
            
            metadataOutput.setMetadataObjectsDelegate(self, queue: DispatchQueue.main)
            metadataOutput.metadataObjectTypes = [.ean8, .ean13, .pdf417, .qr]
            
            self.captureSession = session
        } else {
            delegate?.didFailWithError(ScannerError.invalidSetup)
        }
    }
    
    func startScanning() {
        DispatchQueue.global(qos: .background).async { [weak self] in
            self?.captureSession?.startRunning()
        }
    }
    
    func stopScanning() {
        captureSession?.stopRunning()
    }
}

extension BarcodeScanner: AVCaptureMetadataOutputObjectsDelegate {
    func metadataOutput(_ output: AVCaptureMetadataOutput,
                       didOutput metadataObjects: [AVMetadataObject],
                       from connection: AVCaptureConnection) {
        if let metadataObject = metadataObjects.first as? AVMetadataMachineReadableCodeObject,
           let stringValue = metadataObject.stringValue {
            delegate?.didScanBarcode(stringValue)
        }
    }
}

enum ScannerError: LocalizedError {
    case noCameraAccess
    case deviceNotFound
    case invalidSetup
    
    var errorDescription: String? {
        switch self {
        case .noCameraAccess:
            return "Camera access is required to scan barcodes"
        case .deviceNotFound:
            return "No camera device found"
        case .invalidSetup:
            return "Failed to setup camera"
        }
    }
}
