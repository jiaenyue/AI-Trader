from fastmcp import FastMCP
import sys
import os
from typing import Dict, List, Optional, Any
# 将项目根目录添加到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
from tools.price_tools import get_yesterday_date, get_open_prices, get_yesterday_open_and_close_price, get_latest_position, get_yesterday_profit
import json
from tools.general_tools import get_config_value,write_config_value
mcp = FastMCP("TradeTools")



@mcp.tool()
def buy(symbol: str, amount: int) -> Dict[str, Any]:
    """
    买入股票函数。

    该函数模拟股票买入操作，包括以下步骤：
    1. 获取当前仓位和操作 ID。
    2. 获取当天的股票开盘价。
    3. 验证买入条件（现金是否充足）。
    4. 更新仓位（增加股票数量，减少现金）。
    5. 将交易记录到 position.jsonl 文件中。

    Args:
        symbol (str): 股票代码，例如 "AAPL", "MSFT" 等。
        amount (int): 买入数量，必须是正整数，表示要买入多少股。

    Returns:
        Dict[str, Any]:
          - 成功: 返回新的仓位字典（包含股票数量和现金余额）。
          - 失败: 返回 {"error": 错误信息, ...} 字典。

    Raises:
        ValueError: 当 SIGNATURE 环境变量未设置时引发。

    示例:
        >>> result = buy("AAPL", 10)
        >>> print(result)  # {"AAPL": 110, "MSFT": 5, "CASH": 5000.0, ...}
    """
    # 步骤 1: 获取环境变量和基本信息
    signature = get_config_value("SIGNATURE")
    if signature is None:
        raise ValueError("SIGNATURE 环境变量未设置")
    
    today_date = get_config_value("TODAY_DATE")
    
    # 步骤 2: 获取当前最新仓位和操作 ID
    try:
        current_position, current_action_id = get_latest_position(today_date, signature)
    except Exception as e:
        print(e)
        return {"error": f"获取最新仓位时出错: {e}", "symbol": symbol, "date": today_date}

    # 步骤 3: 获取当天的股票开盘价
    try:
        this_symbol_price = get_open_prices(today_date, [symbol])[f'{symbol}_price']
    except KeyError:
        return {"error": f"未找到股票代码 {symbol}！此操作不允许。", "symbol": symbol, "date": today_date}

    # 步骤 4: 验证买入条件
    try:
        cash_left = current_position["CASH"] - this_symbol_price * amount
    except Exception as e:
        return {"error": f"计算所需现金时出错: {e}", "symbol": symbol, "date": today_date}

    if cash_left < 0:
        return {"error": "现金不足！此操作不允许。", "required_cash": this_symbol_price * amount, "cash_available": current_position.get("CASH", 0), "symbol": symbol, "date": today_date}
    else:
        # 步骤 5: 执行买入操作，更新仓位
        new_position = current_position.copy()
        new_position["CASH"] = cash_left
        new_position[symbol] = new_position.get(symbol, 0) + amount
        
        # 步骤 6: 将交易记录到 position.jsonl 文件
        position_file_path = os.path.join(project_root, "data", "agent_data", signature, "position", "position.jsonl")
        with open(position_file_path, "a") as f:
            log_entry = {
                "date": today_date,
                "id": current_action_id + 1,
                "this_action": {'action': 'buy', 'symbol': symbol, 'amount': amount},
                "positions": new_position
            }
            print(f"正在写入 position.jsonl: {json.dumps(log_entry)}")
            f.write(json.dumps(log_entry) + "\n")

        # 步骤 7: 返回更新后的仓位
        write_config_value("IF_TRADE", True)
        print("IF_TRADE", get_config_value("IF_TRADE"))
        return new_position

@mcp.tool()
def sell(symbol: str, amount: int) -> Dict[str, Any]:
    """
    卖出股票函数。

    该函数模拟股票卖出操作，包括以下步骤：
    1. 获取当前仓位和操作 ID。
    2. 获取当天的股票开盘价。
    3. 验证卖出条件（是否存在仓位，数量是否充足）。
    4. 更新仓位（减少股票数量，增加现金）。
    5. 将交易记录到 position.jsonl 文件中。

    Args:
        symbol (str): 股票代码，例如 "AAPL", "MSFT" 等。
        amount (int): 卖出数量，必须是正整数，表示要卖出多少股。

    Returns:
        Dict[str, Any]:
          - 成功: 返回新的仓位字典（包含股票数量和现金余额）。
          - 失败: 返回 {"error": 错误信息, ...} 字典。

    Raises:
        ValueError: 当 SIGNATURE 环境变量未设置时引发。

    示例:
        >>> result = sell("AAPL", 10)
        >>> print(result)  # {"AAPL": 90, "MSFT": 5, "CASH": 15000.0, ...}
    """
    # 步骤 1: 获取环境变量和基本信息
    signature = get_config_value("SIGNATURE")
    if signature is None:
        raise ValueError("SIGNATURE 环境变量未设置")
    
    today_date = get_config_value("TODAY_DATE")
    
    # 步骤 2: 获取当前最新仓位和操作 ID
    try:
        current_position, current_action_id = get_latest_position(today_date, signature)
    except Exception as e:
        print(e)
        return {"error": f"获取最新仓位时出错: {e}", "symbol": symbol, "date": today_date}
    
    # 步骤 3: 获取当天的股票开盘价
    try:
        this_symbol_price = get_open_prices(today_date, [symbol])[f'{symbol}_price']
    except KeyError:
        return {"error": f"未找到股票代码 {symbol}！此操作不允许。", "symbol": symbol, "date": today_date}

    # 步骤 4: 验证卖出条件
    if symbol not in current_position or current_position.get(symbol, 0) == 0:
        return {"error": f"{symbol} 无仓位！此操作不允许。", "symbol": symbol, "date": today_date}

    if current_position.get(symbol, 0) < amount:
        return {"error": "持股不足！此操作不允许。", "have": current_position.get(symbol, 0), "want_to_sell": amount, "symbol": symbol, "date": today_date}

    # 步骤 5: 执行卖出操作，更新仓位
    new_position = current_position.copy()
    new_position[symbol] -= amount
    new_position["CASH"] = new_position.get("CASH", 0) + this_symbol_price * amount

    # 步骤 6: 将交易记录到 position.jsonl 文件
    position_file_path = os.path.join(project_root, "data", "agent_data", signature, "position", "position.jsonl")
    with open(position_file_path, "a") as f:
        log_entry = {
            "date": today_date,
            "id": current_action_id + 1,
            "this_action": {'action': 'sell', 'symbol': symbol, 'amount': amount},
            "positions": new_position
        }
        print(f"正在写入 position.jsonl: {json.dumps(log_entry)}")
        f.write(json.dumps(log_entry) + "\n")

    # 步骤 7: 返回更新后的仓位
    write_config_value("IF_TRADE", True)
    return new_position

if __name__ == "__main__":
    port = int(os.getenv("TRADE_HTTP_PORT", "8002"))
    mcp.run(transport="streamable-http", port=port)
