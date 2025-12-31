import requests
from typing import Optional, Dict

class HitokotoAPI:
    def __init__(self, token: str):
        self.url = "https://v3.alapi.cn/api/hitokoto"
        self.token = token

    def _get_default_hitokoto(self) -> Dict[str, str]:
        return {
            'hitokoto': '生活就像骑自行车，想保持平衡就得往前走。',
            'from': '未知'
        }

    def get_hitokoto_sync(self) -> Dict[str, str]:
        """
        同步获取今日一言
        
        Returns:
            Dict[str, str]: 包含 'hitokoto' 和 'from' 的字典
        """
        try:
            params = {"token": self.token}
            headers = {"Content-Type": "application/json"}
            response = requests.get(self.url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
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
                print(f"[警告] API返回异常: code={code}, success={success}, message={data.get('message', '未知错误')}")
                return self._get_default_hitokoto()
        except requests.exceptions.RequestException as e:
            print(f"[错误] 获取今日一言失败: {e}")
            return self._get_default_hitokoto()
        except Exception as e:
            print(f"[错误] 解析今日一言数据失败: {e}")
            return self._get_default_hitokoto()

    async def get_hitokoto_async(self) -> Dict[str, str]:
        """
        异步获取今日一言（用于AstrBot）
        
        Returns:
            Dict[str, str]: 包含 'hitokoto' 和 'from' 的字典
        """
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                params = {"token": self.token}
                headers = {"Content-Type": "application/json"}
                async with session.get(self.url, headers=headers, params=params, timeout=10) as response:
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
                        print(f"[警告] API返回异常: code={code}, success={success}, message={data.get('message', '未知错误')}")
                        return self._get_default_hitokoto()
        except Exception as e:
            print(f"[错误] 获取今日一言失败: {e}")
            return self._get_default_hitokoto()



