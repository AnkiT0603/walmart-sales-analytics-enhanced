import pandas as pd

from src.analytics import kpi_summary, prepare_sales_frame
from src.analytics import detect_dataset_type, forecast_weekly_sales, prepare_weekly_sales_frame, weekly_insights, weekly_kpi_summary
from src.etl import build_dimensions, build_facts


def sample_frame() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "invoice_id": "A-001",
                "branch": "A",
                "city": "Yangon",
                "customer_type": "Member",
                "gender": "Female",
                "product_line": "Food and beverages",
                "unit_price": 10,
                "quantity": 2,
                "tax_5": 1,
                "total": 21,
                "date": "2024-01-01",
                "time": "10:30:00",
                "payment": "Cash",
                "cogs": 20,
                "gross_margin_percentage": 4.7619,
                "gross_income": 1,
                "rating": 8.5,
            }
        ]
    )


def test_prepare_sales_frame_adds_time_fields():
    frame = prepare_sales_frame(sample_frame())
    assert frame.loc[0, "month"] == "2024-01"
    assert frame.loc[0, "weekday"] == "Monday"
    assert frame.loc[0, "hour"] == 10


def test_kpi_summary():
    frame = prepare_sales_frame(sample_frame())
    summary = kpi_summary(frame)
    assert summary["revenue"] == 21
    assert summary["invoices"] == 1
    assert summary["quantity"] == 2


def test_build_dimensions_and_facts():
    frame = prepare_sales_frame(sample_frame())
    dimensions = build_dimensions(frame)
    facts = build_facts(frame, dimensions)
    assert len(dimensions["stores"]) == 1
    assert len(facts["transactions"]) == 1
    assert facts["transaction_items"].loc[0, "product_id"] == 1


def test_prepare_weekly_sales_frame():
    frame = pd.DataFrame(
        [
            {
                "Store": 1,
                "Date": "05-02-2010",
                "Weekly_Sales": 1643690.9,
                "Holiday_Flag": 0,
                "Temperature": 42.31,
                "Fuel_Price": 2.572,
                "CPI": 211.0963582,
                "Unemployment": 8.106,
            }
        ]
    )
    assert detect_dataset_type(frame) == "weekly"
    prepared = prepare_weekly_sales_frame(frame)
    summary = weekly_kpi_summary(prepared)
    assert prepared.loc[0, "month"] == "2010-02"
    assert prepared.loc[0, "holiday_period"] == "Regular week"
    assert summary["total_sales"] == 1643690.9


def test_forecast_weekly_sales_adds_future_rows():
    frame = pd.DataFrame(
        [
            {
                "Store": 1,
                "Date": "05-02-2010",
                "Weekly_Sales": 100,
                "Holiday_Flag": 0,
                "Temperature": 42.31,
                "Fuel_Price": 2.572,
                "CPI": 211.0963582,
                "Unemployment": 8.106,
            },
            {
                "Store": 1,
                "Date": "12-02-2010",
                "Weekly_Sales": 120,
                "Holiday_Flag": 1,
                "Temperature": 38.51,
                "Fuel_Price": 2.548,
                "CPI": 211.2421698,
                "Unemployment": 8.106,
            },
        ]
    )
    prepared = prepare_weekly_sales_frame(frame)
    forecast = forecast_weekly_sales(prepared, periods=2, window=2)
    assert len(forecast[forecast["series_type"] == "Forecast"]) == 2
    assert forecast.loc[forecast["series_type"] == "Forecast", "sales"].iloc[0] == 110


def test_weekly_insights_returns_messages():
    frame = pd.DataFrame(
        [
            {
                "Store": 1,
                "Date": "05-02-2010",
                "Weekly_Sales": 100,
                "Holiday_Flag": 0,
                "Temperature": 42.31,
                "Fuel_Price": 2.572,
                "CPI": 211.0963582,
                "Unemployment": 8.106,
            }
        ]
    )
    prepared = prepare_weekly_sales_frame(frame)
    insights = weekly_insights(prepared)
    assert len(insights) == 4
    assert "Store 1" in insights[0]
