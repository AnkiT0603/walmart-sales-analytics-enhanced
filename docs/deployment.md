# Streamlit Deployment Guide

Use Streamlit Community Cloud to deploy this project from GitHub.

## Steps

1. Push the latest project code to GitHub.
2. Go to [Streamlit Community Cloud](https://streamlit.io/cloud).
3. Click **New app**.
4. Select this repository:

```text
AnkiT0603/Walmart-Sales-Analytics-Dashboard-with-SQL
```

5. Set the main file path:

```text
app.py
```

6. Deploy the app.
7. Copy the live URL and add it to the top of `README.md`.

## Optional Database Secrets

If you connect the dashboard to PostgreSQL or MySQL, add the connection string in Streamlit secrets instead of committing it to GitHub.

Example `.streamlit/secrets.toml` for local use:

```toml
DATABASE_URL = "postgresql+psycopg2://user:password@localhost:5432/walmart_sales"
```

Do not commit real database passwords.

