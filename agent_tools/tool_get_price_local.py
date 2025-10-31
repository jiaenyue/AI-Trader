from pathlib import Path
import json
from datetime import datetime
from typing import Dict, Any
from fastmcp import FastMCP
import os
from dotenv import load_dotenv
load_dotenv()

mcp = FastMCP("LocalPrices")
from tools.general_tools import get_config_value

def _workspace_data_path(filename: str) -> Path:
    """
    获取工作区数据文件的路径。

    Args:
        filename (str): 数据文件名。

    Returns:
        Path: 数据文件的完整路径。
    """
    base_dir = Path(__file__).resolve().parents[1]
    return base_dir / "data" / filename


def _validate_date(date_str: str) -> None:
    """
    验证日期字符串是否为 "YYYY-MM-DD" 格式。

    Args:
        date_str (str): 要验证的日期字符串。

    Raises:
        ValueError: 如果日期格式不正确。
    """
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError as exc:
        raise ValueError("日期必须是 YYYY-MM-DD 格式") from exc


@mcp.tool()
def get_price_local(symbol: str, date: str) -> Dict[str, Any]:
    """
    读取指定股票和日期的 OHLCV (开盘价, 最高价, 最低价, 收盘价, 交易量) 数据。
    用于获取指定股票的历史信息。

    Args:
        symbol (str): 股票代码，例如 'IBM' 或 '600243.SHH'。
        date (str): 'YYYY-MM-DD' 格式的日期。

    Returns:
        Dict[str, Any]: 包含股票代码、日期和 ohlcv 数据的字典。如果出错则包含错误信息。
    """
    filename = "merged.jsonl"
    try:
        _validate_date(date)
    except ValueError as e:
        return {"error": str(e), "symbol": symbol, "date": date}

    data_path = _workspace_data_path(filename)
    if not data_path.exists():
        return {"error": f"数据文件未找到: {data_path}", "symbol": symbol, "date": date}

    with data_path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            doc = json.loads(line)
            meta = doc.get("Meta Data", {})
            if meta.get("2. Symbol") != symbol:
                continue
            series = doc.get("Time Series (Daily)", {})
            day = series.get(date)
            if day is None:
                sample_dates = sorted(series.keys(), reverse=True)[:5]
                return {
                    "error": f"日期 {date} 的数据未找到。请验证该日期是否存在于数据中。可用日期示例: {sample_dates}",
                    "symbol": symbol,
                    "date": date
                }
            return {
                "symbol": symbol,
                "date": date,
                "ohlcv": {
                    "open": day.get("1. buy price"),
                    "high": day.get("2. high"),
                    "low": day.get("3. low"), 
                    "close": day.get("4. sell price"),
                    "volume": day.get("5. volume"),
                },
            }

    return {"error": f"在本地数据中未找到股票 {symbol} 的记录", "symbol": symbol, "date": date}


if __name__ == "__main__":
    # print("一个测试用例")
    port = int(os.getenv("GETPRICE_HTTP_PORT", "8003"))
    mcp.run(transport="streamable-http", port=port)
