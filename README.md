# Investment Assistant

一個投資助手應用程式，提供 **股票績效查詢** 以及 **退休試算** 功能。  
最初修課時為小組以 `tkinter` 製作桌面版，後續我自己改寫為 **Streamlit Web App** 部署至雲端。

---

## Demo

[點此打開應用程式](https://investmentassistant-6dyzzhzmkkxjhwar7qryhd.streamlit.app/)

---

## 專案結構

- `Group16.Final.py`  
  - 期末課程專案，使用 **Tkinter** 製作的桌面版投資助手。  
  - 功能包含股票查詢、退休試算、音樂播放（僅桌面版）。  

- `InvestmentHelper.py`  
  - 改寫後的 **Streamlit Web 版本**，可於瀏覽器操作。  
  - 移除音樂功能，保留股票查詢與退休試算功能。  
  - 目前部署於 Streamlit Cloud。  

---

## 功能特色

- **股票查詢**  
  - 股票代號輸入（支援美國、台灣、日本、英國市場）  
  - 自訂查詢期間  
  - 輸出績效指標：  
    - 累積報酬率  
    - 年化報酬率 (CAGR)  
    - 年化標準差 (Volatility)  
    - Sharpe Ratio  
    - Sortino Ratio  
  - 互動式股價報酬率圖表 (Plotly)  
  - 原始資料表格 & CSV 下載  

- **退休試算**  
  - 輸入年支出、通膨率、投資標的  
  - 計算安全提領率 (Safe Withdrawal Rate)  
  - 推估所需退休資產金額  
  - 互動式股價走勢圖 (Plotly)  
  - 原始資料表格 & CSV 下載  

---
