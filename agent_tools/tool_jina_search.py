from typing import Dict, Any, Optional, List
import os
import logging
import requests
from fastmcp import FastMCP
from dotenv import load_dotenv
load_dotenv()
import random
from datetime import datetime, timedelta
import re
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.general_tools import get_config_value

logger = logging.getLogger(__name__)


def parse_date_to_standard(date_str: str) -> str:
    """
    将各种日期格式转换为标准格式 (YYYY-MM-DD HH:MM:SS)。

    Args:
        date_str (str): 各种格式的日期字符串，例如 "2025-10-01T08:19:28+00:00", "4 hours ago", "1 day ago", "May 31, 2025"。

    Returns:
        str: 标准格式的日期时间字符串，例如 "2025-10-01 08:19:28"。
    """
    if not date_str or date_str == 'unknown':
        return 'unknown'
    
    # 处理相对时间格式
    if 'ago' in date_str.lower():
        try:
            now = datetime.now()
            if 'hour' in date_str.lower():
                hours = int(re.findall(r'\d+', date_str)[0])
                target_date = now - timedelta(hours=hours)
            elif 'day' in date_str.lower():
                days = int(re.findall(r'\d+', date_str)[0])
                target_date = now - timedelta(days=days)
            elif 'week' in date_str.lower():
                weeks = int(re.findall(r'\d+', date_str)[0])
                target_date = now - timedelta(weeks=weeks)
            elif 'month' in date_str.lower():
                months = int(re.findall(r'\d+', date_str)[0])
                target_date = now - timedelta(days=months * 30)  # 近似处理
            else:
                return 'unknown'
            return target_date.strftime('%Y-%m-%d %H:%M:%S')
        except Exception:
            pass
    
    # 处理 ISO 8601 格式
    try:
        if 'T' in date_str and ('+' in date_str or 'Z' in date_str or date_str.endswith('00:00')):
            if '+' in date_str:
                date_part = date_str.split('+')[0]
            elif 'Z' in date_str:
                date_part = date_str.replace('Z', '')
            else:
                date_part = date_str
            
            if '.' in date_part:
                parsed_date = datetime.strptime(date_part.split('.')[0], '%Y-%m-%dT%H:%M:%S')
            else:
                parsed_date = datetime.strptime(date_part, '%Y-%m-%dT%H:%M:%S')
            return parsed_date.strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        pass
    
    # 处理其他常见格式
    try:
        if ',' in date_str and len(date_str.split()) >= 3:
            parsed_date = datetime.strptime(date_str, '%b %d, %Y')
            return parsed_date.strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        pass
    
    try:
        if re.match(r'\d{4}-\d{2}-\d{2}$', date_str):
            parsed_date = datetime.strptime(date_str, '%Y-%m-%d')
            return parsed_date.strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        pass
    
    return date_str

