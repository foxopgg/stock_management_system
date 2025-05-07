import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import mysql.connector
import csv

class StockManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Stock Management System")
        self.root.geometry("650x700")
        self.root.configure(bg="#f0f2f5")

        # MySQL Connection
        self.db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",  # Replace with your MySQL password
            database="stock_db"
        )
        self.cursor = self.db.cursor()

        # Configure styles
        style = ttk.Style()
        style.configure("TLabel", font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI", 10), padding=6)
        style.configure("TEntry", font=("Segoe UI", 10))
        style.configure("TCombobox", font=("Segoe UI", 10))

        # Title
        ttk.Label(root, text="📦 Stock Management System", font=("Segoe UI", 16, "bold")).pack(pady=15)

        # Add Stock Section
        add_frame = ttk.LabelFrame(root, text="➕ Add Stock", padding=10)
        add_frame.pack(pady=5, fill="x", padx=20)

        ttk.Label(add_frame, text="Product Name:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.add_product_entry = ttk.Entry(add_frame, width=30)
        self.add_product_entry.grid(row=0, column=1, padx=5)

        ttk.Label(add_frame, text="Quantity to Add:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.add_quantity_entry = ttk.Entry(add_frame, width=30)
        self.add_quantity_entry.grid(row=1, column=1, padx=5)

        ttk.Button(add_frame, text="Add Stock", command=self.add_stock).grid(row=2, columnspan=2, pady=5)

        # Withdraw Stock Section
        withdraw_frame = ttk.LabelFrame(root, text="🧾 Withdraw Stock", padding=10)
        withdraw_frame.pack(pady=5, fill="x", padx=20)

        ttk.Label(withdraw_frame, text="Select Product:").grid(row=0, column=0, sticky="w")
        self.withdraw_product_combo = ttk.Combobox(withdraw_frame, state="readonly", width=28)
        self.withdraw_product_combo.grid(row=0, column=1, padx=5, pady=5)
        self.withdraw_product_combo.bind("<<ComboboxSelected>>", self.update_available_stock_label)

        self.stock_info_label = ttk.Label(withdraw_frame, text="Available: N/A", foreground="gray")
        self.stock_info_label.grid(row=1, column=1, sticky="w", padx=5)

        ttk.Label(withdraw_frame, text="Withdraw Quantity:").grid(row=2, column=0, sticky="w")
        self.withdraw_quantity_entry = ttk.Entry(withdraw_frame, width=30)
        self.withdraw_quantity_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Button(withdraw_frame, text="Withdraw", command=self.withdraw_stock).grid(row=3, column=1, sticky="e", pady=10)

        # Remove Stock Section
        remove_frame = ttk.LabelFrame(root, text="❌ Remove Stock", padding=10)
        remove_frame.pack(pady=5, fill="x", padx=20)

        ttk.Label(remove_frame, text="Select Product:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.product_dropdown = ttk.Combobox(remove_frame, state="readonly", width=28)
        self.product_dropdown.grid(row=0, column=1, padx=5)

        ttk.Label(remove_frame, text="Quantity to Remove:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.remove_quantity_entry = ttk.Entry(remove_frame, width=30)
        self.remove_quantity_entry.grid(row=1, column=1, padx=5)

        ttk.Button(remove_frame, text="Remove Stock", command=self.remove_stock).grid(row=2, columnspan=2, pady=5)

        # View/Export Controls
        control_frame = ttk.Frame(root)
        control_frame.pack(pady=10)

        ttk.Button(control_frame, text="🔄 View Stock", command=self.view_stock).grid(row=0, column=0, padx=10)
        ttk.Button(control_frame, text="📁 Export CSV", command=self.export_csv).grid(row=0, column=1, padx=10)

        # Filter Section
        filter_frame = ttk.Frame(root)
        filter_frame.pack(pady=5)

        ttk.Label(filter_frame, text="Sort By:").grid(row=0, column=0, padx=5)
        self.sort_field = ttk.Combobox(filter_frame, values=["product_name", "quantity"], state="readonly", width=15)
        self.sort_field.set("product_name")
        self.sort_field.grid(row=0, column=1)

        self.sort_order = ttk.Combobox(filter_frame, values=["ASC", "DESC"], state="readonly", width=10)
        self.sort_order.set("ASC")
        self.sort_order.grid(row=0, column=2, padx=5)

        ttk.Button(filter_frame, text="Apply Filter", command=self.view_stock).grid(row=0, column=3, padx=5)

        # Stock Display
        self.stock_display = tk.Text(root, height=20, width=75, font=("Consolas", 10), bg="#ffffff", relief="solid", borderwidth=1)
        self.stock_display.pack(pady=10, padx=20)

        # Initialize dropdowns
        self.update_product_dropdown()
        self.update_withdraw_product_combo()

    def add_stock(self):
        product = self.add_product_entry.get().strip()
        quantity = self.add_quantity_entry.get().strip()
        if product and quantity.isdigit():
            self.cursor.execute("INSERT INTO stock (product_name, quantity, action) VALUES (%s, %s, %s)",
                               (product, int(quantity), 'add'))
            self.db.commit()
            messagebox.showinfo("Success", f"Added {quantity} units to {product}")
            self.add_product_entry.delete(0, tk.END)
            self.add_quantity_entry.delete(0, tk.END)
            self.update_product_dropdown()
            self.update_withdraw_product_combo()
            self.view_stock()
        else:
            messagebox.showerror("Error", "Enter valid product and quantity")

    def withdraw_stock(self):
        product = self.withdraw_product_combo.get()
        quantity_str = self.withdraw_quantity_entry.get()
        if not product or not quantity_str.isdigit():
            messagebox.showerror("Error", "Select product and enter quantity.")
            return

        quantity = int(quantity_str)
        self.cursor.execute("""
            SELECT SUM(CASE WHEN action='add' THEN quantity ELSE -quantity END)
            FROM stock
            WHERE product_name = %s
        """, (product,))
        available = self.cursor.fetchone()[0] or 0

        if quantity <= available:
            self.cursor.execute("INSERT INTO stock (product_name, quantity, action) VALUES (%s, %s, 'remove')",
                               (product, quantity))
            self.db.commit()
            messagebox.showinfo("Success", f"{quantity} withdrawn from {product}")
            self.withdraw_quantity_entry.delete(0, tk.END)
            self.update_product_dropdown()
            self.update_withdraw_product_combo()
            self.view_stock()
        else:
            messagebox.showerror("Error", "Insufficient stock.")

    def remove_stock(self):
        product = self.product_dropdown.get()
        quantity = self.remove_quantity_entry.get()
        if product and quantity.isdigit():
            quantity = int(quantity)
            self.cursor.execute("""
                SELECT SUM(CASE WHEN action='add' THEN quantity ELSE -quantity END)
                FROM stock
                WHERE product_name = %s
            """, (product,))
            available = self.cursor.fetchone()[0] or 0

            if available >= quantity:
                self.cursor.execute("INSERT INTO stock (product_name, quantity, action) VALUES (%s, %s, 'remove')",
                                   (product, quantity))
                self.db.commit()
                messagebox.showinfo("Success", f"Removed {quantity} of {product}")
                self.remove_quantity_entry.delete(0, tk.END)
                self.update_product_dropdown()
                self.update_withdraw_product_combo()
                self.view_stock()
            else:
                messagebox.showerror("Error", "Not enough stock to remove.")
        else:
            messagebox.showerror("Error", "Please enter valid product and quantity.")

    def update_product_dropdown(self):
        self.cursor.execute("""
            SELECT product_name
            FROM stock
            GROUP BY product_name
            HAVING SUM(CASE WHEN action='add' THEN quantity ELSE -quantity END) > 0
        """)
        products = [row[0] for row in self.cursor.fetchall()]
        self.product_dropdown['values'] = products

    def update_withdraw_product_combo(self):
        self.cursor.execute("""
            SELECT product_name
            FROM stock
            GROUP BY product_name
            HAVING SUM(CASE WHEN action='add' THEN quantity ELSE -quantity END) > 0
        """)
        products = [row[0] for row in self.cursor.fetchall()]
        self.withdraw_product_combo['values'] = products

    def update_available_stock_label(self, event=None):
        product = self.withdraw_product_combo.get()
        self.cursor.execute("""
            SELECT SUM(CASE WHEN action='add' THEN quantity ELSE -quantity END)
            FROM stock
            WHERE product_name = %s
        """, (product,))
        stock = self.cursor.fetchone()[0] or 0
        self.stock_info_label.config(text=f"Available: {stock}")

    def view_stock(self):
        sort_field = self.sort_field.get()
        sort_order = self.sort_order.get()
        self.stock_display.delete(1.0, tk.END)  # Clear previous data

        # Query to get stock data
        query = f"""
            SELECT product_name,
                   SUM(CASE WHEN action='add' THEN quantity ELSE -quantity END) AS total
            FROM stock
            GROUP BY product_name
            HAVING total > 0
            ORDER BY {sort_field} {sort_order}
        """
        
        try:
            self.cursor.execute(query)
            rows = self.cursor.fetchall()

            if rows:
                self.stock_display.insert(tk.END, f"{'Product':<30}{'Quantity':<10}\n")
                self.stock_display.insert(tk.END, "-" * 40 + "\n")
                for row in rows:
                    self.stock_display.insert(tk.END, f"{row[0].title():<30}{row[1]:<10}\n")
            else:
                self.stock_display.insert(tk.END, "No stock available.\n")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while viewing stock: {e}")

    def export_csv(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return

        self.cursor.execute("""
            SELECT product_name,
                   SUM(CASE WHEN action='add' THEN quantity ELSE -quantity END) AS total
            FROM stock
            GROUP BY product_name
            HAVING total > 0
        """)
        rows = self.cursor.fetchall()

        with open(file_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Product Name", "Quantity"])
            for row in rows:
                writer.writerow(row)

        messagebox.showinfo("Exported", f"Stock data exported to {file_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = StockManagementSystem(root)
    root.mainloop()