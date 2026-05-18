# Final Report: Walmart Sales Analytics Dashboard with SQL

## Executive Summary

This project builds an end-to-end Walmart sales analytics system using SQL, Python, and Streamlit. It supports two analytical tracks:

- A normalized POS-style retail schema for customer, product, store, transaction, and transaction-item analysis.
- A real Walmart weekly store sales dataset with store-level sales, holiday flags, temperature, fuel price, CPI, and unemployment indicators.

The system can run from CSV files for quick exploration or connect to PostgreSQL/MySQL for database-backed reporting.

## Dataset

The real dataset used in `data/raw/walmart_real_sales.csv` comes from the public Hugging Face dataset `Ammok/walmart_sales_prediction`, which mirrors the common Walmart weekly sales forecasting dataset.

Fields:

| Field | Meaning |
| --- | --- |
| `Store` | Walmart store identifier |
| `Date` | Weekly reporting date |
| `Weekly_Sales` | Store sales for that week |
| `Holiday_Flag` | Whether the week contains a major holiday |
| `Temperature` | Local temperature |
| `Fuel_Price` | Fuel price in the region |
| `CPI` | Consumer price index |
| `Unemployment` | Unemployment rate |

## Business Questions

1. Which stores generate the highest total and average weekly sales?
2. Do holiday weeks outperform regular weeks?
3. How do weekly and monthly sales trends change over time?
4. Are fuel price, CPI, unemployment, or temperature useful operational signals?
5. Which customer, product, and branch segments perform best in POS-style data?

## Database Implementation

The project includes PostgreSQL and MySQL scripts:

- `01_schema.sql`: creates normalized POS tables and weekly store sales table
- `02_indexes.sql`: adds indexes for filtering, joins, and trend analysis
- `03_views.sql`: defines reusable reporting views
- `04_analytics_queries.sql`: answers business-analysis questions directly in SQL

## Dashboard Implementation

The Streamlit dashboard supports:

- Real weekly CSV mode
- Sample POS CSV mode
- CSV upload mode
- PostgreSQL/MySQL database mode
- Store, year, holiday, branch, product, customer, payment, rating, and sales-range filters
- KPI cards, trend charts, segmentation views, store ranking, economic signal plots, auto-generated insights, and moving-average forecasting

## Forecasting

The dashboard includes a lightweight moving-average forecast for weekly sales. This provides an interpretable baseline that helps users compare recent sales behavior against the next several forecasted weeks.

## Deployment and CI

The project includes:

- `.streamlit/config.toml` for Streamlit Cloud configuration
- `docs/deployment.md` with deployment steps
- `.github/workflows/tests.yml` for automated test execution on GitHub

## Conclusion

The project is suitable as a major academic or portfolio project because it demonstrates database design, ETL, SQL analytics, dashboarding, forecasting, documentation, deployment readiness, and reproducible reporting. It can be extended further with advanced forecasting models, scheduled data refresh, and role-based dashboard pages.