class WebScrapingJinaTool:
    """
    一个使用 Jina AI API 进行网页搜索和内容提取的工具类。
    """
    def __init__(self):
        """
        初始化工具，并检查 JINA_API_KEY 是否已设置。
        """
        self.api_key = os.environ.get("JINA_API_KEY")
        if not self.api_key:
            raise ValueError("未提供 Jina API 密钥！请设置 JINA_API_KEY 环境变量。")

    def __call__(self, query: str) -> List[Dict[str, Any]]:
        """
        执行搜索和内容抓取。

        Args:
            query (str): 搜索查询。

        Returns:
            List[Dict[str, Any]]: 包含抓取内容的字典列表。
        """
        print(f"正在搜索: {query}")
        all_urls = self._jina_search(query)
        return_content = []
        print(f"找到 {len(all_urls)} 个 URL")
        if len(all_urls)>1:
            all_urls = random.sample(all_urls, 1)
        for url in all_urls:
            print(f"正在抓取: {url}")
            return_content.append(self._jina_scrape(url))
            print(f"已抓取: {url}")

        return return_content  

    def _jina_scrape(self, url: str) -> Dict[str, Any]:
        """
        使用 Jina AI Reader API 抓取单个 URL 的内容。

        Args:
            url (str): 要抓取的 URL。

        Returns:
            Dict[str, Any]: 包含 URL、标题、描述、内容和发布时间的字典。
        """
        try:
            jina_url = f'https://r.jina.ai/{url}'
            headers = {
                "Accept": "application/json",
                'Authorization': self.api_key,
                'X-Timeout': "10",
                "X-With-Generated-Alt": "true",
            }
            response = requests.get(jina_url, headers=headers)

            if response.status_code != 200:
                raise Exception(f"Jina AI Reader 在抓取 {url} 时失败: {response.status_code}")

            response_dict = response.json()

            return {
                'url': response_dict['data']['url'],
                'title': response_dict['data']['title'],
                'description': response_dict['data']['description'],
                'content': response_dict['data']['content'],
                'publish_time': response_dict['data'].get('publishedTime', 'unknown')
            }

        except Exception as e:
            logger.error(str(e))
            return {
                'url': url,
                'content': '',
                'error': str(e)
            }

    def _jina_search(self, query: str) -> List[str]:
        """
        使用 Jina AI Search API 搜索与查询相关的 URL。

        Args:
            query (str): 搜索查询。

        Returns:
            List[str]: URL 字符串列表。
        """
        url = f'https://s.jina.ai/?q={query}&n=1'
        headers = {
            'Authorization': f'Bearer {self.api_key}',        
            "Accept": "application/json",
            "X-Respond-With": "no-content"
        }
   
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            json_data = response.json()
            
            if json_data is None:
                print(f"⚠️ Jina API 返回空数据, 查询: {query}")
                return []
            
            if 'data' not in json_data:
                print(f"⚠️ Jina API 响应格式异常, 查询: {query}, 响应: {json_data}")
                return []
            
            filtered_urls = []
            
            for item in json_data.get('data', []):
                if 'url' not in item:
                    continue
                    
                raw_date = item.get('date', 'unknown')
                standardized_date = parse_date_to_standard(raw_date)
                
                if standardized_date == 'unknown' or standardized_date == raw_date:
                    filtered_urls.append(item['url'])
                    continue
                
                today_date = get_config_value("TODAY_DATE")
                if today_date:
                    if today_date > standardized_date:
                        filtered_urls.append(item['url'])
                else:
                    filtered_urls.append(item['url'])
            
            print(f"过滤后找到 {len(filtered_urls)} 个 URL")
            return filtered_urls
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Jina API 请求失败: {e}")
            return []
        except ValueError as e:
            print(f"❌ Jina API 响应解析失败: {e}")
            return []
        except Exception as e:
            print(f"❌ Jina 搜索未知错误: {e}")
            return []


mcp = FastMCP("Search")


@mcp.tool()
def get_information(query: str) -> str:
    """
    使用搜索工具抓取并以结构化方式返回与指定查询相关的主要内容信息。

    Args:
        query (str): 您想要检索的关键信息或搜索词，将在互联网上搜索最匹配的结果。

    Returns:
        str: 一个包含多个检索到的网页内容的字符串，结构化内容包括：
        - URL: 原始网页链接
        - 标题: 网页标题
        - 描述: 网页的简要描述
        - 发布时间: 内容发布日期（如果可用）
        - 内容: 网页的主要文本内容（前 1000 个字符）

        如果抓取失败，则返回相应的错误信息。
    """
    try:
        tool = WebScrapingJinaTool()
        results = tool(query)
        
        if not results:
            return f"⚠️ 搜索查询 '{query}' 未找到结果。可能是网络问题或 API 限制。"
        
        formatted_results = []
        for result in results:
            if 'error' in result:
                formatted_results.append(f"错误: {result['error']}")
            else:
                formatted_results.append(f"""
URL: {result['url']}
标题: {result['title']}
描述: {result['description']}
发布时间: {result['publish_time']}
内容: {result['content'][:1000]}...
""")
        
        if not formatted_results:
            return f"⚠️ 搜索查询 '{query}' 返回了空结果。"
        
        return "\n".join(formatted_results)
        
    except Exception as e:
        return f"❌ 搜索工具执行失败: {str(e)}"


if __name__ == "__main__":
    port = int(os.getenv("SEARCH_HTTP_PORT", "8001"))
    mcp.run(transport="streamable-http", port=port)
