"""
节假日 API 处理模块
用于获取和解析节假日数据，供日报模板使用
"""
import aiohttp
from datetime import datetime, date
from typing import List, Dict, Optional

from astrbot.api import logger


class HolidayAPI:
    """节假日 API 处理类"""
    
    def __init__(self, token: str, session: Optional[aiohttp.ClientSession] = None, year: Optional[int] = None):
        """
        初始化
        
        Args:
            token: API token
            session: 可选的 aiohttp.ClientSession，如果提供则复用，否则每次请求时创建
            year: 指定年份，None 则使用当前年份
        """
        self.token = token
        self.url = "https://v3.alapi.cn/api/holiday"
        self.headers = {"Content-Type": "application/json"}
        self.year = year or datetime.now().year
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
    
    async def get_holidays_async(self) -> Optional[Dict]:
        """
        异步方式获取节假日数据（推荐用于 AstrBot）
        
        Returns:
            API 返回的原始数据，失败返回 None
        """
        try:
            session = await self._get_session()
            params = {"token": self.token}
            async with session.get(
                self.url,
                headers=self.headers,
                params=params,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as e:
            logger.warning(f"请求节假日 API 失败: {e}")
            return None
        except Exception as e:
            logger.error(f"获取节假日数据失败: {e}", exc_info=True)
            return None
    
    def parse_holidays(self, api_data: Optional[Dict], max_count: int = 3) -> List[Dict]:
        """
        解析节假日数据，转换为模板需要的格式
        
        Args:
            api_data: API 返回的原始数据
            max_count: 最多返回几个节假日
            
        Returns:
            格式化的节假日列表，格式：
            [
                {'name': '春节', 'days_left': 25},
                {'name': '清明节', 'days_left': 78},
                ...
            ]
        """
        if not api_data:
            return self._get_default_holidays()
        
        try:
            # 提取数据
            holidays_data = api_data.get('data', [])
            if not isinstance(holidays_data, list) or len(holidays_data) == 0:
                return self._get_default_holidays()
            
            # 获取当前日期
            today = date.today()
            
            # 处理节假日数据
            processed_holidays = []
            seen_holidays = set()  # 用于去重连续假期的第一天
            
            for holiday in holidays_data:
                if not isinstance(holiday, dict):
                    continue
                
                # 只处理实际放假的日期
                is_off_day = holiday.get('is_off_day')
                if is_off_day != 1:
                    continue
                
                # 获取日期
                date_str = holiday.get('date')
                if not date_str:
                    continue
                
                # 解析日期
                try:
                    holiday_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                except ValueError as e:
                    logger.warning(f"日期解析失败: {date_str}, 错误: {e}")
                    continue
                
                # 只保留未来的节假日（包括今天）
                if holiday_date < today:
                    continue
                
                # 计算天数差
                days_left = (holiday_date - today).days
                
                # 获取节假日名称
                name = holiday.get('name', '未知')
                
                # 对于连续多天的假期，只取第一天（天数最少的）
                # 如果名称已存在，比较天数，保留更近的
                if name in seen_holidays:
                    # 找到已存在的同名假期，比较天数
                    for i, existing in enumerate(processed_holidays):
                        if existing['name'] == name:
                            if days_left < existing['days_left']:
                                processed_holidays[i] = {
                                    'name': name,
                                    'days_left': days_left,
                                    'date': date_str
                                }
                            break
                else:
                    seen_holidays.add(name)
                    processed_holidays.append({
                        'name': name,
                        'days_left': days_left,
                        'date': date_str
                    })
            
            # 按天数排序，取最近的几个
            processed_holidays.sort(key=lambda x: x['days_left'])
            result = processed_holidays[:max_count]
            
            # 如果没有找到未来的节假日，返回默认值
            if len(result) == 0:
                logger.warning("未找到未来的节假日数据，使用默认数据")
                return self._get_default_holidays()
            
            # 格式化输出（移除 date 字段，只保留模板需要的）
            return [
                {'name': item['name'], 'days_left': item['days_left']}
                for item in result
            ]
            
        except Exception as e:
            logger.error(f"解析节假日数据时出错: {e}", exc_info=True)
            return self._get_default_holidays()
    
    def _get_default_holidays(self) -> List[Dict]:
        """
        返回默认的节假日数据（当 API 失败时使用）
        
        Returns:
            默认节假日列表
        """
        return [
            {'name': '周末', 'days_left': 3},
            {'name': '春节', 'days_left': 25},
            {'name': '清明节', 'days_left': 78}
        ]
    
    async def get_moyu_list_async(self, max_count: int = 3) -> List[Dict]:
        """
        异步方式获取摸鱼日历数据（推荐用于 AstrBot）
        
        Args:
            max_count: 最多返回几个节假日
            
        Returns:
            格式化的摸鱼日历列表
        """
        api_data = await self.get_holidays_async()
        return self.parse_holidays(api_data, max_count)
