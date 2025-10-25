
# 🌍 International Rice Prices (Easy Fetch)

Fetch rice prices from **two international sources** with **no API keys**:

1. **Yahoo Finance — Rough Rice futures (ZR=F)** (daily)
2. **World Bank — Thai 5% broken (Pink Sheet)** (monthly)

## Deploy (Streamlit Cloud)
- Upload this repo.
- Main file path: `streamlit_app.py`
- Python: 3.11
- Click **Fetch latest data** in the app.

## Automate (GitHub Actions)
A daily workflow at `.github/workflows/daily.yml` saves CSVs to `data/` and commits them to the repo.

## Files
- `fetchers.py` — download functions (no keys)
- `model.py` — simple 30‑day forecast
- `streamlit_app.py` — UI
- `.github/workflows/daily.yml` — scheduler
- `requirements.txt`
