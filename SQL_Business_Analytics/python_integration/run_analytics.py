"""
SQL Analytics Runner
Execute SQL queries and display results

Author: Data Analysis Portfolio
"""

import sqlite3
import pandas as pd
import os


class SQLAnalytics:
    """Execute and display SQL analytics queries"""

    def __init__(self, db_path='data/ecommerce.db'):
        """Initialize with database connection"""
        self.db_path = db_path
        self.conn = None

    def connect(self):
        """Connect to database"""
        if not os.path.exists(self.db_path):
            print(f"Database not found at {self.db_path}")
            print("Please run setup_database.py first")
            return False

        self.conn = sqlite3.connect(self.db_path)
        return True

    def execute_query(self, query, description=None):
        """Execute a query and return results as DataFrame"""
        if description:
            print(f"\n{'='*60}")
            print(f"  {description}")
            print(f"{'='*60}")

        try:
            df = pd.read_sql_query(query, self.conn)
            return df
        except Exception as e:
            print(f"Error executing query: {e}")
            return None

    def revenue_summary(self):
        """Display revenue summary"""
        query = """
        SELECT
            strftime('%Y-%m', order_date) AS month,
            COUNT(order_id) AS orders,
            COUNT(DISTINCT customer_id) AS customers,
            ROUND(SUM(total_amount), 2) AS revenue,
            ROUND(AVG(total_amount), 2) AS avg_order_value
        FROM orders
        WHERE status = 'completed'
        GROUP BY strftime('%Y-%m', order_date)
        ORDER BY month DESC
        LIMIT 12
        """
        df = self.execute_query(query, "MONTHLY REVENUE SUMMARY (Last 12 Months)")
        if df is not None:
            print(df.to_string(index=False))
        return df

    def top_customers(self, limit=10):
        """Display top customers by revenue"""
        query = f"""
        SELECT
            c.customer_id,
            c.first_name || ' ' || c.last_name AS customer_name,
            c.segment,
            COUNT(DISTINCT o.order_id) AS orders,
            ROUND(SUM(o.total_amount), 2) AS total_spent,
            ROUND(AVG(o.total_amount), 2) AS avg_order
        FROM customers c
        JOIN orders o ON c.customer_id = o.customer_id
        WHERE o.status = 'completed'
        GROUP BY c.customer_id
        ORDER BY total_spent DESC
        LIMIT {limit}
        """
        df = self.execute_query(query, f"TOP {limit} CUSTOMERS BY REVENUE")
        if df is not None:
            print(df.to_string(index=False))
        return df

    def top_products(self, limit=10):
        """Display top products by revenue"""
        query = f"""
        SELECT
            p.product_id,
            p.name,
            p.category,
            SUM(oi.quantity) AS units_sold,
            ROUND(SUM(oi.quantity * oi.unit_price), 2) AS revenue,
            ROUND(SUM(oi.quantity * (oi.unit_price - p.cost)), 2) AS profit
        FROM products p
        JOIN order_items oi ON p.product_id = oi.product_id
        JOIN orders o ON oi.order_id = o.order_id
        WHERE o.status = 'completed'
        GROUP BY p.product_id
        ORDER BY revenue DESC
        LIMIT {limit}
        """
        df = self.execute_query(query, f"TOP {limit} PRODUCTS BY REVENUE")
        if df is not None:
            print(df.to_string(index=False))
        return df

    def category_performance(self):
        """Display category performance"""
        query = """
        SELECT
            p.category,
            COUNT(DISTINCT p.product_id) AS products,
            SUM(oi.quantity) AS units_sold,
            ROUND(SUM(oi.quantity * oi.unit_price), 2) AS revenue,
            ROUND(SUM(oi.quantity * oi.unit_price) * 100.0 /
                  (SELECT SUM(quantity * unit_price) FROM order_items), 2) AS market_share_pct
        FROM products p
        JOIN order_items oi ON p.product_id = oi.product_id
        JOIN orders o ON oi.order_id = o.order_id
        WHERE o.status = 'completed'
        GROUP BY p.category
        ORDER BY revenue DESC
        """
        df = self.execute_query(query, "CATEGORY PERFORMANCE")
        if df is not None:
            print(df.to_string(index=False))
        return df

    def customer_segments(self):
        """Display customer segment analysis"""
        query = """
        SELECT
            c.segment,
            COUNT(DISTINCT c.customer_id) AS customers,
            COUNT(DISTINCT o.order_id) AS orders,
            ROUND(SUM(o.total_amount), 2) AS revenue,
            ROUND(AVG(o.total_amount), 2) AS avg_order,
            ROUND(SUM(o.total_amount) / COUNT(DISTINCT c.customer_id), 2) AS revenue_per_customer
        FROM customers c
        LEFT JOIN orders o ON c.customer_id = o.customer_id AND o.status = 'completed'
        GROUP BY c.segment
        ORDER BY revenue DESC
        """
        df = self.execute_query(query, "CUSTOMER SEGMENT ANALYSIS")
        if df is not None:
            print(df.to_string(index=False))
        return df

    def retention_analysis(self):
        """Display basic retention metrics"""
        query = """
        WITH customer_orders AS (
            SELECT
                customer_id,
                COUNT(order_id) AS order_count
            FROM orders
            WHERE status = 'completed'
            GROUP BY customer_id
        )
        SELECT
            CASE
                WHEN order_count = 1 THEN '1 order'
                WHEN order_count = 2 THEN '2 orders'
                WHEN order_count BETWEEN 3 AND 5 THEN '3-5 orders'
                WHEN order_count BETWEEN 6 AND 10 THEN '6-10 orders'
                ELSE '10+ orders'
            END AS purchase_frequency,
            COUNT(*) AS customers,
            ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM customer_orders), 2) AS pct
        FROM customer_orders
        GROUP BY
            CASE
                WHEN order_count = 1 THEN '1 order'
                WHEN order_count = 2 THEN '2 orders'
                WHEN order_count BETWEEN 3 AND 5 THEN '3-5 orders'
                WHEN order_count BETWEEN 6 AND 10 THEN '6-10 orders'
                ELSE '10+ orders'
            END
        ORDER BY
            CASE purchase_frequency
                WHEN '1 order' THEN 1
                WHEN '2 orders' THEN 2
                WHEN '3-5 orders' THEN 3
                WHEN '6-10 orders' THEN 4
                ELSE 5
            END
        """
        df = self.execute_query(query, "CUSTOMER PURCHASE FREQUENCY")
        if df is not None:
            print(df.to_string(index=False))
        return df

    def run_all_analytics(self):
        """Run all analytics queries"""
        print("\n" + "=" * 70)
        print(" " * 15 + "SQL BUSINESS ANALYTICS REPORT")
        print("=" * 70)

        self.revenue_summary()
        self.top_customers()
        self.top_products()
        self.category_performance()
        self.customer_segments()
        self.retention_analysis()

        print("\n" + "=" * 70)
        print(" " * 15 + "ANALYTICS COMPLETE")
        print("=" * 70)

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


def main():
    """Main execution"""
    analytics = SQLAnalytics()

    if analytics.connect():
        analytics.run_all_analytics()
        analytics.close()


if __name__ == "__main__":
    main()
