import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sb

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="📊 Stock Market Dashboard",
    page_icon="📈",
    layout="wide"
)

sb.set_style("whitegrid")

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    df = pd.read_csv("stock_hk.csv")
    df["Date"] = pd.to_datetime(df["Date"])
    return df

df = load_data()

# ---------------- SIDEBAR ----------------
st.sidebar.title("⚙ Dashboard Controls")

stock = st.sidebar.selectbox("📌 Select Stock", df["Stock"].unique())
price_col = st.sidebar.selectbox("💰 Price Type", ["Open", "High", "Low", "Close"])

ma20 = st.sidebar.checkbox("📈 20 Days Moving Average")
ma50 = st.sidebar.checkbox("📉 50 Days Moving Average")

stock_df = df[df["Stock"] == stock]

start_date, end_date = st.sidebar.date_input(
    "📅 Select Date Range",
    [stock_df.Date.min(), stock_df.Date.max()]
)

stock_df = stock_df[
    (stock_df.Date >= pd.to_datetime(start_date)) &
    (stock_df.Date <= pd.to_datetime(end_date))
]

# ---------------- KPI METRICS ----------------
latest = stock_df.iloc[-1]
prev = stock_df.iloc[-2] if len(stock_df) > 1 else latest

change = ((latest["Close"] - prev["Close"]) / prev["Close"]) * 100

st.title("📊 Stock Market Analysis Dashboard")

col1, col2, col3, col4 = st.columns(4)

col1.metric("📌 Latest Close", f"{latest['Close']:.2f}")
col2.metric("📈 Day High", f"{latest['High']:.2f}")
col3.metric("📉 Day Low", f"{latest['Low']:.2f}")
col4.metric("🔄 Change %", f"{change:.2f}%", 
            delta=f"{change:.2f}%")

# ---------------- PRICE CHART ----------------
st.subheader("📈 Price Trend")

fig, ax = plt.subplots(figsize=(14, 5))
sb.lineplot(data=stock_df, x="Date", y=price_col, label=price_col, ax=ax)

if ma20:
    stock_df["MA20"] = stock_df[price_col].rolling(20).mean()
    sb.lineplot(data=stock_df, x="Date", y="MA20", label="MA 20", ax=ax)

if ma50:
    stock_df["MA50"] = stock_df[price_col].rolling(50).mean()
    sb.lineplot(data=stock_df, x="Date", y="MA50", label="MA 50", ax=ax)

ax.set_xlabel("Date")
ax.set_ylabel("Price")
ax.legend()

st.pyplot(fig)

# ---------------- VOLUME CHART ----------------
st.subheader("📊 Volume Analysis")

fig2, ax2 = plt.subplots(figsize=(14, 4))
sb.barplot(data=stock_df, x="Date", y="Volume", ax=ax2)
ax2.set_xlabel("Date")
ax2.set_ylabel("Volume")
ax2.tick_params(axis='x', rotation=45)

st.pyplot(fig2)

# ---------------- DOWNLOAD ----------------
st.subheader("⬇ Download Data")

csv = stock_df.to_csv(index=False).encode("utf-8")
st.download_button(
    "📥 Download Filtered Data",
    csv,
    file_name=f"{stock}_data.csv",
    mime="text/csv"
)

# ---------------- RAW DATA ----------------
with st.expander("📄 View Raw Data"):
    st.dataframe(stock_df)
