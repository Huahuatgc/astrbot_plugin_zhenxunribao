"""
今日一言 API 处理模块
用于获取今日一言数据
"""
import aiohttp
from typing import Optional, Dict

from astrbot.api import logger
from .base_api import BaseAPI


class HitokotoAPI(BaseAPI):
    """今日一言 API 处理类"""
    
    def __init__(self, token: str, session: Optional[aiohttp.ClientSession] = None):
        """
        初始化
        
        Args:
            token: API token
            session: 可选的 aiohttp.ClientSession，如果提供则复用
        """
        super().__init__(session)
        self.url = "https://v3.alapi.cn/api/hitokoto"
        self.token = token
        self.headers = {"Content-Type": "application/json"}

    def _get_default_hitokoto(self) -> Dict[str, str]:
        return {
            'hitokoto': '生活就像骑自行车，想保持平衡就得往前走。',
            'from': '未知'
        }

    async def get_hitokoto_async(self) -> Dict[str, str]:
        """
        异步获取今日一言（用于AstrBot）
        
        Returns:
            Dict[str, str]: 包含 'hitokoto' 和 'from' 的字典
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
                data = await response.json()
                
                # 检查返回状态，支持 success 字段或 code 字段
                code = data.get("code")
                success = data.get("success", False)
                
                if (code == 200 or success) and data.get("data"):
                    hitokoto_data = data["data"]
                    # 获取from字段
                    from_value = hitokoto_data.get("from") or hitokoto_data.get("from_who") or ""
                    
                    # 如果为空或"网络"则使用"佚名"
                    if not from_value or (isinstance(from_value, str) and (from_value.strip() == "" or from_value.strip() == "网络")):
                        from_value = "佚名"
                    else:
                        from_value = str(from_value).strip()
                    
                    hitokoto_text = hitokoto_data.get("hitokoto", "")
                    
                    return {
                        'hitokoto': hitokoto_text,
                        'from': from_value
                    }
                else:
                    logger.warning(f"API返回异常: code={code}, success={success}, message={data.get('message', '未知错误')}")
                    return self._get_default_hitokoto()
        except Exception as e:
            logger.error(f"获取今日一言失败: {e}", exc_info=True)
            return self._get_default_hitokoto()
