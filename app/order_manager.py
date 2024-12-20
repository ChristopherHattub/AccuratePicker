import json
import logging
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path

class OrderManager:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.current_order: Optional[Dict] = None
        self.setup_logging()
        
    def setup_logging(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def load_order(self, order_code: str) -> Dict:
        """
        Load order data from barcode or file.
        
        Args:
            order_code: Order identifier or barcode data
            
        Returns:
            Dict containing order data
        """
        try:
            # Try parsing order code as JSON first
            order_data = json.loads(order_code)
        except json.JSONDecodeError:
            # If not JSON, try loading from file
            order_file = self.data_dir / f"{order_code}.json"
            if not order_file.exists():
                raise FileNotFoundError(f"Order {order_code} not found")
                
            with open(order_file) as f:
                order_data = json.load(f)
        
        self._validate_order_data(order_data)
        self.current_order = order_data
        self.current_order['picked_items'] = {}
        self.logger.info(f"Loaded order {order_data['order_id']}")
        
        return order_data
        
    def _validate_order_data(self, data: Dict) -> None:
        """Validate order data has required fields."""
        required_fields = ['order_id', 'items']
        missing = [f for f in required_fields if f not in data]
        if missing:
            raise ValueError(f"Missing required fields: {missing}")
            
        if not data['items']:
            raise ValueError("Order contains no items")
            
    def update_order(self, sku: str) -> Dict:
        """
        Mark an item as picked in the current order.
        
        Args:
            sku: SKU of picked item
            
        Returns:
            Dict with updated item status
        """
        if not self.current_order:
            raise RuntimeError("No order currently loaded")
            
        # Find item in order
        order_item = next(
            (item for item in self.current_order['items'] 
             if item['sku'] == sku),
            None
        )
        
        if not order_item:
            raise ValueError(f"SKU {sku} not in current order")
            
        # Update pick count
        if sku not in self.current_order['picked_items']:
            self.current_order['picked_items'][sku] = 0
        self.current_order['picked_items'][sku] += 1
        
        picked_count = self.current_order['picked_items'][sku]
        required_count = order_item['quantity']
        
        self.logger.info(
            f"Updated {sku}: {picked_count}/{required_count} picked"
        )
        
        return {
            'sku': sku,
            'picked': picked_count,
            'required': required_count,
            'complete': picked_count >= required_count
        }
        
    def get_remaining_items(self) -> List[Dict]:
        """Get items that still need to be picked."""
        if not self.current_order:
            raise RuntimeError("No order currently loaded")
            
        remaining = []
        for item in self.current_order['items']:
            sku = item['sku']
            picked = self.current_order['picked_items'].get(sku, 0)
            remaining_quantity = item['quantity'] - picked
            
            if remaining_quantity > 0:
                remaining.append({
                    'sku': sku,
                    'remaining': remaining_quantity
                })
                
        return remaining
        
    def complete_order(self, order_id: str) -> None:
        """
        Mark order as complete and save completion data.
        
        Args:
            order_id: ID of order to complete
        """
        if not self.current_order:
            raise RuntimeError("No order currently loaded")
            
        if self.current_order['order_id'] != order_id:
            raise ValueError("Order ID mismatch")
            
        # Save completion data
        completion_data = {
            'order_id': order_id,
            'completed_at': datetime.now().isoformat(),
            'picked_items': self.current_order['picked_items']
        }
        
        completion_file = (
            self.data_dir / 
            f"completed_{order_id}_{completion_data['completed_at']}.json"
        )
        
        with open(completion_file, 'w') as f:
            json.dump(completion_data, f, indent=2)
            
        self.logger.info(f"Completed order {order_id}")
        self.current_order = None