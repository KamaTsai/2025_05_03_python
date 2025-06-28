import yfinance as yf
import datetime
import os
import glob
import pandas as pd

# --- 設定區 ---
# 將設定值統一放在開頭，方便未來修改
DATA_DIR = 'data'
STOCKS = ['2330.TW', '2303.TW', '2454.TW', '2317.TW']
START_DATE = '2000-01-01'
# 新增需求：股票代碼與中文名稱的對應
STOCK_MAP = {
    '2330': '台積電',
    '2317': '鴻海',
    '2303': '聯電',
    '2454': '聯發科'
}

def download_data():
    """
    下載指定股票的歷史資料，並依據執行日期管理檔案。

    功能：
    1. 下載 yfinance 的多檔股票資料。
    2. 自動建立儲存資料的資料夾 (預設為 'data')。
    3. 儲存的 CSV 檔名包含股票代碼與執行日期 (例: 2330_2024-07-26.csv)。
    4. 每次執行時，會自動刪除該股票對應的舊日期檔案。
    5. 如果當天的檔案已存在，則跳過下載。
    6. 處理下載失敗或無資料的例外情況。
    """
    # 確保資料夾存在，如果不存在則建立
    # exist_ok=True 讓程式在資料夾已存在時不會報錯
    os.makedirs(DATA_DIR, exist_ok=True)

    # 取得當前日期作為資料結束日期
    today = datetime.date.today()

    for stock_symbol in STOCKS:
        stock_code = stock_symbol.split('.')[0]
        
        # 根據需求 #3，建立包含執行日期的檔案名稱
        new_file_name = f"{DATA_DIR}/{stock_code}_{today.strftime('%Y-%m-%d')}.csv"

        # 根據需求 #4，刪除此股票的舊檔案
        # 使用 glob 尋找所有符合 '代碼_*.csv' 格式的檔案
        old_files = glob.glob(f"{DATA_DIR}/{stock_code}_*.csv")
        for old_file in old_files:
            if old_file != new_file_name:
                try:
                    os.remove(old_file)
                    print(f"已刪除舊檔案: {old_file}")
                except OSError as e:
                    print(f"刪除檔案 {old_file} 失敗: {e}")

        # 根據需求 #5，如果今日檔案已存在，則跳過
        if os.path.exists(new_file_name):
            print(f"今日檔案 {new_file_name} 已存在，跳過下載。")
            continue

        # 執行下載
        print(f"開始下載 {stock_symbol} 資料...")
        try:
            # yfinance 的 end 參數可以接受 datetime 物件
            data = yf.download(stock_symbol, start=START_DATE, end=today)
            
            if data.empty:
                print(f"警告：無法下載 {stock_symbol} 的資料，可能是代碼錯誤或該日期範圍無資料。")
            else:
                data.to_csv(new_file_name)
                print(f"已成功下載並儲存至 {new_file_name}")
        except Exception as e:
            print(f"下載 {stock_symbol} 時發生錯誤: {e}")

def combine_data():
    """
    讀取下載的 CSV 檔案，將各股的收盤價合併成一個 DataFrame。
    """
    today = datetime.date.today()
    all_closes = []

    print("\n--- 開始合併收盤價資料 ---")
    for stock_symbol in STOCKS:
        stock_code = stock_symbol.split('.')[0]
        file_path = f"{DATA_DIR}/{stock_code}_{today.strftime('%Y-%m-%d')}.csv"

        if os.path.exists(file_path):
            # 修正：使用 index_col=0 來讀取 CSV。
            # 錯誤 'ValueError: 'Date' is not in list' 表示 'Date' 欄位未找到。
            # yfinance 儲存的 CSV 中，日期通常是第一欄(索引)，但欄位名稱可能不固定。
            # 使用 index_col=0 更穩健，它會直接將第一欄作為索引。
            df = pd.read_csv(file_path, index_col=0, parse_dates=True)
            df.index.name = 'Date'  # 確保索引名稱統一為 'Date'
            
            # 檢查 STOCK_MAP 中是否存在該代碼
            if stock_code in STOCK_MAP:
                # 取得收盤價，並根據 STOCK_MAP 重新命名
                close_series = df[['Close']].rename(columns={'Close': STOCK_MAP[stock_code]})
                all_closes.append(close_series)
            else:
                print(f"警告：在 STOCK_MAP 中找不到代碼 {stock_code} 的對應名稱。")
        else:
            print(f"警告：找不到檔案 {file_path}，無法合併資料。")

    if not all_closes:
        print("沒有任何資料可供合併。")
        return None

    # 使用 concat 將所有 Series 合併成一個 DataFrame
    # axis=1 表示將 Series 作為新的欄位進行水平合併
    combined_df = pd.concat(all_closes, axis=1)
    
    # 移除所有值都是 NaN 的列 (例如假日)，確保資料乾淨
    combined_df.dropna(how='all', inplace=True)
    
    return combined_df

def main():
    """主執行函式"""
    download_data()
    
    combined_data = combine_data()
    if combined_data is not None:
        print("\n--- 合併後的資料 (顯示最後5筆) ---")
        print(combined_data.tail())

if __name__ == "__main__":
    main()