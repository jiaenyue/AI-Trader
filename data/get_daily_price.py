import requests
import os
from dotenv import load_dotenv
import json
import time

load_dotenv()

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

def get_daily_price(symbol: str):
    """
    从 Alpha Vantage API 获取指定股票的每日时间序列数据，并将其保存为 JSON 文件。

    Args:
        symbol (str): 要获取数据的股票代码。
    """
    FUNCTION = "TIME_SERIES_DAILY"
    OUTPUTSIZE = 'compact'
    APIKEY = os.getenv("ALPHAADVANTAGE_API_KEY")
    if not APIKEY:
        raise ValueError("ALPHAADVANTAGE_API_KEY 环境变量未设置。")

    url = f'https://www.alphavantage.co/query?function={FUNCTION}&symbol={symbol}&outputsize={OUTPUTSIZE}&apikey={APIKEY}'

    try:
        r = requests.get(url)
        r.raise_for_status()  # 如果请求失败则引发 HTTPError
        data = r.json()

        if 'Note' in data or 'Information' in data:
            print(f"获取 {symbol} 数据时收到API限制或信息提示: {data}")
            return

        if "Error Message" in data:
            print(f"获取 {symbol} 数据时出错: {data['Error Message']}")
            return

        # 保存数据到文件
        filename = f'./daily_prices_{symbol}.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"已成功为 {symbol} 保存数据到 {filename}")

        if symbol == "QQQ":
            # 为 QQQ 创建一个额外的副本，用于特殊处理
            with open(f'./Adaily_prices_{symbol}.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

    except requests.exceptions.RequestException as e:
        print(f"请求 {symbol} 数据时发生网络错误: {e}")
    except json.JSONDecodeError:
        print(f"无法解析 {symbol} 的JSON响应。")
    except Exception as e:
        print(f"处理 {symbol} 时发生未知错误: {e}")


if __name__ == "__main__":
    # 确保 ALPHAADVANTAGE_API_KEY 已设置
    if not os.getenv("ALPHAADVANTAGE_API_KEY"):
        print("错误: 请在 .env 文件中或作为环境变量设置 ALPHAADVANTAGE_API_KEY。")
    else:
        # 依次获取所有纳斯达克100指数成分股的数据
        for i, symbol in enumerate(all_nasdaq_100_symbols):
            print(f"正在获取 {symbol} 的数据 ({i+1}/{len(all_nasdaq_100_symbols)})...")
            get_daily_price(symbol)
            # Alpha Vantage 的免费API有速率限制（例如，每分钟5次调用），因此在请求之间添加延迟
            time.sleep(15)  # 暂停15秒

        # 单独获取 QQQ 的数据
        print("正在获取 QQQ 的数据...")
        get_daily_price("QQQ")
        print("所有数据获取完成。")
