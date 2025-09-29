# 投資助手 Web 版 (Streamlit + Plotly Interactive)
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

# --------- 全域參數 ---------
risk_free_rate = 0

# --------- 工具函式 ---------
def format_ticker(raw: str, market: str) -> str:
    raw = raw.strip().upper()
    if market == "美國":
        return raw
    return raw + {"台灣": ".TW", "日本": ".T", "英國": ".L"}.get(market, "")

def flatten(df: pd.DataFrame) -> pd.DataFrame:
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df

def fetch_price_and_metrics(ticker: str, start_date=None, end_date=None):
    raw_df = yf.download(ticker, period="max", progress=False, auto_adjust=False)
    df = flatten(raw_df)
    if df.empty or "Adj Close" not in df.columns:
        raise ValueError("抓不到資料或缺少 Adjusted Close 欄位")
    df = df.reset_index()

    if start_date:
        sd = pd.to_datetime(start_date)
        df = df[df["Date"] >= sd]
    if end_date:
        ed = pd.to_datetime(end_date)
        df = df[df["Date"] <= ed]

    if df.empty:
        raise ValueError("指定期間內無成交資料")

    df["Return"] = df["Adj Close"].pct_change()
    df.dropna(subset=["Return"], inplace=True)
    df["CumReturn"] = (1 + df["Return"]).cumprod() - 1

    t0, t1 = df["Date"].iloc[0], df["Date"].iloc[-1]
    years = (t1 - t0).days / 365.25
    cagr = (df["Adj Close"].iloc[-1] / df["Adj Close"].iloc[0]) ** (1/years) - 1
    std_annual = df["Return"].std() * np.sqrt(252)
    sharpe = (cagr - risk_free_rate) / std_annual if std_annual else np.nan

    df["Downside"] = df["Return"].clip(upper=0)
    d_std = df["Downside"].std() * np.sqrt(252)
    sortino = (cagr - risk_free_rate) / d_std if d_std else np.nan

    metrics = {
        "start": t0.date(),
        "end": t1.date(),
        "years": years,
        "cum": df["CumReturn"].iloc[-1] * 100,
        "ann": cagr * 100,
        "std": std_annual * 100,
        "sharpe": sharpe,
        "sortino": sortino
    }
    return df, metrics

# --------- Streamlit UI ---------
st.set_page_config(page_title="投資助手", layout="wide")

st.title("📈 投資助手 ")

menu = st.sidebar.radio("功能選單", ["查詢股票資料", "存多少錢可能退休？"])

# --- 股票查詢 ---
if menu == "查詢股票資料":
    st.header("🔎 股票查詢")
    col1, col2 = st.columns(2)

    with col1:
        ticker_raw = st.text_input("股票代號", "AAPL")
        market = st.selectbox("市場", ["美國", "台灣", "日本", "英國"])
        start_date = st.text_input("開始日期 (YYYY-MM-DD)", "")
        end_date = st.text_input("結束日期 (YYYY-MM-DD)", "")

    if st.button("查詢股票資料"):
        ticker = format_ticker(ticker_raw, market)
        try:
            df, m = fetch_price_and_metrics(
                ticker,
                start_date if start_date else None,
                end_date if end_date else None
            )

            # 分頁
            tab1, tab2 = st.tabs(["📊 圖表", "📋 資料表"])

            with tab1:
                fig = px.line(
                    df,
                    x="Date",
                    y=df["CumReturn"] * 100,
                    title=f"{ticker} Cumulative Return (%)",
                    labels={"Date": "Date", "y": "Cumulative Return (%)"},
                    template="plotly_white"
                )
                st.plotly_chart(fig, use_container_width=True)

                st.subheader("績效指標")
                st.text(
                    f"股票：{ticker}\n"
                    f"查詢期間：{m['start']} → {m['end']} ({m['years']:.2f} 年)\n"
                    f"累積報酬率：{m['cum']:.2f}%\n"
                    f"年化報酬率：{m['ann']:.2f}%\n"
                    f"年化標準差：{m['std']:.2f}%\n"
                    f"Sharpe 比率：{m['sharpe']:.2f}\n"
                    f"Sortino 比率：{m['sortino']:.2f}"
                )

            with tab2:
                st.dataframe(df, use_container_width=True)

                # 下載 CSV
                csv = df.to_csv(index=False).encode("utf-8-sig")
                st.download_button(
                    label="⬇️ 下載資料表 (CSV)",
                    data=csv,
                    file_name=f"{ticker}_data.csv",
                    mime="text/csv"
                )

        except Exception as e:
            st.error(f"下載失敗: {e}")

# --- 退休試算 ---
elif menu == "存多少錢可能退休？":
    st.header("💰 退休試算")

    col1, col2 = st.columns(2)
    with col1:
        expense = st.number_input("年支出 (元)", min_value=0, value=500000, step=10000)
        ticker_raw = st.text_input("股票代號", "AAPL")
        market = st.selectbox("市場", ["美國", "台灣", "日本", "英國"])
        infl = st.number_input("預估通膨率 (%)", value=2.0, step=0.1)
        start_date = st.text_input("開始日期 (YYYY-MM-DD)", "")
        end_date = st.text_input("結束日期 (YYYY-MM-DD)", "")

    if st.button("計算退休金"):
        ticker = format_ticker(ticker_raw, market)
        try:
            df, m = fetch_price_and_metrics(
                ticker,
                start_date if start_date else None,
                end_date if end_date else None
            )

            real_withdraw = (m["ann"] / 100) - (infl / 100)
            if real_withdraw <= 0:
                st.warning("⚠ 年化報酬不足以支付通膨率")
            else:
                need_capital = expense / real_withdraw

                tab1, tab2 = st.tabs(["📊 圖表", "📋 資料表"])

                with tab1:
                    fig = px.line(
                        df,
                        x="Date",
                        y="Adj Close",
                        title=f"{ticker} Adjusted Close Price",
                        labels={"Date": "Date", "Adj Close": "Price"},
                        template="plotly_white"
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    st.subheader("計算結果")
                    st.text(
                        f"股票：{ticker}\n"
                        f"查詢期間：{m['start']} → {m['end']} ({m['years']:.2f} 年)\n"
                        f"年化報酬率：{m['ann']:.2f}%\n"
                        f"預估通膨：{infl:.2f}%\n"
                        f"安全提領率：{real_withdraw * 100:.2f}%\n"
                        f"年支出：{expense:,.0f} 元\n"
                        f"所需退休資產：約 {need_capital:,.0f} 元"
                    )

                with tab2:
                    st.dataframe(df, use_container_width=True)

                    # 下載 CSV
                    csv = df.to_csv(index=False).encode("utf-8-sig")
                    st.download_button(
                        label="⬇️ 下載資料表 (CSV)",
                        data=csv,
                        file_name=f"{ticker}_data.csv",
                        mime="text/csv"
                    )

        except Exception as e:
            st.error(f"下載失敗: {e}")
