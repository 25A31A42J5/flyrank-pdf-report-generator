import random
import sqlite3
from datetime import datetime, timedelta

DB_NAME = "report.db"

CUSTOMERS = [
    "Sai", "Ravi", "Priya", "Arjun", "Ananya",
    "Kiran", "Divya", "Rahul", "Sneha", "Vikram"
]

PRODUCTS = [
    ("Laptop", 55000),
    ("Monitor", 12000),
    ("Keyboard", 1500),
    ("Mouse", 800),
    ("Headphones", 2500),
    ("Webcam", 3500),
    ("USB Hub", 1200),
    ("SSD", 6000),
]

def seed_database():
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer TEXT NOT NULL,
            product TEXT NOT NULL,
            amount REAL NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    # Ensure repeated runs still leave exactly 200 orders.
    cursor.execute("DELETE FROM orders")

    orders = []
    now = datetime.now()

    for _ in range(200):
        customer = random.choice(CUSTOMERS)
        product, base_price = random.choice(PRODUCTS)
        amount = round(base_price * random.uniform(0.85, 1.15), 2)
        created_at = now - timedelta(
            days=random.randint(0, 29),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
        )

        orders.append((
            customer,
            product,
            amount,
            created_at.strftime("%Y-%m-%d %H:%M:%S")
        ))

    cursor.executemany("""
        INSERT INTO orders (customer, product, amount, created_at)
        VALUES (?, ?, ?, ?)
    """, orders)

    connection.commit()

    cursor.execute("SELECT COUNT(*) FROM orders")
    count = cursor.fetchone()[0]

    connection.close()
    print(f"Database seeded successfully: {count} orders")

if __name__ == "__main__":
    seed_database()