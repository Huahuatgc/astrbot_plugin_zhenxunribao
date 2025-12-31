"""
日期工具模块
用于获取当前日期、星期、农历等信息
"""
from datetime import datetime
from typing import Dict

# 星期映射
WEEKDAYS_CN = {
    0: '星期一',
    1: '星期二',
    2: '星期三',
    3: '星期四',
    4: '星期五',
    5: '星期六',
    6: '星期日'
}


def get_current_date_info() -> Dict[str, str]:
    """
    获取当前日期信息
    
    Returns:
        {
            'week_cn': '星期一',
            'date_str': '2024-01-15',
            'cn_date_str': '腊月初五'
        }
    """
    now = datetime.now()
    
    # 星期
    week_cn = WEEKDAYS_CN[now.weekday()]
    
    # 日期字符串
    date_str = now.strftime('%Y-%m-%d')
    
    # 农历日期（简化版，实际应该使用农历库）
    # 这里先用一个简单的占位符，后续可以集成 zhdate 等库
    cn_date_str = get_lunar_date_simple(now)
    
    return {
        'week_cn': week_cn,
        'date_str': date_str,
        'cn_date_str': cn_date_str
    }


def get_lunar_date_simple(date_obj: datetime) -> str:
    """
    简化版农历日期获取（占位符）
    实际应该使用 zhdate 或类似的库
    
    Args:
        date_obj: 日期对象
        
    Returns:
        农历日期字符串，如 '腊月初五'
    """
    # TODO: 集成真正的农历库，如 zhdate
    # 临时返回一个占位符
    return '腊月初五'


def get_lunar_date_with_library(date_obj: datetime) -> str:
    """
    使用 zhdate 库获取农历日期（需要安装: pip install zhdate）
    
    Args:
        date_obj: 日期对象
        
    Returns:
        农历日期字符串，如 '腊月初五'
    """
    try:
        from zhdate import ZhDate
        lunar = ZhDate.from_datetime(date_obj)
        return f"{lunar.lunar_month}月{lunar.lunar_day}日"
    except ImportError:
        print("警告: 未安装 zhdate 库，使用简化版农历日期")
        return get_lunar_date_simple(date_obj)
    except Exception as e:
        print(f"获取农历日期失败: {e}")
        return get_lunar_date_simple(date_obj)


if __name__ == "__main__":
    # 测试
    info = get_current_date_info()
    print("当前日期信息：")
    print(f"  星期: {info['week_cn']}")
    print(f"  日期: {info['date_str']}")
    print(f"  农历: {info['cn_date_str']}")



