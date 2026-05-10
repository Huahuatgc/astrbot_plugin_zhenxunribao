"""
BGM (Bangumi) API 处理模块
用于获取今日新番数据，供日报模板使用
"""
import socket
import asyncio
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
    
    async def get_calendar_async(self) -> List:
        """
        异步方式获取 BGM 日历数据（推荐用于 AstrBot）

        先用 IPv4 重试 3 次；若全部失败，再用 IPv4/IPv6 自动选择重试 3 次。
        失败时返回空列表，由 parse_today_anime 降级为默认新番数据。

        Returns:
            API 返回的原始数据，失败返回空列表 []
        """
        timeout = aiohttp.ClientTimeout(total=30, connect=10, sock_read=20)
        headers = {
            "User-Agent": "AstrBot zhenxunribao/1.0",
            "Accept": "application/json",
        }

        async def _try_requests(family: int, label: str) -> List:
            """以指定地址族重试请求，成功返回数据，失败返回空列表。"""
            connector = aiohttp.TCPConnector(family=family)
            last_error = None

            async with aiohttp.ClientSession(
                timeout=timeout,
                connector=connector,
                headers=headers,
            ) as session:
                for attempt in range(1, 4):
                    try:
                        async with session.get(self.url) as resp:
                            if resp.status == 200:
                                logger.info(f"BGM 数据获取成功 ({label})")
                                return await resp.json()

                            if resp.status in (502, 503, 504):
                                logger.warning(
                                    f"BGM API 返回 {resp.status} ({label})，"
                                    f"第 {attempt}/3 次重试，{attempt} 秒后重试..."
                                )
                                if attempt < 3:
                                    await asyncio.sleep(attempt)
                                continue

                            logger.warning(
                                f"BGM API 请求失败: HTTP {resp.status} ({label})"
                            )
                            return []

                    except (asyncio.TimeoutError, aiohttp.ClientError) as e:
                        logger.warning(
                            f"BGM API 请求异常 ({label})，第 {attempt}/3 次: "
                            f"{type(e).__name__}: {e}"
                        )
                        last_error = e
                        if attempt < 3:
                            await asyncio.sleep(attempt)

                    except Exception as e:
                        logger.error(
                            f"BGM API 未预期异常 ({label}): "
                            f"{type(e).__name__}: {e}",
                            exc_info=True,
                        )
                        return []

            logger.error(
                f"BGM API ({label}) 最终失败，已重试 3 次。"
                f"最后异常: {type(last_error).__name__}: {last_error}"
            )
            return []

        # 阶段 1：IPv4 only（最多 3 次）
        result = await _try_requests(socket.AF_INET, "IPv4")
        if result:
            return result

        # 阶段 2：IPv4 + IPv6 自动选择（最多 3 次）
        logger.info("IPv4 阶段全部失败，切换为 IPv4/IPv6 自动选择重试...")
        result = await _try_requests(0, "IPv4/IPv6")
        return result
    
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
            {'title': '葬送的芙莉莲 第二季', 'image': './res/image/1.no-bg.png'},
            {'title': '咒术回战 涉谷事变篇', 'image': './res/image/1.no-bg.png'},
            {'title': '间谍过家家 第三季', 'image': './res/image/1.no-bg.png'},
            {'title': '鬼灭之刃 柱训练篇', 'image': './res/image/1.no-bg.png'},
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
