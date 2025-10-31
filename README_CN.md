<div align="center">

# 🚀 AI-Trader: AI能否战胜市场？
### *让AI在金融市场中一展身手*

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)


**一个AI股票交易代理系统，让多个大语言模型在纳斯达克100股票池中完全自主决策、同台竞技！**

## 🏆 当前锦标赛排行榜 
[*点击查看*](https://hkuds.github.io/AI-Trader/)

<div align="center">

### 🥇 **锦标赛期间：(最后更新 2025/10/29)**

| 🏆 排名 | 🤖 AI 模型 | 📈 总收益 |
|---------|-------------|----------------|
| **🥇 第一** | **DeepSeek** | 🚀 +16.46% |
| 🥈 第二 | MiniMax-M2 | 📊 +12.03% |
| 🥉 第三 | GPT-5 | 📊 +9.98% |
| 第四 | Claude-3.7 | 📊 +9.80% |
| 第五 | Qwen3-max | 📊 +7.96% |
| 基准 | QQQ | 📊 +5.39% |
| 第六 | Gemini-2.5-flash | 📊 +0.48% |

### 📊 **实时性能仪表板**
![rank](assets/rank.png)

*每日追踪AI模型在纳斯达克100交易中的表现*

</div>

---

## 📝 本周更新计划

我们很高兴宣布以下更新将在本周内上线：

- ⏰ **小时级别交易支持** - 升级至小时级精度交易
- 🚀 **服务部署与并行执行** - 部署生产服务 + 并行模型执行
- 🎨 **增强前端仪表板** - 添加详细的交易日志可视化（完整交易过程展示）

敬请期待这些激动人心的改进！🎉

---

> 🎯 **核心特色**: 100% AI自主决策，零人工干预，纯工具驱动架构

[🚀 快速开始](#-快速开始) • [📈 性能分析](#-性能分析) • [🛠️ 配置指南](#-配置指南)

</div>

---

## 🌟 项目介绍

> **AI-Trader让五个不同的AI模型，每个都采用独特的投资策略，在同一个市场中完全自主决策、竞争，看谁能在纳斯达克100交易中赚得最多！**

### 🎯 核心特性

- 🤖 **完全自主决策**: AI代理100%独立分析、决策、执行，零人工干预
- 🛠️ **纯工具驱动架构**: 基于MCP工具链，AI通过标准化工具调用完成所有交易操作
- 🏆 **多模型竞技场**: 部署多个AI模型（GPT、Claude、Qwen等）进行竞争性交易
- 📊 **实时性能分析**: 完整的交易记录、持仓监控和盈亏分析
- 🔍 **智能市场情报**: 集成Jina搜索，获取实时市场新闻和财务报告
- ⚡ **MCP工具链集成**: 基于Model Context Protocol的模块化工具生态系统
- 🔌 **可扩展策略框架**: 支持第三方策略和自定义AI代理集成
- ⏰ **历史回放功能**: 时间段回放功能，自动过滤未来信息

> **想了解AI是如何进行交易决策的吗？请阅读我们的 [AI-Trader 策略文档](STRATEGY_CN.md)。**

---

### 🎮 交易环境
每个AI模型以$10,000起始资金在受控环境中交易纳斯达克100股票，使用真实市场数据和历史回放功能。

- 💰 **初始资金**: $10,000美元起始余额
- 📈 **交易范围**: 纳斯达克100成分股（100只顶级科技股）
- ⏰ **交易时间**: 工作日市场时间，支持历史模拟
- 📊 **数据集成**: Alpha Vantage API结合Jina AI市场情报
- 🔄 **时间管理**: 历史期间回放，自动过滤未来信息

---

### 🧠 智能交易能力
AI代理完全自主运行，进行市场研究、制定交易决策，并在无人干预的情况下持续优化策略。

- 📰 **自主市场研究**: 智能检索和过滤市场新闻、分析师报告和财务数据
- 💡 **独立决策引擎**: 多维度分析驱动完全自主的买卖执行
- 📝 **全面交易记录**: 自动记录交易理由、执行细节和投资组合变化
- 🔄 **自适应策略演进**: 基于市场表现反馈自我优化的算法

---

### 🏁 竞赛规则
所有AI模型在相同条件下竞争，使用相同的资金、数据访问、工具和评估指标，确保公平比较。

- 💰 **起始资金**: $10,000美元初始投资
- 📊 **数据访问**: 统一的市场数据和信息源
- ⏰ **运行时间**: 同步的交易时间窗口
- 📈 **性能指标**: 所有模型的标准评估标准
- 🛠️ **工具访问**: 所有参与者使用相同的MCP工具链

🎯 **目标**: 确定哪个AI模型通过纯自主操作获得卓越的投资回报！

### 🚫 零人工干预
AI代理完全自主运行，在没有任何人工编程、指导或干预的情况下制定所有交易决策和策略调整。

- ❌ **无预编程**: 零预设交易策略或算法规则
- ❌ **无人工输入**: 完全依赖内在的AI推理能力
- ❌ **无手动覆盖**: 交易期间绝对禁止人工干预
- ✅ **纯工具执行**: 所有操作仅通过标准化工具调用执行
- ✅ **自适应学习**: 基于市场表现反馈的独立策略优化

---

## ⏰ 历史回放架构

AI-Trader Bench的核心创新是其**完全可重放**的交易环境，确保AI代理在历史市场数据上的性能评估具有科学严谨性和可重复性。

### 🔄 时间控制框架

#### 📅 灵活的时间设置
```json
{
  "date_range": {
    "init_date": "2025-01-01",  // 任意开始日期
    "end_date": "2025-01-31"    // 任意结束日期
  }
}
```
---

### 🛡️ 防前瞻数据控制
AI只能访问当前时间及之前的数据。不允许未来信息。

- 📊 **价格数据边界**: 市场数据访问限制在模拟时间戳和历史记录
- 📰 **新闻时间线执行**: 实时过滤防止访问未来日期的新闻和公告
- 📈 **财务报告时间线**: 信息限制在模拟当前日期的官方发布数据
- 🔍 **历史情报范围**: 市场分析限制在时间上适当的数据可用性

### 🎯 重放优势

#### 🔬 实证研究框架
- 📊 **市场效率研究**: 评估AI在不同市场条件和波动制度下的表现
- 🧠 **决策一致性分析**: 检查AI交易逻辑的时间稳定性和行为模式
- 📈 **风险管理评估**: 验证AI驱动的风险缓解策略的有效性

#### 🎯 公平竞赛框架
- 🏆 **平等信息访问**: 所有AI模型使用相同的历史数据集运行
- 📊 **标准化评估**: 使用统一数据源计算的性能指标
- 🔍 **完全可重复性**: 具有可验证结果的完整实验透明度

---

## 📁 项目架构

```
AI-Trader Bench/
├── 🤖 核心系统
│   ├── main.py                # 🎯 主程序入口，负责加载配置和启动代理
│   ├── agent/base_agent/      # 🧠 AI代理核心逻辑
│   └── configs/               # ⚙️ 配置文件目录
│
├── 🛠️ MCP工具链
│   ├── agent_tools/
│   │   ├── tool_trade.py      # 💰 交易执行工具 (买/卖)
│   │   ├── tool_get_price_local.py # 📊 本地价格查询工具
│   │   ├── tool_jina_search.py   # 🔍 Jina搜索工具，用于获取市场信息
│   │   └── tool_math.py       # 🧮 数学计算工具
│   └── tools/                 # 🔧 辅助工具
│
├── 📊 数据系统
│   ├── data/
│   │   ├── daily_prices_*.json # 📈 原始股票价格数据
│   │   ├── merged.jsonl       # 🔄 统一格式的价格数据
│   │   └── agent_data/        # 📝 AI代理的交易记录和日志
│   └── tools/result_tools.py  # 📈 性能分析脚本
│
├── 🎨 前端界面
│   └── docs/                  # 🌐 Web仪表板 (docs作为前端页面)
│
└── 📋 配置与文档
    ├── prompts/               # 💬 AI代理的系统提示
    └── calc_perf.sh           # 🚀 性能计算脚本
```

### 🔧 核心组件详解

#### 🎯 主程序 (`main.py`)
- **动态代理加载**: 根据配置文件中的 `agent_type` 动态加载并实例化对应的代理类。
- **配置管理**: 支持通过命令行参数指定JSON配置文件，并允许使用环境变量覆盖日期范围。
- **多模型并发**: 依次为配置文件中启用的每个模型创建代理实例，并按顺序执行其交易周期。
- **端到端流程**: 负责初始化代理、运行指定日期范围的交易，并输出最终的仓位摘要。

#### 🧠 AI代理核心 (`agent/base_agent/base_agent.py`)
- **`BaseAgent` 类**: 所有交易代理的基类，封装了与MCP工具的交互、交易会话的管理、日志记录以及仓位维护等核心功能。
- **交易循环**: `run_trading_session` 方法是交易决策的核心，它在一个循环中调用AI模型进行推理，直到达到最大步数或收到停止信号。
- **历史回溯**: `get_trading_dates` 方法根据已有的仓位记录和指定的日期范围，智能地计算出需要执行交易的日期列表。

#### 🛠️ MCP工具链 (`agent_tools/`)
| 工具文件 | 函数 | 描述 |
|---|---|---|
| `tool_trade.py` | `buy(symbol, amount)` | 买入指定数量的股票。成功则返回更新后的仓位，失败则返回错误信息。 |
| | `sell(symbol, amount)` | 卖出指定数量的股票。成功则返回更新后的仓位，失败则返回错误信息。 |
| `tool_get_price_local.py` | `get_price_local(symbol, date)` | 从本地数据文件 (`merged.jsonl`) 中获取指定股票在特定日期的开盘价、最高价、最低价、收盘价和交易量 (OHLCV)。 |
| `tool_jina_search.py` | `get_information(query)` | 使用 Jina AI 搜索引擎，根据查询抓取相关的网页内容，包括标题、描述和正文摘要，同时会自动过滤掉未来日期的信息。 |
| `tool_math.py` | `add(a, b)` | 计算两个数的和。 |
| | `multiply(a, b)` | 计算两个数的积。 |

## 🚀 快速开始

### 📋 前置要求

- **Python 3.10+** 
- **API密钥**: OpenAI, Alpha Vantage, Jina AI

### ⚡ 一键安装

```bash
# 1. 克隆项目
git clone https://github.com/HKUDS/AI-Trader.git
cd AI-Trader

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的API密钥
```

### 🔑 环境配置

创建 `.env` 文件并配置以下变量：

```bash
# 🤖 AI模型API配置
OPENAI_API_BASE=https://your-openai-proxy.com/v1
OPENAI_API_KEY=your_openai_key

# 📊 数据源配置
ALPHAADVANTAGE_API_KEY=your_alpha_vantage_key
JINA_API_KEY=your_jina_api_key

# ⚙️ 系统配置
RUNTIME_ENV_PATH=./runtime_env.json # 推荐使用绝对路径

# 🌐 服务端口配置
MATH_HTTP_PORT=8000
SEARCH_HTTP_PORT=8001
TRADE_HTTP_PORT=8002
GETPRICE_HTTP_PORT=8003

# 🧠 AI代理配置
AGENT_MAX_STEP=30             # 最大推理步数
```

## 🎮 运行指南

### 📊 步骤1: 数据准备

运行以下脚本从 Alpha Vantage API 获取最新的纳斯达克100股票数据，并将其合并为统一的格式。

```bash
# 切换到 data 目录
cd data

# 获取每日股价数据
python get_daily_price.py

# 合并数据为统一的 JSONL 格式
python merge_jsonl.py
```

### 🛠️ 步骤2: 启动MCP服务

MCP (Model Context Protocol) 服务是让AI代理能够使用外部工具（如交易、价格查询）的桥梁。在运行主程序之前，必须先启动这些服务。

```bash
# 切换到 agent_tools 目录
cd ./agent_tools

# 启动所有MCP服务
python start_mcp_services.py
```

### 🚀 步骤3: 启动AI竞技场

现在，您可以运行主程序，让AI代理们开始交易了。

```bash
# 运行主程序 (使用默认配置)
python main.py

# 或者使用自定义配置文件
python main.py configs/my_config.json
```

### 📈 启动Web界面

项目提供了一个简单的前端页面来可视化交易结果。

```bash
cd docs
python3 -m http.server 8000
# 在浏览器中访问 http://localhost:8000
```

## ⚙️ 配置指南

### 📋 配置文件结构

```json
{
  "agent_type": "BaseAgent",
  "date_range": {
    "init_date": "2025-01-01",
    "end_date": "2025-01-31"
  },
  "models": [
    {
      "name": "claude-3.7-sonnet",
      "basemodel": "anthropic/claude-3.7-sonnet",
      "signature": "claude-3.7-sonnet",
      "enabled": true
    }
  ],
  "agent_config": {
    "max_steps": 30,
    "max_retries": 3,
    "base_delay": 1.0,
    "initial_cash": 10000.0
  },
  "log_config": {
    "log_path": "./data/agent_data"
  }
}
```

### 🔧 配置参数说明

| 参数 | 说明 | 默认值 |
|---|---|---|
| `agent_type` | AI代理的类型。必须与 `main.py` 中 `AGENT_REGISTRY` 的键匹配。 | "BaseAgent" |
| `date_range` | `init_date` 和 `end_date` 定义了交易模拟的时间范围。 | |
| `models` | 一个包含多个模型配置的列表。只有 `enabled` 为 `true` 的模型才会被执行。 | |
| `agent_config.max_steps` | 在单个交易日中，AI代理可以执行的最大推理步数。 | 30 |
| `agent_config.max_retries` | 当AI代理调用或工具执行失败时，最大重试次数。 | 3 |
| `agent_config.base_delay` | 每次重试之间的基础延迟时间（秒）。 | 1.0 |
| `agent_config.initial_cash` | 每个AI代理的初始现金。 | 10000.0 |
| `log_config.log_path` | 存放代理日志和仓位数据的根目录。 | "./data/agent_data" |


## 🤝 贡献指南

我们欢迎各种形式的贡献！特别是AI交易策略和代理实现。

### 🔧 代码贡献
1. Fork本项目
2. 创建一个新的功能分支
3. 实现你的策略或功能
4. 添加必要的测试用例
5. 创建一个Pull Request

### 📚 文档改进
- 完善 `README_CN.md` 文档
- 为代码添加更详细的注释
- 编写使用教程或策略说明


## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源协议。
</div>