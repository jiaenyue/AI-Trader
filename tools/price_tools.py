import os
from dotenv import load_dotenv
load_dotenv()
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import sys

# 将项目根目录加入 Python 路径，便于从子目录直接运行本文件
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from tools.general_tools import get_config_value

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

def get_yesterday_date(today_date: str) -> str:
    """
    获取前一个交易日的日期。

    此函数会考虑周末，如果昨天是周六或周日，则会向前追溯到最近的周五。

    Args:
        today_date (str): 代表今天的日期字符串，格式为 "YYYY-MM-DD"。

    Returns:
        str: 前一个交易日的日期字符串，格式为 "YYYY-MM-DD"。
    """
    today_dt = datetime.strptime(today_date, "%Y-%m-%d")
    yesterday_dt = today_dt - timedelta(days=1)
    
    while yesterday_dt.weekday() >= 5:  # 5=周六, 6=周日
        yesterday_dt -= timedelta(days=1)
    
    return yesterday_dt.strftime("%Y-%m-%d")

def get_open_prices(today_date: str, symbols: List[str], merged_path: Optional[str] = None) -> Dict[str, Optional[float]]:
    """
    从 data/merged.jsonl 文件中读取指定日期和股票的开盘价。

    Args:
        today_date (str): 日期字符串，格式为 "YYYY-MM-DD"。
        symbols (List[str]): 需要查询的股票代码列表。
        merged_path (Optional[str]): 可选，自定义 merged.jsonl 路径；默认读取项目根目录下 data/merged.jsonl。

    Returns:
        Dict[str, Optional[float]]: 一个字典，键为 "{symbol}_price"，值为对应的开盘价。如果未找到，则值为 None。
    """
    wanted = set(symbols)
    results: Dict[str, Optional[float]] = {}

    if merged_path is None:
        base_dir = Path(__file__).resolve().parents[1]
        merged_file = base_dir / "data" / "merged.jsonl"
    else:
        merged_file = Path(merged_path)

    if not merged_file.exists():
        return results

    with merged_file.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                doc = json.loads(line)
                meta = doc.get("Meta Data", {})
                sym = meta.get("2. Symbol")
                if sym in wanted:
                    series = doc.get("Time Series (Daily)", {})
                    bar = series.get(today_date)
                    if bar:
                        open_val = bar.get("1. buy price")
                        results[f'{sym}_price'] = float(open_val) if open_val is not None else None
            except (json.JSONDecodeError, AttributeError):
                continue
    return results

def get_yesterday_open_and_close_price(today_date: str, symbols: List[str], merged_path: Optional[str] = None) -> Tuple[Dict[str, Optional[float]], Dict[str, Optional[float]]]:
    """
    从 data/merged.jsonl 中读取指定股票在前一个交易日的开盘价和收盘价。

    Args:
        today_date (str): 代表今天的日期字符串，格式为 "YYYY-MM-DD"。
        symbols (List[str]): 需要查询的股票代码列表。
        merged_path (Optional[str]): 可选，自定义 merged.jsonl 路径。

    Returns:
        Tuple[Dict[str, Optional[float]], Dict[str, Optional[float]]]: 包含开盘价字典和收盘价字典的元组。
    """
    wanted = set(symbols)
    buy_results: Dict[str, Optional[float]] = {}
    sell_results: Dict[str, Optional[float]] = {}

    if merged_path is None:
        base_dir = Path(__file__).resolve().parents[1]
        merged_file = base_dir / "data" / "merged.jsonl"
    else:
        merged_file = Path(merged_path)

    if not merged_file.exists():
        return buy_results, sell_results

    yesterday_date = get_yesterday_date(today_date)

    with merged_file.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                doc = json.loads(line)
                meta = doc.get("Meta Data", {})
                sym = meta.get("2. Symbol")
                if sym in wanted:
                    series = doc.get("Time Series (Daily)", {})
                    bar = series.get(yesterday_date)
                    if bar:
                        buy_val = bar.get("1. buy price")
                        sell_val = bar.get("4. sell price")
                        buy_results[f'{sym}_price'] = float(buy_val) if buy_val is not None else None
                        sell_results[f'{sym}_price'] = float(sell_val) if sell_val is not None else None
            except (json.JSONDecodeError, AttributeError):
                continue
    return buy_results, sell_results

def get_yesterday_profit(today_date: str, yesterday_buy_prices: Dict[str, Optional[float]], yesterday_sell_prices: Dict[str, Optional[float]], yesterday_init_position: Dict[str, float]) -> Dict[str, float]:
    """
    计算昨日持仓的收益。

    收益计算方式为：(昨日收盘价 - 昨日开盘价) * 昨日持仓数量。

    Args:
        today_date (str): 今天的日期。
        yesterday_buy_prices (Dict[str, Optional[float]]): 昨日开盘价字典。
        yesterday_sell_prices (Dict[str, Optional[float]]): 昨日收盘价字典。
        yesterday_init_position (Dict[str, float]): 昨日初始持仓字典。

    Returns:
        Dict[str, float]: 每个股票的收益字典。
    """
    profit_dict = {}
    
    for symbol in all_nasdaq_100_symbols:
        symbol_price_key = f'{symbol}_price'
        buy_price = yesterday_buy_prices.get(symbol_price_key)
        sell_price = yesterday_sell_prices.get(symbol_price_key)
        position_amount = yesterday_init_position.get(symbol, 0.0)
        
        if buy_price is not None and sell_price is not None and position_amount > 0:
            profit = (sell_price - buy_price) * position_amount
            profit_dict[symbol] = round(profit, 4)
        else:
            profit_dict[symbol] = 0.0
    
    return profit_dict

