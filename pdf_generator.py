from pathlib import Path
from playwright.sync_api import sync_playwright

from report_data import get_report_data

REPORTS_DIR = Path("reports")


def generate_pdf(output_path="reports/test.pdf"):
    REPORTS_DIR.mkdir(exist_ok=True)

    data = get_report_data()

    top_products_html = ""
    for product in data["top_products"]:
        top_products_html += f"""
        <tr>
            <td>{product['product']}</td>
            <td>₹{product['revenue']:,.2f}</td>
        </tr>
        """

    daily_orders_html = ""
    for day in data["orders_per_day"]:
        daily_orders_html += f"""
        <tr>
            <td>{day['order_date']}</td>
            <td>{day['order_count']}</td>
        </tr>
        """

    all_orders_html = ""
    for order in data["all_orders"]:
        all_orders_html += f"""
        <tr>
            <td>{order['id']}</td>
            <td>{order['customer']}</td>
            <td>{order['product']}</td>
            <td>₹{order['amount']:,.2f}</td>
            <td>{order['created_at']}</td>
        </tr>
        """

    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Orders Report</title>
        <style>
            @page {{
                size: A4;
                margin: 16mm;
            }}

            body {{
                font-family: Arial, sans-serif;
                color: #222;
                font-size: 11px;
            }}

            h1 {{
                font-size: 25px;
                margin-bottom: 5px;
            }}

            h2 {{
                margin-top: 24px;
                border-bottom: 1px solid #ccc;
                padding-bottom: 5px;
            }}

            .generated {{
                color: #666;
                margin-bottom: 20px;
            }}

            .summary {{
                display: flex;
                gap: 15px;
                margin: 20px 0;
            }}

            .card {{
                border: 1px solid #ddd;
                padding: 15px;
                flex: 1;
            }}

            .label {{
                color: #666;
                font-size: 10px;
            }}

            .value {{
                font-size: 18px;
                font-weight: bold;
                margin-top: 6px;
            }}

            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 10px;
                font-size: 9px;
            }}

            th, td {{
                border: 1px solid #ddd;
                padding: 6px;
                text-align: left;
                overflow-wrap: anywhere;
            }}

            th {{
                background: #edf2f7;
            }}

            thead {{
                display: table-header-group;
            }}

            tr {{
                break-inside: avoid;
                page-break-inside: avoid;
            }}

            .orders-table {{
                font-size: 8px;
            }}

            .orders-table th,
            .orders-table td {{
                padding: 4px;
            }}
        </style>
    </head>
    <body>
        <h1>Orders Report</h1>
        <div class="generated">
            Generated at: {data['generated_at']}
        </div>

        <div class="summary">
            <div class="card">
                <div class="label">Total Orders</div>
                <div class="value">{data['total_orders']}</div>
            </div>
            <div class="card">
                <div class="label">Total Revenue</div>
                <div class="value">₹{data['total_revenue']:,.2f}</div>
            </div>
        </div>

        <h2>Top 5 Products by Revenue</h2>
        <table>
            <thead>
                <tr><th>Product</th><th>Revenue</th></tr>
            </thead>
            <tbody>{top_products_html}</tbody>
        </table>

        <h2>Orders per Day — Last 7 Days</h2>
        <table>
            <thead>
                <tr><th>Date</th><th>Number of Orders</th></tr>
            </thead>
            <tbody>{daily_orders_html}</tbody>
        </table>

        <h2>All Orders</h2>
        <table class="orders-table">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Customer</th>
                    <th>Product</th>
                    <th>Amount</th>
                    <th>Created At</th>
                </tr>
            </thead>
            <tbody>{all_orders_html}</tbody>
        </table>
    </body>
    </html>
    """

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()
        page.set_content(html, wait_until="networkidle")

        page.pdf(
            path=str(output.resolve()),
            format="A4",
            print_background=True,
        )

        browser.close()

    print(f"PDF generated: {output.resolve()}")


if __name__ == "__main__":
    generate_pdf()