import requests
from typing import List, Optional, Dict

class BilibiliAPI:
    def __init__(self):
        self.url = "https://s.search.bilibili.com/main/hotword"

    def _get_default_hotwords(self) -> List[str]:
        return [
            'AI技术新突破引发热议',
            '游戏更新引发玩家讨论',
            '科技区UP主发布新视频',
            '二次元新番话题持续升温'
        ]

    def get_hotwords_sync(self, max_count: int = 4) -> List[str]:
        """
        同步获取B站热点
        
        Args:
            max_count: 最大返回数量，默认4条
            
        Returns:
            List[str]: 热点标题列表
        """
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = requests.get(self.url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("code") == 0 and data.get("list"):
                return self.parse_hotwords_data(data, max_count)
            else:
                print(f"[警告] API返回异常: code={data.get('code')}")
                return self._get_default_hotwords()[:max_count]
        except requests.exceptions.RequestException as e:
            print(f"[错误] 获取B站热点失败: {e}")
            return self._get_default_hotwords()[:max_count]
        except Exception as e:
            print(f"[错误] 解析B站热点数据失败: {e}")
            return self._get_default_hotwords()[:max_count]

    async def get_hotwords_async(self, max_count: int = 4) -> List[str]:
        """
        异步获取B站热点（用于AstrBot）
        
        Args:
            max_count: 最大返回数量，默认4条
            
        Returns:
            List[str]: 热点标题列表
        """
        try:
            import aiohttp
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            async with aiohttp.ClientSession() as session:
                async with session.get(self.url, headers=headers, timeout=10) as response:
                    response.raise_for_status()
                    data = await response.json()
                    
                    if data.get("code") == 0 and data.get("list"):
                        return self.parse_hotwords_data(data, max_count)
                    else:
                        print(f"[警告] API返回异常: code={data.get('code')}")
                        return self._get_default_hotwords()[:max_count]
        except Exception as e:
            print(f"[错误] 获取B站热点失败: {e}")
            return self._get_default_hotwords()[:max_count]

    def parse_hotwords_data(self, api_data: Optional[Dict], max_count: int = 4) -> List[str]:
        """
        解析B站热点数据
        
        Args:
            api_data: API返回的完整数据
            max_count: 最大返回数量
            
        Returns:
            List[str]: 热点标题列表
        """
        hotwords = []
        if not api_data or not api_data.get("list"):
            return self._get_default_hotwords()[:max_count]
        
        for item in api_data["list"][:max_count]:
            # 优先使用 show_name，如果没有则使用 keyword
            title = item.get("show_name") or item.get("keyword", "")
            if title:
                hotwords.append(title)
        
        # 如果解析到的数据不足，用默认数据补充
        if len(hotwords) < max_count:
            default_list = self._get_default_hotwords()
            hotwords.extend(default_list[:max_count - len(hotwords)])
        
        return hotwords[:max_count]



