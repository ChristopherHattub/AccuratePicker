from pathlib import Path

# File paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
ASSETS_DIR = BASE_DIR / "assets"
ORDER_DATA_FILE = DATA_DIR / "sample_orders.json"
SKU_DATA_FILE = DATA_DIR / "item_skus.csv"

# UI Settings
WINDOW_TITLE = "Warehouse Picking System"
WINDOW_SIZE = "800x600"

COLORS = {
    "background": "#F5F5F5",
    "header": "#2C3E50",
    "unpicked": "#FFCDD2",
    "picked": "#C8E6C9",
    "error": "#FFEBEE",
    "button_primary": "#1976D2",
    "button_complete": "#4CAF50",
    "button_disabled": "#9E9E9E"
}

FONTS = {
    "header": ("Arial", 16, "bold"),
    "item": ("Arial", 14),
    "status": ("Arial", 14, "bold"),
    "error": ("Arial", 13)
}

# Messages
MESSAGES = {
    "scan_order": "Scan Order Barcode",
    "scan_item": "Scan Item Barcode",
    "order_complete": "Order Complete",
    "invalid_sku": "Invalid SKU scanned",
    "duplicate_scan": "Item already picked",
    "camera_error": "Error accessing camera",
    "no_barcode": "No barcode detected",
    "complete_confirm": "Complete order and reset?"
}

# Scanner settings
CAMERA_TIMEOUT = 5  # seconds
SCAN_DELAY = 0.5    # seconds between scans