DROP TABLE IF EXISTS transaction_items;
DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS stores;
DROP TABLE IF EXISTS weekly_store_sales;

CREATE TABLE stores (
    store_id INT PRIMARY KEY,
    branch VARCHAR(10) NOT NULL,
    city VARCHAR(80) NOT NULL,
    region VARCHAR(80) DEFAULT 'Unknown',
    UNIQUE KEY uq_store_branch_city (branch, city)
);

CREATE TABLE customers (
    customer_id INT PRIMARY KEY,
    customer_type VARCHAR(40) NOT NULL,
    gender VARCHAR(20) NOT NULL,
    UNIQUE KEY uq_customer_segment (customer_type, gender)
);

CREATE TABLE products (
    product_id INT PRIMARY KEY,
    product_line VARCHAR(120) NOT NULL UNIQUE
);

CREATE TABLE transactions (
    transaction_id INT PRIMARY KEY,
    invoice_id VARCHAR(40) NOT NULL UNIQUE,
    store_id INT NOT NULL,
    customer_id INT NOT NULL,
    date DATE NOT NULL,
    time TIME NOT NULL,
    payment VARCHAR(40) NOT NULL,
    cogs DECIMAL(12, 2) NOT NULL,
    tax_5 DECIMAL(12, 2) NOT NULL,
    total DECIMAL(12, 2) NOT NULL,
    gross_margin_percentage DECIMAL(8, 4) NOT NULL,
    rating DECIMAL(4, 2),
    CONSTRAINT fk_transactions_store FOREIGN KEY (store_id) REFERENCES stores(store_id),
    CONSTRAINT fk_transactions_customer FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    CONSTRAINT chk_transaction_amounts CHECK (total >= 0 AND cogs >= 0 AND tax_5 >= 0)
);

CREATE TABLE transaction_items (
    transaction_item_id INT PRIMARY KEY,
    transaction_id INT NOT NULL,
    product_id INT NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    quantity INT NOT NULL,
    gross_income DECIMAL(12, 2) NOT NULL,
    CONSTRAINT fk_items_transaction FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id),
    CONSTRAINT fk_items_product FOREIGN KEY (product_id) REFERENCES products(product_id),
    CONSTRAINT chk_item_amounts CHECK (unit_price >= 0 AND quantity > 0 AND gross_income >= 0)
);

CREATE TABLE weekly_store_sales (
    weekly_sale_id INT AUTO_INCREMENT PRIMARY KEY,
    store INT NOT NULL,
    date DATE NOT NULL,
    weekly_sales DECIMAL(14, 2) NOT NULL,
    holiday_flag INT NOT NULL,
    temperature DECIMAL(8, 2),
    fuel_price DECIMAL(8, 3),
    cpi DECIMAL(12, 4),
    unemployment DECIMAL(8, 3),
    UNIQUE KEY uq_weekly_store_date (store, date),
    CONSTRAINT chk_weekly_sales_amount CHECK (weekly_sales >= 0),
    CONSTRAINT chk_holiday_flag CHECK (holiday_flag IN (0, 1))
);
