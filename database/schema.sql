-- ============================================
-- Enterprise Production Resolution Agent
-- Synthetic Enterprise Database Schema
-- ============================================

-- 1. Customers
CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    customer_name TEXT NOT NULL,
    status TEXT NOT NULL,
    created_date TEXT NOT NULL
);

-- 2. Orders
CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    order_date TEXT NOT NULL,
    order_status TEXT NOT NULL,
    order_amount REAL NOT NULL,

    FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id)
);

-- 3. Invoices
CREATE TABLE invoices (
    invoice_id INTEGER PRIMARY KEY,
    order_id INTEGER NOT NULL,
    invoice_date TEXT NOT NULL,
    invoice_status TEXT NOT NULL,
    invoice_amount REAL NOT NULL,

    FOREIGN KEY (order_id)
        REFERENCES orders(order_id)
);

-- 4. Payments
CREATE TABLE payments (
    payment_id INTEGER PRIMARY KEY,
    invoice_id INTEGER NOT NULL,
    payment_date TEXT NOT NULL,
    payment_status TEXT NOT NULL,
    payment_amount REAL NOT NULL,

    FOREIGN KEY (invoice_id)
        REFERENCES invoices(invoice_id)
);

-- 5. Interface transactions
CREATE TABLE interface_transactions (
    interface_id INTEGER PRIMARY KEY,
    order_id INTEGER NOT NULL,
    interface_name TEXT NOT NULL,
    status TEXT NOT NULL,
    error_code TEXT,
    error_message TEXT,
    created_date TEXT NOT NULL,

    FOREIGN KEY (order_id)
        REFERENCES orders(order_id)
);

-- 6. Application/database errors
CREATE TABLE error_log (
    error_id INTEGER PRIMARY KEY,
    interface_id INTEGER,
    error_timestamp TEXT NOT NULL,
    error_code TEXT NOT NULL,
    error_message TEXT NOT NULL,
    severity TEXT NOT NULL,

    FOREIGN KEY (interface_id)
        REFERENCES interface_transactions(interface_id)
);