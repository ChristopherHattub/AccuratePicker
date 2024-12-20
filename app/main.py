import tkinter as tk
from tkinter import messagebox
from scanner import BarcodeScanner
from order_manager import OrderManager
from display import PickingDisplay
from matcher import ItemMatcher

class WarehousePickingApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Warehouse Picking System")
        
        # Initialize components
        self.scanner = BarcodeScanner()
        self.order_manager = OrderManager()
        self.matcher = ItemMatcher()
        self.display = PickingDisplay(self.root)
        
        # Set initial state
        self.waiting_for_order = True
        self.current_order = None
        
        self.setup_ui()
        
    def setup_ui(self):
        self.display.show_scan_prompt("Scan Order Barcode")
        self.root.bind('<Return>', self.handle_scan)
        
        self.complete_button = tk.Button(
            self.root,
            text="Complete Order",
            bg="blue",
            fg="white",
            command=self.complete_order,
            state="disabled"
        )
        self.complete_button.pack(pady=10)
        
    def handle_scan(self, event=None):
        try:
            scanned_code = self.scanner.scan_barcode()
            
            if self.waiting_for_order:
                self.process_order_scan(scanned_code)
            else:
                self.process_item_scan(scanned_code)
                
        except Exception as e:
            messagebox.showerror("Scan Error", str(e))
            
    def process_order_scan(self, order_code):
        try:
            self.current_order = self.order_manager.load_order(order_code)
            self.display.show_order_items(self.current_order)
            self.waiting_for_order = False
            self.complete_button.config(state="normal")
            
        except Exception as e:
            messagebox.showerror("Order Error", f"Invalid order: {str(e)}")
            
    def process_item_scan(self, item_sku):
        try:
            match_result = self.matcher.check_item(item_sku, self.current_order)
            
            if match_result["valid"]:
                self.display.update_item_status(item_sku, "picked")
                
                if match_result["order_complete"]:
                    self.complete_button.config(bg="green")
            else:
                messagebox.showwarning("Mismatch", "Item not in order")
                
        except Exception as e:
            messagebox.showerror("Scan Error", str(e))
            
    def complete_order(self):
        if not self.matcher.is_order_complete(self.current_order):
            if not messagebox.askyesno("Incomplete Order", 
                "Order is not complete. Do you want to finish anyway?"):
                return
                
        self.order_manager.complete_order(self.current_order["order_id"])
        self.reset_state()
        
    def reset_state(self):
        self.waiting_for_order = True
        self.current_order = None
        self.display.reset()
        self.complete_button.config(state="disabled", bg="blue")
        self.display.show_scan_prompt("Scan Order Barcode")
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = WarehousePickingApp()
    app.run()