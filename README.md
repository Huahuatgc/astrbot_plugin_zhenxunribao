# 真寻日报 (astrbot_plugin_zhenxunribao)

✨ 基于 AstrBot 的一个插件 ✨

小真寻记者为你献上今天报道！

> **小真寻也很可爱呀，也会很喜欢你！**

## 📖 介绍

这是一个从 [nonebot-plugin-zxreport](https://github.com/HibiKier/nonebot-plugin-zxreport) 移植到 AstrBot 的真寻日报插件。插件会每日为你汇总最新的资讯内容，包含今日新番、B站热点、世界新闻、IT资讯、摸鱼日历和今日一言等内容。

## 💿 安装

### 通过 AstrBot 插件市场安装（推荐）

1. 在 AstrBot WebUI 中打开插件市场
2. 搜索 `astrbot_plugin_zhenxunribao` 或 `真寻日报`
3. 点击安装

### 手动安装

1. 克隆仓库到 AstrBot 插件目录：
```bash
cd AstrBot/data/plugins
git clone https://github.com/luminacry/astrbot_plugin_zhenxunribao
```

2. 安装依赖：
```bash
cd astrbot_plugin_zhenxunribao
pip install -r requirements.txt
playwright install chromium
```

3. 在 AstrBot WebUI 的插件管理中启用插件

## ⚙️ 配置

在 AstrBot WebUI 的插件配置页面进行配置：

| 配置 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `api_token` | str | `""` | ALAPI Token，用于节假日、今日一言、早报API。在 [https://admin.alapi.cn/user/login](https://admin.alapi.cn/user/login) 登录后获取token |
| `max_anime_count` | int | `4` | 今日新番最大显示数量，建议设置为4-8之间 |
| `max_news_count` | int | `5` | 新闻最大显示数量，建议设置为5-10之间 |
| `max_hotword_count` | int | `4` | B站热点最大显示数量，建议设置为4-8之间 |
| `max_holiday_count` | int | `3` | 摸鱼日历最大显示数量，建议设置为3-5之间 |
| `render_dpr` | int | `5` | 渲染清晰度（DPR），越大越清晰但图片更大更慢，建议 3-6 |
| `enable_scheduled_push` | bool | `false` | 是否启用定时推送，启用后会在指定时间自动推送日报到配置的群组 |
| `scheduled_push_time` | str | `"08:00"` | 定时推送时间，HH:MM格式（24小时制），例如：`08:00` 表示每天早上8点 |
| `scheduled_push_groups` | list | `[]` | 定时推送目标群组列表，直接填写群号即可，如：`["957880653", "123456789"]` |
| `enable_ai_greeting` | bool | `false` | 是否启用 AI 生成个性化问候语，启用后会调用 AstrBot 当前配置的大模型生成推送问候语 |

## 🎁 使用

### 手动生成日报

在QQ群或其他支持的平台中发送指令：
```
/日报
```

机器人将自动生成并发送当日日报图片。

### 刷新当天日报

当天内重复请求 `/日报` 会自动复用缓存的图片，如需强制重新生成：
```
/日报刷新
```

### 获取群组ID（可选）

如果直接填写群号无法推送，可以在群内发送：
```
/日报群组ID
```

机器人会返回当前会话的完整标识，将其添加到配置中即可。

### 定时推送

1. 在插件配置中启用 `enable_scheduled_push`
2. 设置 `scheduled_push_time`（推送时间，默认 08:00）
3. 在 `scheduled_push_groups` 中填写目标群号，如：`["957880653"]`
4. 保存配置并重载插件，定时任务将自动启动

## 📋 依赖

- `aiohttp>=3.8.0` - 异步HTTP请求库
- `jinja2>=3.0.0` - HTML模板渲染引擎
- `playwright>=1.40.0` - 浏览器自动化，用于HTML转图片
- `zhdate>=0.1` - 农历日期计算支持

安装 Playwright 浏览器：
```bash
playwright install chromium
```

## 🖋 字体说明

本插件渲染日报图片时使用了 **HarmonyOS Sans** 字体文件以提升跨系统一致性与清晰度。


## ⚠️ 注意事项

1. **API Token 配置**：部分功能（节假日、今日一言、早报）需要配置 ALAPI Token，否则相关数据可能无法获取
2. **Playwright 安装**：首次使用需要安装 Playwright 的 Chromium 浏览器，执行 `playwright install chromium`
3. **网络环境**：插件需要访问多个外部API，请确保网络连接正常
4. **群组ID获取**：配置定时推送时，可以通过在目标群内发送 `/日报` 后查看日志获取正确的群组ID格式
5. **日报缓存**：当天内多次请求 `/日报` 会自动复用已生成的图片，次日凌晨自动清理。如需当天内强制刷新，请使用 `/日报刷新`

## 🔧 常见问题与排查思路

以下为日报功能出现异常时的排查参考，大部分问题已在最新版本中内置修复或降级处理。

### 1. 确认命令在 AstrBot 容器内执行

如果使用 Docker 部署，所有命令需要在容器内运行：

```bash
docker exec -it astrbot bash
```

### 2. Playwright Chromium 未安装

**现象**：日志出现 `playwright` 相关错误，日报生成失败。

**排查**：
```bash
python -c "from playwright.sync_api import sync_playwright; print('OK')"
```

如果报错，执行：
```bash
playwright install chromium
```

### 3. Chromium 已下载但启动失败（缺少系统依赖）

**现象**：`playwright install chromium` 成功，但运行时报 `error while loading shared libraries: libXXX.so` 或 `Failed to launch browser`。

**原因**：Debian/Alpine 等精简镜像缺少 Chromium 所需的系统库。

**排查**（在容器内）：
```bash
playwright install-deps chromium
# 如果上面的命令不可用，手动安装缺失依赖：
apt-get update && apt-get install -y libnss3 libnspr4 libatk-bridge2.0-0 libdrm2 libxkbcommon0 libgbm1 libasound2
```

### 4. 图片资源或图标缺失

**现象**：日报图片中某处显示空白/占位符。日志提示 `资源文件不存在`。

**原因**：`res/icon/` 或 `res/image/` 目录下缺少对应图片文件。

**排查**：以下为日报模板实际使用的资源文件：

| 用途 | 文件路径 | 缺失时的表现 |
|------|---------|-------------|
| 真寻头像 | `res/image/1.no-bg.png` | 头部图片空白 |
| 摸鱼日历图标 | `res/icon/fish.png` | 标签旁图片消失 |
| B站热点图标 | `res/icon/bilibili.png` | 标签旁图片消失 |
| 今日新番图标 | `res/icon/bgm.png` | 标签旁图片消失 |
| 60s读懂世界图标 | `res/icon/60.png` | 标签旁图片消失 |
| IT资讯图标 | `res/icon/it.png` | 标签旁图片消失 |
| 今日一言图标 | `res/icon/hitokoto.png` | 标签旁图片消失 |


### 5. BGM API 偶发 502 / Timeout（已内置修复）

**状态**：最新版本已内置 IPv4 优先连接 + 最多 3 次重试 + 失败后降级为系统默认 DNS（IPv4/IPv6 双栈）。若所有网络请求均失败，日报「今日新番」部分会自动使用 `1.no-bg.png` 作为默认图片，不会出现破损图或崩溃。

**仍想验证**（在容器内）：
```bash
# 测试 BGM API 连通性（IPv4 强制）
curl -4 --max-time 10 "https://api.bgm.tv/calendar/today"
# 如果上述失败，尝试系统默认解析
curl --max-time 10 "https://api.bgm.tv/calendar/today"
```

如果两者都失败，说明是网络/防火墙层面的问题，与插件代码无关。

### 6. 图片发送遇 retcode=1200（已内置降级处理）

**现象**：QQ群内日报图片正常显示，但日志出现 `ActionFailed retcode=1200`。

**原因**：NapCat/QQNT 协议在发送完成后回执超时，图片**可能**已成功送达，不一定是失败。

**状态**：最新版本在异常信息包含 `sendMsg`、`onMsgInfoListUpdate`、`NTEvent` 等关键字时，会记录以下 Warning 而不抛出异常：
```
图片可能已成功发送，但 NapCat/QQNT 回执超时 (retcode=1200)
```
定时推送通道同样对此做了降级处理。**注意**：若 retcode=1200 不含预期关键字（极少见），仍可能输出错误堆栈，此时可在群内重试 `/日报` 确认。

### 7. curl 测试 BGM API 返回 JSON 后报 `curl: (23) Failure writing output to destination`

**现象**：
```bash
$ curl -4 --max-time 10 "https://api.bgm.tv/calendar/today"
[{"id": 456, ...}]curl: (23) Failure writing output to destination
```

**原因**：API 返回了 JSON 但体积较大，终端缓冲区无法完整接收。**JSON 已成功返回**，`curl: (23)` 只是写入终端的错误，不影响实际网络请求。**这不是 BGM API 的问题。**

### 8. 其他问题排查入口

```bash
# 1. 查看 AstrBot 日志（包含插件加载和日报生成详细日志）
docker logs -f astrbot --tail 100

# 2. 在 WebUI 中检查插件是否已启用、配置是否正常

# 3. 重启插件：WebUI → 插件管理 → 重载插件

# 4. 确保容器时间正确
date
```

## 推荐排查顺序

1. 确认容器时间正确（`date`）
2. 检查 Playwright Chromium 是否安装（`playwright install chromium`）
3. 检查系统依赖（`playwright install-deps chromium`）
4. 检查资源文件完整性（`res/icon/` 和 `res/image/` 目录）
5. 用 curl 测试 BGM API 是否可达
6. 查看 AstrBot 日志中是否有其他异常

## 一句话总结

> **资源完整 + Chromium 安装成功 + 系统依赖齐全 + 网络可达 = 日报正常生成与发送。** 其余大多数异常（retcode=1200、BGM API 502）已在最新版本中内置修复或降级处理，可放心使用。

## ️ 技术实现

- 使用 **Jinja2** 渲染HTML模板
- 使用 **Playwright** 进行HTML到图片的转换，支持2倍分辨率高清渲染
- 使用 **aiohttp** 异步获取多个数据源
- 资源文件通过 Base64 编码嵌入HTML，确保图片和字体正常显示

## 📝 功能特性

- 📺 **今日新番** - 显示今日更新的动画番剧信息
- 🔥 **B站热点** - 汇总B站当前热门内容
- 🌍 **世界新闻** - 获取最新的国际新闻资讯
- 💻 **IT资讯** - IT之家最新科技资讯
- 🐟 **摸鱼日历** - 显示节假日和重要日期提醒
- 💬 **今日一言** - 每日一句精美文案

## 📝 更新日志

- 最新版本：`1.2.0`
- 详细变更见 `CHANGELOG.md`

## 📄 许可证

本项目采用 [AGPL-3.0](LICENSE) 许可证。

## ❤ 致谢

- [nonebot-plugin-zxreport](https://github.com/HibiKier/nonebot-plugin-zxreport) - 原始项目，由 [HibiKier](https://github.com/HibiKier) 开发
- [AstrBot](https://github.com/AstrBotDevs/AstrBot) - 优秀的机器人框架
- [ALAPI](https://www.alapi.cn/) - 提供API服务
- [Bangumi](https://bgm.tv/) - 番剧数据来源
- [IT之家](https://www.ithome.com/) - IT资讯来源

## 📮 反馈与建议

如有问题或建议，欢迎提交 Issue 或 Pull Request！

仓库地址：[https://github.com/Huahuatgc/astrbot_plugin_zhenxunribao](https://github.com/Huahuatgc/astrbot_plugin_zhenxunribao)
