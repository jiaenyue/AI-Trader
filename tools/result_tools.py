import os
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import sys

# 将项目根目录添加到Python路径，以便从子目录运行此文件
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from tools.price_tools import (
    get_yesterday_date, 
    get_open_prices, 
    get_yesterday_open_and_close_price,
    get_today_init_position,
    get_latest_position,
    all_nasdaq_100_symbols
)
from tools.general_tools import get_config_value


def calculate_portfolio_value(positions: Dict[str, float], prices: Dict[str, Optional[float]], cash: float = 0.0) -> float:
    """
    计算投资组合的总价值。

    Args:
        positions (Dict[str, float]): 持仓字典，格式为 {股票代码: 股数}。
        prices (Dict[str, Optional[float]]): 价格字典，格式为 {股票代码_price: 价格}。
        cash (float): 现金余额。

    Returns:
        float: 投资组合的总价值。
    """
    total_value = cash
    
    for symbol, shares in positions.items():
        if symbol == "CASH":
            continue
        price_key = f'{symbol}_price'
        price = prices.get(price_key)
        if price is not None and shares > 0:
            total_value += shares * price
    
    return total_value


def get_available_date_range(modelname: str) -> Tuple[str, str]:
    """
    获取可用数据的日期范围。

    Args:
        modelname (str): 模型名称。

    Returns:
        Tuple[str, str]: (最早日期, 最晚日期) 的元组，格式为 "YYYY-MM-DD"。
    """
    base_dir = Path(__file__).resolve().parents[1]
    position_file = base_dir / "data" / "agent_data" / modelname / "position" / "position.jsonl"
    
    if not position_file.exists():
        return "", ""
    
    dates = []
    
    with position_file.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                doc = json.loads(line)
                date = doc.get("date")
                if date:
                    dates.append(date)
            except Exception:
                continue
    
    if not dates:
        return "", ""
    
    dates.sort()
    return dates[0], dates[-1]


def get_daily_portfolio_values(modelname: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, float]:
    """
    获取每日的投资组合价值。

    Args:
        modelname (str): 模型名称。
        start_date (Optional[str]): 开始日期，格式为 "YYYY-MM-DD"。如果为 None，则使用最早的可用日期。
        end_date (Optional[str]): 结束日期，格式为 "YYYY-MM-DD"。如果为 None，则使用最晚的可用日期。

    Returns:
        Dict[str, float]: 每日投资组合价值的字典，格式为 {日期: 价值}。
    """
    base_dir = Path(__file__).resolve().parents[1]
    position_file = base_dir / "data" / "agent_data" / modelname / "position" / "position.jsonl"
    merged_file = base_dir / "data" / "merged.jsonl"
    
    if not position_file.exists() or not merged_file.exists():
        return {}
    
    # Get available date range if not specified
    if start_date is None or end_date is None:
        earliest_date, latest_date = get_available_date_range(modelname)
        if not earliest_date or not latest_date:
            return {}
        
        if start_date is None:
            start_date = earliest_date
        if end_date is None:
            end_date = latest_date
    
    # Read position data
    position_data = []
    with position_file.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                doc = json.loads(line)
                position_data.append(doc)
            except Exception:
                continue
    
    # Read price data
    price_data = {}
    with merged_file.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                doc = json.loads(line)
                meta = doc.get("Meta Data", {})
                symbol = meta.get("2. Symbol")
                if symbol:
                    price_data[symbol] = doc.get("Time Series (Daily)", {})
            except Exception:
                continue
    
    # Calculate daily portfolio values
    daily_values = {}
    
    # Group position data by date
    positions_by_date = {}
    for record in position_data:
        date = record.get("date")
        if date:
            if date not in positions_by_date:
                positions_by_date[date] = []
            positions_by_date[date].append(record)
    
    # For each date, sort records by id and take latest position
    for date, records in positions_by_date.items():
        if start_date and date < start_date:
            continue
        if end_date and date > end_date:
            continue
            
        # Sort by id and take latest position
        latest_record = max(records, key=lambda x: x.get("id", 0))
        positions = latest_record.get("positions", {})
        
        # Get daily prices
        daily_prices = {}
        for symbol in all_nasdaq_100_symbols:
            if symbol in price_data:
                symbol_prices = price_data[symbol]
                if date in symbol_prices:
                    price_info = symbol_prices[date]
                    buy_price = price_info.get("1. buy price")
                    sell_price = price_info.get("4. sell price")
                    # Use closing (sell) price to calculate value
                    if sell_price is not None:
                        daily_prices[f'{symbol}_price'] = float(sell_price)
        
        # Calculate portfolio value
        cash = positions.get("CASH", 0.0)
        portfolio_value = calculate_portfolio_value(positions, daily_prices, cash)
        daily_values[date] = portfolio_value
    
    return daily_values


