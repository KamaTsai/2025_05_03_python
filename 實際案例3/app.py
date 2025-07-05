"""
主應用程式入口，提供命令列介面(CLI)功能。
"""
import pandas as pd
import argparse
import os

def read_input_file(file_path: str) -> pd.DataFrame:
    """根據副檔名自動讀取CSV或Excel檔案，並回傳DataFrame。"""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.csv':
        df = pd.read_csv(file_path)
    elif ext in ['.xls', '.xlsx']:
        df = pd.read_excel(file_path)
    else:
        raise ValueError('僅支援CSV或Excel檔案')
    return df

def process_to_excel(input_path: str, excel_path: str):
    """讀取CSV或Excel檔案，建立樞紐表，並輸出為Excel檔案。"""
    tips_df = read_input_file(input_path)
    tips_df.columns = ['總票價', '小費', '吸煙者', '日期', '時間', '大小']
    tips_df['小費比例'] = tips_df['小費'] / tips_df['總票價']
    grouped = tips_df.groupby(by=['吸煙者', '日期'])
    functions = [('數量', 'count'), ('平均', 'mean'), ('最大值', 'max')]
    tips_df3 = grouped[['小費', '總票價']].agg(functions)
    tips_df3.to_excel(excel_path)
    print(f"已將樞紐表輸出至 {excel_path}")

def main():
    """主程式進入點，解析命令列參數."""
    parser = argparse.ArgumentParser(description="CSV/Excel 轉樞紐表並輸出 Excel 檔案")
    parser.add_argument('--csv', help='輸入的CSV檔案路徑')
    parser.add_argument('--excel', help='輸入的Excel檔案路徑')
    parser.add_argument('--output', required=True, help='輸出的Excel檔案路徑')
    args = parser.parse_args()
    # 優先使用 --csv，其次 --excel
    input_path = args.csv if args.csv else args.excel
    if not input_path:
        parser.error('請指定 --csv 或 --excel 其中之一作為輸入檔案')
    process_to_excel(input_path, args.output)

if __name__ == "__main__":
    main()
