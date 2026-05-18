# Raw Dataset

This folder contains the bundled Walmart weekly sales dataset sample used by the dashboard.

Main dataset file:

```text
data/raw/walmart_real_sales.csv
```

The bundled CSV is a representative multi-store sample from the public Walmart weekly sales dataset. It covers all 45 stores so store-ranking and comparison dashboards work meaningfully.

To refresh it with the full 6,435-row dataset, run:

```bash
python -m src.download_dataset
```
