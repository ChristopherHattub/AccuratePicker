import unittest
from matcher import ItemMatcher

class TestItemMatcher(unittest.TestCase):
    def setUp(self):
        """Initialize matcher and sample data before each test"""
        self.matcher = ItemMatcher()
        self.sample_order = {
            "order_id": "TEST001",
            "items": [
                {"sku": "ABC123", "quantity": 2},
                {"sku": "XYZ789", "quantity": 1}
            ]
        }
        self.matcher.load_order_items(self.sample_order["items"])

    def test_valid_sku_match(self):
        """Test matching a valid SKU"""
        result = self.matcher.check_item("ABC123", self.sample_order)
        self.assertTrue(result["valid"])
        self.assertFalse(result["order_complete"])

    def test_invalid_sku(self):
        """Test handling invalid SKU"""
        result = self.matcher.check_item("INVALID", self.sample_order)
        self.assertFalse(result["valid"])
        self.assertEqual(
            result["message"],
            "SKU INVALID not in order"
        )

    def test_duplicate_scan_within_quantity(self):
        """Test scanning same item within required quantity"""
        # First scan
        self.matcher.check_item("ABC123", self.sample_order)
        
        # Second scan (still within quantity limit)
        result = self.matcher.check_item("ABC123", self.sample_order)
        self.assertTrue(result["valid"])

    def test_duplicate_scan_over_quantity(self):
        """Test scanning same item more than required"""
        # Scan up to quantity
        self.matcher.check_item("ABC123", self.sample_order)
        self.matcher.check_item("ABC123", self.sample_order)
        
        # Try scanning one more time
        result = self.matcher.check_item("ABC123", self.sample_order)
        self.assertFalse(result["valid"])
        self.assertTrue("already picked" in result["message"])

    def test_order_completion(self):
        """Test detecting when order is complete"""
        # Pick all required items
        self.matcher.check_item("ABC123", self.sample_order)
        self.matcher.check_item("ABC123", self.sample_order)
        result = self.matcher.check_item("XYZ789", self.sample_order)
        
        self.assertTrue(result["valid"])
        self.assertTrue(result["order_complete"])

    def test_partial_completion(self):
        """Test order status with some items picked"""
        self.matcher.check_item("ABC123", self.sample_order)
        result = self.matcher.check_item("XYZ789", self.sample_order)
        
        self.assertTrue(result["valid"])
        self.assertFalse(result["order_complete"])

    def test_get_remaining_items(self):
        """Test retrieving remaining unpicked items"""
        # Pick one ABC123
        self.matcher.check_item("ABC123", self.sample_order)
        
        remaining = self.matcher.get_remaining_items()
        self.assertEqual(len(remaining), 2)  # One ABC123 and XYZ789 left
        
        # Verify remaining quantities
        abc_item = next(item for item in remaining if item["sku"] == "ABC123")
        xyz_item = next(item for item in remaining if item["sku"] == "XYZ789")
        
        self.assertEqual(abc_item["remaining"], 1)
        self.assertEqual(xyz_item["remaining"], 1)

    def test_reset(self):
        """Test resetting matcher state"""
        self.matcher.check_item("ABC123", self.sample_order)
        self.matcher.reset()
        
        # After reset, matcher should have no items
        self.assertEqual(len(self.matcher.current_items), 0)

    def test_check_without_order(self):
        """Test checking item without loading order"""
        matcher = ItemMatcher()  # New matcher without loaded order
        with self.assertRaises(ValueError):
            matcher.check_item("ABC123", self.sample_order)

if __name__ == '__main__':
    unittest.main()