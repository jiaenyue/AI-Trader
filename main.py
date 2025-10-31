import os
import asyncio
from datetime import datetime
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# 导入工具和提示
from tools.general_tools import write_config_value
from prompts.agent_prompt import all_nasdaq_100_symbols


# 代理类映射表 - 用于动态导入和实例化
AGENT_REGISTRY = {
    "BaseAgent": {
        "module": "agent.base_agent.base_agent",
        "class": "BaseAgent"
    },
}


def get_agent_class(agent_type):
    """
    根据代理类型名称动态导入并返回相应的类。

    Args:
        agent_type (str): 代理类型名称 (例如, "BaseAgent")。

    Returns:
        type: 代理的类定义。

    Raises:
        ValueError: 如果代理类型不受支持。
        ImportError: 如果无法导入代理模块。
        AttributeError: 如果在模块中找不到指定的类。
    """
    if agent_type not in AGENT_REGISTRY:
        supported_types = ", ".join(AGENT_REGISTRY.keys())
        raise ValueError(
            f"❌ 不支持的代理类型: {agent_type}\n"
            f"   支持的类型: {supported_types}"
        )
    
    agent_info = AGENT_REGISTRY[agent_type]
    module_path = agent_info["module"]
    class_name = agent_info["class"]
    
    try:
        import importlib
        module = importlib.import_module(module_path)
        agent_class = getattr(module, class_name)
        print(f"✅ 成功加载代理类: {agent_type} (来自 {module_path})")
        return agent_class
    except ImportError as e:
        raise ImportError(f"❌ 无法导入代理模块 {module_path}: {e}")
    except AttributeError as e:
        raise AttributeError(f"❌ 在模块 {module_path} 中未找到类 {class_name}: {e}")


def load_config(config_path=None):
    """
    从 configs 目录加载配置文件。

    Args:
        config_path (str, optional): 配置文件路径。如果为 None，则使用默认配置。

    Returns:
        dict: 配置字典。
    """
    if config_path is None:
        config_path = Path(__file__).parent / "configs" / "default_config.json"
    else:
        config_path = Path(config_path)
    
    if not config_path.exists():
        print(f"❌ 配置文件不存在: {config_path}")
        exit(1)
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print(f"✅ 成功加载配置文件: {config_path}")
        return config
    except json.JSONDecodeError as e:
        print(f"❌ 配置文件 JSON 格式错误: {e}")
        exit(1)
    except Exception as e:
        print(f"❌ 加载配置文件失败: {e}")
        exit(1)


async def main(config_path=None):
    """
    使用 BaseAgent 类运行交易实验。

    Args:
        config_path (str, optional): 配置文件路径。如果为 None，则使用默认配置。
    """
    config = load_config(config_path)
    
    agent_type = config.get("agent_type", "BaseAgent")
    try:
        AgentClass = get_agent_class(agent_type)
    except (ValueError, ImportError, AttributeError) as e:
        print(str(e))
        exit(1)
    
    INIT_DATE = config["date_range"]["init_date"]
    END_DATE = config["date_range"]["end_date"]
    
    if os.getenv("INIT_DATE"):
        INIT_DATE = os.getenv("INIT_DATE")
        print(f"⚠️  使用环境变量覆盖 INIT_DATE: {INIT_DATE}")
    if os.getenv("END_DATE"):
        END_DATE = os.getenv("END_DATE")
        print(f"⚠️  使用环境变量覆盖 END_DATE: {END_DATE}")
    
    INIT_DATE_obj = datetime.strptime(INIT_DATE, "%Y-%m-%d").date()
    END_DATE_obj = datetime.strptime(END_DATE, "%Y-%m-%d").date()
    if INIT_DATE_obj > END_DATE_obj:
        print("❌ INIT_DATE 大于 END_DATE")
        exit(1)
 
    enabled_models = [
        model for model in config["models"] 
        if model.get("enabled", True)
    ]
    
    agent_config = config.get("agent_config", {})
    log_config = config.get("log_config", {})
    max_steps = agent_config.get("max_steps", 10)
    max_retries = agent_config.get("max_retries", 3)
    base_delay = agent_config.get("base_delay", 0.5)
    initial_cash = agent_config.get("initial_cash", 10000.0)
    
    model_names = [m.get("name", m.get("signature")) for m in enabled_models]
    
    print("🚀 开始交易实验")
    print(f"🤖 代理类型: {agent_type}")
    print(f"📅 日期范围: {INIT_DATE} 到 {END_DATE}")
    print(f"🤖 模型列表: {model_names}")
    print(f"⚙️  代理配置: max_steps={max_steps}, max_retries={max_retries}, base_delay={base_delay}, initial_cash={initial_cash}")
                    
    for model_config in enabled_models:
        model_name = model_config.get("name", "unknown")
        basemodel = model_config.get("basemodel")
        signature = model_config.get("signature")
        openai_base_url = model_config.get("openai_base_url", None)
        openai_api_key = model_config.get("openai_api_key", None)

        if not basemodel:
            print(f"❌ 模型 {model_name} 缺少 basemodel 字段")
            continue
        if not signature:
            print(f"❌ 模型 {model_name} 缺少 signature 字段")
            continue
        
        print("=" * 60)
        print(f"🤖 正在处理模型: {model_name}")
        print(f"📝 签名: {signature}")
        print(f"🔧 基础模型: {basemodel}")
        
        write_config_value("SIGNATURE", signature)
        write_config_value("TODAY_DATE", END_DATE)
        write_config_value("IF_TRADE", False)

        log_path = log_config.get("log_path", "./data/agent_data")

        try:
            agent = AgentClass(
                signature=signature,
                basemodel=basemodel,
                stock_symbols=all_nasdaq_100_symbols,
                log_path=log_path,
                openai_base_url=openai_base_url,
                openai_api_key=openai_api_key,
                max_steps=max_steps,
                max_retries=max_retries,
                base_delay=base_delay,
                initial_cash=initial_cash,
                init_date=INIT_DATE
            )
            
            print(f"✅ {agent_type} 实例创建成功: {agent}")
            
            await agent.initialize()
            print("✅ 初始化成功")
            await agent.run_date_range(INIT_DATE, END_DATE)
            
            summary = agent.get_position_summary()
            print(f"📊 最终仓位摘要:")
            print(f"   - 最新日期: {summary.get('latest_date')}")
            print(f"   - 总记录数: {summary.get('total_records')}")
            print(f"   - 现金余额: ${summary.get('positions', {}).get('CASH', 0):.2f}")
            
        except Exception as e:
            print(f"❌ 处理模型 {model_name} ({signature}) 时出错: {str(e)}")
            print(f"📋 错误详情: {e}")
            exit()
        
        print("=" * 60)
        print(f"✅ 模型 {model_name} ({signature}) 处理完成")
        print("=" * 60)
    
    print("🎉 所有模型处理完成!")
    
if __name__ == "__main__":
    import sys
    
    config_path = sys.argv[1] if len(sys.argv) > 1 else None
    
    if config_path:
        print(f"📄 使用指定的配置文件: {config_path}")
    else:
        print(f"📄 使用默认配置文件: configs/default_config.json")
    
    asyncio.run(main(config_path))
