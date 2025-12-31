"""
节假日 API 处理模块
用于获取和解析节假日数据，供日报模板使用
"""
import requests
from datetime import datetime, date
from typing import List, Dict, Optional
import json

# 异步支持（可选）
try:
    import aiohttp
    HAS_AIOHTTP = True
except ImportError:
    HAS_AIOHTTP = False


class HolidayAPI:
    """节假日 API 处理类"""
    
    def __init__(self, token: str, year: Optional[int] = None):
        """
        初始化
        
        Args:
            token: API token
            year: 指定年份，None 则使用当前年份
        """
        self.token = token
        self.url = "https://v3.alapi.cn/api/holiday"
        self.headers = {"Content-Type": "application/json"}
        self.year = year or datetime.now().year
    
    def get_holidays_sync(self, year: Optional[int] = None) -> Optional[Dict]:
        """
        同步方式获取节假日数据
        
        Args:
            year: 指定年份，None 则使用初始化时的年份
            
        Returns:
            API 返回的原始数据，失败返回 None
        """
        try:
            params = {"token": self.token}
            # 如果 API 支持年份参数，可以添加
            # params["year"] = year or self.year
            response = requests.get(
                self.url, 
                headers=self.headers, 
                params=params,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            # 如果 API 返回的是当前年份的数据，但我们需要下一年的
            # 可以尝试获取下一年的数据
            current_year = datetime.now().year
            if year and year > current_year:
                # 如果指定了未来年份，但 API 只返回当前年份
                # 这里可以根据实际情况调整
                pass
            
            return data
        except requests.exceptions.RequestException as e:
            print(f"请求节假日 API 失败: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"解析 JSON 失败: {e}")
            return None
    
    async def get_holidays_async(self) -> Optional[Dict]:
        """
        异步方式获取节假日数据（推荐用于 AstrBot）
        
        Returns:
            API 返回的原始数据，失败返回 None
        """
        if not HAS_AIOHTTP:
            raise ImportError("需要安装 aiohttp 库才能使用异步功能: pip install aiohttp")
        
        try:
            params = {"token": self.token}
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
            print(f"请求节假日 API 失败: {e}")
            return None
        except Exception as e:
            print(f"获取节假日数据失败: {e}")
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
                    print(f"日期解析失败: {date_str}, 错误: {e}")
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
                print("警告: 未找到未来的节假日数据，使用默认数据")
                return self._get_default_holidays()
            
            # 格式化输出（移除 date 字段，只保留模板需要的）
            return [
                {'name': item['name'], 'days_left': item['days_left']}
                for item in result
            ]
            
        except Exception as e:
            print(f"解析节假日数据时出错: {e}")
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
    
    def get_moyu_list_sync(self, max_count: int = 3) -> List[Dict]:
        """
        同步方式获取摸鱼日历数据（一步到位）
        
        Args:
            max_count: 最多返回几个节假日
            
        Returns:
            格式化的摸鱼日历列表
        """
        api_data = self.get_holidays_sync()
        return self.parse_holidays(api_data, max_count)
    
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


# 使用示例
if __name__ == "__main__":
    # 初始化
    api = HolidayAPI(token="uc5d9ns71w33my1aep94g61w0zn9in")
    
    # 同步方式测试
    print("=" * 50)
    print("同步方式获取摸鱼日历：")
    print("=" * 50)
    moyu_list = api.get_moyu_list_sync(max_count=5)
    for item in moyu_list:
        print(f"  {item['name']}: 还剩 {item['days_left']} 天")
    
    print("\n" + "=" * 50)
    print("JSON 格式（可用于模板）：")
    print("=" * 50)
    print(json.dumps(moyu_list, ensure_ascii=False, indent=2))

