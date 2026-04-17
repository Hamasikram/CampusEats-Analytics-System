"""
CampusEats Data Generation Script
Generates sample data for the database with 100+ rows
"""

import sqlite3
import random
from datetime import datetime, timedelta
import pandas as pd
import os

# Get the database path (go up one level from data_generation folder)
db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'campuseats.db')

# Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# ========== EXECUTE SETUP SQL ==========
setup_sql_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'setup.sql')
with open(setup_sql_path, 'r') as sql_file:
    cursor.executescript(sql_file.read())
    print("✓ Database schema created successfully!")

conn.commit()

# ========== INSERT UNIVERSITIES ==========
universities = [
    ('NUST', 'Islamabad'),
    ('UET Lahore', 'Lahore'),
    ('IBA Karachi', 'Karachi')
]

cursor.executemany(
    'INSERT INTO universities (university_name, location) VALUES (?, ?)',
    universities
)
print(f"✓ Inserted {len(universities)} universities")

# ========== INSERT CATEGORIES ==========
categories = [
    ('Desi', 'Traditional Pakistani Food'),
    ('BBQ', 'Grilled Meat & Kebabs'),
    ('Beverages', 'Drinks & Shakes'),
    ('Fast Food', 'Burgers & Fries'),
    ('Snacks', 'Light Bites & Appetizers')
]

cursor.executemany(
    'INSERT INTO categories (category_name, description) VALUES (?, ?)',
    categories
)
print(f"✓ Inserted {len(categories)} categories")

conn.commit()

# Get IDs
universities_data = cursor.execute('SELECT university_id FROM universities').fetchall()
categories_data = cursor.execute('SELECT category_id, category_name FROM categories').fetchall()

# ========== INSERT STUDENTS ==========
student_names = [
    'Ali Khan', 'Fatima Ahmed', 'Hassan Ali', 'Zainab Hassan', 'Muhammad Usman',
    'Ayesha Khan', 'Bilal Ahmad', 'Hina Malik', 'Samir Khan', 'Noor Fatima',
    'Faisal Ahmed', 'Maryam Khan', 'Tariq Hassan', 'Amna Ali', 'Karim Khan',
    'Sara Malik', 'Imran Hassan', 'Leila Ahmed', 'Yasir Khan', 'Dina Fatima',
    'Adnan Ali', 'Rabia Khan', 'Hassan Malik', 'Samina Ahmed', 'Rashid Khan',
    'Nadia Malik', 'Jamal Ahmed', 'Hiba Khan', 'Saqib Hassan', 'Rukhsana Ali'
]

students = []
for i, name in enumerate(student_names):
    uni_id = universities_data[i % 3][0]
    email = name.lower().replace(' ', '.') + f'{i}@campus.edu'
    phone = f'03{random.randint(100000000, 999999999)}'
    students.append((uni_id, name, email, phone))

cursor.executemany(
    'INSERT INTO students (university_id, student_name, email, phone) VALUES (?, ?, ?, ?)',
    students
)
print(f"✓ Inserted {len(students)} students")

conn.commit()

# ========== INSERT STALLS ==========
stall_names = {
    'Desi': ['Desi Hut', 'Karahi Palace', 'Biryani House', 'Food Street'],
    'BBQ': ['BBQ Corner', 'Grill Master', 'Seekh Kebab', 'Tikka Inn'],
    'Beverages': ['Shake Station', 'Coffee Hub', 'Juice Bar', 'Tea Time'],
    'Fast Food': ['Burger Barn', 'Pizza Point', 'Sandwich Shop', 'Wrap King'],
    'Snacks': ['Snack Attack', 'Samosa King', 'Chips & Dips', 'Roll Corner']
}

stalls = []
stall_counter = 0

for cat_id, cat_name in categories_data:
    for uni_id in [1, 2, 3]:
        stall_list = stall_names.get(cat_name, stall_names['Fast Food'])
        for stall_name in stall_list[:2]:
            owner_name = f"Owner {stall_counter + 1}"
            phone = f'03{random.randint(100000000, 999999999)}'
            opening_time = f'{random.randint(7, 10):02d}:00:00'
            closing_time = f'{random.randint(19, 22):02d}:00:00'
            stalls.append((uni_id, cat_id, stall_name, owner_name, phone, opening_time, closing_time))
            stall_counter += 1

cursor.executemany('''
    INSERT INTO stalls (university_id, category_id, stall_name, owner_name, contact_phone, opening_time, closing_time)
    VALUES (?, ?, ?, ?, ?, ?, ?)
''', stalls)
print(f"✓ Inserted {len(stalls)} stalls")

conn.commit()

