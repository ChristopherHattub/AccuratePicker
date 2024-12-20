import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, List

class PickingDisplay:
    def __init__(self, root):
        self.root = root
        self.root.configure(bg="#F5F5F5")
        self.setup_ui()
        
    def setup_ui(self):
        # Main container
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Status label
        self.status_label = ttk.Label(
            self.main_frame,
            text="",
            font=('Arial', 16, 'bold'),
            foreground="#2C3E50"
        )
        self.status_label.pack(pady=10)
        
        # Order items frame
        self.items_frame = ttk.Frame(self.main_frame)
        self.items_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollable items list
        self.canvas = tk.Canvas(self.items_frame)
        scrollbar = ttk.Scrollbar(
            self.items_frame,
            orient="vertical",
            command=self.canvas.yview
        )
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Dictionary to track item labels
        self.item_labels = {}
        
    def show_scan_prompt(self, message: str):
        """Display message prompting for scan"""
        self.status_label.config(text=message)
        self.clear_items()
        
    def show_order_items(self, order: Dict):
        """
        Display order items in scrollable list
        
        Args:
            order: Dict containing order data with items list
        """
        self.clear_items()
        self.status_label.config(text=f"Order: {order['order_id']}")
        
        # Create label for each item
        for item in order['items']:
            item_frame = ttk.Frame(self.scrollable_frame)
            item_frame.pack(fill=tk.X, pady=2)
            
            label_text = f"{item['sku']}: {item['quantity']} units"
            label = ttk.Label(
                item_frame,
                text=label_text,
                padding="5",
                background="#FFCDD2",
                font=('Arial', 14)
            )
            label.pack(fill=tk.X)
            
            self.item_labels[item['sku']] = label
            
    def update_item_status(self, sku: str, status: str):
        """
        Update display status of an item
        
        Args:
            sku: Item SKU to update
            status: Status type ('picked' or 'error')
        """
        status_colors = {
            'picked': "#C8E6C9",
            'error': "#FFEBEE"
        }
        if sku in self.item_labels:
            self.item_labels[sku].configure(background=status_colors[status])
            
    def show_error(self, message: str):
        """Display error message"""
        messagebox.showerror("Error", message)
        
    def clear_items(self):
        """Clear all displayed items"""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.item_labels.clear()
        
    def reset(self):
        """Reset display to initial state"""
        self.status_label.config(text="")
        self.clear_items()