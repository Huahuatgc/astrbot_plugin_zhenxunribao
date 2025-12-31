"""
早报 API 处理模块
用于获取60秒读懂世界新闻，供日报模板使用
"""
import requests
from typing import List, Dict, Optional
import json
import re

# 异步支持（可选）
try:
    import aiohttp
    HAS_AIOHTTP = True
except ImportError:
    HAS_AIOHTTP = False


class ZaobaoAPI:
    """早报 API 处理类"""
    
    def __init__(self, token: str):
        """
        初始化
        
        Args:
            token: API token
        """
        self.token = token
        self.url = "https://v3.alapi.cn/api/zaobao"
        self.headers = {"Content-Type": "application/json"}
    
    def get_zaobao_sync(self) -> Optional[Dict]:
        """
        同步方式获取早报数据
        
        Returns:
            API 返回的原始数据，失败返回 None
        """
        try:
            params = {
                "token": self.token,
                "format": "json"
            }
            response = requests.get(
                self.url,
                headers=self.headers,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"请求早报 API 失败: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"解析 JSON 失败: {e}")
            return None
    
    async def get_zaobao_async(self) -> Optional[Dict]:
        """
        异步方式获取早报数据（推荐用于 AstrBot）
        
        Returns:
            API 返回的原始数据，失败返回 None
        """
        if not HAS_AIOHTTP:
            raise ImportError("需要安装 aiohttp 库才能使用异步功能: pip install aiohttp")
        
        try:
            params = {
                "token": self.token,
                "format": "json"
            }
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.url,
                    headers=self.headers,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    response.raise_for_status()
                    return await response.json()
        except aiohttp.ClientError as e:
            print(f"请求早报 API 失败: {e}")
            return None
        except Exception as e:
            print(f"获取早报数据失败: {e}")
            return None
    
    def parse_news(self, api_data: Optional[Dict], max_count: int = 5) -> List[str]:
        """
        解析早报数据，提取新闻列表
        
        Args:
            api_data: API 返回的原始数据
            max_count: 最多返回几条新闻
            
        Returns:
            新闻列表，格式：['新闻1', '新闻2', ...]
        """
        if not api_data:
            return self._get_default_news()
        
        try:
            # 提取 data.news 字段
            if 'data' in api_data and isinstance(api_data['data'], dict):
                news_data = api_data['data'].get('news', [])
                
                if isinstance(news_data, list):
                    news_list = []
                    for item in news_data:
                        if isinstance(item, str):
                            # 移除开头的编号（如 "1."、"1、"等）
                            cleaned = item.strip()
                            # 移除开头的数字、点号、顿号等
                            cleaned = re.sub(r'^\d+[\.、]\s*', '', cleaned)
                            if cleaned:
                                news_list.append(cleaned)
                        
                        # 达到最大数量就停止
                        if len(news_list) >= max_count:
                            break
                    
                    if len(news_list) > 0:
                        return news_list
            
            # 如果没有找到数据，返回默认值
            print("警告: 未找到新闻数据，使用默认数据")
            return self._get_default_news()
            
        except Exception as e:
            print(f"解析早报数据时出错: {e}")
            return self._get_default_news()
    
    def _get_default_news(self) -> List[str]:
        """
        返回默认的新闻数据（当 API 失败时使用）
        
        Returns:
            默认新闻列表
        """
        return [
            '全球科技峰会召开，AI发展成焦点',
            '国际油价波动引发市场关注',
            '新政策影响国际贸易',
            '环保议题持续升温',
            '体育赛事精彩纷呈'
        ]
    
    def get_world_news_sync(self, max_count: int = 5) -> List[str]:
        """
        同步方式获取世界新闻数据（一步到位）
        
        Args:
            max_count: 最多返回几条新闻
            
        Returns:
            新闻列表
        """
        api_data = self.get_zaobao_sync()
        return self.parse_news(api_data, max_count)
    
    async def get_world_news_async(self, max_count: int = 5) -> List[str]:
        """
        异步方式获取世界新闻数据（推荐用于 AstrBot）
        
        Args:
            max_count: 最多返回几条新闻
            
        Returns:
            新闻列表
        """
        api_data = await self.get_zaobao_async()
        return self.parse_news(api_data, max_count)


# 使用示例
if __name__ == "__main__":
    # 初始化
    api = ZaobaoAPI(token="uc5d9ns71w33my1aep94g61w0zn9in")
    
    # 同步方式测试
    print("=" * 50)
    print("同步方式获取世界新闻：")
    print("=" * 50)
    news_list = api.get_world_news_sync(max_count=5)
    for i, news in enumerate(news_list, 1):
        print(f"  {i}. {news}")
    
    print("\n" + "=" * 50)
    print("JSON 格式（可用于模板）：")
    print("=" * 50)
    print(json.dumps(news_list, ensure_ascii=False, indent=2))