def calculate_daily_returns(portfolio_values: Dict[str, float]) -> List[float]:
    """
    计算每日收益率。

    Args:
        portfolio_values (Dict[str, float]): 每日投资组合价值字典。

    Returns:
        List[float]: 每日收益率列表。
    """
    if len(portfolio_values) < 2:
        return []
    
    # Sort by date
    sorted_dates = sorted(portfolio_values.keys())
    returns = []
    
    for i in range(1, len(sorted_dates)):
        prev_date = sorted_dates[i-1]
        curr_date = sorted_dates[i]
        
        prev_value = portfolio_values[prev_date]
        curr_value = portfolio_values[curr_date]
        
        if prev_value > 0:
            daily_return = (curr_value - prev_value) / prev_value
            returns.append(daily_return)
    
    return returns


def calculate_sharpe_ratio(returns: List[float], risk_free_rate: float = 0.02) -> float:
    """
    计算夏普比率。

    Args:
        returns (List[float]): 收益率列表。
        risk_free_rate (float): 无风险利率（年化）。

    Returns:
        float: 夏普比率。
    """
    if not returns or len(returns) < 2:
        return 0.0
    
    returns_array = np.array(returns)
    
    # Calculate annualized return and volatility
    mean_return = np.mean(returns_array)
    std_return = np.std(returns_array, ddof=1)
    
    # Assume 252 trading days per year
    annualized_return = mean_return * 252
    annualized_volatility = std_return * np.sqrt(252)
    
    if annualized_volatility == 0:
        return 0.0
    
    # Calculate Sharpe ratio
    sharpe_ratio = (annualized_return - risk_free_rate) / annualized_volatility
    
    return sharpe_ratio


def calculate_max_drawdown(portfolio_values: Dict[str, float]) -> Tuple[float, str, str]:
    """
    计算最大回撤。

    Args:
        portfolio_values (Dict[str, float]): 每日投资组合价值字典。

    Returns:
        Tuple[float, str, str]: (最大回撤百分比, 回撤开始日期, 回撤结束日期)。
    """
    if not portfolio_values:
        return 0.0, "", ""
    
    # Sort by date
    sorted_dates = sorted(portfolio_values.keys())
    values = [portfolio_values[date] for date in sorted_dates]
    
    max_drawdown = 0.0
    peak_value = values[0]
    peak_date = sorted_dates[0]
    drawdown_start_date = ""
    drawdown_end_date = ""
    
    for i, (date, value) in enumerate(zip(sorted_dates, values)):
        if value > peak_value:
            peak_value = value
            peak_date = date
        
        drawdown = (peak_value - value) / peak_value
        if drawdown > max_drawdown:
            max_drawdown = drawdown
            drawdown_start_date = peak_date
            drawdown_end_date = date
    
    return max_drawdown, drawdown_start_date, drawdown_end_date


def calculate_cumulative_return(portfolio_values: Dict[str, float]) -> float:
    """
    计算累计回报率。

    Args:
        portfolio_values (Dict[str, float]): 每日投资组合价值字典。

    Returns:
        float: 累计回报率。
    """
    if not portfolio_values:
        return 0.0
    
    # Sort by date
    sorted_dates = sorted(portfolio_values.keys())
    initial_value = portfolio_values[sorted_dates[0]]
    final_value = portfolio_values[sorted_dates[-1]]
    
    if initial_value == 0:
        return 0.0
    
    cumulative_return = (final_value - initial_value) / initial_value
    return cumulative_return


