# Database Design

## Entities

The project models point-of-sale data as a retail star schema with normalized dimensions.

| Table | Purpose |
| --- | --- |
| `stores` | Branch, city, and region metadata |
| `customers` | Customer type and demographic segment attributes |
| `products` | Product line and product attributes |
| `transactions` | Invoice-level facts such as date, payment, subtotal, tax, and total |
| `transaction_items` | Line-item facts such as quantity, unit price, COGS, and gross income |
| `weekly_store_sales` | Real Walmart weekly store sales with holiday and economic indicators |

## Why This Design

The source CSV is invoice-oriented, but dashboards and SQL analysis are easier when repeated values are split into dimensions. This design avoids duplicated store, customer, and product attributes while keeping invoice facts queryable.

## Analytical Views

| View | Use |
| --- | --- |
| `vw_daily_sales` | Revenue and invoice trends over time |
| `vw_product_performance` | Product-line revenue, margin, and quantity analysis |
| `vw_customer_segments` | Segment-level customer behavior |
| `vw_store_performance` | Store and city KPIs |
| `vw_weekly_sales_trend` | Real dataset weekly sales trend with economic indicators |
| `vw_weekly_store_performance` | Store-level sales ranking for real weekly dataset |

## Weekly Store Sales Model

The real Walmart dataset uses a forecasting-style grain: one row per store per week. It is stored in `weekly_store_sales` because it has a different business grain from invoice-level POS transactions.

This table supports:

- Weekly and monthly sales trends
- Holiday versus regular week analysis
- Store ranking by total and average weekly sales
- Economic signal review using fuel price, CPI, unemployment, and temperature
