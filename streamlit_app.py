
import os
import streamlit as st, pandas as pd
from fetchers import fetch_yahoo_rough_rice, fetch_worldbank_pinksheet_rice
from model import simple_forecast

st.set_page_config(page_title="International Rice (Easy Fetch)", page_icon="🌍", layout="wide")
st.title("🌍 International Rice Prices (Easy Fetch)")

src = st.radio("Data source", ["Yahoo Finance — Rough Rice futures (daily)", "World Bank — Thai 5% broken (monthly)"], index=0)

if st.button("Fetch latest data"):
    if src.startswith("Yahoo"):
        path = fetch_yahoo_rough_rice("data/rough_rice_yahoo.csv")
    else:
        path = fetch_worldbank_pinksheet_rice("data/rice_wb_thai5.csv")
    st.success(f"Saved: {path}")

st.divider()

col1, col2 = st.columns([2,1])
with col1:
    f = "data/rough_rice_yahoo.csv" if src.startswith("Yahoo") else "data/rice_wb_thai5.csv"
    if os.path.exists(f):
        df = pd.read_csv(f)
        st.subheader("Latest data")
        st.dataframe(df.tail(30), use_container_width=True)
        st.download_button("Download CSV", data=df.to_csv(index=False).encode("utf-8"), file_name=os.path.basename(f), mime="text/csv")
        st.subheader("Forecast (30 days)")
        fore = simple_forecast(df, horizon_days=30)
        st.dataframe(fore.head(), use_container_width=True)
    else:
        st.info("Click 'Fetch latest data' to download the dataset.")

with col2:
    st.markdown("**Notes**")
    st.markdown("- Yahoo: symbol `ZR=F` (CBOT Rough Rice futures).")
    st.markdown("- World Bank: monthly Thai 5% broken export price (USD/mt).")
    st.caption("Both sources require no API keys.")

st.caption("You can schedule daily updates with the included GitHub Action.")
