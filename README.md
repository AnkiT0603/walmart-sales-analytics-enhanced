# Walmart Sales Analytics Dashboard with SQL

A major end-to-end SQL analytics project for Walmart sales data. The project includes a bundled sample from a real Walmart weekly sales dataset, a normalized POS database model, PostgreSQL/MySQL scripts, ETL loaders, an interactive Streamlit dashboard, forecasting, diagrams, CI, deployment instructions, report material, and a presentation outline.

> Live dashboard: add your Streamlit Community Cloud URL here after deployment.

## Dashboard Preview

- [Dashboard overview SVG](docs/screenshots/dashboard_overview.svg)
- [Project architecture SVG](docs/screenshots/project_architecture.svg)

To generate PNG screenshots locally:

```bash
python -m src.generate_assets
```

Expected PNG outputs:

```text
docs/screenshots/dashboard_overview.png
docs/screenshots/project_architecture.png
```

## What This Project Includes

- Bundled multi-store sample from a real Walmart weekly sales dataset in `data/raw/walmart_real_sales.csv`
- Dataset downloader for the full public dataset
- Normalized POS schema for stores, customers, products, transactions, and line items
- Weekly store sales table for real Walmart forecasting-style data
- PostgreSQL and MySQL schema, indexes, views, and analytics queries
- ETL pipeline for POS-style and weekly-store-sales CSV files
- Streamlit dashboard with CSV, upload, and database modes
- KPI pages, trend analysis, store ranking, product/customer analysis, economic signal analysis, auto-insights, and forecasting
- ER diagram, architecture diagram, final report, deployment guide, and presentation outline
- Unit tests for transformation logic
- GitHub Actions workflow for automated tests

## Dataset

The bundled dataset is a representative multi-store sample from the public Walmart weekly sales forecasting dataset hosted at:

[Hugging Face: Ammok/walmart_sales_prediction](https://huggingface.co/datasets/Ammok/walmart_sales_prediction)

Bundled file:

```text
data/raw/walmart_real_sales.csv
```

Columns:

```text
Store, Date, Weekly_Sales, Holiday_Flag, Temperature, Fuel_Price, CPI, Unemployment
```

To refresh the full dataset:

```bash
python -m src.download_dataset
```

## Folder Structure

```text
.
|-- app.py
|-- data/
|   |-- raw/
|   |-- sample/
|-- docs/
|-- reports/
|-- sql/
|   |-- mysql/
|   |-- postgres/
|-- src/
|-- tests/
```

## Quick Start

Use Python 3.10-3.12 for the smoothest setup.

```bash
python -m venv .venv
.venv\Scripts\activate
python --version
pip install -r requirements.txt
streamlit run app.py
```

The dashboard opens at:

```text
http://localhost:8501
```

## Dashboard Modes

| Mode | Purpose |
| --- | --- |
| Real weekly CSV | Uses `data/raw/walmart_real_sales.csv` |
| Sample POS CSV | Uses `data/sample/walmart_sales_sample.csv` |
| Upload CSV | Lets you upload another Walmart CSV |
| Database | Connects to PostgreSQL/MySQL using a SQLAlchemy URL |

Dashboard tabs include:

- Overview
- Stores
- Economic Signals
- Forecast
- Insights
- Data

Database URL examples:

```text
postgresql+psycopg2://postgres:password@localhost:5432/walmart_sales
mysql+pymysql://root:password@localhost:3306/walmart_sales
```

## PostgreSQL Setup

```bash
psql -U postgres -c "CREATE DATABASE walmart_sales;"
psql -U postgres -d walmart_sales -f sql/postgres/01_schema.sql
psql -U postgres -d walmart_sales -f sql/postgres/02_indexes.sql
psql -U postgres -d walmart_sales -f sql/postgres/03_views.sql
python -m src.etl --dataset-type weekly --csv data/raw/walmart_real_sales.csv --db postgresql+psycopg2://postgres:password@localhost:5432/walmart_sales
```

## MySQL Setup

```bash
mysql -u root -p -e "CREATE DATABASE walmart_sales;"
mysql -u root -p walmart_sales < sql/mysql/01_schema.sql
mysql -u root -p walmart_sales < sql/mysql/02_indexes.sql
mysql -u root -p walmart_sales < sql/mysql/03_views.sql
python -m src.etl --dataset-type weekly --csv data/raw/walmart_real_sales.csv --db mysql+pymysql://root:password@localhost:3306/walmart_sales
```

## Business Questions

- Which stores generate the highest total and average weekly sales?
- Do holiday weeks outperform regular weeks?
- How do weekly and monthly sales trends change over time?
- What is the baseline forecast for upcoming weekly sales?
- Are fuel price, CPI, unemployment, or temperature useful sales signals?
- Which product lines, branches, and customer segments perform best in POS-style data?
- Which payment methods and hours are most important in transaction-level analysis?

## Advanced SQL Coverage

The query packs include:

- CTE-based monthly trend analysis
- Window-function rankings
- 4-week rolling averages
- Month-over-month growth
- Holiday uplift analysis
- Fuel-price bucket analysis
- Store performance ranking

## Diagrams, Deployment, and Report

- Architecture and ER diagrams: `docs/architecture.md`
- Final project report: `docs/final_report.md`
- Deployment guide: `docs/deployment.md`
- Presentation outline: `reports/presentation_outline.md`

To generate PNG previews and an editable PowerPoint deck in a normal local filesystem:

```bash
python -m src.generate_assets
```

## Tests

```bash
python -m pytest
```
