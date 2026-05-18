DROP TABLE IF EXISTS transaction_items;
DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS stores;
DROP TABLE IF EXISTS weekly_store_sales;

CREATE TABLE stores (
    store_id INTEGER PRIMARY KEY,
    branch VARCHAR(10) NOT NULL,
    city VARCHAR(80) NOT NULL,
    region VARCHAR(80) DEFAULT 'Unknown',
    UNIQUE (branch, city)
);

CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    customer_type VARCHAR(40) NOT NULL,
    gender VARCHAR(20) NOT NULL,
    UNIQUE (customer_type, gender)
);

CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    product_line VARCHAR(120) NOT NULL UNIQUE
);

CREATE TABLE transactions (
    transaction_id INTEGER PRIMARY KEY,
    invoice_id VARCHAR(40) NOT NULL UNIQUE,
    store_id INTEGER NOT NULL REFERENCES stores(store_id),
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
    date DATE NOT NULL,
    time TIME NOT NULL,
    payment VARCHAR(40) NOT NULL,
    cogs NUMERIC(12, 2) NOT NULL,
    tax_5 NUMERIC(12, 2) NOT NULL,
    total NUMERIC(12, 2) NOT NULL,
    gross_margin_percentage NUMERIC(8, 4) NOT NULL,
    rating NUMERIC(4, 2),
    CONSTRAINT chk_transaction_amounts CHECK (total >= 0 AND cogs >= 0 AND tax_5 >= 0)
);

CREATE TABLE transaction_items (
    transaction_item_id INTEGER PRIMARY KEY,
    transaction_id INTEGER NOT NULL REFERENCES transactions(transaction_id),
    product_id INTEGER NOT NULL REFERENCES products(product_id),
    unit_price NUMERIC(10, 2) NOT NULL,
    quantity INTEGER NOT NULL,
    gross_income NUMERIC(12, 2) NOT NULL,
    CONSTRAINT chk_item_amounts CHECK (unit_price >= 0 AND quantity > 0 AND gross_income >= 0)
);

CREATE TABLE weekly_store_sales (
    weekly_sale_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    store INTEGER NOT NULL,
    date DATE NOT NULL,
    weekly_sales NUMERIC(14, 2) NOT NULL,
    holiday_flag INTEGER NOT NULL,
    temperature NUMERIC(8, 2),
    fuel_price NUMERIC(8, 3),
    cpi NUMERIC(12, 4),
    unemployment NUMERIC(8, 3),
    UNIQUE (store, date),
    CONSTRAINT chk_weekly_sales_amount CHECK (weekly_sales >= 0),
    CONSTRAINT chk_holiday_flag CHECK (holiday_flag IN (0, 1))
);