def calculate_annualized_return(portfolio_values: Dict[str, float]) -> float:
    """
    计算年化回报率。

    Args:
        portfolio_values (Dict[str, float]): 每日投资组合价值字典。

    Returns:
        float: 年化回报率。
    """
    if not portfolio_values:
        return 0.0
    
    # Sort by date
    sorted_dates = sorted(portfolio_values.keys())
    initial_value = portfolio_values[sorted_dates[0]]
    final_value = portfolio_values[sorted_dates[-1]]
    
    if initial_value == 0:
        return 0.0
    
    # Calculate investment days
    start_date = datetime.strptime(sorted_dates[0], "%Y-%m-%d")
    end_date = datetime.strptime(sorted_dates[-1], "%Y-%m-%d")
    days = (end_date - start_date).days
    
    if days == 0:
        return 0.0
    
    # Calculate annualized return
    total_return = (final_value - initial_value) / initial_value
    annualized_return = (1 + total_return) ** (365 / days) - 1
    
    return annualized_return


def calculate_volatility(returns: List[float]) -> float:
    """
    计算年化波动率。

    Args:
        returns (List[float]): 收益率列表。

    Returns:
        float: 年化波动率。
    """
    if not returns or len(returns) < 2:
        return 0.0
    
    returns_array = np.array(returns)
    daily_volatility = np.std(returns_array, ddof=1)
    
    # Annualize volatility (assuming 252 trading days)
    annualized_volatility = daily_volatility * np.sqrt(252)
    
    return annualized_volatility


def calculate_win_rate(returns: List[float]) -> float:
    """
    计算胜率。

    Args:
        returns (List[float]): 收益率列表。

    Returns:
        float: 胜率 (正收益天数的百分比)。
    """
    if not returns:
        return 0.0
    
    positive_days = sum(1 for r in returns if r > 0)
    total_days = len(returns)
    
    return positive_days / total_days


def calculate_profit_loss_ratio(returns: List[float]) -> float:
    """
    计算盈亏比。

    Args:
        returns (List[float]): 收益率列表。

    Returns:
        float: 盈亏比 (平均盈利 / 平均亏损)。
    """
    if not returns:
        return 0.0
    
    positive_returns = [r for r in returns if r > 0]
    negative_returns = [r for r in returns if r < 0]
    
    if not positive_returns or not negative_returns:
        return 0.0
    
    avg_profit = np.mean(positive_returns)
    avg_loss = abs(np.mean(negative_returns))
    
    if avg_loss == 0:
        return 0.0
    
    return avg_profit / avg_loss


def calculate_all_metrics(modelname: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, any]:
    """
    计算所有性能指标。

    Args:
        modelname (str): 模型名称。
        start_date (Optional[str]): 开始日期。
        end_date (Optional[str]): 结束日期。

    Returns:
        Dict[str, any]: 包含所有指标的字典。
    """
    # Get available date range if not specified
    if start_date is None or end_date is None:
        earliest_date, latest_date = get_available_date_range(modelname)
        if not earliest_date or not latest_date:
            return {
                "error": "无法获取可用数据日期范围",
                "portfolio_values": {},
                "daily_returns": [],
                "sharpe_ratio": 0.0,
                "max_drawdown": 0.0,
                "max_drawdown_start": "",
                "max_drawdown_end": "",
                "cumulative_return": 0.0,
                "annualized_return": 0.0,
                "volatility": 0.0,
                "win_rate": 0.0,
                "profit_loss_ratio": 0.0,
                "total_trading_days": 0,
                "start_date": "",
                "end_date": ""
            }
        
        if start_date is None:
            start_date = earliest_date
        if end_date is None:
            end_date = latest_date
    
    # 获取每日投资组合价值
    portfolio_values = get_daily_portfolio_values(modelname, start_date, end_date)
    
    if not portfolio_values:
        return {
            "error": "无法获取投资组合数据",
            "portfolio_values": {},
            "daily_returns": [],
            "sharpe_ratio": 0.0,
            "max_drawdown": 0.0,
            "max_drawdown_start": "",
            "max_drawdown_end": "",
            "cumulative_return": 0.0,
            "annualized_return": 0.0,
            "volatility": 0.0,
            "win_rate": 0.0,
            "profit_loss_ratio": 0.0,
            "total_trading_days": 0,
            "start_date": "",
            "end_date": ""
        }
    
    # Calculate daily returns
    daily_returns = calculate_daily_returns(portfolio_values)
    
    # Calculate various metrics
    sharpe_ratio = calculate_sharpe_ratio(daily_returns)
    max_drawdown, drawdown_start, drawdown_end = calculate_max_drawdown(portfolio_values)
    cumulative_return = calculate_cumulative_return(portfolio_values)
    annualized_return = calculate_annualized_return(portfolio_values)
    volatility = calculate_volatility(daily_returns)
    win_rate = calculate_win_rate(daily_returns)
    profit_loss_ratio = calculate_profit_loss_ratio(daily_returns)
    
    # Get date range
    sorted_dates = sorted(portfolio_values.keys())
    start_date_actual = sorted_dates[0] if sorted_dates else ""
    end_date_actual = sorted_dates[-1] if sorted_dates else ""
    
    return {
        "portfolio_values": portfolio_values,
        "daily_returns": daily_returns,
        "sharpe_ratio": round(sharpe_ratio, 4),
        "max_drawdown": round(max_drawdown, 4),
        "max_drawdown_start": drawdown_start,
        "max_drawdown_end": drawdown_end,
        "cumulative_return": round(cumulative_return, 4),
        "annualized_return": round(annualized_return, 4),
        "volatility": round(volatility, 4),
        "win_rate": round(win_rate, 4),
        "profit_loss_ratio": round(profit_loss_ratio, 4),
        "total_trading_days": len(portfolio_values),
        "start_date": start_date_actual,
        "end_date": end_date_actual
    }


