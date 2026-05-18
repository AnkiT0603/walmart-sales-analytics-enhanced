import pandas as pd
import plotly.express as px
import streamlit as st

from src.analytics import (
    aggregate_sales,
    aggregate_weekly_sales,
    detect_dataset_type,
    forecast_weekly_sales,
    kpi_summary,
    prepare_sales_frame,
    prepare_weekly_sales_frame,
    weekly_insights,
    weekly_kpi_summary,
)
from src.config import RAW_DATA_PATH, SAMPLE_DATA_PATH
from src.db import make_engine

st.set_page_config(page_title="Walmart Sales Analytics", page_icon="W", layout="wide")


@st.cache_data
def load_csv(path: str) -> pd.DataFrame:
    frame = pd.read_csv(path)
    dataset_type = detect_dataset_type(frame)
    if dataset_type == "weekly":
        return prepare_weekly_sales_frame(frame)
    if dataset_type == "pos":
        return prepare_sales_frame(frame)
    raise ValueError("Unsupported Walmart CSV schema.")


@st.cache_data
def load_uploaded_csv(uploaded_file) -> tuple[str, pd.DataFrame]:
    frame = pd.read_csv(uploaded_file)
    dataset_type = detect_dataset_type(frame)
    if dataset_type == "weekly":
        return dataset_type, prepare_weekly_sales_frame(frame)
    if dataset_type == "pos":
        return dataset_type, prepare_sales_frame(frame)
    raise ValueError("Unsupported Walmart CSV schema.")


@st.cache_data
def load_weekly_from_database(connection_url: str) -> pd.DataFrame:
    query = """
        SELECT store, date, weekly_sales, holiday_flag, temperature, fuel_price, cpi, unemployment
        FROM weekly_store_sales
    """
    return prepare_weekly_sales_frame(pd.read_sql(query, make_engine(connection_url)))


@st.cache_data
def load_pos_from_database(connection_url: str) -> pd.DataFrame:
    query = """
        SELECT
            t.invoice_id,
            s.branch,
            s.city,
            c.customer_type,
            c.gender,
            p.product_line,
            ti.unit_price,
            ti.quantity,
            t.tax_5,
            t.total,
            t.date,
            t.time,
            t.payment,
            t.cogs,
            t.gross_margin_percentage,
            ti.gross_income,
            t.rating
        FROM transactions t
        JOIN stores s ON s.store_id = t.store_id
        JOIN customers c ON c.customer_id = t.customer_id
        JOIN transaction_items ti ON ti.transaction_id = t.transaction_id
        JOIN products p ON p.product_id = ti.product_id
    """
    return prepare_sales_frame(pd.read_sql(query, make_engine(connection_url)))


def metric_row(values: list[tuple[str, str]]) -> None:
    cols = st.columns(len(values))
    for col, (label, value) in zip(cols, values):
        col.metric(label, value)


