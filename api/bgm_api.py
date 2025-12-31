"""
BGM (Bangumi) API 处理模块
用于获取今日新番数据，供日报模板使用
"""
import requests
from datetime import datetime
from typing import List, Dict, Optional
import json

# 异步支持（可选）
try:
    import aiohttp
    HAS_AIOHTTP = True
except ImportError:
    HAS_AIOHTTP = False


class BGMAPI:
    """BGM API 处理类"""
    
    def __init__(self):
        """初始化"""
        self.url = "https://api.bgm.tv/calendar"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    
    def get_calendar_sync(self) -> Optional[List]:
        """
        同步方式获取 BGM 日历数据
        
        Returns:
            API 返回的原始数据，失败返回 None
        """
        try:
            response = requests.get(
                self.url,
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"请求 BGM API 失败: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"解析 JSON 失败: {e}")
            return None
    
    async def get_calendar_async(self) -> Optional[List]:
        """
        异步方式获取 BGM 日历数据（推荐用于 AstrBot）
        
        Returns:
            API 返回的原始数据，失败返回 None
        """
        if not HAS_AIOHTTP:
            raise ImportError("需要安装 aiohttp 库才能使用异步功能: pip install aiohttp")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.url,
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    response.raise_for_status()
                    return await response.json()
        except aiohttp.ClientError as e:
            print(f"请求 BGM API 失败: {e}")
            return None
        except Exception as e:
            print(f"获取 BGM 数据失败: {e}")
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
                print("警告: 未找到今日新番数据，使用默认数据")
                return self._get_default_anime()
            
            return anime_list
            
        except Exception as e:
            print(f"解析 BGM 数据时出错: {e}")
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
    
    def get_today_anime_sync(self, max_count: int = 4) -> List[Dict]:
        """
        同步方式获取今日新番数据（一步到位）
        
        Args:
            max_count: 最多返回几个新番
            
        Returns:
            格式化的今日新番列表
        """
        api_data = self.get_calendar_sync()
        return self.parse_today_anime(api_data, max_count)
    
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


# 使用示例
if __name__ == "__main__":
    # 初始化
    api = BGMAPI()
    
    # 同步方式测试
    print("=" * 50)
    print("同步方式获取今日新番：")
    print("=" * 50)
    anime_list = api.get_today_anime_sync(max_count=4)
    for i, anime in enumerate(anime_list, 1):
        print(f"  {i}. {anime['title']}")
        print(f"     图片: {anime['image']}")
    
    print("\n" + "=" * 50)
    print("JSON 格式（可用于模板）：")
    print("=" * 50)
    print(json.dumps(anime_list, ensure_ascii=False, indent=2))