def print_performance_report(metrics: Dict[str, any]) -> None:
    """
    打印性能报告。

    Args:
        metrics (Dict[str, any]): 包含所有指标的字典。
    """
    print("=" * 60)
    print("投资组合性能报告")
    print("=" * 60)
    
    if "error" in metrics:
        print(f"错误: {metrics['error']}")
        return
    
    print(f"分析期间: {metrics['start_date']} 到 {metrics['end_date']}")
    print(f"交易天数: {metrics['total_trading_days']}")
    print()
    
    print("回报指标:")
    print(f"  累计回报率: {metrics['cumulative_return']:.2%}")
    print(f"  年化回报率: {metrics['annualized_return']:.2%}")
    print(f"  年化波动率: {metrics['volatility']:.2%}")
    print()
    
    print("风险指标:")
    print(f"  夏普比率: {metrics['sharpe_ratio']:.4f}")
    print(f"  最大回撤: {metrics['max_drawdown']:.2%}")
    if metrics['max_drawdown_start'] and metrics['max_drawdown_end']:
        print(f"  回撤期间: {metrics['max_drawdown_start']} 到 {metrics['max_drawdown_end']}")
    print()
    
    print("交易统计:")
    print(f"  胜率: {metrics['win_rate']:.2%}")
    print(f"  盈亏比: {metrics['profit_loss_ratio']:.4f}")
    print()
    
    # Show portfolio value changes
    portfolio_values = metrics['portfolio_values']
    if portfolio_values:
        sorted_dates = sorted(portfolio_values.keys())
        initial_value = portfolio_values[sorted_dates[0]]
        final_value = portfolio_values[sorted_dates[-1]]
        
        print("投资组合价值:")
        print(f"  初始价值: ${initial_value:,.2f}")
        print(f"  最终价值: ${final_value:,.2f}")
        print(f"  价值变化: ${final_value - initial_value:,.2f}")


def get_next_id(filepath: Path) -> int:
    """
    获取下一个ID号。

    Args:
        filepath (Path): JSONL文件路径。

    Returns:
        int: 下一个ID号。
    """
    if not filepath.exists():
        return 0
    
    max_id = -1
    with filepath.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                data = json.loads(line)
                current_id = data.get("id", -1)
                if current_id > max_id:
                    max_id = current_id
            except Exception:
                continue
    
    return max_id + 1