def render_weekly_dashboard(sales: pd.DataFrame) -> None:
    st.sidebar.subheader("Weekly Sales Filters")
    stores = st.sidebar.multiselect(
        "Store",
        sorted(sales["store"].dropna().astype(int).unique()),
        default=sorted(sales["store"].dropna().astype(int).unique()),
    )
    holiday_periods = st.sidebar.multiselect(
        "Week type",
        sorted(sales["holiday_period"].dropna().unique()),
        default=sorted(sales["holiday_period"].dropna().unique()),
    )
    years = st.sidebar.multiselect(
        "Year",
        sorted(sales["year"].dropna().astype(int).unique()),
        default=sorted(sales["year"].dropna().astype(int).unique()),
    )
    sales_range = st.sidebar.slider(
        "Weekly sales range",
        min_value=float(sales["weekly_sales"].min()),
        max_value=float(sales["weekly_sales"].max()),
        value=(float(sales["weekly_sales"].min()), float(sales["weekly_sales"].max())),
    )

    filtered = sales[
        sales["store"].astype(int).isin(stores)
        & sales["holiday_period"].isin(holiday_periods)
        & sales["year"].astype(int).isin(years)
        & sales["weekly_sales"].between(sales_range[0], sales_range[1])
    ].copy()

    summary = weekly_kpi_summary(filtered)
    metric_row(
        [
            ("Total Sales", f"${summary['total_sales']:,.0f}"),
            ("Stores", f"{summary['stores']:,}"),
            ("Weeks", f"{summary['weeks']:,}"),
            ("Avg Weekly Sales", f"${summary['average_weekly_sales']:,.0f}"),
            ("Holiday Sales", f"${summary['holiday_sales']:,.0f}"),
            ("Regular Sales", f"${summary['regular_sales']:,.0f}"),
        ]
    )

    tab_overview, tab_stores, tab_economy, tab_forecast, tab_insights, tab_data = st.tabs(
        ["Overview", "Stores", "Economic Signals", "Forecast", "Insights", "Data"]
    )

    with tab_overview:
        weekly_trend = filtered.groupby("date", as_index=False).agg(sales=("weekly_sales", "sum"))
        monthly_trend = filtered.groupby("month", as_index=False).agg(sales=("weekly_sales", "sum"))
        holiday_sales = aggregate_weekly_sales(filtered, "holiday_period")

        left, right = st.columns((2, 1))
        with left:
            st.plotly_chart(
                px.line(weekly_trend, x="date", y="sales", markers=True, title="Weekly Sales Trend"),
                width="stretch",
            )
        with right:
            st.plotly_chart(
                px.bar(holiday_sales, x="holiday_period", y="sales", color="holiday_period", title="Holiday vs Regular Sales"),
                width="stretch",
            )
        st.plotly_chart(px.bar(monthly_trend, x="month", y="sales", title="Monthly Sales"), width="stretch")

    with tab_stores:
        store_sales = aggregate_weekly_sales(filtered, "store")
        col_a, col_b = st.columns(2)
        with col_a:
            st.plotly_chart(
                px.bar(store_sales.head(15), x="store", y="sales", title="Top Stores by Sales"),
                width="stretch",
            )
        with col_b:
            st.plotly_chart(
                px.scatter(
                    store_sales,
                    x="avg_weekly_sales",
                    y="weeks",
                    size="sales",
                    color="store",
                    title="Store Consistency and Scale",
                ),
                width="stretch",
            )
        st.dataframe(store_sales, width="stretch")

    with tab_economy:
        col_a, col_b = st.columns(2)
        with col_a:
            st.plotly_chart(
                px.scatter(
                    filtered,
                    x="fuel_price",
                    y="weekly_sales",
                    color="holiday_period",
                    title="Fuel Price vs Weekly Sales",
                ),
                width="stretch",
            )
        with col_b:
            st.plotly_chart(
                px.scatter(
                    filtered,
                    x="unemployment",
                    y="weekly_sales",
                    color="holiday_period",
                    title="Unemployment vs Weekly Sales",
                ),
                width="stretch",
            )

    with tab_forecast:
        forecast_periods = st.slider("Forecast weeks", min_value=4, max_value=16, value=8)
        forecast_window = st.slider("Moving average window", min_value=2, max_value=12, value=4)
        forecast = forecast_weekly_sales(filtered, periods=forecast_periods, window=forecast_window)
        st.plotly_chart(
            px.line(
                forecast,
                x="date",
                y="sales",
                color="series_type",
                markers=True,
                title="Weekly Sales Forecast using Moving Average",
            ),
            width="stretch",
        )
        latest_forecast = forecast.loc[forecast["series_type"] == "Forecast", "sales"]
        if not latest_forecast.empty:
            st.metric("Next Forecasted Weekly Sales", f"${latest_forecast.iloc[0]:,.0f}")
        st.caption(
            "This lightweight forecast uses the average of recent weekly sales. It is designed as an interpretable baseline model."
        )

    with tab_insights:
        st.subheader("Auto-Generated Insights")
        for insight in weekly_insights(filtered):
            st.write(f"- {insight}")

    with tab_data:
        st.dataframe(filtered.sort_values("date", ascending=False), width="stretch")


