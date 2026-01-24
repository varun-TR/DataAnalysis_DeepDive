"""
Database Setup Script
Creates SQLite database with sample e-commerce data

Author: Data Analysis Portfolio
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import random

def create_database(db_path='data/ecommerce.db'):
    """Create database and tables"""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Read and execute schema
    schema_path = os.path.join(os.path.dirname(__file__), '..', 'schema', 'create_tables.sql')
    if os.path.exists(schema_path):
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
            # Split by semicolon and execute each statement
            for statement in schema_sql.split(';'):
                if statement.strip():
                    try:
                        cursor.execute(statement)
                    except sqlite3.Error as e:
                        print(f"Warning: {e}")

    conn.commit()
    return conn


def generate_customers(n=5000, seed=42):
    """Generate customer data"""
    np.random.seed(seed)
    random.seed(seed)

    first_names = ['James', 'Mary', 'John', 'Patricia', 'Robert', 'Jennifer',
                   'Michael', 'Linda', 'William', 'Elizabeth', 'David', 'Susan',
                   'Richard', 'Jessica', 'Joseph', 'Sarah', 'Thomas', 'Karen',
                   'Christopher', 'Nancy', 'Daniel', 'Lisa', 'Matthew', 'Betty']

    last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia',
                  'Miller', 'Davis', 'Rodriguez', 'Martinez', 'Wilson', 'Anderson',
                  'Taylor', 'Thomas', 'Hernandez', 'Moore', 'Martin', 'Jackson']

    cities = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix',
              'Philadelphia', 'San Antonio', 'San Diego', 'Dallas', 'San Jose',
              'Austin', 'Seattle', 'Denver', 'Boston', 'Portland']

    countries = ['USA', 'Canada', 'UK', 'Germany', 'Australia']
    segments = ['standard', 'premium', 'enterprise']

    customers = []
    for i in range(n):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        signup_date = datetime(2022, 1, 1) + timedelta(days=np.random.randint(0, 730))

        customers.append({
            'customer_id': i + 1,
            'first_name': first_name,
            'last_name': last_name,
            'email': f"{first_name.lower()}.{last_name.lower()}{i}@email.com",
            'signup_date': signup_date.strftime('%Y-%m-%d'),
            'segment': np.random.choice(segments, p=[0.7, 0.2, 0.1]),
            'city': random.choice(cities),
            'country': np.random.choice(countries, p=[0.6, 0.15, 0.1, 0.1, 0.05])
        })

    return pd.DataFrame(customers)


def generate_products(n=200, seed=42):
    """Generate product data"""
    np.random.seed(seed)

    categories = {
        'Electronics': ['Headphones', 'Speakers', 'Chargers', 'Cables', 'Cases'],
        'Clothing': ['T-Shirts', 'Jeans', 'Jackets', 'Shoes', 'Accessories'],
        'Home': ['Furniture', 'Decor', 'Kitchen', 'Bedding', 'Storage'],
        'Sports': ['Equipment', 'Apparel', 'Footwear', 'Accessories', 'Nutrition'],
        'Beauty': ['Skincare', 'Makeup', 'Haircare', 'Fragrance', 'Tools']
    }

    products = []
    for i in range(n):
        category = random.choice(list(categories.keys()))
        subcategory = random.choice(categories[category])

        # Price varies by category
        base_prices = {
            'Electronics': (20, 300),
            'Clothing': (15, 150),
            'Home': (25, 500),
            'Sports': (10, 200),
            'Beauty': (8, 100)
        }

        price_range = base_prices[category]
        price = round(np.random.uniform(price_range[0], price_range[1]), 2)
        cost = round(price * np.random.uniform(0.3, 0.6), 2)

        products.append({
            'product_id': i + 1,
            'name': f"{category} {subcategory} {i+1}",
            'category': category,
            'subcategory': subcategory,
            'price': price,
            'cost': cost,
            'stock_quantity': np.random.randint(10, 500),
            'is_active': 1 if np.random.random() > 0.1 else 0
        })

    return pd.DataFrame(products)


def generate_orders(customers_df, n=20000, seed=42):
    """Generate order data"""
    np.random.seed(seed)

    statuses = ['completed', 'completed', 'completed', 'completed',
                'pending', 'cancelled', 'refunded']
    payment_methods = ['credit_card', 'debit_card', 'paypal', 'apple_pay', 'bank_transfer']

    orders = []
    for i in range(n):
        customer = customers_df.sample(1).iloc[0]
        order_date = datetime.strptime(customer['signup_date'], '%Y-%m-%d') + \
                     timedelta(days=np.random.randint(0, 365))

        # Ensure order date is not in future
        if order_date > datetime(2024, 1, 15):
            order_date = datetime(2024, 1, 15) - timedelta(days=np.random.randint(1, 30))

        total_amount = round(np.random.lognormal(4, 0.8), 2)  # Log-normal distribution
        total_amount = min(total_amount, 1000)  # Cap at $1000

        orders.append({
            'order_id': i + 1,
            'customer_id': customer['customer_id'],
            'order_date': order_date.strftime('%Y-%m-%d'),
            'total_amount': total_amount,
            'discount_amount': round(total_amount * np.random.uniform(0, 0.2), 2) if np.random.random() > 0.7 else 0,
            'shipping_cost': round(np.random.uniform(0, 15), 2),
            'status': random.choice(statuses),
            'payment_method': random.choice(payment_methods),
            'shipping_address': f"{np.random.randint(100, 9999)} Main St"
        })

    return pd.DataFrame(orders)


def generate_order_items(orders_df, products_df, seed=42):
    """Generate order items data"""
    np.random.seed(seed)

    items = []
    item_id = 1

    for _, order in orders_df.iterrows():
        # 1-5 items per order
        n_items = np.random.randint(1, 6)
        order_products = products_df.sample(n_items)

        for _, product in order_products.iterrows():
            quantity = np.random.randint(1, 4)
            # Sometimes apply a discount
            discount = np.random.uniform(0, 0.15) if np.random.random() > 0.8 else 0

            items.append({
                'item_id': item_id,
                'order_id': order['order_id'],
                'product_id': product['product_id'],
                'quantity': quantity,
                'unit_price': product['price'],
                'discount_pct': round(discount * 100, 2)
            })
            item_id += 1

    return pd.DataFrame(items)


def load_data_to_db(conn, customers_df, products_df, orders_df, order_items_df):
    """Load data into database"""
    customers_df.to_sql('customers', conn, if_exists='replace', index=False)
    products_df.to_sql('products', conn, if_exists='replace', index=False)
    orders_df.to_sql('orders', conn, if_exists='replace', index=False)
    order_items_df.to_sql('order_items', conn, if_exists='replace', index=False)
    print("Data loaded successfully!")


def main():
    """Main execution"""
    print("=" * 50)
    print("E-Commerce Database Setup")
    print("=" * 50)

    # Create database
    print("\n1. Creating database...")
    db_path = 'data/ecommerce.db'
    conn = create_database(db_path)

    # Generate data
    print("2. Generating customer data...")
    customers_df = generate_customers(5000)
    print(f"   Generated {len(customers_df)} customers")

    print("3. Generating product data...")
    products_df = generate_products(200)
    print(f"   Generated {len(products_df)} products")

    print("4. Generating order data...")
    orders_df = generate_orders(customers_df, 20000)
    print(f"   Generated {len(orders_df)} orders")

    print("5. Generating order items data...")
    order_items_df = generate_order_items(orders_df, products_df)
    print(f"   Generated {len(order_items_df)} order items")

    # Load to database
    print("6. Loading data to database...")
    load_data_to_db(conn, customers_df, products_df, orders_df, order_items_df)

    # Print summary
    print("\n" + "=" * 50)
    print("DATABASE SUMMARY")
    print("=" * 50)

    cursor = conn.cursor()

    tables = ['customers', 'products', 'orders', 'order_items']
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"{table:15} {count:,} records")

    # Revenue summary
    cursor.execute("""
        SELECT
            SUM(total_amount) as total_revenue,
            COUNT(*) as total_orders,
            AVG(total_amount) as avg_order_value
        FROM orders
        WHERE status = 'completed'
    """)
    result = cursor.fetchone()
    print(f"\nTotal Revenue: ${result[0]:,.2f}")
    print(f"Total Orders: {result[1]:,}")
    print(f"Avg Order Value: ${result[2]:.2f}")

    conn.close()
    print(f"\nDatabase saved to: {db_path}")
    print("=" * 50)


if __name__ == "__main__":
    main()
