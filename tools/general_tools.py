
import os
import json
from typing import Any, Dict, List
from dotenv import load_dotenv
load_dotenv()

def _load_runtime_env() -> dict:
    """
    加载运行时环境配置文件。

    从 `RUNTIME_ENV_PATH` 环境变量指定的路径加载 JSON 文件。

    Returns:
        dict: 如果文件存在且格式正确，则返回文件内容的字典；否则返回空字典。
    """
    path = os.environ.get("RUNTIME_ENV_PATH")
    if path is None:
        return {}
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
    except Exception:
        pass
    return {}


def get_config_value(key: str, default=None) -> Any:
    """
    获取配置值。

    首先尝试从运行时环境文件获取，如果未找到，则回退到环境变量。

    Args:
        key (str): 配置项的键。
        default (Any, optional): 如果未找到键，则返回的默认值。默认为 None。

    Returns:
        Any: 配置项的值。
    """
    _RUNTIME_ENV = _load_runtime_env()
    
    if key in _RUNTIME_ENV:
        return _RUNTIME_ENV[key]
    return os.getenv(key, default)

def write_config_value(key: str, value: Any) -> None:
    """
    将配置值写入运行时环境文件。

    如果 `RUNTIME_ENV_PATH` 环境变量未设置，则无法持久化配置。

    Args:
        key (str): 配置项的键。
        value (Any): 要写入的值。
    """
    path = os.environ.get("RUNTIME_ENV_PATH")
    if path is None:
        print(f"⚠️  警告: RUNTIME_ENV_PATH 未设置，配置值 '{key}' 未持久化")
        return
    _RUNTIME_ENV = _load_runtime_env()
    _RUNTIME_ENV[key] = value
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(_RUNTIME_ENV, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"❌ 写入配置到 {path} 时出错: {e}")

def extract_conversation(conversation: dict, output_type: str) -> Any:
    """
    从对话负载中提取信息。

    Args:
        conversation (dict): 一个包含 'messages' 键的映射（消息列表）。
        output_type (str): 'final' 返回模型的最终答案内容；'all' 返回完整的消息列表。

    Returns:
        Any:
          - 对于 'final': 如果找到，则为最终的助手内容字符串；否则为 None。
          - 对于 'all': 原始消息列表（如果缺少则为空列表）。
    """

    def get_field(obj, key, default=None):
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    messages = get_field(conversation, "messages", []) or []

    if output_type == "all":
        return messages

    if output_type == "final":
        # 查找最后一条带有 'tool_calls' 的消息，并返回其内容
        for msg in reversed(messages):
            additional_kwargs = get_field(msg, "additional_kwargs", {})
            if isinstance(additional_kwargs, dict) and "tool_calls" in additional_kwargs:
                return get_field(msg, "content")

        # 回退：返回最后一条非工具消息的内容
        for msg in reversed(messages):
            if not get_field(msg, "tool_call_id"):
                 content = get_field(msg, "content")
                 if isinstance(content, str) and content.strip():
                    return content

        return None

    raise ValueError("output_type 必须是 'final' 或 'all'")


def extract_tool_messages(conversation: dict) -> List[Dict]:
    """
    从对话中返回所有类似工具消息的条目。

    工具消息通过以下启发式方法识别：
      - 具有非空的 'tool_call_id'，或
      - 具有字符串 'name'（工具名称）

    支持基于字典和基于对象的两种消息格式。

    Args:
        conversation (dict): 包含消息列表的对话。

    Returns:
        List[Dict]: 工具消息的列表。
    """
    def get_field(obj, key, default=None):
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    messages = get_field(conversation, "messages", []) or []
    tool_messages = []
    for msg in messages:
        if get_field(msg, "tool_call_id") or get_field(msg, "name"):
            tool_messages.append(msg)
    return tool_messages


def extract_first_tool_message_content(conversation: dict) -> Any:
    """
    如果可用，则返回第一条工具消息的内容，否则返回 None。

    Args:
        conversation (dict): 包含消息列表的对话。

    Returns:
        Any: 第一条工具消息的内容，如果不存在则为 None。
    """
    msgs = extract_tool_messages(conversation)
    if not msgs:
        return None

    first = msgs[0]
    if isinstance(first, dict):
        return first.get("content")
    return getattr(first, "content", None)
