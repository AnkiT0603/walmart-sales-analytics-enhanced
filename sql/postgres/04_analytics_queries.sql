-- 1. Monthly revenue trend
SELECT
    DATE_TRUNC('month', date)::date AS sales_month,
    COUNT(DISTINCT invoice_id) AS invoices,
    SUM(total) AS revenue,
    SUM(tax_5) AS tax_collected
FROM transactions
GROUP BY sales_month
ORDER BY sales_month;

-- 2. Top product lines by revenue
SELECT
    p.product_line,
    SUM(ti.quantity) AS units_sold,
    SUM(ti.quantity * ti.unit_price) AS revenue,
    SUM(ti.gross_income) AS gross_income
FROM transaction_items ti
JOIN products p ON p.product_id = ti.product_id
GROUP BY p.product_line
ORDER BY revenue DESC;

-- 3. Best performing branches
SELECT
    s.branch,
    s.city,
    COUNT(DISTINCT t.invoice_id) AS invoices,
    SUM(t.total) AS revenue,
    AVG(t.rating) AS avg_rating
FROM transactions t
JOIN stores s ON s.store_id = t.store_id
GROUP BY s.branch, s.city
ORDER BY revenue DESC;

-- 4. Customer segment analysis
SELECT
    c.customer_type,
    c.gender,
    COUNT(DISTINCT t.invoice_id) AS invoices,
    SUM(t.total) AS revenue,
    AVG(t.total) AS average_order_value
FROM transactions t
JOIN customers c ON c.customer_id = t.customer_id
GROUP BY c.customer_type, c.gender
ORDER BY revenue DESC;

-- 5. Payment method popularity
SELECT
    payment,
    COUNT(*) AS transactions,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS transaction_share_percent,
    SUM(total) AS revenue
FROM transactions
GROUP BY payment
ORDER BY transactions DESC;

-- 6. Weekday versus weekend performance
SELECT
    CASE WHEN EXTRACT(ISODOW FROM date) IN (6, 7) THEN 'Weekend' ELSE 'Weekday' END AS day_type,
    COUNT(DISTINCT invoice_id) AS invoices,
    SUM(total) AS revenue,
    AVG(total) AS average_order_value
FROM transactions
GROUP BY day_type
ORDER BY revenue DESC;

-- 7. Hourly sales pattern
SELECT
    EXTRACT(HOUR FROM time) AS sale_hour,
    COUNT(*) AS transactions,
    SUM(total) AS revenue
FROM transactions
GROUP BY sale_hour
ORDER BY sale_hour;

-- 8. Product lines below average revenue
WITH product_revenue AS (
    SELECT
        p.product_line,
        SUM(ti.quantity * ti.unit_price) AS revenue
    FROM transaction_items ti
    JOIN products p ON p.product_id = ti.product_id
    GROUP BY p.product_line
)
SELECT product_line, revenue
FROM product_revenue
WHERE revenue < (SELECT AVG(revenue) FROM product_revenue)
ORDER BY revenue;

-- 9. Real dataset: weekly sales trend
SELECT
    DATE_TRUNC('month', date)::date AS sales_month,
    COUNT(DISTINCT store) AS stores,
    SUM(weekly_sales) AS sales,
    AVG(weekly_sales) AS avg_store_weekly_sales
FROM weekly_store_sales
GROUP BY sales_month
ORDER BY sales_month;

-- 10. Real dataset: holiday impact
SELECT
    CASE WHEN holiday_flag = 1 THEN 'Holiday week' ELSE 'Regular week' END AS week_type,
    COUNT(*) AS observations,
    SUM(weekly_sales) AS sales,
    AVG(weekly_sales) AS avg_weekly_sales
FROM weekly_store_sales
GROUP BY week_type
ORDER BY avg_weekly_sales DESC;

-- 11. Real dataset: top stores
SELECT
    store,
    COUNT(*) AS weeks_reported,
    SUM(weekly_sales) AS total_sales,
    AVG(weekly_sales) AS avg_weekly_sales
FROM weekly_store_sales
GROUP BY store
ORDER BY total_sales DESC
LIMIT 10;

-- 12. Real dataset: economic signal correlations input
SELECT
    store,
    date,
    weekly_sales,
    fuel_price,
    cpi,
    unemployment,
    temperature
FROM weekly_store_sales
ORDER BY date, store;

-- 13. Real dataset: 4-week rolling sales average by store
SELECT
    store,
    date,
    weekly_sales,
    AVG(weekly_sales) OVER (
        PARTITION BY store
        ORDER BY date
        ROWS BETWEEN 3 PRECEDING AND CURRENT ROW
    ) AS rolling_4_week_avg
FROM weekly_store_sales
ORDER BY store, date;

-- 14. Real dataset: month-over-month sales growth
WITH monthly_sales AS (
    SELECT
        DATE_TRUNC('month', date)::date AS sales_month,
        SUM(weekly_sales) AS sales
    FROM weekly_store_sales
    GROUP BY sales_month
),
monthly_growth AS (
    SELECT
        sales_month,
        sales,
        LAG(sales) OVER (ORDER BY sales_month) AS previous_month_sales
    FROM monthly_sales
)
SELECT
    sales_month,
    sales,
    previous_month_sales,
    ROUND(
        100 * (sales - previous_month_sales) / NULLIF(previous_month_sales, 0),
        2
    ) AS mom_growth_percent
FROM monthly_growth
ORDER BY sales_month;

-- 15. Real dataset: store rank by total sales and average weekly sales
SELECT
    store,
    SUM(weekly_sales) AS total_sales,
    AVG(weekly_sales) AS avg_weekly_sales,
    RANK() OVER (ORDER BY SUM(weekly_sales) DESC) AS total_sales_rank,
    RANK() OVER (ORDER BY AVG(weekly_sales) DESC) AS avg_sales_rank
FROM weekly_store_sales
GROUP BY store
ORDER BY total_sales_rank;

-- 16. Real dataset: holiday sales uplift
WITH week_type_sales AS (
    SELECT
        holiday_flag,
        AVG(weekly_sales) AS avg_weekly_sales
    FROM weekly_store_sales
    GROUP BY holiday_flag
)
SELECT
    holiday.avg_weekly_sales AS holiday_avg_sales,
    regular.avg_weekly_sales AS regular_avg_sales,
    ROUND(
        100 * (holiday.avg_weekly_sales - regular.avg_weekly_sales) / NULLIF(regular.avg_weekly_sales, 0),
        2
    ) AS holiday_uplift_percent
FROM week_type_sales holiday
CROSS JOIN week_type_sales regular
WHERE holiday.holiday_flag = 1
  AND regular.holiday_flag = 0;

-- 17. Real dataset: fuel-price bucket analysis
SELECT
    CASE
        WHEN fuel_price < 3 THEN 'Low fuel price'
        WHEN fuel_price < 3.5 THEN 'Medium fuel price'
        ELSE 'High fuel price'
    END AS fuel_price_bucket,
    COUNT(*) AS observations,
    SUM(weekly_sales) AS sales,
    AVG(weekly_sales) AS avg_weekly_sales
FROM weekly_store_sales
GROUP BY fuel_price_bucket
ORDER BY avg_weekly_sales DESC;
