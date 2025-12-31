"""
IT之家 RSS 处理模块
用于获取 IT 资讯，供日报模板使用
"""
import requests
import xml.etree.ElementTree as ET
from typing import List, Optional
from html import unescape

# 异步支持（可选）
try:
    import aiohttp
    HAS_AIOHTTP = True
except ImportError:
    HAS_AIOHTTP = False


class ITHomeRSS:
    """IT之家 RSS 处理类"""
    
    def __init__(self):
        """初始化"""
        self.url = "https://www.ithome.com/rss/"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    
    def get_rss_sync(self) -> Optional[ET.Element]:
        """
        同步方式获取 RSS 数据
        
        Returns:
            XML 根元素，失败返回 None
        """
        try:
            response = requests.get(
                self.url,
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return ET.fromstring(response.content)
        except requests.exceptions.RequestException as e:
            print(f"请求 IT之家 RSS 失败: {e}")
            return None
        except ET.ParseError as e:
            print(f"解析 XML 失败: {e}")
            return None
    
    async def get_rss_async(self) -> Optional[ET.Element]:
        """
        异步方式获取 RSS 数据（推荐用于 AstrBot）
        
        Returns:
            XML 根元素，失败返回 None
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
                    content = await response.read()
                    return ET.fromstring(content)
        except aiohttp.ClientError as e:
            print(f"请求 IT之家 RSS 失败: {e}")
            return None
        except ET.ParseError as e:
            print(f"解析 XML 失败: {e}")
            return None
        except Exception as e:
            print(f"获取 RSS 数据失败: {e}")
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
                print("警告: 未找到新闻数据，使用默认数据")
                return self._get_default_news()
            
            return news_list
            
        except Exception as e:
            print(f"解析 RSS 数据时出错: {e}")
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
    
    def get_it_news_sync(self, max_count: int = 5) -> List[str]:
        """
        同步方式获取 IT 资讯数据（一步到位）
        
        Args:
            max_count: 最多返回几条新闻
            
        Returns:
            新闻标题列表
        """
        rss_root = self.get_rss_sync()
        return self.parse_news(rss_root, max_count)
    
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


# 使用示例
if __name__ == "__main__":
    import json
    
    # 初始化
    rss = ITHomeRSS()
    
    # 同步方式测试
    print("=" * 50)
    print("同步方式获取 IT 资讯：")
    print("=" * 50)
    news_list = rss.get_it_news_sync(max_count=5)
    for i, news in enumerate(news_list, 1):
        print(f"  {i}. {news}")
    
    print("\n" + "=" * 50)
    print("JSON 格式（可用于模板）：")
    print("=" * 50)
    print(json.dumps(news_list, ensure_ascii=False, indent=2))

