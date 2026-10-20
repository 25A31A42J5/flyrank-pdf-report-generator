import sqlite3
from datetime import datetime, timedelta

DB_NAME = "report.db"


def get_report_data():
    connection = sqlite3.connect(DB_NAME)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    # 1. Total number of orders
    cursor.execute("SELECT COUNT(*) FROM orders")
    total_orders = cursor.fetchone()[0]

    # 2. Total revenue
    cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM orders")
    total_revenue = cursor.fetchone()[0]

    # 3. Top 5 products by revenue
    cursor.execute("""
        SELECT product, SUM(amount) AS revenue
        FROM orders
        GROUP BY product
        ORDER BY revenue DESC
        LIMIT 5
    """)
    top_products = [dict(row) for row in cursor.fetchall()]

    # 4. Orders per day over the last 7 days
    today = datetime.now().date()
    seven_days_ago = today - timedelta(days=6)

    cursor.execute("""
        SELECT DATE(created_at) AS order_date,
               COUNT(*) AS order_count
        FROM orders
        WHERE DATE(created_at) BETWEEN ? AND ?
        GROUP BY DATE(created_at)
        ORDER BY order_date
    """, (seven_days_ago.isoformat(), today.isoformat()))

    orders_per_day = [dict(row) for row in cursor.fetchall()]

    # 5. All orders for the detailed table in the PDF
    cursor.execute("""
        SELECT id, customer, product, amount, created_at
        FROM orders
        ORDER BY created_at DESC
    """)
    all_orders = [dict(row) for row in cursor.fetchall()]

    connection.close()

    return {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_orders": total_orders,
        "total_revenue": round(total_revenue, 2),
        "top_products": top_products,
        "orders_per_day": orders_per_day,
        "all_orders": all_orders,
    }


if __name__ == "__main__":
    data = get_report_data()

    print("Total orders:", data["total_orders"])
    print("Total revenue:", data["total_revenue"])
    print("\nTop 5 products:")
    for product in data["top_products"]:
        print(product)

    print("\nOrders per day (last 7 days):")
    for day in data["orders_per_day"]:
        print(day)

    print("\nDetailed orders:", len(data["all_orders"]))