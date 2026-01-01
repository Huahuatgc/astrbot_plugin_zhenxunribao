"""
BGM (Bangumi) API 处理模块
用于获取今日新番数据，供日报模板使用
"""
import aiohttp
from datetime import datetime
from typing import List, Dict, Optional

from astrbot.api import logger
from .base_api import BaseAPI


class BGMAPI(BaseAPI):
    """BGM API 处理类"""
    
    def __init__(self, session: Optional[aiohttp.ClientSession] = None):
        """
        初始化
        
        Args:
            session: 可选的 aiohttp.ClientSession，如果提供则复用
        """
        super().__init__(session)
        self.url = "https://api.bgm.tv/calendar"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    
    async def get_calendar_async(self) -> Optional[List]:
        """
        异步方式获取 BGM 日历数据（推荐用于 AstrBot）
        
        Returns:
            API 返回的原始数据，失败返回 None
        """
        try:
            session = await self._get_session()
            async with session.get(
                self.url,
                headers=self.headers,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as e:
            logger.warning(f"请求 BGM API 失败: {e}")
            return None
        except Exception as e:
            logger.error(f"获取 BGM 数据失败: {e}", exc_info=True)
            return None
    
    def parse_today_anime(self, api_data: Optional[List], max_count: int = 4) -> List[Dict]:
        """
        解析 BGM 数据，提取今日新番
        
        Args:
            api_data: API 返回的原始数据
            max_count: 最多返回几个新番
            
        Returns:
            格式化的新番列表，格式：
            [
                {
                    'title': '动画名称',
                    'image': '图片URL'
                },
                ...
            ]
        """
        if not api_data or not isinstance(api_data, list):
            return self._get_default_anime()
        
        try:
            # 获取今天是星期几 (0=周一, 6=周日)
            # BGM API 使用 1-7 表示周一到周日
            today_weekday = datetime.now().weekday() + 1
            
            anime_list = []
            
            # 查找今天的数据
            for day_data in api_data:
                if not isinstance(day_data, dict):
                    continue
                
                weekday_info = day_data.get('weekday', {})
                weekday_id = weekday_info.get('id')
                
                # 找到今天的数据
                if weekday_id == today_weekday:
                    items = day_data.get('items', [])
                    
                    for item in items:
                        if not isinstance(item, dict):
                            continue
                        
                        # 优先使用中文名，没有则使用日文名
                        name_cn = item.get('name_cn', '')
                        name_jp = item.get('name', '')
                        title = name_cn if name_cn else name_jp
                        
                        # 获取图片（使用 medium 尺寸）
                        images = item.get('images', {})
                        image_url = images.get('medium', '') or images.get('common', '')
                        
                        if title and image_url:
                            anime_list.append({
                                'title': title,
                                'image': image_url
                            })
                        
                        # 达到最大数量就停止
                        if len(anime_list) >= max_count:
                            break
                    
                    break
            
            # 如果没有找到数据，返回默认值
            if len(anime_list) == 0:
                logger.warning("未找到今日新番数据，使用默认数据")
                return self._get_default_anime()
            
            return anime_list
            
        except Exception as e:
            logger.error(f"解析 BGM 数据时出错: {e}", exc_info=True)
            return self._get_default_anime()
    
    def _get_default_anime(self) -> List[Dict]:
        """
        返回默认的新番数据（当 API 失败时使用）
        
        Returns:
            默认新番列表
        """
        return [
            {'title': '葬送的芙莉莲 第二季', 'image': './res/image/anime1.jpg'},
            {'title': '咒术回战 涉谷事变篇', 'image': './res/image/anime2.jpg'},
            {'title': '间谍过家家 第三季', 'image': './res/image/anime3.jpg'},
            {'title': '鬼灭之刃 柱训练篇', 'image': './res/image/anime4.jpg'}
        ]
    
    async def get_today_anime_async(self, max_count: int = 4) -> List[Dict]:
        """
        异步方式获取今日新番数据（推荐用于 AstrBot）
        
        Args:
            max_count: 最多返回几个新番
            
        Returns:
            格式化的今日新番列表
        """
        api_data = await self.get_calendar_async()
        return self.parse_today_anime(api_data, max_count)
