# Presentation Outline

Use `python -m src.generate_assets` to export an editable PowerPoint deck when filesystem binary writes are available.

## Slide 1: Walmart Sales Analytics Dashboard

SQL database design, ETL, real weekly sales analytics, and Streamlit reporting.

## Slide 2: Project Scope

- PostgreSQL and MySQL schemas
- POS and real weekly store sales analysis
- ETL validation and loading
- Streamlit dashboard with CSV and database modes

## Slide 3: Real Dataset Snapshot

- Real weekly Walmart dataset
- Store, date, weekly sales, holiday flag, temperature, fuel price, CPI, unemployment
- Useful for store performance and economic signal analysis

## Slide 4: Top Stores

Rank stores by total sales, average weekly sales, and reporting weeks.

## Slide 5: Dashboard and SQL Deliverables

- Overview, Stores, Economic Signals, Products, Customers, Operations, Data
- SQL views and business questions
- PostgreSQL/MySQL support

## Slide 6: Recommended Enhancements

- Load full dataset with `python -m src.download_dataset`
- Add forecasting models
- Deploy dashboard with managed PostgreSQL
- Add scheduled refresh and role-based views
