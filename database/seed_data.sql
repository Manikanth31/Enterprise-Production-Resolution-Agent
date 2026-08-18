-- ============================================
-- AegisOps Synthetic Enterprise Data
-- ============================================

-- Customers
INSERT INTO customers
    (customer_id, customer_name, status, created_date)
VALUES
    (1001, 'Acme Manufacturing', 'ACTIVE', '2026-08-01'),
    (1002, 'Global Retail Corp', 'ACTIVE', '2026-08-02'),
    (1003, 'Northwind Services', 'ACTIVE', '2026-08-03'),
    (1004, 'BlueSky Logistics', 'ACTIVE', '2026-08-04'),
    (1005, 'Vertex Healthcare', 'ACTIVE', '2026-08-05');


    -- Orders
INSERT INTO orders
    (order_id, customer_id, order_date, order_status, order_amount)
VALUES
    (5001, 1001, '2026-08-10', 'COMPLETED', 12500.00),
    (5002, 1002, '2026-08-10', 'COMPLETED', 8750.00),
    (5003, 1003, '2026-08-11', 'COMPLETED', 4200.00),
    (5004, 1004, '2026-08-11', 'PENDING',    15300.00),
    (5005, 1005, '2026-08-12', 'FAILED',      9800.00);


-- Invoices



    -- Invoices
INSERT INTO invoices
    (invoice_id, order_id, invoice_date, invoice_status, invoice_amount)
VALUES
    (9001, 5001, '2026-08-10', 'PAID',    12500.00),
    (9002, 5002, '2026-08-10', 'PAID',     8750.00),
    (9003, 5003, '2026-08-11', 'PAID',     4200.00),
    (9004, 5004, '2026-08-11', 'PENDING', 15300.00),
    (9005, 5005, '2026-08-12', 'FAILED',   9800.00);


-- Payments
INSERT INTO payments
    (payment_id, invoice_id, payment_date, payment_status, payment_amount)
VALUES
    (7001, 9001, '2026-08-10', 'SUCCESS', 12500.00),
    (7002, 9002, '2026-08-10', 'SUCCESS',  8750.00),
    (7003, 9003, '2026-08-11', 'SUCCESS',  4200.00),
    (7004, 9004, 'PENDING',  'PENDING',   15300.00),
    (7005, 9005, '2026-08-12', 'FAILED',    9800.00);


    -- Interface transactions
INSERT INTO interface_transactions
    (interface_id, order_id, interface_name, status,
     error_code, error_message, created_date)
VALUES
    (
        3001,
        5001,
        'ORDER_TO_ERP',
        'SUCCESS',
        NULL,
        NULL,
        '2026-08-10 09:15:00'
    ),
    (
        3002,
        5002,
        'ORDER_TO_ERP',
        'SUCCESS',
        NULL,
        NULL,
        '2026-08-10 09:30:00'
    ),
    (
        3003,
        5003,
        'ORDER_TO_ERP',
        'SUCCESS',
        NULL,
        NULL,
        '2026-08-11 10:15:00'
    ),
    (
        3004,
        5004,
        'ORDER_TO_ERP',
        'FAILED',
        'INT-500',
        'Interface timeout while sending order',
        '2026-08-11 14:20:00'
    ),
    (
        3005,
        5005,
        'ORDER_TO_ERP',
        'FAILED',
        'DB-409',
        'Duplicate transaction detected',
        '2026-08-12 16:45:00'
    );


    -- Error logs
INSERT INTO error_log
    (error_id, interface_id, error_timestamp,
     error_code, error_message, severity)
VALUES
    (
        4001,
        3004,
        '2026-08-11 14:20:05',
        'INT-500',
        'Connection timeout while calling downstream ERP interface',
        'HIGH'
    ),
    (
        4002,
        3005,
        '2026-08-12 16:45:12',
        'DB-409',
        'Duplicate transaction detected for order 5005',
        'CRITICAL'
    );
    