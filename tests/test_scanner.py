import unittest
from unittest.mock import Mock, patch
import json
from scanner import BarcodeScanner

class TestBarcodeScanner(unittest.TestCase):
    def setUp(self):
        """Initialize scanner and mocks before each test"""
        with patch('AVFoundation.AVCaptureSession') as mock_session:
            with patch('AVFoundation.AVCaptureDevice') as mock_device:
                self.scanner = BarcodeScanner()
                self.scanner.session = mock_session
                self.scanner.device = mock_device

    def test_valid_order_barcode(self):
        """Test scanning valid order barcode"""
        mock_data = {
            "order_id": "ORD001",
            "items": [{"sku": "ABC123", "quantity": 1}]
        }
        
        with patch.object(
            self.scanner, 
            '_convert_sample_buffer_to_image',
            return_value=Mock()
        ) as mock_convert:
            with patch('pyzbar.pyzbar.decode') as mock_decode:
                # Setup mock barcode data
                mock_decode.return_value = [
                    Mock(
                        data=json.dumps(mock_data).encode('utf-8')
                    )
                ]
                
                # Test scan
                result = self.scanner.scan_barcode()
                
                # Verify result
                self.assertEqual(
                    json.loads(result),
                    mock_data
                )
                
                # Verify scan was attempted
                mock_convert.assert_called_once()
                mock_decode.assert_called_once()

    def test_valid_item_barcode(self):
        """Test scanning valid item barcode"""
        mock_sku = "ABC123"
        
        with patch.object(
            self.scanner,
            '_convert_sample_buffer_to_image',
            return_value=Mock()
        ) as mock_convert:
            with patch('pyzbar.pyzbar.decode') as mock_decode:
                mock_decode.return_value = [
                    Mock(
                        data=mock_sku.encode('utf-8')
                    )
                ]
                
                result = self.scanner.scan_barcode()
                self.assertEqual(result, mock_sku)

    def test_no_barcode_detected(self):
        """Test handling when no barcode is found"""
        with patch.object(
            self.scanner,
            '_convert_sample_buffer_to_image',
            return_value=Mock()
        ):
            with patch('pyzbar.pyzbar.decode', return_value=[]):
                with self.assertRaises(RuntimeError):
                    self.scanner.scan_barcode()

    def test_camera_error(self):
        """Test handling camera/hardware errors"""
        self.scanner.session.startRunning.side_effect = Exception(
            "Camera error"
        )
        
        with self.assertRaises(Exception):
            self.scanner.scan_barcode()

    def test_invalid_json_order(self):
        """Test handling invalid JSON in order barcode"""
        with patch.object(
            self.scanner,
            '_convert_sample_buffer_to_image',
            return_value=Mock()
        ):
            with patch('pyzbar.pyzbar.decode') as mock_decode:
                mock_decode.return_value = [
                    Mock(
                        data=b"Invalid JSON data"
                    )
                ]
                
                # Should return raw string since it's not JSON
                result = self.scanner.scan_barcode()
                self.assertEqual(result, "Invalid JSON data")

    def test_cleanup(self):
        """Test scanner cleanup on destruction"""
        self.scanner.__del__()
        self.scanner.session.stopRunning.assert_called_once()

if __name__ == '__main__':
    unittest.main()