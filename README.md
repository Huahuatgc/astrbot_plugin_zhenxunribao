# 日盼日报 (astrbot_plugin_ripan_daily)

一个为 AstrBot 设计的精美日报生成插件，每日为您汇总最新的资讯内容。

## ✨ 功能特性

- 📺 **今日新番** - 显示今日更新的动画番剧信息
- 🔥 **B站热点** - 汇总B站当前热门内容
- 🌍 **世界新闻** - 获取最新的国际新闻资讯
- 💻 **IT资讯** - IT之家最新科技资讯
- 🐟 **摸鱼日历** - 显示节假日和重要日期提醒
- 💬 **今日一言** - 每日一句精美文案

## 📦 安装方法

### 通过 AstrBot 插件市场安装（推荐）

1. 在 AstrBot WebUI 中打开插件市场
2. 搜索 `astrbot_plugin_ripan_daily` 或 `日盼日报`
3. 点击安装

### 手动安装

1. 克隆仓库到 AstrBot 插件目录：
```bash
cd AstrBot/data/plugins
git clone https://github.com/Huahuatgc/astrbot_plugin_zhenxunribao.git astrbot_plugin_ripan_daily
```

2. 安装依赖：
```bash
cd astrbot_plugin_ripan_daily
pip install -r requirements.txt
playwright install chromium
```

3. 在 AstrBot WebUI 的插件管理中启用插件

## ⚙️ 配置说明

在 AstrBot WebUI 的插件配置页面进行配置：

### 必需配置

- **api_token** (string): ALAPI Token
  - 描述：用于节假日、今日一言、早报API
  - 获取方式：在 [https://www.alapi.cn/](https://www.alapi.cn/) 注册获取Token
  - 默认值：`""`

### 可选配置

- **max_anime_count** (int): 今日新番最大显示数量
  - 建议值：4-8
  - 默认值：`4`

- **max_news_count** (int): 新闻最大显示数量
  - 建议值：5-10
  - 默认值：`5`

- **max_hotword_count** (int): B站热点最大显示数量
  - 建议值：4-8
  - 默认值：`4`

- **max_holiday_count** (int): 摸鱼日历最大显示数量
  - 建议值：3-5
  - 默认值：`3`

### 定时推送配置

- **enable_scheduled_push** (bool): 是否启用定时推送
  - 描述：启用后会在指定时间自动推送日报到配置的群组
  - 默认值：`false`

- **scheduled_push_time** (string): 定时推送时间
  - 格式：HH:MM（24小时制，如 `08:00` 表示每天早上8点）
  - 默认值：`"08:00"`

- **scheduled_push_groups** (list): 定时推送目标群组列表
  - 格式：`["aiocqhttp:group:123456789", ...]`
  - 获取群组ID：在群内发送 `/日报` 后查看日志获取
  - 默认值：`[]`

## 🚀 使用方法

### 手动生成日报

在QQ群或其他支持的平台中发送指令：
```
/日报
```

机器人将自动生成并发送当日日报图片。

### 定时推送

1. 在插件配置中启用 `enable_scheduled_push`
2. 设置 `scheduled_push_time`（推送时间）
3. 配置 `scheduled_push_groups`（目标群组列表）
4. 保存配置，插件将自动在指定时间推送日报

## 📋 依赖说明

- `aiohttp>=3.8.0` - 异步HTTP请求库
- `jinja2>=3.0.0` - HTML模板渲染引擎
- `playwright>=1.40.0` - 浏览器自动化，用于HTML转图片

安装 Playwright 浏览器：
```bash
playwright install chromium
```

## ⚠️ 注意事项

1. **API Token 配置**：部分功能（节假日、今日一言、早报）需要配置 ALAPI Token，否则相关数据可能无法获取
2. **Playwright 安装**：首次使用需要安装 Playwright 的 Chromium 浏览器，执行 `playwright install chromium`
3. **网络环境**：插件需要访问多个外部API，请确保网络连接正常
4. **群组ID获取**：配置定时推送时，可以通过在目标群内发送 `/日报` 后查看日志获取正确的群组ID格式

## 🛠️ 技术实现

- 使用 **Jinja2** 渲染HTML模板
- 使用 **Playwright** 进行HTML到图片的转换，支持2倍分辨率高清渲染
- 使用 **aiohttp** 异步获取多个数据源
- 资源文件通过 Base64 编码嵌入HTML，确保图片和字体正常显示

## 📝 更新日志

### v1.0.0
- ✨ 初始版本发布
- 📺 支持今日新番显示
- 🔥 支持B站热点汇总
- 🌍 支持世界新闻获取
- 💻 支持IT资讯获取
- 🐟 支持摸鱼日历显示
- 💬 支持今日一言显示
- ⏰ 支持定时推送功能

## 📄 许可证

本项目采用 [AGPL-3.0](LICENSE) 许可证。

## 🙏 致谢

- [AstrBot](https://github.com/AstrBotDevs/AstrBot) - 优秀的机器人框架
- [ALAPI](https://www.alapi.cn/) - 提供API服务
- [Bangumi](https://bgm.tv/) - 番剧数据来源
- [IT之家](https://www.ithome.com/) - IT资讯来源

## 📮 反馈与建议

如有问题或建议，欢迎提交 Issue 或 Pull Request！

仓库地址：[https://github.com/Huahuatgc/astrbot_plugin_zhenxunribao](https://github.com/Huahuatgc/astrbot_plugin_zhenxunribao)
