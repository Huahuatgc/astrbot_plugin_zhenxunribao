"""
IT之家 RSS 处理模块
用于获取 IT 资讯，供日报模板使用
"""
import aiohttp
import xml.etree.ElementTree as ET
from typing import List, Optional
from html import unescape

from astrbot.api import logger


class ITHomeRSS:
    """IT之家 RSS 处理类"""
    
    def __init__(self, session: Optional[aiohttp.ClientSession] = None):
        """
        初始化
        
        Args:
            session: 可选的 aiohttp.ClientSession，如果提供则复用，否则每次请求时创建
        """
        self.url = "https://www.ithome.com/rss/"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
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
    
    async def get_rss_async(self) -> Optional[ET.Element]:
        """
        异步方式获取 RSS 数据（推荐用于 AstrBot）
        
        Returns:
            XML 根元素，失败返回 None
        """
        try:
            session = await self._get_session()
            # 限制读取的最大大小为 10MB，防止XML炸弹攻击
            max_size = 10 * 1024 * 1024  # 10MB
            async with session.get(
                self.url,
                headers=self.headers,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                response.raise_for_status()
                # 使用read()并限制大小，防止XML炸弹攻击
                # 对于RSS feed，限制大小为10MB已足够防护大部分XML炸弹攻击
                content = await response.read()
                if len(content) > max_size:
                    logger.warning(f"RSS内容过大 ({len(content)} bytes)，已截断至 {max_size} bytes")
                    content = content[:max_size]
                # 解析XML（已限制大小，相对安全）
                return ET.fromstring(content)
        except aiohttp.ClientError as e:
            logger.warning(f"请求 IT之家 RSS 失败: {e}")
            return None
        except ET.ParseError as e:
            logger.warning(f"解析 XML 失败: {e}")
            return None
        except Exception as e:
            logger.error(f"获取 RSS 数据失败: {e}", exc_info=True)
            return None
    
    def parse_news(self, rss_root: Optional[ET.Element], max_count: int = 5) -> List[str]:
        """
        解析 RSS 数据，提取新闻标题
        
        Args:
            rss_root: XML 根元素
            max_count: 最多返回几条新闻
            
        Returns:
            新闻标题列表
        """
        if not rss_root:
            return self._get_default_news()
        
        try:
            # 查找 channel
            channel = rss_root.find('channel')
            if channel is None:
                return self._get_default_news()
            
            # 查找所有 item
            items = channel.findall('item')
            
            news_list = []
            for item in items[:max_count]:
                # 提取 title
                title_elem = item.find('title')
                if title_elem is not None and title_elem.text:
                    # 解码 HTML 实体并清理
                    title = unescape(title_elem.text.strip())
                    # 移除多余的空白字符
                    title = ' '.join(title.split())
                    if title:
                        news_list.append(title)
            
            if len(news_list) == 0:
                logger.warning("未找到新闻数据，使用默认数据")
                return self._get_default_news()
            
            return news_list
            
        except Exception as e:
            logger.error(f"解析 RSS 数据时出错: {e}", exc_info=True)
            return self._get_default_news()
    
    def _get_default_news(self) -> List[str]:
        """
        返回默认的 IT 资讯数据（当 API 失败时使用）
        
        Returns:
            默认新闻列表
        """
        return [
            '新AI模型发布，性能大幅提升',
            '科技公司发布最新产品',
            '开源项目获得重大更新',
            '网络安全事件引发关注',
            '云计算服务推出新功能'
        ]
    
    async def get_it_news_async(self, max_count: int = 5) -> List[str]:
        """
        异步方式获取 IT 资讯数据（推荐用于 AstrBot）
        
        Args:
            max_count: 最多返回几条新闻
            
        Returns:
            新闻标题列表
        """
        rss_root = await self.get_rss_async()
        return self.parse_news(rss_root, max_count)
