
import pandas as pd, numpy as np
from statsmodels.tsa.statespace.sarimax import SARIMAX

def simple_forecast(date_price_df: pd.DataFrame, horizon_days=30):
    df = date_price_df.copy()
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date").set_index("Date")
    s = df["Price"].astype(float).asfreq("D").ffill()
    if len(s) < 20:
        last = s.iloc[-1] if len(s) else 0.0
        idx = pd.date_range(s.index.max() if len(s) else pd.Timestamp.today(), periods=horizon_days, freq="D")
        return pd.DataFrame({"date": idx, "forecast": last})
    m = SARIMAX(s, order=(1,1,1), seasonal_order=(0,1,1,7), enforce_stationarity=False, enforce_invertibility=False).fit(disp=False)
    f = m.get_forecast(steps=horizon_days)
    out = f.predicted_mean.rename("forecast").to_frame()
    out.index.name = "date"
    return out.reset_index()
