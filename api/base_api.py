"""
API 基类模块
封装 HTTP Session 管理逻辑，供所有 API 类继承
"""
import aiohttp
from typing import Optional

from astrbot.api import logger


class BaseAPI:
    """API 基类 - 统一管理 HTTP Session"""
    
    def __init__(self, session: Optional[aiohttp.ClientSession] = None):
        """
        初始化
        
        Args:
            session: 可选的 aiohttp.ClientSession，如果提供则复用
        """
        self._session = session
        self._own_session = False
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """获取 session，如果已有则复用，否则创建新的"""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
            self._own_session = True
        return self._session
    
    async def _close_session(self):
        """关闭自己创建的 session"""
        if self._own_session and self._session and not self._session.closed:
            await self._session.close()
            self._session = None
            self._own_session = False
    
    def set_session(self, session: aiohttp.ClientSession):
        """设置新的 session（用于 session 重置）"""
        self._session = session
        self._own_session = False