def save_metrics_to_jsonl(metrics: Dict[str, any], modelname: str, output_dir: Optional[str] = None) -> str:
    """
    将指标增量保存为JSONL格式。

    Args:
        metrics (Dict[str, any]): 包含所有指标的字典。
        modelname (str): 模型名称。
        output_dir (Optional[str]): 输出目录，默认为 data/agent_data/{modelname}/metrics/。

    Returns:
        str: 保存文件的路径。
    """
    base_dir = Path(__file__).resolve().parents[1]
    
    if output_dir is None:
        output_dir = base_dir / "data" / "agent_data" / modelname / "metrics"
    else:
        output_dir = Path(output_dir)
    
    # Create directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Use fixed filename
    filename = "performance_metrics.jsonl"
    filepath = output_dir / filename
    
    # Get next ID number
    next_id = get_next_id(filepath)
    
    # Prepare data to save
    save_data = {
        "id": next_id,
        "model_name": modelname,
        "analysis_period": {
            "start_date": metrics.get("start_date", ""),
            "end_date": metrics.get("end_date", ""),
            "total_trading_days": metrics.get("total_trading_days", 0)
        },
        "performance_metrics": {
            "sharpe_ratio": metrics.get("sharpe_ratio", 0.0),
            "max_drawdown": metrics.get("max_drawdown", 0.0),
            "max_drawdown_period": {
                "start_date": metrics.get("max_drawdown_start", ""),
                "end_date": metrics.get("max_drawdown_end", "")
            },
            "cumulative_return": metrics.get("cumulative_return", 0.0),
            "annualized_return": metrics.get("annualized_return", 0.0),
            "volatility": metrics.get("volatility", 0.0),
            "win_rate": metrics.get("win_rate", 0.0),
            "profit_loss_ratio": metrics.get("profit_loss_ratio", 0.0)
        },
        "portfolio_summary": {}
    }
    
    # Add portfolio value summary
    portfolio_values = metrics.get("portfolio_values", {})
    if portfolio_values:
        sorted_dates = sorted(portfolio_values.keys())
        initial_value = portfolio_values[sorted_dates[0]]
        final_value = portfolio_values[sorted_dates[-1]]
        
        save_data["portfolio_summary"] = {
            "initial_value": initial_value,
            "final_value": final_value,
            "value_change": final_value - initial_value,
            "value_change_percent": ((final_value - initial_value) / initial_value) if initial_value > 0 else 0.0
        }
    
    # Incrementally save to JSONL file (append mode)
    with filepath.open("a", encoding="utf-8") as f:
        f.write(json.dumps(save_data, ensure_ascii=False) + "\n")
    
    return str(filepath)


def get_latest_metrics(modelname: str, output_dir: Optional[str] = None) -> Optional[Dict[str, any]]:
    """
    获取最新的性能指标记录。

    Args:
        modelname (str): 模型名称。
        output_dir (Optional[str]): 输出目录。

    Returns:
        Optional[Dict[str, any]]: 最新的指标记录，如果没有记录则为 None。
    """
    base_dir = Path(__file__).resolve().parents[1]
    
    if output_dir is None:
        output_dir = base_dir / "data" / "agent_data" / modelname / "metrics"
    else:
        output_dir = Path(output_dir)
    
    filepath = output_dir / "performance_metrics.jsonl"
    
    if not filepath.exists():
        return None
    
    latest_record = None
    max_id = -1
    
    with filepath.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                data = json.loads(line)
                current_id = data.get("id", -1)
                if current_id > max_id:
                    max_id = current_id
                    latest_record = data
            except Exception:
                continue
    
    return latest_record


def get_metrics_history(modelname: str, output_dir: Optional[str] = None, limit: Optional[int] = None) -> List[Dict[str, any]]:
    """
    获取性能指标历史记录。

    Args:
        modelname (str): 模型名称。
        output_dir (Optional[str]): 输出目录。
        limit (Optional[int]): 限制返回的记录数，None 返回所有记录。

    Returns:
        List[Dict[str, any]]: 指标记录列表，按ID排序。
    """
    base_dir = Path(__file__).resolve().parents[1]
    
    if output_dir is None:
        output_dir = base_dir / "data" / "agent_data" / modelname / "metrics"
    else:
        output_dir = Path(output_dir)
    
    filepath = output_dir / "performance_metrics.jsonl"
    
    if not filepath.exists():
        return []
    
    records = []
    
    with filepath.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                data = json.loads(line)
                records.append(data)
            except Exception:
                continue
    
    # Sort by ID
    records.sort(key=lambda x: x.get("id", 0))
    
    # Return latest records if limit specified
    if limit is not None and limit > 0:
        records = records[-limit:]
    
    return records