def render_pos_dashboard(sales: pd.DataFrame) -> None:
    st.sidebar.subheader("POS Filters")
    branches = st.sidebar.multiselect("Branch", sorted(sales["branch"].dropna().unique()), default=sorted(sales["branch"].dropna().unique()))
    product_lines = st.sidebar.multiselect(
        "Product line",
        sorted(sales["product_line"].dropna().unique()),
        default=sorted(sales["product_line"].dropna().unique()),
    )
    customer_types = st.sidebar.multiselect(
        "Customer type",
        sorted(sales["customer_type"].dropna().unique()),
        default=sorted(sales["customer_type"].dropna().unique()),
    )
    payments = st.sidebar.multiselect(
        "Payment",
        sorted(sales["payment"].dropna().unique()),
        default=sorted(sales["payment"].dropna().unique()),
    )
    rating_range = st.sidebar.slider(
        "Rating range",
        min_value=float(sales["rating"].min()),
        max_value=float(sales["rating"].max()),
        value=(float(sales["rating"].min()), float(sales["rating"].max())),
    )

    filtered = sales[
        sales["branch"].isin(branches)
        & sales["product_line"].isin(product_lines)
        & sales["customer_type"].isin(customer_types)
        & sales["payment"].isin(payments)
        & sales["rating"].between(rating_range[0], rating_range[1])
    ].copy()

    summary = kpi_summary(filtered)
    metric_row(
        [
            ("Revenue", f"${summary['revenue']:,.0f}"),
            ("Invoices", f"{summary['invoices']:,}"),
            ("Units Sold", f"{summary['quantity']:,}"),
            ("Gross Income", f"${summary['gross_income']:,.0f}"),
            ("Avg Order", f"${summary['average_order_value']:,.2f}"),
            ("Avg Rating", f"{summary['average_rating']:.1f}"),
        ]
    )

    tab_overview, tab_products, tab_customers, tab_operations, tab_data = st.tabs(
        ["Overview", "Products", "Customers", "Operations", "Data"]
    )

    with tab_overview:
        daily_sales = filtered.groupby("date", as_index=False).agg(revenue=("total", "sum"), invoices=("invoice_id", "nunique"))
        monthly_sales = filtered.groupby("month", as_index=False).agg(revenue=("total", "sum"))
        col_a, col_b = st.columns((2, 1))
        with col_a:
            st.plotly_chart(px.line(daily_sales, x="date", y="revenue", markers=True, title="Daily Revenue Trend"), width="stretch")
        with col_b:
            st.plotly_chart(px.bar(monthly_sales, x="month", y="revenue", title="Monthly Revenue"), width="stretch")

    with tab_products:
        product_sales = aggregate_sales(filtered, "product_line")
        st.plotly_chart(px.bar(product_sales, x="revenue", y="product_line", orientation="h", title="Product Line Revenue"), width="stretch")
        st.dataframe(product_sales, width="stretch")

    with tab_customers:
        col_a, col_b = st.columns(2)
        with col_a:
            st.plotly_chart(px.pie(aggregate_sales(filtered, "customer_type"), names="customer_type", values="revenue", title="Revenue by Customer Type"), width="stretch")
        with col_b:
            st.plotly_chart(px.bar(aggregate_sales(filtered, "gender"), x="gender", y="revenue", color="gender", title="Revenue by Gender"), width="stretch")

    with tab_operations:
        col_a, col_b = st.columns(2)
        with col_a:
            st.plotly_chart(px.bar(aggregate_sales(filtered, "payment"), x="payment", y="invoices", title="Payment Method Usage"), width="stretch")
        with col_b:
            hourly = filtered.groupby("hour", as_index=False).agg(revenue=("total", "sum"), invoices=("invoice_id", "nunique"))
            st.plotly_chart(px.line(hourly, x="hour", y="revenue", markers=True, title="Hourly Revenue Pattern"), width="stretch")

    with tab_data:
        st.dataframe(filtered.sort_values("date", ascending=False), width="stretch")


st.title("Walmart Sales Analytics Dashboard")

with st.sidebar:
    st.header("Data Source")
    source = st.radio("Choose source", ["Real weekly CSV", "Sample POS CSV", "Upload CSV", "Database"], index=0)
    dataset_type = "weekly"
    connection_url = ""

    if source == "Database":
        dataset_type = st.selectbox("Database dataset", ["weekly", "pos"])
        connection_url = st.text_input(
            "SQLAlchemy URL",
            placeholder="postgresql+psycopg2://user:password@localhost:5432/walmart_sales",
            type="password",
        )

try:
    if source == "Real weekly CSV":
        dataset_type = "weekly"
        sales_data = load_csv(str(RAW_DATA_PATH))
    elif source == "Sample POS CSV":
        dataset_type = "pos"
        sales_data = load_csv(str(SAMPLE_DATA_PATH))
    elif source == "Upload CSV":
        uploaded = st.sidebar.file_uploader("Upload Walmart CSV", type=["csv"])
        if uploaded is None:
            st.info("Upload a Walmart CSV to begin.")
            st.stop()
        dataset_type, sales_data = load_uploaded_csv(uploaded)
    elif connection_url:
        sales_data = load_weekly_from_database(connection_url) if dataset_type == "weekly" else load_pos_from_database(connection_url)
    else:
        st.info("Enter a PostgreSQL or MySQL SQLAlchemy connection URL to load database data.")
        st.stop()

    st.caption(f"Loaded `{dataset_type}` dataset with {len(sales_data):,} rows.")
    if dataset_type == "weekly":
        render_weekly_dashboard(sales_data)
    else:
        render_pos_dashboard(sales_data)
except Exception as exc:
    st.error(f"Unable to load dashboard data: {exc}")
