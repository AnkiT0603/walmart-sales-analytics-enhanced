CREATE OR REPLACE VIEW vw_daily_sales AS
SELECT
    t.date AS sales_date,
    COUNT(DISTINCT t.invoice_id) AS invoices,
    SUM(t.total) AS revenue,
    SUM(t.cogs) AS cogs,
    SUM(t.tax_5) AS tax_collected,
    AVG(t.rating) AS avg_rating
FROM transactions t
GROUP BY t.date;

CREATE OR REPLACE VIEW vw_product_performance AS
SELECT
    p.product_line,
    SUM(ti.quantity) AS units_sold,
    SUM(ti.quantity * ti.unit_price) AS merchandise_revenue,
    SUM(ti.gross_income) AS gross_income,
    AVG(ti.unit_price) AS avg_unit_price
FROM transaction_items ti
JOIN products p ON p.product_id = ti.product_id
GROUP BY p.product_line;

CREATE OR REPLACE VIEW vw_customer_segments AS
SELECT
    c.customer_type,
    c.gender,
    COUNT(DISTINCT t.invoice_id) AS invoices,
    SUM(t.total) AS revenue,
    AVG(t.total) AS average_order_value,
    AVG(t.rating) AS avg_rating
FROM transactions t
JOIN customers c ON c.customer_id = t.customer_id
GROUP BY c.customer_type, c.gender;

CREATE OR REPLACE VIEW vw_store_performance AS
SELECT
    s.branch,
    s.city,
    COUNT(DISTINCT t.invoice_id) AS invoices,
    SUM(t.total) AS revenue,
    SUM(t.cogs) AS cogs,
    SUM(t.tax_5) AS tax_collected,
    AVG(t.rating) AS avg_rating
FROM transactions t
JOIN stores s ON s.store_id = t.store_id
GROUP BY s.branch, s.city;

CREATE OR REPLACE VIEW vw_weekly_sales_trend AS
SELECT
    date AS week_start,
    COUNT(DISTINCT store) AS active_stores,
    SUM(weekly_sales) AS total_sales,
    AVG(weekly_sales) AS avg_store_weekly_sales,
    AVG(fuel_price) AS avg_fuel_price,
    AVG(unemployment) AS avg_unemployment
FROM weekly_store_sales
GROUP BY date;

CREATE OR REPLACE VIEW vw_weekly_store_performance AS
SELECT
    store,
    COUNT(*) AS weeks_reported,
    SUM(weekly_sales) AS total_sales,
    AVG(weekly_sales) AS avg_weekly_sales,
    MAX(weekly_sales) AS best_week_sales,
    MIN(weekly_sales) AS lowest_week_sales
FROM weekly_store_sales
GROUP BY store;