def print_metrics_summary(modelname: str, output_dir: Optional[str] = None) -> None:
    """
    打印性能指标摘要。

    Args:
        modelname (str): 模型名称。
        output_dir (Optional[str]): 输出目录。
    """
    print(f"📊 模型 '{modelname}' 性能指标摘要")
    print("=" * 60)
    
    # Get history records
    history = get_metrics_history(modelname, output_dir)
    
    if not history:
        print("❌ 未找到历史记录")
        return
    
    print(f"📈 总记录数: {len(history)}")
    
    # Show latest record
    latest = history[-1]
    print(f"🕒 最新记录 (ID: {latest['id']}):")
    print(f"   分析期间: {latest['analysis_period']['start_date']} 到 {latest['analysis_period']['end_date']}")
    print(f"   交易天数: {latest['analysis_period']['total_trading_days']}")
    
    metrics = latest['performance_metrics']
    print(f"   夏普比率: {metrics['sharpe_ratio']}")
    print(f"   最大回撤: {metrics['max_drawdown']:.2%}")
    print(f"   累计回报率: {metrics['cumulative_return']:.2%}")
    print(f"   年化回报率: {metrics['annualized_return']:.2%}")
    
    # Show trends (if multiple records exist)
    if len(history) > 1:
        print(f"\n📊 趋势分析 (最近 {min(5, len(history))} 条记录):")
        
        recent_records = history[-5:] if len(history) >= 5 else history
        
        print("ID  | 时间                | 累计回报 | 年化回报 | 夏普")
        print("-" * 70)
        
        for record in recent_records:
            metrics = record['performance_metrics']
            print(f"{record['id']:2d} | {metrics['cumulative_return']:8.2%} | {metrics['annualized_return']:8.2%} | {metrics['sharpe_ratio']:8.4f}")


def calculate_and_save_metrics(modelname: str, start_date: Optional[str] = None, end_date: Optional[str] = None, output_dir: Optional[str] = None, print_report: bool = True) -> Dict[str, any]:
    """
    计算所有指标并以JSONL格式保存的入口函数。

    Args:
        modelname (str): 模型名称 (SIGNATURE)。
        start_date (Optional[str]): 开始日期。
        end_date (Optional[str]): 结束日期。
        output_dir (Optional[str]): 输出目录。
        print_report (bool): 是否打印报告。

    Returns:
        Dict[str, any]: 包含所有指标和已保存文件路径的字典。
    """
    print(f"正在分析模型: {modelname}")
    
    # Show date range to be used if not specified
    if start_date is None or end_date is None:
        earliest_date, latest_date = get_available_date_range(modelname)
        if earliest_date and latest_date:
            if start_date is None:
                start_date = earliest_date
                print(f"使用默认开始日期: {start_date}")
            if end_date is None:
                end_date = latest_date
                print(f"使用默认结束日期: {end_date}")
        else:
            print("❌ 无法获取可用数据日期范围")
    
    # Calculate all metrics
    metrics = calculate_all_metrics(modelname, start_date, end_date)
    
    if "error" in metrics:
        print(f"错误: {metrics['error']}")
        return metrics
    
    # Save in JSONL format
    try:
        saved_file = save_metrics_to_jsonl(metrics, modelname, output_dir)
        print(f"指标已保存至: {saved_file}")
        metrics["saved_file"] = saved_file
        
        # Get ID of just saved record
        latest_record = get_latest_metrics(modelname, output_dir)
        if latest_record:
            metrics["record_id"] = latest_record["id"]
            print(f"记录 ID: {latest_record['id']}")
    except Exception as e:
        print(f"保存文件时出错: {e}")
        metrics["save_error"] = str(e)
    
    # Print report
    if print_report:
        print_performance_report(metrics)
    
    return metrics


if __name__ == "__main__":
    # Test code
    # 测试代码
    modelname = get_config_value("SIGNATURE")
    if modelname is None:
        print("错误: 未设置 SIGNATURE 环境变量")
        print("请设置环境变量 SIGNATURE，例如: export SIGNATURE=claude-3.7-sonnet")
        sys.exit(1)
    
    # 使用入口函数计算和保存指标
    result = calculate_and_save_metrics(modelname)