def get_today_init_position(today_date: str, modelname: str) -> Dict[str, float]:
    """
    获取今日开盘时的初始持仓（即前一个交易日的最终持仓）。

    Args:
        today_date (str): 今天的日期。
        modelname (str): 模型名称。

    Returns:
        Dict[str, float]: 初始持仓字典。
    """
    base_dir = Path(__file__).resolve().parents[1]
    position_file = base_dir / "data" / "agent_data" / modelname / "position" / "position.jsonl"

    if not position_file.exists():
        return {}
    
    yesterday_date = get_yesterday_date(today_date)
    max_id = -1
    latest_positions = {}
  
    with position_file.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                doc = json.loads(line)
                if doc.get("date") == yesterday_date:
                    current_id = doc.get("id", -1)
                    if current_id > max_id:
                        max_id = current_id
                        latest_positions = doc.get("positions", {})
            except (json.JSONDecodeError, AttributeError):
                continue
    
    return latest_positions

def get_latest_position(today_date: str, modelname: str) -> Tuple[Dict[str, float], int]:
    """
    获取最新持仓和对应的操作ID。

    优先查找当天的记录；如果当天没有，则查找前一个交易日的记录。

    Args:
        today_date (str): 今天的日期。
        modelname (str): 模型名称。

    Returns:
        Tuple[Dict[str, float], int]: (最新持仓字典, 操作ID)。
    """
    base_dir = Path(__file__).resolve().parents[1]
    position_file = base_dir / "data" / "agent_data" / modelname / "position" / "position.jsonl"

    if not position_file.exists():
        return {}, -1
    
    max_id = -1
    latest_positions = {}
    target_date = today_date
    
    for _ in range(2): # 最多检查两天：今天和昨天
        with position_file.open("r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    doc = json.loads(line)
                    if doc.get("date") == target_date:
                        current_id = doc.get("id", -1)
                        if current_id > max_id:
                            max_id = current_id
                            latest_positions = doc.get("positions", {})
                except (json.JSONDecodeError, AttributeError):
                    continue
        if max_id != -1:
            return latest_positions, max_id
        target_date = get_yesterday_date(target_date)

    return latest_positions, max_id

def add_no_trade_record(today_date: str, modelname: str) -> None:
    """
    如果当天没有交易，则添加一条 "no_trade" 记录。

    该记录会继承前一天的最终持仓。

    Args:
        today_date (str): 今天的日期。
        modelname (str): 模型名称。
    """
    current_position, current_action_id = get_latest_position(today_date, modelname)
    
    # 检查今天是否已有交易记录
    base_dir = Path(__file__).resolve().parents[1]
    position_file = base_dir / "data" / "agent_data" / modelname / "position" / "position.jsonl"
    if position_file.exists():
        with position_file.open("r", encoding="utf-8") as f:
            for line in f:
                 if not line.strip():
                    continue
                 try:
                    doc = json.loads(line)
                    if doc.get("date") == today_date and doc.get("id", -1) > current_action_id:
                        return # 已有新交易，无需添加
                 except (json.JSONDecodeError, AttributeError):
                    continue

    save_item = {
        "date": today_date,
        "id": current_action_id + 1,
        "this_action": {"action": "no_trade", "symbol": "", "amount": 0},
        "positions": current_position
    }

    with position_file.open("a", encoding="utf-8") as f:
        f.write(json.dumps(save_item) + "\n")

if __name__ == "__main__":
    today_date = get_config_value("TODAY_DATE", "2025-10-13")
    signature = get_config_value("SIGNATURE", "gpt-4")

    print(f"日期: {today_date}, 模型: {signature}")

    yesterday_date = get_yesterday_date(today_date)
    print(f"昨天日期: {yesterday_date}")

    today_buy_price = get_open_prices(today_date, all_nasdaq_100_symbols)
    # print(f"今日开盘价: {today_buy_price}")

    yesterday_buy_prices, yesterday_sell_prices = get_yesterday_open_and_close_price(today_date, all_nasdaq_100_symbols)
    # print(f"昨日开盘价: {yesterday_buy_prices}")
    # print(f"昨日收盘价: {yesterday_sell_prices}")

    today_init_position = get_today_init_position(today_date, signature)
    # print(f"今日初始持仓: {today_init_position}")

    latest_position, latest_action_id = get_latest_position(today_date, signature)
    print(f"最新持仓: {latest_position}, 最新操作ID: {latest_action_id}")

    yesterday_profit = get_yesterday_profit(today_date, yesterday_buy_prices, yesterday_sell_prices, today_init_position)
    # print(f"昨日收益: {yesterday_profit}")

    add_no_trade_record(today_date, signature)
