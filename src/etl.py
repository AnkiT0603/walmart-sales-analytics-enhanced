import argparse
from pathlib import Path

import pandas as pd
from sqlalchemy import text

from src.analytics import prepare_sales_frame
from src.analytics import prepare_weekly_sales_frame
from src.config import REQUIRED_COLUMNS
from src.config import WEEKLY_REQUIRED_COLUMNS
from src.db import make_engine


def validate_columns(df: pd.DataFrame) -> None:
    missing = sorted(REQUIRED_COLUMNS - set(df.columns))
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")


def validate_weekly_columns(df: pd.DataFrame) -> None:
    missing = sorted(WEEKLY_REQUIRED_COLUMNS - set(df.columns))
    if missing:
        raise ValueError(f"Missing required weekly dataset columns: {', '.join(missing)}")


def read_sales_csv(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df = prepare_sales_frame(df)
    validate_columns(df)
    return df


def read_weekly_sales_csv(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df = prepare_weekly_sales_frame(df)
    validate_weekly_columns(df)
    return df


def build_dimensions(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    stores = (
        df[["branch", "city"]]
        .drop_duplicates()
        .sort_values(["branch", "city"])
        .reset_index(drop=True)
        .assign(store_id=lambda frame: frame.index + 1, region="Unknown")
    )[["store_id", "branch", "city", "region"]]

    customers = (
        df[["customer_type", "gender"]]
        .drop_duplicates()
        .sort_values(["customer_type", "gender"])
        .reset_index(drop=True)
        .assign(customer_id=lambda frame: frame.index + 1)
    )[["customer_id", "customer_type", "gender"]]

    products = (
        df[["product_line"]]
        .drop_duplicates()
        .sort_values("product_line")
        .reset_index(drop=True)
        .assign(product_id=lambda frame: frame.index + 1)
    )[["product_id", "product_line"]]

    return {"stores": stores, "customers": customers, "products": products}


def build_facts(df: pd.DataFrame, dimensions: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    enriched = df.merge(dimensions["stores"], on=["branch", "city"], how="left")
    enriched = enriched.merge(dimensions["customers"], on=["customer_type", "gender"], how="left")
    enriched = enriched.merge(dimensions["products"], on="product_line", how="left")

    transactions = enriched[
        [
            "invoice_id",
            "store_id",
            "customer_id",
            "date",
            "time",
            "payment",
            "cogs",
            "tax_5",
            "total",
            "gross_margin_percentage",
            "rating",
        ]
    ].copy()
    transactions["transaction_id"] = range(1, len(transactions) + 1)
    transactions = transactions[
        [
            "transaction_id",
            "invoice_id",
            "store_id",
            "customer_id",
            "date",
            "time",
            "payment",
            "cogs",
            "tax_5",
            "total",
            "gross_margin_percentage",
            "rating",
        ]
    ]

    transaction_items = enriched[["invoice_id", "product_id", "unit_price", "quantity", "gross_income"]].copy()
    transaction_items = transaction_items.merge(
        transactions[["transaction_id", "invoice_id"]], on="invoice_id", how="left"
    )
    transaction_items["transaction_item_id"] = range(1, len(transaction_items) + 1)
    transaction_items = transaction_items[
        ["transaction_item_id", "transaction_id", "product_id", "unit_price", "quantity", "gross_income"]
    ]

    return {"transactions": transactions, "transaction_items": transaction_items}


def load_to_database(csv_path: str | Path, connection_url: str) -> None:
    df = read_sales_csv(csv_path)
    dimensions = build_dimensions(df)
    facts = build_facts(df, dimensions)
    engine = make_engine(connection_url)

    with engine.begin() as connection:
        for table in ["transaction_items", "transactions", "products", "customers", "stores"]:
            connection.execute(text(f"DELETE FROM {table}"))

    for table_name, frame in {**dimensions, **facts}.items():
        frame.to_sql(table_name, engine, if_exists="append", index=False)


def load_weekly_to_database(csv_path: str | Path, connection_url: str) -> None:
    df = read_weekly_sales_csv(csv_path)
    engine = make_engine(connection_url)
    with engine.begin() as connection:
        connection.execute(text("DELETE FROM weekly_store_sales"))
    df[
        [
            "store",
            "date",
            "weekly_sales",
            "holiday_flag",
            "temperature",
            "fuel_price",
            "cpi",
            "unemployment",
        ]
    ].to_sql("weekly_store_sales", engine, if_exists="append", index=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="Load Walmart sales CSV into PostgreSQL or MySQL.")
    parser.add_argument("--csv", required=True, help="Path to the Walmart sales CSV file.")
    parser.add_argument("--db", required=True, help="SQLAlchemy database URL.")
    parser.add_argument("--dataset-type", choices=["pos", "weekly"], default="pos")
    args = parser.parse_args()
    if args.dataset_type == "weekly":
        load_weekly_to_database(args.csv, args.db)
    else:
        load_to_database(args.csv, args.db)


if __name__ == "__main__":
    main()
