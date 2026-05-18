from __future__ import annotations

import csv
from datetime import date, timedelta
from pathlib import Path
import random

from src.config import SAMPLE_DATA_PATH


def generate_sample_sales(rows: int = 1200, output_path: Path = SAMPLE_DATA_PATH) -> Path:
    random.seed(42)

    branches = [("A", "Yangon"), ("B", "Mandalay"), ("C", "Naypyitaw")]
    customer_types = ["Member", "Normal"]
    genders = ["Female", "Male"]
    product_lines = [
        "Electronic accessories",
        "Fashion accessories",
        "Food and beverages",
        "Health and beauty",
        "Home and lifestyle",
        "Sports and travel",
    ]
    payments = ["Cash", "Credit card", "Ewallet"]
    start_date = date(2024, 1, 1)
    dates = [start_date + timedelta(days=offset) for offset in range(366)]

    records = []
    for index in range(rows):
        branch, city = random.choice(branches)
        product_line = random.choice(product_lines)
        unit_price = round(random.uniform(8, 100), 2)
        quantity = random.randint(1, 10)
        cogs = round(unit_price * quantity, 2)
        tax = round(cogs * 0.05, 2)
        total = round(cogs + tax, 2)
        sale_date = random.choice(dates)
        sale_time = f"{random.randint(9, 21):02d}:{random.choice([0, 5, 10, 15, 20, 30, 45, 50]):02d}:00"
        gross_income = tax
        records.append(
            {
                "invoice_id": f"{branch}-{sale_date.strftime('%m%d')}-{index + 1:05d}",
                "branch": branch,
                "city": city,
                "customer_type": random.choice(customer_types),
                "gender": random.choice(genders),
                "product_line": product_line,
                "unit_price": unit_price,
                "quantity": quantity,
                "tax_5": tax,
                "total": total,
                "date": sale_date.strftime("%Y-%m-%d"),
                "time": sale_time,
                "payment": random.choice(payments),
                "cogs": cogs,
                "gross_margin_percentage": 4.7619,
                "gross_income": gross_income,
                "rating": round(random.uniform(4, 10), 1),
            }
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(records[0].keys()))
        writer.writeheader()
        writer.writerows(records)
    return output_path


if __name__ == "__main__":
    path = generate_sample_sales()
    print(f"Generated {path}")
