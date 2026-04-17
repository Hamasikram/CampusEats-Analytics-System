-- CampusEats Analytics Database
DROP TABLE IF EXISTS ratings;
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS payments;
DROP TABLE IF EXISTS stalls;
DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS universities;

CREATE TABLE universities (
    university_id INTEGER PRIMARY KEY AUTOINCREMENT,
    university_name VARCHAR(100) NOT NULL,
    location VARCHAR(100) NOT NULL
);

CREATE TABLE categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name VARCHAR(50) NOT NULL,
    description TEXT
);

CREATE TABLE students (
    student_id INTEGER PRIMARY KEY AUTOINCREMENT,
    university_id INTEGER NOT NULL,
    student_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(20),
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_spending DECIMAL(10,2) DEFAULT 0,
    FOREIGN KEY (university_id) REFERENCES universities(university_id)
);

CREATE TABLE stalls (
    stall_id INTEGER PRIMARY KEY AUTOINCREMENT,
    university_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    stall_name VARCHAR(100) NOT NULL,
    owner_name VARCHAR(100),
    contact_phone VARCHAR(20),
    opening_time TIME,
    closing_time TIME,
    is_active BOOLEAN DEFAULT 1,
    FOREIGN KEY (university_id) REFERENCES universities(university_id),
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
);

CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    stall_id INTEGER NOT NULL,
    university_id INTEGER NOT NULL,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_amount DECIMAL(10,2) NOT NULL,
    payment_method VARCHAR(50),
    delivery_status VARCHAR(50) DEFAULT 'pending',
    delivery_time INTEGER,
    is_exam_period BOOLEAN DEFAULT 0,
    notes TEXT,
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (stall_id) REFERENCES stalls(stall_id),
    FOREIGN KEY (university_id) REFERENCES universities(university_id)
);

CREATE TABLE order_items (
    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    item_name VARCHAR(100) NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    item_total DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

CREATE TABLE payments (
    payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    payment_method VARCHAR(50),
    payment_status VARCHAR(50) DEFAULT 'completed',
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

CREATE TABLE ratings (
    rating_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    stall_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    rating DECIMAL(2,1) NOT NULL CHECK(rating >= 1 AND rating <= 5),
    comment TEXT,
    rated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (stall_id) REFERENCES stalls(stall_id),
    FOREIGN KEY (student_id) REFERENCES students(student_id)
);

CREATE INDEX idx_order_date ON orders(order_date);
CREATE INDEX idx_student_university ON students(university_id);
CREATE INDEX idx_stall_category ON stalls(category_id);
