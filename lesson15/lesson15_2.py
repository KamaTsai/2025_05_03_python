import streamlit as st
import yfinance as yf
import os
import pandas as pd
from datetime import date
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib

# --- 核心資料處理邏輯 (從原腳本繼承並優化) ---

@st.cache_data(ttl=3600) # 快取資料，ttl=3600秒 (1小時) 後過期
def load_data():
    """
    一個整合性的函式，負責下載和處理股票資料。
    1. 智慧下載更新股票資料。
    2. 讀取最新的CSV檔並合併成一個DataFrame。
    3. 使用Streamlit快取來避免重複下載和處理。
    """
    # --- Part 1: 智慧下載 (原 download_data) ---
    data_dir = 'data'
    os.makedirs(data_dir, exist_ok=True)
    tickers = ['2330.TW', '2303.TW', '2454.TW', '2317.TW']

    for ticker in tickers:
        stock_code = ticker.split('.')[0]
        try:
            df = yf.download(ticker, start='2000-01-01', end=date.today(), auto_adjust=True, progress=False)
            if df.empty:
                continue

            last_trade_date = df.index.max().date()
            last_trade_date_str = last_trade_date.strftime('%Y-%m-%d')
            new_filename = f"{stock_code}_{last_trade_date_str}.csv"
            new_filepath = os.path.join(data_dir, new_filename)

            if os.path.exists(new_filepath):
                continue
            
            df.to_csv(new_filepath)

            for old_file in os.listdir(data_dir):
                if old_file.startswith(f"{stock_code}_") and old_file.endswith(".csv") and old_file != new_filename:
                    old_filepath = os.path.join(data_dir, old_file)
                    os.remove(old_filepath)
        except Exception as e:
            st.error(f"下載 {ticker} 資料時發生錯誤: {e}")
            continue

    # --- Part 2: 處理與合併 (原 process_and_combine_data) ---
    stock_map = {
        '2330': '台積電',
        '2303': '聯電',
        '2317': '鴻海',
        '2454': '聯發科'
    }
    
    all_close_prices = []

    for code, name in stock_map.items():
        try:
            files = [f for f in os.listdir(data_dir) if f.startswith(f"{code}_") and f.endswith(".csv")]
            if not files:
                continue
            
            latest_file = sorted(files, reverse=True)[0]
            filepath = os.path.join(data_dir, latest_file)

            # 使用 index_col=0 來讀取第一欄作為索引，使其更具備彈性，避免因CSV檔頭名稱不同而報錯
            df = pd.read_csv(filepath, index_col=0, parse_dates=True)
            df.index.name = 'Date' # 確保索引名稱統一為 'Date'
            df.rename(columns={'Close': name}, inplace=True)
            all_close_prices.append(df[[name]])
        except Exception as e:
            st.error(f"處理 {name} 資料時發生錯誤: {e}")
            continue

    if not all_close_prices:
        return None

    # --- Data Cleaning and Merging ---
    combined_df = pd.concat(all_close_prices, axis=1)
    
    # 1. 強制將索引轉換為 datetime 物件。
    #    errors='coerce' 會將任何無法解析的字串 (如 'Ticker' 或其他髒資料) 轉換為 NaT (Not a Time)。
    combined_df.index = pd.to_datetime(combined_df.index, errors='coerce')

    # 2. 移除索引為 NaT 的無效資料行。
    #    這能有效清除從CSV讀取到的、非日期的標頭或錯誤行。
    combined_df = combined_df[combined_df.index.notna()]
    
    # 3. 在清理完無效資料後，再對時間序列中的缺失值進行向前填充。
    combined_df.fillna(method='ffill', inplace=True)
    return combined_df

# --- Streamlit 介面設計 ---

def run_app():
    # 設定網頁標題和佈局
    st.set_page_config(page_title="台股股價儀表板", layout="wide")

    # 設定中文字體，以解決Matplotlib圖表中的中文顯示問題
    try:
        # 這裡假設使用者環境有 'Microsoft JhengHei' 字體
        matplotlib.rcParams['font.family'] = 'Microsoft JhengHei'
        matplotlib.rcParams['axes.unicode_minus'] = False # 正常顯示負號
    except:
        st.warning("未找到 'Microsoft JhengHei' 字體，熱圖中的中文可能無法正常顯示。")

    st.title("📈 台灣主要電子股股價儀表板")
    st.write("這是一個互動式儀表板，用於視覺化台積電、聯電、鴻海和聯發科的歷史股價。")

    # 載入資料，使用 spinner 提示使用者
    with st.spinner('正在更新與載入最新股價資料...'):
        all_data = load_data()

    if all_data is None or all_data.empty:
        st.error("無法載入任何資料，請檢查網路連線或資料來源。")
        return

    # --- 側邊欄控制項 ---
    st.sidebar.header("⚙️ 控制面板")

    # 股票選擇器
    stock_options = list(all_data.columns)
    selected_stocks = st.sidebar.multiselect(
        "選擇股票 (可複選):",
        options=stock_options,
        default=stock_options[0] # 預設選取第一支股票
    )

    # 日期範圍選擇器
    min_date = all_data.index.min().date()
    max_date = all_data.index.max().date()
    start_date, end_date = st.sidebar.date_input(
        "選擇日期範圍:",
        value=(max_date.replace(year=max_date.year - 1), max_date), # 預設顯示最近一年
        min_value=min_date,
        max_value=max_date
    )

    # --- 主畫面顯示 ---
    if not selected_stocks:
        st.warning("請從左方側邊欄選擇至少一支股票。")
        return

    if start_date > end_date:
        st.error("錯誤：開始日期不能晚於結束日期。")
        return

    # 根據使用者選擇過濾資料
    filtered_data = all_data.loc[start_date:end_date, selected_stocks]

    # 1. 股價走勢圖
    st.subheader("收盤價走勢圖")
    st.line_chart(filtered_data)

    # 2. 相關性熱圖 (當選擇多於一檔股票時顯示)
    if len(selected_stocks) > 1:
        st.subheader("股價相關性熱圖")
        correlation_matrix = filtered_data.corr()
        
        fig, ax = plt.subplots()
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f", ax=ax)
        st.pyplot(fig)

    # 3. 數據表格
    st.subheader("詳細數據")
    st.dataframe(filtered_data.sort_index(ascending=False))


if __name__ == "__main__":
    run_app()