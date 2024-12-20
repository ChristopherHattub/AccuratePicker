from typing import Dict, List
import logging
from dataclasses import dataclass

@dataclass
class OrderItem:
    sku: str
    quantity_required: int
    quantity_picked: int = 0

class ItemMatcher:
    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.current_items: Dict[str, OrderItem] = {}
        
    def load_order_items(self, items: List[Dict[str, int]]) -> None:
        """
        Initialize matcher with order items and their quantities.
        
        Args:
            items: List of dicts with 'sku' and 'quantity' keys
        """
        self.current_items = {
            item['sku']: OrderItem(
                sku=item['sku'],
                quantity_required=item['quantity']
            )
            for item in items
        }
        self.logger.info(f"Loaded {len(items)} items for matching")

    def check_item(self, sku: str, order: Dict) -> Dict:
        """
        Validate a scanned SKU against the current order.
        
        Args:
            sku: The scanned SKU to validate
            order: Current order data (for reference)
            
        Returns:
            Dict with keys:
                valid: bool - If SKU is valid for this order
                order_complete: bool - If order is now complete
                message: str - Status/error message
        """
        if not self.current_items:
            raise ValueError("No order items loaded")
            
        if sku not in self.current_items:
            self.logger.warning(f"Invalid SKU scanned: {sku}")
            return {
                "valid": False,
                "order_complete": False,
                "message": f"SKU {sku} not in order"
            }
            
        item = self.current_items[sku]
        
        if item.quantity_picked >= item.quantity_required:
            self.logger.warning(f"Item {sku} already fully picked")
            return {
                "valid": False,
                "order_complete": False,
                "message": f"Required quantity for {sku} already picked"
            }
            
        # Update pick count
        item.quantity_picked += 1
        self.logger.info(
            f"Validated {sku}: {item.quantity_picked}/{item.quantity_required}"
        )
        
        return {
            "valid": True,
            "order_complete": self.is_order_complete(order),
            "message": "Item validated"
        }
        
    def is_order_complete(self, order: Dict) -> bool:
        """Check if all items have been picked in required quantities."""
        return all(
            item.quantity_picked >= item.quantity_required
            for item in self.current_items.values()
        )
        
    def get_remaining_items(self) -> List[Dict]:
        """Get list of items still needing to be picked."""
        remaining = []
        for item in self.current_items.values():
            remaining_quantity = item.quantity_required - item.quantity_picked
            if remaining_quantity > 0:
                remaining.append({
                    "sku": item.sku,
                    "remaining": remaining_quantity
                })
        return remaining

    def reset(self) -> None:
        """Clear current order data."""
        self.current_items.clear()
        self.logger.info("Matcher reset")