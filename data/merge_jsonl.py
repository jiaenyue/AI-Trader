import json
import os
import glob

def merge_price_files():
    """
    合并所有以 "daily_prices_" 开头的 JSON 文件到一个名为 "merged.jsonl" 的 JSONL 文件中。

    该函数会执行以下操作：
    1. 查找当前目录下所有符合 "daily_prices_*.json" 模式的文件。
    2. 逐个读取这些文件。
    3. 对每个文件的数据进行处理：
        - 将 "1. open" 重命名为 "1. buy price"。
        - 将 "4. close" 重命名为 "4. sell price"。
        - 对于最新一个交易日的数据，只保留 "1. buy price"。
    4. 将处理后的数据作为单行 JSON 写入到 "merged.jsonl" 文件中。
    """
    all_nasdaq_100_symbols = [
        "NVDA", "MSFT", "AAPL", "GOOG", "GOOGL", "AMZN", "META", "AVGO", "TSLA",
        "NFLX", "PLTR", "COST", "ASML", "AMD", "CSCO", "AZN", "TMUS", "MU", "LIN",
        "PEP", "SHOP", "APP", "INTU", "AMAT", "LRCX", "PDD", "QCOM", "ARM", "INTC",
        "BKNG", "AMGN", "TXN", "ISRG", "GILD", "KLAC", "PANW", "ADBE", "HON",
        "CRWD", "CEG", "ADI", "ADP", "DASH", "CMCSA", "VRTX", "MELI", "SBUX",
        "CDNS", "ORLY", "SNPS", "MSTR", "MDLZ", "ABNB", "MRVL", "CTAS", "TRI",
        "MAR", "MNST", "CSX", "ADSK", "PYPL", "FTNT", "AEP", "WDAY", "REGN", "ROP",
        "NXPI", "DDOG", "AXON", "ROST", "IDXX", "EA", "PCAR", "FAST", "EXC", "TTWO",
        "XEL", "ZS", "PAYX", "WBD", "BKR", "CPRT", "CCEP", "FANG", "TEAM", "CHTR",
        "KDP", "MCHP", "GEHC", "VRSK", "CTSH", "CSGP", "KHC", "ODFL", "DXCM", "TTD",
        "ON", "BIIB", "LULU", "CDW", "GFS"
    ]

    current_dir = os.path.dirname(__file__)
    pattern = os.path.join(current_dir, 'daily_prices_*.json')
    files = sorted(glob.glob(pattern))
    output_file = os.path.join(current_dir, 'merged.jsonl')

    with open(output_file, 'w', encoding='utf-8') as fout:
        for fp in files:
            basename = os.path.basename(fp)
            # 仅处理包含纳斯达克100成分股代码的文件
            if not any(symbol in basename for symbol in all_nasdaq_100_symbols):
                continue

            with open(fp, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    print(f"警告: 无法解析JSON文件: {fp}")
                    continue

            try:
                # 查找时间序列数据
                series = next((v for k, v in data.items() if k.startswith("Time Series")), None)

                if isinstance(series, dict) and series:
                    # 重命名键
                    for date, bar in series.items():
                        if isinstance(bar, dict):
                            if "1. open" in bar:
                                bar["1. buy price"] = bar.pop("1. open")
                            if "4. close" in bar:
                                bar["4. sell price"] = bar.pop("4. close")

                    # 只保留最新日期的买入价
                    latest_date = max(series.keys())
                    latest_bar = series.get(latest_date, {})
                    if isinstance(latest_bar, dict):
                        buy_val = latest_bar.get("1. buy price")
                        series[latest_date] = {"1. buy price": buy_val} if buy_val is not None else {}

                # 更新元数据信息
                meta = data.get("Meta Data", {})
                if isinstance(meta, dict):
                    meta["1. Information"] = "Daily Prices (buy price, high, low, sell price) and Volumes"
            except Exception as e:
                print(f"处理文件 {fp} 时发生错误: {e}")

            fout.write(json.dumps(data, ensure_ascii=False) + "\n")

    print(f"已成功将 {len(files)} 个文件合并到 {output_file}")


if __name__ == "__main__":
    merge_price_files()
