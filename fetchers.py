
import io, os, re, datetime as dt
import pandas as pd, requests
import yfinance as yf

WB_XLSX = "https://thedocs.worldbank.org/en/doc/5d903e848db1d1b83e0ec8f744e55570-0350012021/related/CMO-Historical-Data-Monthly.xlsx"

def fetch_yahoo_rough_rice(out_csv="data/rough_rice_yahoo.csv", period="max", interval="1d"):
    """Fetch daily Rough Rice futures from Yahoo Finance (symbol ZR=F).
    Returns path to CSV with columns Date, Price.
    """
    os.makedirs(os.path.dirname(out_csv), exist_ok=True)
    t = yf.Ticker("ZR=F")
    df = t.history(period=period, interval=interval, auto_adjust=False)
    if df.empty:
        # fallback: download with yfinance.download
        df = yf.download("ZR=F", period=period, interval=interval)
    if df.empty:
        pd.DataFrame(columns=["Date","Price"]).to_csv(out_csv, index=False); return out_csv
    out = df[["Close"]].reset_index().rename(columns={"Date":"Date","Close":"Price"})
    out["Date"] = pd.to_datetime(out["Date"]).dt.date
    out.to_csv(out_csv, index=False)
    return out_csv

def fetch_worldbank_pinksheet_rice(out_csv="data/rice_wb_thai5.csv"):
    """Download World Bank CMO Historical Monthly Excel (no key), extract 'Rice, Thailand 5% broken' monthly series.
    Saves columns Date, Price (USD/mt).
    """
    os.makedirs(os.path.dirname(out_csv), exist_ok=True)
    r = requests.get(WB_XLSX, timeout=60)
    r.raise_for_status()
    xls = pd.ExcelFile(io.BytesIO(r.content))
    # The sheet name often contains "Monthly Prices" or similar; search for 'Monthly'
    sheet = [s for s in xls.sheet_names if "Monthly" in s or "monthly" in s]
    sheet = sheet[0] if sheet else xls.sheet_names[0]
    df = xls.parse(sheet, header=None)
    # Find the row containing 'Rice, Thailand, 5%'
    row_idx = None
    for i in range(min(200, len(df))):
        row = " ".join(str(x) for x in df.iloc[i].tolist())
        if re.search(r"Rice\s*\(Thailand\).*\(5%|5 %\).*broken", row, flags=re.I):
            row_idx = i; break
    if row_idx is None:
        pd.DataFrame(columns=["Date","Price"]).to_csv(out_csv, index=False); return out_csv
    # Find a header row with years
    header_row = None
    for j in range(row_idx-5, row_idx+5):
        if j < 0: continue
        vals = df.iloc[j].tolist()
        if any(str(v).strip().isdigit() and len(str(v))==4 for v in vals):
            header_row = j; break
    if header_row is None: header_row = row_idx-1 if row_idx>0 else row_idx
    wide = xls.parse(sheet, header=header_row)
    mask = wide.iloc[:,0].astype(str).str.contains("Rice", case=False, na=False) &            wide.iloc[:,0].astype(str).str.contains("Thailand", case=False, na=False) &            wide.iloc[:,0].astype(str).str.contains("5", na=False)
    series_row = wide[mask]
    if series_row.empty:
        pd.DataFrame(columns=["Date","Price"]).to_csv(out_csv, index=False); return out_csv
    series = series_row.squeeze()
    tidy = series.to_frame(name="Price").reset_index().rename(columns={"index":"Period"})
    def parse_period(x):
        s = str(x)
        m = re.match(r"(\d{4})[^\d]?(\d{1,2})$", s) or re.match(r"(\d{4})M(\d{1,2})", s) or re.match(r"(\d{4})-(\d{1,2})", s)
        if m:
            y, mth = int(m.group(1)), int(m.group(2))
            import datetime as _dt
            return _dt.date(y, mth, 1)
        try:
            d = pd.to_datetime(s, errors="raise")
            return d.date().replace(day=1)
        except Exception:
            return None
    tidy["Date"] = tidy["Period"].map(parse_period)
    tidy = tidy.dropna(subset=["Date"])
    tidy["Price"] = pd.to_numeric(tidy["Price"], errors="coerce")
    tidy = tidy.dropna(subset=["Price"]).sort_values("Date")[["Date","Price"]]
    tidy.to_csv(out_csv, index=False)
    return out_csv
