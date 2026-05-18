CREATE INDEX idx_transactions_date ON transactions(date);
CREATE INDEX idx_transactions_store ON transactions(store_id);
CREATE INDEX idx_transactions_customer ON transactions(customer_id);
CREATE INDEX idx_transactions_payment ON transactions(payment);
CREATE INDEX idx_transaction_items_product ON transaction_items(product_id);
CREATE INDEX idx_weekly_store_sales_store ON weekly_store_sales(store);
CREATE INDEX idx_weekly_store_sales_date ON weekly_store_sales(date);
CREATE INDEX idx_weekly_store_sales_holiday ON weekly_store_sales(holiday_flag);
