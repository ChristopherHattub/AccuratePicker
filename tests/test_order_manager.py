import unittest
from unittest.mock import mock_open, patch
import json
from pathlib import Path
from order_manager import OrderManager

class TestOrderManager(unittest.TestCase):
    def setUp(self):
        self.manager = OrderManager(data_dir="test_data")
        self.sample_order = {
            "order_id": "TEST001",
            "items": [
                {"sku": "ABC123", "quantity": 2},
                {"sku": "XYZ789", "quantity": 1}
            ]
        }
        
    def test_load_order_from_json_string(self):
        """Test loading order from JSON string (barcode data)"""
        order_json = json.dumps(self.sample_order)
        loaded_order = self.manager.load_order(order_json)
        
        self.assertEqual(loaded_order["order_id"], "TEST001")
        self.assertEqual(len(loaded_order["items"]), 2)
        self.assertEqual(loaded_order["items"][0]["quantity"], 2)
        
    def test_load_order_from_file(self):
        """Test loading order from JSON file"""
        mock_file_content = json.dumps(self.sample_order)
        
        with patch("pathlib.Path.exists") as mock_exists:
            mock_exists.return_value = True
            with patch("builtins.open", mock_open(read_data=mock_file_content)):
                loaded_order = self.manager.load_order("TEST001")
                
                self.assertEqual(loaded_order["order_id"], "TEST001")
                self.assertEqual(len(loaded_order["items"]), 2)
                
    def test_load_invalid_order_file(self):
        """Test handling non-existent order file"""
        with patch("pathlib.Path.exists") as mock_exists:
            mock_exists.return_value = False
            with self.assertRaises(FileNotFoundError):
                self.manager.load_order("INVALID")
                
    def test_load_invalid_order_data(self):
        """Test loading order with missing required fields"""
        invalid_order = {
            "order_id": "TEST002"
            # Missing 'items' field
        }
        
        with self.assertRaises(ValueError):
            self.manager.load_order(json.dumps(invalid_order))
            
    def test_update_order_progress(self):
        """Test updating order progress with picked items"""
        self.manager.load_order(json.dumps(self.sample_order))
        
        # Update first item
        result = self.manager.update_order("ABC123")
        self.assertEqual(result["picked"], 1)
        self.assertEqual(result["required"], 2)
        self.assertFalse(result["complete"])
        
        # Update same item again
        result = self.manager.update_order("ABC123")
        self.assertEqual(result["picked"], 2)
        self.assertTrue(result["complete"])
        
    def test_update_invalid_sku(self):
        """Test updating with invalid SKU"""
        self.manager.load_order(json.dumps(self.sample_order))
        
        with self.assertRaises(ValueError):
            self.manager.update_order("INVALID")
            
    def test_update_without_order(self):
        """Test updating when no order is loaded"""
        with self.assertRaises(RuntimeError):
            self.manager.update_order("ABC123")
            
    def test_get_remaining_items(self):
        """Test retrieving remaining unpicked items"""
        self.manager.load_order(json.dumps(self.sample_order))
        
        # Pick one ABC123
        self.manager.update_order("ABC123")
        
        remaining = self.manager.get_remaining_items()
        self.assertEqual(len(remaining), 2)  # One ABC123 and XYZ789 left
        
        # Verify remaining quantities
        abc_item = next(item for item in remaining if item["sku"] == "ABC123")
        xyz_item = next(item for item in remaining if item["sku"] == "XYZ789")
        
        self.assertEqual(abc_item["remaining"], 1)
        self.assertEqual(xyz_item["remaining"], 1)
        
    def test_complete_order(self):
        """Test completing an order"""
        self.manager.load_order(json.dumps(self.sample_order))
        
        with patch("builtins.open", mock_open()) as mock_file:
            self.manager.complete_order("TEST001")
            
            # Verify completion file was written
            mock_file.assert_called_once()
            # Verify order was cleared
            self.assertIsNone(self.manager.current_order)
            
    def test_complete_wrong_order(self):
        """Test completing with wrong order ID"""
        self.manager.load_order(json.dumps(self.sample_order))
        
        with self.assertRaises(ValueError):
            self.manager.complete_order("WRONG_ID")
            
    def test_complete_without_order(self):
        """Test completing when no order is loaded"""
        with self.assertRaises(RuntimeError):
            self.manager.complete_order("TEST001")

if __name__ == '__main__':
    unittest.main()