# ========== GENERATE ORDERS ==========
items_by_category = {
    'Desi': [('Chicken Biryani', 350), ('Mutton Karahi', 450), ('Daal Chawal', 250), ('Nihari', 400)],
    'BBQ': [('Seekh Kebab', 250), ('Chicken Tikka', 300), ('Malai Boti', 350), ('Tandoori Chicken', 400)],
    'Beverages': [('Mango Shake', 150), ('Cold Coffee', 180), ('Fresh Juice', 120), ('Tea', 80)],
    'Fast Food': [('Zinger Burger', 350), ('Chicken Burger', 250), ('Pizza Slice', 200), ('Fries', 120)],
    'Snacks': [('Samosa', 60), ('Spring Roll', 80), ('Pakora', 100), ('Popcorn', 120)]
}

base_date = datetime.now() - timedelta(days=90)
orders = []
order_items_list = []
ratings_list = []
payments_list = []

order_id_counter = 1
students_data = cursor.execute('SELECT student_id, university_id FROM students').fetchall()
stalls_data = cursor.execute('SELECT stall_id, university_id, category_id FROM stalls').fetchall()

# Generate 150 orders
for _ in range(150):
    student_id, uni_id = random.choice(students_data)
    matching_stalls = [s for s in stalls_data if s[1] == uni_id]
    if not matching_stalls:
        continue
    stall = random.choice(matching_stalls)
    stall_id, _, cat_id = stall
    
    order_date = base_date + timedelta(days=random.randint(0, 90), hours=random.randint(6, 22))
    payment_methods = ['Card', 'Cash', 'Easypaisa', 'JazzCash']
    delivery_statuses = ['delivered', 'delivered', 'delivered', 'pending', 'cancelled']
    is_exam_period = 1 if order_date.month in [11, 12, 4, 5] else 0
    
    # Get category name
    category_data = cursor.execute('SELECT category_name FROM categories WHERE category_id = ?', (cat_id,)).fetchone()
    category_name = category_data[0] if category_data else 'Fast Food'
    items = items_by_category.get(category_name, items_by_category['Fast Food'])
    
    # Calculate order amount
    num_items = random.randint(1, 4)
    order_total = 0
    
    for _ in range(num_items):
        item_name, unit_price = random.choice(items)
        quantity = random.randint(1, 2)
        item_total = unit_price * quantity
        order_total += item_total
        order_items_list.append((order_id_counter, item_name, quantity, unit_price, item_total))
    
    delivery_time = random.randint(15, 45) if random.random() < 0.8 else None
    
    orders.append((
        student_id, stall_id, uni_id, order_date.strftime('%Y-%m-%d %H:%M:%S'),
        round(order_total, 2), random.choice(payment_methods),
        random.choice(delivery_statuses), delivery_time, is_exam_period
    ))
    
    payments_list.append((order_id_counter, round(order_total, 2), random.choice(payment_methods), 'completed', order_date.strftime('%Y-%m-%d %H:%M:%S')))
    
    # Add rating (70% of delivered orders are rated)
    if random.random() < 0.7 and delivery_statuses[0] in ['delivered']:
        rating_value = round(random.uniform(2.5, 5.0), 1)
        comments = ['Great food!', 'Tasty', 'Quick delivery', 'Amazing', 'Good', 'Average', 'Will order again']
        ratings_list.append((order_id_counter, stall_id, student_id, rating_value, random.choice(comments), order_date.strftime('%Y-%m-%d %H:%M:%S')))
    
    order_id_counter += 1

# Insert orders
cursor.executemany('''
    INSERT INTO orders (student_id, stall_id, university_id, order_date, total_amount, payment_method, delivery_status, delivery_time, is_exam_period)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
''', orders)
print(f"✓ Inserted {len(orders)} orders")

# Insert order items
cursor.executemany('''
    INSERT INTO order_items (order_id, item_name, quantity, unit_price, item_total)
    VALUES (?, ?, ?, ?, ?)
''', order_items_list)
print(f"✓ Inserted {len(order_items_list)} order items")

# Insert payments
cursor.executemany('''
    INSERT INTO payments (order_id, amount, payment_method, payment_status, payment_date)
    VALUES (?, ?, ?, ?, ?)
''', payments_list)
print(f"✓ Inserted {len(payments_list)} payments")

# Insert ratings
cursor.executemany('''
    INSERT INTO ratings (order_id, stall_id, student_id, rating, comment, rated_at)
    VALUES (?, ?, ?, ?, ?, ?)
''', ratings_list)
print(f"✓ Inserted {len(ratings_list)} ratings")

# Update student total spending
cursor.execute('''
    UPDATE students 
    SET total_spending = (
        SELECT COALESCE(SUM(o.total_amount), 0)
        FROM orders o
        WHERE o.student_id = students.student_id
    )
''')

conn.commit()
conn.close()

print("\n" + "="*50)
print("✓ DATA GENERATION COMPLETE!")
print("="*50)
print(f"Total Orders: {len(orders)}")
print(f"Total Order Items: {len(order_items_list)}")
print(f"Total Ratings: {len(ratings_list)}")
print(f"Database saved to: {db_path}")
