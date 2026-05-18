from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
RAW_DATA_PATH = DATA_DIR / "raw" / "walmart_real_sales.csv"
SAMPLE_DATA_PATH = DATA_DIR / "sample" / "walmart_sales_sample.csv"
SCREENSHOT_DIR = BASE_DIR / "docs" / "screenshots"
REPORT_DIR = BASE_DIR / "reports"

WALMART_DATASET_URL = "https://huggingface.co/datasets/Ammok/walmart_sales_prediction/resolve/main/Walmart.csv"

REQUIRED_COLUMNS = {
    "invoice_id",
    "branch",
    "city",
    "customer_type",
    "gender",
    "product_line",
    "unit_price",
    "quantity",
    "tax_5",
    "total",
    "date",
    "time",
    "payment",
    "cogs",
    "gross_margin_percentage",
    "gross_income",
    "rating",
}

WEEKLY_REQUIRED_COLUMNS = {
    "store",
    "date",
    "weekly_sales",
    "holiday_flag",
    "temperature",
    "fuel_price",
    "cpi",
    "unemployment",
}
