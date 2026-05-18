# Walmart Sales Analytics Project Report

## Objective

Build an end-to-end SQL analytics system for Walmart point-of-sale records. The project converts raw sales transactions into a structured database and uses SQL plus a dashboard to answer business questions around revenue trends, product performance, customer segments, and store operations.

## Methodology

1. Ingest the Walmart sales CSV.
2. Standardize column names, date/time fields, numeric values, and missing values.
3. Load dimension tables for stores, customers, and products.
4. Load transaction and line-item fact tables.
5. Create SQL views for recurring analysis.
6. Build a dashboard for interactive filtering and visualization.

## Key Analyses

- Revenue by day, month, branch, city, and product line
- Top product categories by revenue and gross income
- Average order value by customer type and gender
- Payment-method distribution
- Weekend versus weekday performance
- Store-level ranking by revenue, invoice count, and rating

## Tools

- SQL: PostgreSQL and MySQL
- Python: pandas, SQLAlchemy
- Dashboard: Streamlit and Plotly

