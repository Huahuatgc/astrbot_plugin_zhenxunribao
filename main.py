import asyncio
import base64
import os
import re
import tempfile
from datetime import datetime, timedelta, time
from urllib.request import pathname2url

import aiohttp
from jinja2 import Template
from playwright.async_api import async_playwright

from astrbot.api import AstrBotConfig, logger
from astrbot.api.event import MessageChain, filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register

from .api.bgm_api import BGMAPI
from .api.bilibili_api import BilibiliAPI
from .api.date_utils import get_current_date_info
from .api.hitokoto_api import HitokotoAPI
from .api.holiday_api import HolidayAPI
from .api.ithome_rss import ITHomeRSS
from .api.zaobao_api import ZaobaoAPI


@register("astrbot_plugin_zhenxunribao", "Huahuatgc", "小真寻记者为你献上今日报道！", "1.0.0", "https://github.com/Huahuatgc/astrbot_plugin_zhenxunribao")
class ZhenxunReportPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.config = config

        plugin_dir = os.path.dirname(os.path.abspath(__file__))
        self.template_path = os.path.join(plugin_dir, "daily_news.html")
        self.plugin_dir = plugin_dir

        # 创建共享的 aiohttp ClientSession，供所有 API 类复用
        self.http_session = aiohttp.ClientSession()

        api_token = config.get("api_token", "")
        self.bgm_api = BGMAPI(session=self.http_session)
        self.bilibili_api = BilibiliAPI(session=self.http_session)
        self.hitokoto_api = HitokotoAPI(token=api_token, session=self.http_session)
        self.holiday_api = HolidayAPI(token=api_token, session=self.http_session)
        self.ithome_rss = ITHomeRSS(session=self.http_session)
        self.zaobao_api = ZaobaoAPI(token=api_token, session=self.http_session)

        if config.get("enable_scheduled_push", False):
            asyncio.create_task(self._scheduled_push_task())
            logger.info("定时推送任务已启动")

        logger.info("真寻日报插件已加载")

    @filter.command("日报")
    async def daily_news(self, event: AstrMessageEvent):
        """生成日报"""
        try:
            image_path = await self._generate_daily_image()
            yield event.image_result(image_path)
        except Exception as e:
            logger.error(f"生成日报时出错: {e}", exc_info=True)
            yield event.plain_result(f"生成日报时出错: {str(e)}")

    async def _generate_daily_image(self) -> str:
        logger.info("开始生成日报")

        max_anime_count = self.config.get("max_anime_count", 4)
        max_news_count = self.config.get("max_news_count", 5)
        max_hotword_count = self.config.get("max_hotword_count", 4)
        max_holiday_count = self.config.get("max_holiday_count", 3)

        date_info = get_current_date_info()

        anime_list, bili_hotwords, hitokoto_data, moyu_list, world_news, it_news = (
            await self._fetch_all_data(
                max_anime_count=max_anime_count,
                max_news_count=max_news_count,
                max_hotword_count=max_hotword_count,
                max_holiday_count=max_holiday_count,
            )
        )

        template_data = {
            "date_info": date_info,
            "anime_list": anime_list or [],
            "bili_hotwords": bili_hotwords or [],
            "hitokoto_data": hitokoto_data or {"hitokoto": "暂无", "from": "未知"},
            "moyu_list": moyu_list or [],
            "world_news": world_news or [],
            "it_news": it_news or [],
        }

        logger.info(
            f"模板数据准备完成: 新番={len(template_data['anime_list'])}, "
            f"热点={len(template_data['bili_hotwords'])}, "
            f"节假日={len(template_data['moyu_list'])}, "
            f"世界新闻={len(template_data['world_news'])}, "
            f"IT新闻={len(template_data['it_news'])}"
        )

        try:
            with open(self.template_path, "r", encoding="utf-8") as f:
                html_template_str = f.read()
        except Exception as e:
            logger.error(f"读取模板文件失败: {e}", exc_info=True)
            raise

        template = Template(html_template_str)
        rendered_html = template.render(**template_data)
        rendered_html = await self._embed_resources(rendered_html)

        style_fix = """
html, body {
  width: 578px;
  margin: 0;
  padding: 0;
  overflow-x: hidden;
}
"""
        rendered_html = rendered_html.replace("</style>", style_fix + "</style>", 1)

        image_path = await self._render_html_with_playwright(rendered_html)
        logger.info("日报生成成功")
        return image_path
    
    async def _fetch_all_data(
        self,
        max_anime_count: int,
        max_news_count: int,
        max_hotword_count: int,
        max_holiday_count: int,
    ):
        results = await asyncio.gather(
            self.bgm_api.get_today_anime_async(max_count=max_anime_count),
            self.bilibili_api.get_hotwords_async(max_count=max_hotword_count),
            self.hitokoto_api.get_hitokoto_async(),
            self.holiday_api.get_moyu_list_async(max_count=max_holiday_count),
            self.zaobao_api.get_world_news_async(max_count=max_news_count),
            self.ithome_rss.get_it_news_async(max_count=max_news_count),
            return_exceptions=True,
        )

        anime_list = results[0] if not isinstance(results[0], Exception) else []
        bili_hotwords = results[1] if not isinstance(results[1], Exception) else []
        hitokoto_data = (
            results[2]
            if not isinstance(results[2], Exception)
            else {"hitokoto": "暂无", "from": "未知"}
        )
        moyu_list = results[3] if not isinstance(results[3], Exception) else []
        world_news = results[4] if not isinstance(results[4], Exception) else []
        it_news = results[5] if not isinstance(results[5], Exception) else []

        if isinstance(hitokoto_data, dict):
            from_value = hitokoto_data.get("from", "未知")
            if not from_value or from_value.strip() == "" or from_value.strip() == "网络":
                hitokoto_data["from"] = "佚名"
            else:
                hitokoto_data["from"] = from_value.strip()

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.warning(f"获取数据时出错 (索引 {i}): {result}")

        return anime_list, bili_hotwords, hitokoto_data, moyu_list, world_news, it_news

    def _file_to_base64(self, file_path: str) -> str | None:
        try:
            if not os.path.exists(file_path):
                logger.warning(f"资源文件不存在: {file_path}")
                return None

            with open(file_path, "rb") as f:
                file_data = f.read()
                base64_data = base64.b64encode(file_data).decode("utf-8")

                ext = os.path.splitext(file_path)[1].lower()
                mime_types = {
                    ".otf": "font/opentype",
                    ".ttf": "font/ttf",
                    ".woff": "font/woff",
                    ".woff2": "font/woff2",
                    ".png": "image/png",
                    ".jpg": "image/jpeg",
                    ".jpeg": "image/jpeg",
                    ".gif": "image/gif",
                    ".svg": "image/svg+xml",
                }
                mime_type = mime_types.get(ext, "application/octet-stream")

                return f"data:{mime_type};base64,{base64_data}"
        except Exception as e:
            logger.warning(f"转换文件到base64失败 {file_path}: {e}")
            return None

    async def _embed_resources(self, html_template: str) -> str:
        def replace_font(match):
            filename = match.group(1)
            file_path = os.path.join(self.plugin_dir, "res", "font", filename)
            base64_uri = self._file_to_base64(file_path)
            if base64_uri:
                return f'url("{base64_uri}")'
            return match.group(0)

        html_template = re.sub(
            r'url\(["\']?\./res/font/([^"\')]+)["\']?\)',
            replace_font,
            html_template,
            flags=re.IGNORECASE,
        )

        def replace_image(match):
            filepath = match.group(1)
            if filepath.startswith("icon/") or filepath.startswith("image/"):
                file_path = os.path.join(self.plugin_dir, "res", filepath)
                base64_uri = self._file_to_base64(file_path)
                if base64_uri:
                    logger.debug(f"转换图片为base64: {filepath}")
                    return f'src="{base64_uri}"'
                else:
                    logger.warning(f"图片转换为base64失败: {filepath}")
            return match.group(0)

        html_template = re.sub(
            r'src=["\']\./res/([^"\']+)["\']',
            replace_image,
            html_template,
            flags=re.IGNORECASE,
        )

        return html_template

    async def _render_html_with_playwright(
        self, html_content: str, output_path: str | None = None
    ) -> str:
        temp_html_path = None
        try:
            temp_dir = tempfile.gettempdir()
            temp_html_path = os.path.join(
                temp_dir,
                f"ripan_daily_{os.getpid()}_{hash(html_content) % 100000}.html",
            )
            with open(temp_html_path, "w", encoding="utf-8") as f:
                f.write(html_content)

            if output_path is None:
                output_path = temp_html_path.replace(".html", ".png")

            async with async_playwright() as p:
                logger.info("启动Playwright浏览器...")
                browser = await p.chromium.launch(headless=True)
                context = None
                try:
                    context = await browser.new_context(
                        viewport={"width": 1156, "height": 6000},
                        device_scale_factor=2,
                    )
                    page = await context.new_page()

                    file_url = f"file://{pathname2url(temp_html_path)}"
                    await page.goto(file_url, wait_until="networkidle")
                    await page.wait_for_timeout(2000)

                    wrapper = await page.query_selector(".wrapper")
                    if not wrapper:
                        raise Exception("未找到.wrapper元素")

                    box = await wrapper.bounding_box()
                    if not box:
                        raise Exception("无法获取.wrapper元素的bounding box")

                    wrapper_x = int(box["x"])
                    wrapper_y = int(box["y"])
                    wrapper_width = int(box["width"])
                    wrapper_height = int(box["height"])

                    logger.info(
                        f"Wrapper位置: x={wrapper_x}, y={wrapper_y}, "
                        f"width={wrapper_width}, height={wrapper_height}"
                    )

                    clip_config = {
                        "x": wrapper_x,
                        "y": wrapper_y,
                        "width": wrapper_width,
                        "height": wrapper_height,
                    }

                    logger.info(
                        f"正在截图到: {output_path} "
                        f"(宽度: {wrapper_width}px, 高度: {wrapper_height}px, 2倍分辨率)"
                    )
                    await page.screenshot(
                        path=output_path, full_page=False, type="png", clip=clip_config
                    )

                    logger.info(f"截图完成: {output_path}")
                    return output_path

                finally:
                    if context:
                        await context.close()
                    await browser.close()

        except Exception as e:
            logger.error(f"Playwright渲染失败: {e}", exc_info=True)
            raise
        finally:
            if temp_html_path and os.path.exists(temp_html_path):
                try:
                    os.remove(temp_html_path)
                except Exception as e:
                    logger.warning(f"删除临时HTML文件失败: {e}")

    async def _scheduled_push_task(self):
        while True:
            try:
                push_time_str = self.config.get("scheduled_push_time", "08:00")
                push_groups = self.config.get("scheduled_push_groups", [])

                if not push_groups:
                    logger.warning("定时推送已启用，但未配置目标群组，跳过本次推送")
                    await asyncio.sleep(3600)
                    continue

                try:
                    hour, minute = map(int, push_time_str.split(":"))
                    push_time = time(hour, minute)
                except (ValueError, AttributeError):
                    logger.error(
                        f"定时推送时间格式错误: {push_time_str}，使用默认时间08:00"
                    )
                    push_time = time(8, 0)

                now = datetime.now()
                next_push = datetime.combine(now.date(), push_time)

                if next_push <= now:
                    next_push += timedelta(days=1)

                wait_seconds = (next_push - now).total_seconds()

                logger.info(
                    f"定时推送任务已启动，下次推送时间: {next_push.strftime('%Y-%m-%d %H:%M:%S')}"
                )
                await asyncio.sleep(wait_seconds)

                logger.info("开始执行定时推送")
                await self._push_daily_to_groups(push_groups)

            except asyncio.CancelledError:
                logger.info("定时推送任务已取消")
                break
            except Exception as e:
                logger.error(f"定时推送任务出错: {e}", exc_info=True)
                await asyncio.sleep(3600)

    async def _push_daily_to_groups(self, group_list: list):
        try:
            image_path = await self._generate_daily_image()
            message_chain = MessageChain().file_image(image_path)

            success_count = 0
            for group_id in group_list:
                try:
                    result = await self.context.send_message(group_id, message_chain)
                    if result:
                        logger.info(f"成功推送日报到群组: {group_id}")
                        success_count += 1
                    else:
                        logger.warning(f"推送失败，未找到群组: {group_id}")
                except Exception as e:
                    logger.error(f"推送到群组 {group_id} 时出错: {e}", exc_info=True)

            logger.info(f"定时推送完成，成功: {success_count}/{len(group_list)}")

            try:
                if os.path.exists(image_path):
                    os.remove(image_path)
            except Exception as e:
                logger.warning(f"清理临时图片文件失败: {e}")

        except Exception as e:
            logger.error(f"定时推送日报失败: {e}", exc_info=True)

    async def terminate(self):
        logger.info("真寻日报插件正在卸载...")
        # 关闭共享的 HTTP session
        if self.http_session and not self.http_session.closed:
            await self.http_session.close()
            logger.info("HTTP session 已关闭")

