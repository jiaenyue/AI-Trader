# AI-Trader 策略文档

本文档详细解释了 AI-Trader 项目中 AI 代理进行交易时所遵循的核心策略、提示词（Prompt）设计，以及其决策过程。

## 核心理念：基本面分析驱动

AI 代理被设定为一个 **股票基本面分析交易助手**。这意味着它的核心决策逻辑并非基于技术指标（如移动平均线、RSI等），而是鼓励其从更宏观和基本面的角度来评估市场和个股。

其主要目标是：**长期最大化投资组合的回报**。

## 决策流程

AI 代理的决策流程是完全自主的，并在一个“单日交易会话” (`run_trading_session`) 的循环中执行。每一天，AI 都会经历以下步骤：

### 1. 接收初始信息

在每个交易日开始时，AI 会收到一个系统提示（System Prompt），其中包含了当天的关键信息。这些信息是AI决策的基础，包括：

- **今日日期** (`{date}`): 当前交易的日期。
- **昨日收盘持仓** (`{positions}`): 上一个交易日结束时，投资组合中持有的各股票数量和剩余现金。
- **昨日收盘价** (`{yesterday_close_price}`): 各股票在上一个交易日的收盘价格。
- **今日买入价** (`{today_buy_price}`): 各股票在今天的开盘价格（即交易执行价格）。

### 2. 信息收集与分析

根据系统提示，AI 被明确指示：**在做出决策之前，通过搜索工具收集尽可能多的信息来辅助决策**。

这意味着AI会利用 `get_information(query)` 工具来主动搜索与市场、特定行业或个股相关的新闻、财报摘要、分析师观点等。例如，AI可能会搜索“NVDA a new server GPU”或“AAPL Q4 earnings report”等。

### 3. 思考与推理

在收集了足够的信息后，AI 会进入一个内部的思考与推理阶段。在这个阶段，它会：

- **评估当前持仓**：结合最新的市场信息，评估当前持有的股票是否仍然具有增长潜力。
- **寻找交易机会**：基于基本面分析，寻找新的投资机会（买入）或识别需要退出的头寸（卖出）。
- **制定交易计划**：形成一个具体的交易计划，例如“卖出10股AAPL，买入5股NVDA”。

### 4. 仓位管理与交易执行

AI 的所有交易操作都必须通过调用工具来完成。它主要使用以下两个工具来管理仓位：

- `buy(symbol, amount)`: 买入指定数量的股票。
- `sell(symbol, amount)`: 卖出指定数量的股票。

**现金管理** 是隐式进行的。当AI调用 `buy` 时，系统会自动从其现金余额中扣除相应的金额。如果现金不足，交易会失败。同样，`sell` 操作会将收益自动计入现金余额。

AI需要自行决定买入或卖出的`amount`（数量）。这个决策过程是其策略的一部分，可能基于对某只股票的信心、风险分散的考虑，或是为了将总投资组合的风险维持在某个水平。

### 5. 结束交易

当AI认为当天的交易任务已经完成时，它会输出一个特殊的停止信号 (`<FINISH_SIGNAL>`)，结束当天的交易会话。

## 核心系统提示词（Prompt）

以下是提供给AI代理的完整系统提示词模板。正是这个提示词，塑造了AI的行为和策略。

```plaintext
You are a stock fundamental analysis trading assistant.

Your goals are:
- Think and reason by calling available tools.
- You need to think about the prices of various stocks and their returns.
- Your long-term goal is to maximize returns through this portfolio.
- Before making decisions, gather as much information as possible through search tools to aid decision-making.

Thinking standards:
- Clearly show key intermediate steps:
  - Read input of yesterday's positions and today's prices
  - Update valuation and adjust weights for each target (if strategy requires)

Notes:
- You don't need to request user permission during operations, you can execute directly
- You must execute operations by calling tools, directly output operations will not be accepted

Here is the information you need:

Today's date:
{date}

Yesterday's closing positions (numbers after stock codes represent how many shares you hold, numbers after CASH represent your available cash):
{positions}

Yesterday's closing prices:
{yesterday_close_price}

Today's buying prices:
{today_buy_price}

When you think your task is complete, output
{STOP_SIGNAL}
```

### 提示词解析

- **角色设定**: "你是一个股票基本面分析交易助手" —— 这为AI的行为定了基调。
- **目标**: 强调了长期回报和信息收集的重要性。
- **思考标准**: 引导AI在日志中展示其思考过程，便于分析和回溯。
- **操作约束**: 明确规定所有操作必须通过工具调用完成，这确保了交易的规范性和可记录性。
- **信息输入**:
    - `{date}`: 当天日期。
    - `{positions}`: 昨收持仓，是决策的起点。
    - `{yesterday_close_price}` 和 `{today_buy_price}`: 价格信息，用于计算估值和交易成本。
- **停止信号**: `{STOP_SIGNAL}` (`<FINISH_SIGNAL>`) 是一个明确的指令，用于结束当天的交易循环，避免不必要的资源消耗。

通过这个精心设计的提示词，AI-Trader项目引导AI代理在模拟的金融市场中，以一种接近人类基本面分析师的方式进行思考和交易。
