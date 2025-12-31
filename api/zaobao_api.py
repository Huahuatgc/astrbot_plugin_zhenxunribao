"""
早报 API 处理模块
用于获取60秒读懂世界新闻，供日报模板使用
"""
import aiohttp
from typing import List, Dict, Optional
import re

from astrbot.api import logger


class ZaobaoAPI:
    """早报 API 处理类"""
    
    def __init__(self, token: str, session: Optional[aiohttp.ClientSession] = None):
        """
        初始化
        
        Args:
            token: API token
            session: 可选的 aiohttp.ClientSession，如果提供则复用，否则每次请求时创建
        """
        self.token = token
        self.url = "https://v3.alapi.cn/api/zaobao"
        self.headers = {"Content-Type": "application/json"}
        self._session = session
        self._own_session = False
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """获取session，如果已有则复用，否则创建新的"""
        if self._session is None:
            self._session = aiohttp.ClientSession()
            self._own_session = True
        return self._session
    
    async def _close_session(self):
        """关闭自己创建的session"""
        if self._own_session and self._session:
            await self._session.close()
            self._session = None
            self._own_session = False
    
    async def get_zaobao_async(self) -> Optional[Dict]:
        """
        异步方式获取早报数据（推荐用于 AstrBot）
        
        Returns:
            API 返回的原始数据，失败返回 None
        """
        try:
            session = await self._get_session()
            params = {
                "token": self.token,
                "format": "json"
            }
            async with session.get(
                self.url,
                headers=self.headers,
                params=params,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as e:
            logger.warning(f"请求早报 API 失败: {e}")
            return None
        except Exception as e:
            logger.error(f"获取早报数据失败: {e}", exc_info=True)
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
            logger.warning("未找到新闻数据，使用默认数据")
            return self._get_default_news()
            
        except Exception as e:
            logger.error(f"解析早报数据时出错: {e}", exc_info=True)
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
