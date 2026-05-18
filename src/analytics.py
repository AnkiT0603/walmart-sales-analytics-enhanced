import pandas as pd


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    renamed = {
        column: column.strip().lower().replace(" ", "_").replace("%", "percent")
        for column in df.columns
    }
    df = df.rename(columns=renamed).copy()
    aliases = {
        "invoice_id": "invoice_id",
        "invoice_id_": "invoice_id",
        "branch": "branch",
        "customer_type": "customer_type",
        "product_line": "product_line",
        "unit_price": "unit_price",
        "tax_5percent": "tax_5",
        "tax_5": "tax_5",
        "gross_margin_percentage": "gross_margin_percentage",
        "gross_margin_percent": "gross_margin_percentage",
        "gross_income": "gross_income",
        "weekly_sales": "weekly_sales",
        "holiday_flag": "holiday_flag",
        "fuel_price": "fuel_price",
    }
    return df.rename(columns={key: value for key, value in aliases.items() if key in df.columns})


def detect_dataset_type(df: pd.DataFrame) -> str:
    columns = set(normalize_columns(df).columns)
    if {"store", "weekly_sales", "holiday_flag"}.issubset(columns):
        return "weekly"
    if {"invoice_id", "product_line", "total"}.issubset(columns):
        return "pos"
    return "unknown"


def prepare_sales_frame(df: pd.DataFrame) -> pd.DataFrame:
    df = normalize_columns(df)
    df = df.copy()

    numeric_columns = [
        "unit_price",
        "quantity",
        "tax_5",
        "total",
        "cogs",
        "gross_margin_percentage",
        "gross_income",
        "rating",
    ]
    for column in numeric_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")

    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df["month"] = df["date"].dt.to_period("M").astype(str)
        df["weekday"] = df["date"].dt.day_name()
        df["is_weekend"] = df["date"].dt.dayofweek >= 5

    if "time" in df.columns:
        df["hour"] = pd.to_datetime(df["time"], format="%H:%M:%S", errors="coerce").dt.hour
        missing_hour = df["hour"].isna()
        if missing_hour.any():
            df.loc[missing_hour, "hour"] = pd.to_datetime(
                df.loc[missing_hour, "time"], format="%H:%M", errors="coerce"
            ).dt.hour

    df["average_order_value"] = df["total"]
    return df


def prepare_weekly_sales_frame(df: pd.DataFrame) -> pd.DataFrame:
    df = normalize_columns(df).copy()
    numeric_columns = ["store", "weekly_sales", "holiday_flag", "temperature", "fuel_price", "cpi", "unemployment"]
    for column in numeric_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")

    df["date"] = pd.to_datetime(df["date"], dayfirst=True, errors="coerce")
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.to_period("M").astype(str)
    df["quarter"] = df["date"].dt.to_period("Q").astype(str)
    df["week"] = df["date"].dt.isocalendar().week.astype("Int64")
    df["holiday_period"] = df["holiday_flag"].map({1: "Holiday week", 0: "Regular week"}).fillna("Unknown")
    return df.dropna(subset=["store", "date", "weekly_sales"])


def kpi_summary(df: pd.DataFrame) -> dict[str, float]:
    return {
        "revenue": float(df["total"].sum()),
        "invoices": int(df["invoice_id"].nunique()),
        "quantity": int(df["quantity"].sum()),
        "gross_income": float(df["gross_income"].sum()),
        "average_order_value": float(df["total"].mean()),
        "average_rating": float(df["rating"].mean()),
    }


def weekly_kpi_summary(df: pd.DataFrame) -> dict[str, float]:
    return {
        "total_sales": float(df["weekly_sales"].sum()),
        "stores": int(df["store"].nunique()),
        "weeks": int(df["date"].nunique()),
        "average_weekly_sales": float(df["weekly_sales"].mean()),
        "holiday_sales": float(df.loc[df["holiday_flag"] == 1, "weekly_sales"].sum()),
        "regular_sales": float(df.loc[df["holiday_flag"] == 0, "weekly_sales"].sum()),
    }


def aggregate_sales(df: pd.DataFrame, group_by: str) -> pd.DataFrame:
    return (
        df.groupby(group_by, dropna=False)
        .agg(
            revenue=("total", "sum"),
            invoices=("invoice_id", "nunique"),
            quantity=("quantity", "sum"),
            gross_income=("gross_income", "sum"),
            avg_rating=("rating", "mean"),
        )
        .reset_index()
        .sort_values("revenue", ascending=False)
    )


def aggregate_weekly_sales(df: pd.DataFrame, group_by: str) -> pd.DataFrame:
    return (
        df.groupby(group_by, dropna=False)
        .agg(
            sales=("weekly_sales", "sum"),
            avg_weekly_sales=("weekly_sales", "mean"),
            weeks=("date", "nunique"),
            avg_temperature=("temperature", "mean"),
            avg_fuel_price=("fuel_price", "mean"),
            avg_cpi=("cpi", "mean"),
            avg_unemployment=("unemployment", "mean"),
        )
        .reset_index()
        .sort_values("sales", ascending=False)
    )


def forecast_weekly_sales(df: pd.DataFrame, periods: int = 8, window: int = 4) -> pd.DataFrame:
    weekly = (
        df.groupby("date", as_index=False)
        .agg(weekly_sales=("weekly_sales", "sum"))
        .sort_values("date")
    )
    weekly["series_type"] = "Actual"

    if weekly.empty:
        return weekly.rename(columns={"weekly_sales": "sales"})

    recent_average = weekly["weekly_sales"].tail(window).mean()
    if pd.isna(recent_average):
        recent_average = weekly["weekly_sales"].mean()

    last_date = weekly["date"].max()
    future_dates = pd.date_range(last_date + pd.Timedelta(days=7), periods=periods, freq="7D")
    forecast = pd.DataFrame(
        {
            "date": future_dates,
            "weekly_sales": [recent_average] * periods,
            "series_type": "Forecast",
        }
    )

    result = pd.concat([weekly, forecast], ignore_index=True)
    return result.rename(columns={"weekly_sales": "sales"})


def weekly_insights(df: pd.DataFrame) -> list[str]:
    if df.empty:
        return ["No rows are available for the current filter selection."]

    store_sales = aggregate_weekly_sales(df, "store")
    holiday_sales = aggregate_weekly_sales(df, "holiday_period")
    monthly_sales = df.groupby("month", as_index=False).agg(sales=("weekly_sales", "sum")).sort_values("sales", ascending=False)

    top_store = int(store_sales.iloc[0]["store"])
    best_month = monthly_sales.iloc[0]["month"]
    best_week_type = holiday_sales.iloc[0]["holiday_period"]
    avg_sales = df["weekly_sales"].mean()

    return [
        f"Store {top_store} is the top performer in the current selection.",
        f"{best_month} is the highest sales month in the filtered data.",
        f"{best_week_type} contributes the highest total sales.",
        f"Average weekly store sales are ${avg_sales:,.0f}.",
    ]
