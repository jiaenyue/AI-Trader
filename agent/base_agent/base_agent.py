"""
BaseAgent 类 - 交易代理的基类
封装了核心功能，包括 MCP 工具管理、AI 代理创建和交易执行。
"""

import os
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from dotenv import load_dotenv

# 导入项目工具
import sys
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from tools.general_tools import extract_conversation, extract_tool_messages, get_config_value, write_config_value
from tools.price_tools import add_no_trade_record
from prompts.agent_prompt import get_agent_system_prompt, STOP_SIGNAL

# 加载环境变量
load_dotenv()


class BaseAgent:
    """
    交易代理的基类。

    主要功能:
    1. MCP 工具管理和连接。
    2. AI 代理的创建和配置。
    3. 交易执行和决策循环。
    4. 日志记录和管理。
    5. 仓位和配置管理。
    """
    
    # 默认的纳斯达克 100 股票代码
    DEFAULT_STOCK_SYMBOLS = [
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
    
    def __init__(
        self,
        signature: str,
        basemodel: str,
        stock_symbols: Optional[List[str]] = None,
        mcp_config: Optional[Dict[str, Dict[str, Any]]] = None,
        log_path: Optional[str] = None,
        max_steps: int = 10,
        max_retries: int = 3,
        base_delay: float = 0.5,
        openai_base_url: Optional[str] = None,
        openai_api_key: Optional[str] = None,
        initial_cash: float = 10000.0,
        init_date: str = "2025-10-13"
    ):
        """
        初始化 BaseAgent。

        Args:
            signature (str): 代理的签名/名称。
            basemodel (str): 基础模型的名称。
            stock_symbols (Optional[List[str]]): 股票代码列表，默认为纳斯达克 100 指数成分股。
            mcp_config (Optional[Dict[str, Dict[str, Any]]]): MCP 工具配置，包括端口和 URL 信息。
            log_path (Optional[str]): 日志路径，默认为 ./data/agent_data。
            max_steps (int): 最大推理步数。
            max_retries (int): 最大重试次数。
            base_delay (float): 重试的基础延迟时间。
            openai_base_url (Optional[str]): OpenAI API 的基础 URL。
            openai_api_key (Optional[str]): OpenAI API 密钥。
            initial_cash (float): 初始现金金额。
            init_date (str): 初始化日期。
        """
        self.signature = signature
        self.basemodel = basemodel
        self.stock_symbols = stock_symbols or self.DEFAULT_STOCK_SYMBOLS
        self.max_steps = max_steps
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.initial_cash = initial_cash
        self.init_date = init_date
        
        # 设置 MCP 配置
        self.mcp_config = mcp_config or self._get_default_mcp_config()
        
        # 设置日志路径
        self.base_log_path = log_path or "./data/agent_data"
        
        # 设置 OpenAI 配置
        if openai_base_url==None:
            self.openai_base_url = os.getenv("OPENAI_API_BASE")
        else:
            self.openai_base_url = openai_base_url
        if openai_api_key==None:
            self.openai_api_key = os.getenv("OPENAI_API_KEY")
        else:
            self.openai_api_key = openai_api_key
        
        # 初始化组件
        self.client: Optional[MultiServerMCPClient] = None
        self.tools: Optional[List] = None
        self.model: Optional[ChatOpenAI] = None
        self.agent: Optional[Any] = None
        
        # 数据路径
        self.data_path = os.path.join(self.base_log_path, self.signature)
        self.position_file = os.path.join(self.data_path, "position", "position.jsonl")
        
    def _get_default_mcp_config(self) -> Dict[str, Dict[str, Any]]:
        """
        获取默认的 MCP 配置。

        Returns:
            Dict[str, Dict[str, Any]]: 包含各工具服务 URL 的配置字典。
        """
        return {
            "math": {
                "transport": "streamable_http",
                "url": f"http://localhost:{os.getenv('MATH_HTTP_PORT', '8000')}/mcp",
            },
            "stock_local": {
                "transport": "streamable_http",
                "url": f"http://localhost:{os.getenv('GETPRICE_HTTP_PORT', '8003')}/mcp",
            },
            "search": {
                "transport": "streamable_http",
                "url": f"http://localhost:{os.getenv('SEARCH_HTTP_PORT', '8001')}/mcp",
            },
            "trade": {
                "transport": "streamable_http",
                "url": f"http://localhost:{os.getenv('TRADE_HTTP_PORT', '8002')}/mcp",
            },
        }
    
    async def initialize(self) -> None:
        """
        异步初始化 MCP 客户端和 AI 模型。

        Raises:
            ValueError: 如果 OpenAI API 密钥未设置。
            RuntimeError: 如果 MCP 客户端或 AI 模型初始化失败。
        """
        print(f"🚀 Initializing agent: {self.signature}")
        
        # 验证 OpenAI 配置
        if not self.openai_api_key:
            raise ValueError("❌ OpenAI API key not set. Please configure OPENAI_API_KEY in environment or config file.")
        if not self.openai_base_url:
            print("⚠️  OpenAI base URL not set, using default")
        
        try:
            # 创建 MCP 客户端
            self.client = MultiServerMCPClient(self.mcp_config)
            
            # 获取工具
            self.tools = await self.client.get_tools()
            if not self.tools:
                print("⚠️  Warning: No MCP tools loaded. MCP services may not be running.")
                print(f"   MCP configuration: {self.mcp_config}")
            else:
                print(f"✅ Loaded {len(self.tools)} MCP tools")
        except Exception as e:
            raise RuntimeError(
                f"❌ Failed to initialize MCP client: {e}\n"
                f"   Please ensure MCP services are running at the configured ports.\n"
                f"   Run: python agent_tools/start_mcp_services.py"
            )
        
        try:
            # 创建 AI 模型
            self.model = ChatOpenAI(
                model=self.basemodel,
                base_url=self.openai_base_url,
                api_key=self.openai_api_key,
                max_retries=3,
                timeout=30
            )
        except Exception as e:
            raise RuntimeError(f"❌ Failed to initialize AI model: {e}")
        
        # 注意：代理将在 run_trading_session() 中根据特定日期创建
        # 因为 system_prompt 需要当前日期和价格信息
        
        print(f"✅ Agent {self.signature} initialization completed")
    
    def _setup_logging(self, today_date: str) -> str:
        """
        设置并返回当天的日志文件路径。

        Args:
            today_date (str): 当前日期，格式为 "YYYY-MM-DD"。

        Returns:
            str: 日志文件的完整路径。
        """
        log_path = os.path.join(self.base_log_path, self.signature, 'log', today_date)
        if not os.path.exists(log_path):
            os.makedirs(log_path)
        return os.path.join(log_path, "log.jsonl")
    
    def _log_message(self, log_file: str, new_messages: List[Dict[str, str]]) -> None:
        """
        将消息记录到指定的日志文件中。

        Args:
            log_file (str): 日志文件的路径。
            new_messages (List[Dict[str, str]]): 要记录的新消息列表。
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "signature": self.signature,
            "new_messages": new_messages
        }
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    async def _ainvoke_with_retry(self, message: List[Dict[str, str]]) -> Any:
        """
        带重试逻辑的异步代理调用。

        Args:
            message (List[Dict[str, str]]): 发送给代理的消息。

        Returns:
            Any: 代理的响应。

        Raises:
            Exception: 如果所有重试都失败。
        """
        for attempt in range(1, self.max_retries + 1):
            try:
                return await self.agent.ainvoke(
                    {"messages": message}, 
                    {"recursion_limit": 100}
                )
            except Exception as e:
                if attempt == self.max_retries:
                    raise e
                print(f"⚠️ Attempt {attempt} failed, retrying after {self.base_delay * attempt} seconds...")
                print(f"Error details: {e}")
                await asyncio.sleep(self.base_delay * attempt)
    
    async def run_trading_session(self, today_date: str) -> None:
        """
        运行单日的交易会话。

        Args:
            today_date (str): 当前交易日期，格式为 "YYYY-MM-DD"。
        """
        print(f"📈 Starting trading session: {today_date}")
        
        # 设置日志
        log_file = self._setup_logging(today_date)
        
        # 更新系统提示并创建代理
        self.agent = create_agent(
            self.model,
            tools=self.tools,
            system_prompt=get_agent_system_prompt(today_date, self.signature),
        )
        
        # 初始用户查询
        user_query = [{"role": "user", "content": f"Please analyze and update today's ({today_date}) positions."}]
        message = user_query.copy()
        
        # 记录初始消息
        self._log_message(log_file, user_query)
        
        # 交易循环
        current_step = 0
        while current_step < self.max_steps:
            current_step += 1
            print(f"🔄 Step {current_step}/{self.max_steps}")
            
            try:
                # 调用代理
                response = await self._ainvoke_with_retry(message)
                
                # 提取代理响应
                agent_response = extract_conversation(response, "final")
                
                # 检查停止信号
                if STOP_SIGNAL in agent_response:
                    print("✅ Received stop signal, trading session ended")
                    print(agent_response)
                    self._log_message(log_file, [{"role": "assistant", "content": agent_response}])
                    break
                
                # 提取工具消息
                tool_msgs = extract_tool_messages(response)
                tool_response = '\n'.join([msg.content for msg in tool_msgs])
                
                # 准备新消息
                new_messages = [
                    {"role": "assistant", "content": agent_response},
                    {"role": "user", "content": f'Tool results: {tool_response}'}
                ]
                
                # 添加新消息
                message.extend(new_messages)
                
                # 记录消息
                self._log_message(log_file, new_messages[0])
                self._log_message(log_file, new_messages[1])
                
            except Exception as e:
                print(f"❌ Trading session error: {str(e)}")
                print(f"Error details: {e}")
                raise
        
        # 处理交易结果
        await self._handle_trading_result(today_date)
    
    async def _handle_trading_result(self, today_date: str) -> None:
        """
        处理单日交易会话结束后的结果。
        如果发生了交易，则记录；否则，记录为无交易日。

        Args:
            today_date (str): 当前交易日期。
        """
        if_trade = get_config_value("IF_TRADE")
        if if_trade:
            write_config_value("IF_TRADE", False)
            print("✅ Trading completed")
        else:
            print("📊 No trading, maintaining positions")
            try:
                add_no_trade_record(today_date, self.signature)
            except NameError as e:
                print(f"❌ NameError: {e}")
                raise
            write_config_value("IF_TRADE", False)
    
    def register_agent(self) -> None:
        """
        注册新代理。如果仓位文件不存在，则创建初始仓位文件。
        """
        # 检查仓位文件是否已存在
        if os.path.exists(self.position_file):
            print(f"⚠️ Position file {self.position_file} already exists, skipping registration")
            return
        
        # 确保目录结构存在
        position_dir = os.path.join(self.data_path, "position")
        if not os.path.exists(position_dir):
            os.makedirs(position_dir)
            print(f"📁 Created position directory: {position_dir}")
        
        # 创建初始仓位
        init_position = {symbol: 0 for symbol in self.stock_symbols}
        init_position['CASH'] = self.initial_cash
        
        with open(self.position_file, "w") as f:  # 使用 "w" 模式确保创建新文件
            f.write(json.dumps({
                "date": self.init_date, 
                "id": 0, 
                "positions": init_position
            }) + "\n")
        
        print(f"✅ Agent {self.signature} registration completed")
        print(f"📁 Position file: {self.position_file}")
        print(f"💰 Initial cash: ${self.initial_cash}")
        print(f"📊 Number of stocks: {len(self.stock_symbols)}")
    
    def get_trading_dates(self, init_date: str, end_date: str) -> List[str]:
        """
        获取指定日期范围内的交易日期列表（周一至周五）。

        Args:
            init_date (str): 开始日期，格式为 "YYYY-MM-DD"。
            end_date (str): 结束日期，格式为 "YYYY-MM-DD"。
            
        Returns:
            List[str]: 交易日期字符串列表。
        """
        max_date = None
        
        if not os.path.exists(self.position_file):
            self.register_agent()
            max_date = self.init_date
        else:
            # 读取现有仓位文件，找到最新日期
            with open(self.position_file, "r") as f:
                lines = f.readlines()
                if lines:
                    last_line = lines[-1]
                    doc = json.loads(last_line)
                    max_date = doc['date']

        if max_date is None:
            max_date = init_date

        # 检查是否需要处理新日期
        max_date_obj = datetime.strptime(max_date, "%Y-%m-%d")
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
        
        if end_date_obj <= max_date_obj:
            return []
        
        # 生成交易日期列表
        trading_dates = []
        current_date = max_date_obj + timedelta(days=1)
        
        while current_date <= end_date_obj:
            if current_date.weekday() < 5:  # 周一至周五
                trading_dates.append(current_date.strftime("%Y-%m-%d"))
            current_date += timedelta(days=1)
        
        return trading_dates
    
    async def run_with_retry(self, today_date: str) -> None:
        """
        带重试逻辑的运行方法，用于执行单个交易日的会话。

        Args:
            today_date (str): 要运行的交易日期。
        """
        for attempt in range(1, self.max_retries + 1):
            try:
                print(f"🔄 Attempting to run {self.signature} - {today_date} (Attempt {attempt})")
                await self.run_trading_session(today_date)
                print(f"✅ {self.signature} - {today_date} run successful")
                return
            except Exception as e:
                print(f"❌ Attempt {attempt} failed: {str(e)}")
                if attempt == self.max_retries:
                    print(f"💥 {self.signature} - {today_date} all retries failed")
                    raise
                else:
                    wait_time = self.base_delay * attempt
                    print(f"⏳ Waiting {wait_time} seconds before retry...")
                    await asyncio.sleep(wait_time)
    
    async def run_date_range(self, init_date: str, end_date: str) -> None:
        """
        运行指定日期范围内的所有交易日。

        Args:
            init_date (str): 开始日期，格式为 "YYYY-MM-DD"。
            end_date (str): 结束日期，格式为 "YYYY-MM-DD"。
        """
        print(f"📅 Running date range: {init_date} to {end_date}")
        
        # 获取交易日期列表
        trading_dates = self.get_trading_dates(init_date, end_date)
        
        if not trading_dates:
            print(f"ℹ️ No trading days to process")
            return
        
        print(f"📊 Trading days to process: {trading_dates}")
        
        # 处理每个交易日
        for date in trading_dates:
            print(f"🔄 Processing {self.signature} - Date: {date}")
            
            # 设置配置
            write_config_value("TODAY_DATE", date)
            write_config_value("SIGNATURE", self.signature)
            
            try:
                await self.run_with_retry(date)
            except Exception as e:
                print(f"❌ Error processing {self.signature} - Date: {date}")
                print(e)
                raise
        
        print(f"✅ {self.signature} processing completed")
    
    def get_position_summary(self) -> Dict[str, Any]:
        """
        获取最新的仓位摘要。

        Returns:
            Dict[str, Any]: 包含最新仓位信息的字典。如果文件不存在或为空，则返回错误信息。
        """
        if not os.path.exists(self.position_file):
            return {"error": "Position file does not exist"}
        
        positions = []
        with open(self.position_file, "r") as f:
            for line in f:
                positions.append(json.loads(line))
        
        if not positions:
            return {"error": "No position records"}
        
        latest_position = positions[-1]
        return {
            "signature": self.signature,
            "latest_date": latest_position.get("date"),
            "positions": latest_position.get("positions", {}),
            "total_records": len(positions)
        }
    
    def __str__(self) -> str:
        """
        返回代理的字符串表示形式。

        Returns:
            str: 代理的描述字符串。
        """
        return f"BaseAgent(signature='{self.signature}', basemodel='{self.basemodel}', stocks={len(self.stock_symbols)})"
    
    def __repr__(self) -> str:
        """
        返回代理的官方字符串表示形式。

        Returns:
            str: 代理的官方表示字符串。
        """
        return self.__str__()
