import sqlite3

DB_NAME = "crm_inventory.db"


def connect():
    return sqlite3.connect(DB_NAME)


def setup_database():
    with connect() as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                email TEXT
            )
        """)
        con.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                stock INTEGER NOT NULL DEFAULT 0
            )
        """)
        con.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                total REAL NOT NULL,
                FOREIGN KEY (customer_id) REFERENCES customers(id),
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        """)


def add_customer():
    name = input("Customer name: ").strip()
    phone = input("Phone: ").strip()
    email = input("Email: ").strip()
    if not name:
        print("Name is required.")
        return
    with connect() as con:
        con.execute(
            "INSERT INTO customers(name, phone, email) VALUES (?, ?, ?)",
            (name, phone, email)
        )
    print("Customer added.")


def add_product():
    name = input("Product name: ").strip()
    try:
        price = float(input("Price: "))
        stock = int(input("Initial stock: "))
        if price < 0 or stock < 0:
            raise ValueError
    except ValueError:
        print("Enter a valid non-negative price and stock.")
        return
    with connect() as con:
        con.execute(
            "INSERT INTO products(name, price, stock) VALUES (?, ?, ?)",
            (name, price, stock)
        )
    print("Product added.")


def list_customers():
    with connect() as con:
        rows = con.execute(
            "SELECT id, name, phone, email FROM customers ORDER BY id"
        ).fetchall()
    print("\nID | Name | Phone | Email")
    for row in rows:
        print(" | ".join(str(value or "") for value in row))
    if not rows:
        print("No customers yet.")


def list_products():
    with connect() as con:
        rows = con.execute(
            "SELECT id, name, price, stock FROM products ORDER BY id"
        ).fetchall()
    print("\nID | Product | Price | Stock")
    for row in rows:
        print(f"{row[0]} | {row[1]} | {row[2]:.2f} | {row[3]}")
    if not rows:
        print("No products yet.")


def create_order():
    list_customers()
    try:
        customer_id = int(input("\nCustomer ID: "))
        product_id = int(input("Product ID: "))
        quantity = int(input("Quantity: "))
        if quantity <= 0:
            raise ValueError
    except ValueError:
        print("Enter valid IDs and a positive quantity.")
        return

    with connect() as con:
        product = con.execute(
            "SELECT price, stock FROM products WHERE id = ?", (product_id,)
        ).fetchone()
        customer = con.execute(
            "SELECT id FROM customers WHERE id = ?", (customer_id,)
        ).fetchone()

        if not customer:
            print("Customer not found.")
            return
        if not product:
            print("Product not found.")
            return
        price, stock = product
        if stock < quantity:
            print(f"Insufficient stock. Available: {stock}")
            return

        total = price * quantity
        con.execute(
            "INSERT INTO orders(customer_id, product_id, quantity, total) "
            "VALUES (?, ?, ?, ?)",
            (customer_id, product_id, quantity, total)
        )
        con.execute(
            "UPDATE products SET stock = stock - ? WHERE id = ?",
            (quantity, product_id)
        )
    print(f"Order created. Total: {total:.2f}. Stock updated.")


def list_orders():
    with connect() as con:
        rows = con.execute("""
            SELECT o.id, c.name, p.name, o.quantity, o.total
            FROM orders o
            JOIN customers c ON c.id = o.customer_id
            JOIN products p ON p.id = o.product_id
            ORDER BY o.id
        """).fetchall()
    print("\nOrder ID | Customer | Product | Qty | Total")
    for row in rows:
        print(f"{row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]:.2f}")
    if not rows:
        print("No orders yet.")


def main():
    setup_database()
    menu = {
        "1": ("Add customer", add_customer),
        "2": ("Add product", add_product),
        "3": ("View customers", list_customers),
        "4": ("View products", list_products),
        "5": ("Create order", create_order),
        "6": ("View orders", list_orders),
    }

    while True:
        print("\n=== CRM with Inventory Management ===")
        for key, (label, _) in menu.items():
            print(f"{key}. {label}")
        print("0. Exit")
        choice = input("Choose: ").strip()
        if choice == "0":
            break
        action = menu.get(choice)
        if action:
            action[1]()
        else:
            print("Invalid option.")


if __name__ == "__main__":
    main()
