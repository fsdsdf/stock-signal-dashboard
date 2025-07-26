import streamlit as st
import pandas as pd
import yfinance as yf
import datetime
import pytz
from streamlit_autorefresh import st_autorefresh

# 🔁 Auto-refresh every 60s
st_autorefresh(interval=60 * 1000, key="data_refresh")

# Stocks to scan
stock_list = [
    "RELIANCE.NS", "TCS.NS", "INFY.NS", "ACC.NS", "ADANIENT.NS",
    "AMBUJACEM.NS", "APOLLOHOSP.NS", "JSWSTEEL.NS", "JINDALSTEL.NS",
    "CHOLAFIN.NS", "BHARATFORG.NS", "WOCKPHARMA.NS"
]

st.set_page_config(page_title="📊 Stock Signal Dashboard", layout="wide")
st.title("📊 Stock Signal Dashboard (Live 5-min Monitor)")
st.caption("Green candle + volume > previous → WATCHING. Falls below open → SELL.")

# Search and filter UI
search_input = st.text_input("🔍 Search stock (partial name):", "")
filter_option = st.selectbox("📂 Filter signal type:", ["All", "WATCHING", "SELL"])

tz = pytz.timezone("Asia/Kolkata")
now = datetime.datetime.now(tz)

results = []

# Core logic loop
for symbol in stock_list:
    try:
        df = yf.download(symbol, interval="5m", period="5d", progress=False)
        if len(df) < 2:
            continue

        latest = df.iloc[-1]
        prev = df.iloc[-2]

        if latest["Close"] > latest["Open"] and latest["Volume"] > prev["Volume"]:
            live_price = yf.Ticker(symbol).info['regularMarketPrice']
            signal = "WATCHING"
            if live_price < latest["Open"]:
                signal = "SELL"

            results.append({
                "Stock": symbol,
                "Signal": signal,
                "Candle Open": round(latest["Open"], 2),
                "Live Price": round(live_price, 2),
                "Volume": int(latest["Volume"]),
                "Prev Volume": int(prev["Volume"]),
                "Last Checked": now.strftime('%Y-%m-%d %H:%M:%S')
            })

    except Exception as e:
        st.warning(f"⚠️ Error loading {symbol}: {e}")

# Show table if results found
if results:
    df_result = pd.DataFrame(results)

    # 🔍 Apply search filter
    if search_input:
        df_result = df_result[df_result["Stock"].str.contains(search_input.upper())]

    # 📂 Apply signal filter
    if filter_option != "All":
        df_result = df_result[df_result["Signal"] == filter_option]

    # 📊 Sortable table
    st.dataframe(df_result, use_container_width=True)

    # 📤 Export CSV
    csv = df_result.to_csv(index=False).encode('utf-8')
    st.download_button("⬇️ Download CSV", data=csv, file_name="stock_signals.csv", mime="text/csv")

else:
    st.info("No signals matching the logic found yet.")

st.caption("⏱ Last updated: " + now.strftime('%Y-%m-%d %H:%M:%S'))
