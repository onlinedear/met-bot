# 🏥 医疗情报自动收集机器人

**Medical Intelligence Bot - 幼年皮肌炎文献监控**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![GitHub Actions](https://img.shields.io/badge/CI-GitHub%20Actions-2088FF?logo=github-actions&logoColor=white)](https://github.com/features/actions)
[![Telegram](https://img.shields.io/badge/Push-Telegram-26A5E4?logo=telegram&logoColor=white)](https://telegram.org/)

> 🔬 专为**幼年皮肌炎 (Juvenile Dermatomyositis)** 研究设计的自动化文献监控机器人。  
> 每日自动抓取 PubMed 和 ClinicalTrials 最新文献，通过 AI 生成中文日报，推送至 Telegram 和邮箱。

---

## 📖 项目简介

这是一个基于 AI 的医疗情报自动收集机器人。它每天定时从全球权威医学数据库（PubMed, Top Journals, ClinicalTrials）抓取关于 **幼年皮肌炎** 的最新研究，利用大语言模型（DeepSeek/Gemini等）进行深度总结，并推送给用户。


### ✨ 核心功能

| 功能 | 说明 |
| :--- | :--- |
| 🤖 **多模型支持** | 支持 Google Gemini (免费)、DeepSeek (高性价比)、豆包、通义千问，一键切换 |
| ⚙️ **配置驱动** | 无需改代码，通过环境变量即可切换 AI 模型和运行逻辑 |
| 📡 **稳定情报源** | 直连 PubMed / ClinicalTrials 官方 RSS，已解决反爬虫问题 |
| 🔄 **智能去重** | 自动记录已推送文章，避免重复推送 |
| 🌐 **双语支持** | 支持生成 **中文 (CN)** 或 **英文 (EN)** 版本的日报 |
| ⏰ **全自动化** | 专为 GitHub Actions 设计，每日定时运行，零维护 |
| 📱 **多渠道推送** | 支持 **Telegram** 及 **邮件** 推送 (自动长消息分段, Markdown 降级保护) ||


## 📊 信息源

| 来源 | 描述 |
|------|------|
| **PubMed - Juvenile Dermatomyositis** | 幼年皮肌炎相关文献 |
| **Top Journals** | NEJM / Lancet / Nature / ARD 顶级期刊研究 |
| **ClinicalTrials** | 幼年皮肌炎相关临床试验 |

---

## 🚀 一键部署

### 方式一：GitHub Actions 部署（推荐，完全免费）

**点击下方按钮，一键 Fork 并开始配置：**

[![Deploy with GitHub Actions](https://img.shields.io/badge/Deploy-GitHub%20Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white)](https://github.com/YOUR_USERNAME/met-bot/fork)

#### 📝 部署步骤：

1. **Fork 本仓库**  
   点击上方按钮或仓库右上角的 `Fork` 按钮

2. **配置环境变量**  
   进入你 Fork 的仓库 → `Settings` → `Secrets and variables` → `Actions` → `New repository secret`

   **必填配置：**
   
   | Secret 名称 | 说明 | 获取方式 |
   |------------|------|---------|
   | `AI_PROVIDER` | AI 提供商 | 填 `deepseek` 或 `gemini` |
   | `DEEPSEEK_API_KEY` | DeepSeek API Key | [获取地址](https://platform.deepseek.com/) |
   | `EMAIL_RECEIVER` | 收件邮箱 | 填你的邮箱，支持多个（逗号分隔）<br>例如：`user1@163.com,user2@gmail.com` |
   
   **推送配置（至少配置一个）：**
   
   | Secret 名称 | 说明 | 示例值 |
   |------------|------|--------|
   | `TELEGRAM_BOT_TOKEN` | Telegram Bot Token | 通过 [@BotFather](https://t.me/BotFather) 获取 |
   | `TELEGRAM_CHAT_ID` | Telegram 群组/频道 ID | 负数，如 `-1001234567890` |
   | `SMTP_SERVER` | 邮件服务器 | `smtp.mxhichina.com` / `smtp.qq.com` / `smtp.gmail.com` |
   | `SMTP_PORT` | SMTP 端口 | `465` (SSL) 或 `587` (TLS) |
   | `EMAIL_SENDER` | 发件邮箱 | `your@email.com` |
   | `EMAIL_PASSWORD` | 邮箱授权码 | **不是登录密码！**见下方教程 |

3. **启用 Actions**  
   进入 `Actions` 标签页 → 点击 `I understand my workflows, go ahead and enable them`

4. **手动测试**  
   点击左侧 `每日文献摘要` → `Run workflow` → `Run workflow`

5. **完成！** 🎉  
   每天北京时间 **07:30** 自动运行，推送最新文献摘要

## 🔐 如何获取邮箱授权码 (EMAIL_PASSWORD)

为了安全，现代邮箱不允许直接使用登录密码，必须使用“授权码”或“应用专用密码”。

### 🐧 QQ 邮箱 (推荐)
1.  电脑登录 [mail.qq.com](https://mail.qq.com)。
2.  点击左上角 **【设置】** -> 选择 **【账户】**。
3.  向下滚动找到 **“账号与安全-安全”**。
4.  点击 **POP3/IMAP/SMTP/Exchange/CardDAV 服务** 右侧的 **【开启】**。
5.  按提示用手机发送短信验证。
6.  复制弹出的 **16位授权码** (这就是 `EMAIL_PASSWORD`)。
    * *Secret 提示：`SMTP_SERVER` 填 `smtp.qq.com`，`SMTP_PORT` 填 `587`*

### 📮 Gmail (谷歌邮箱)
1.  进入 [Google 账号安全设置](https://myaccount.google.com/security)。
2.  开启 **“两步验证” (2-Step Verification)**。
3.  搜索并进入 **“应用专用密码” (App passwords)**。
4.  创建一个新应用，复制生成的 **16位密码**。
    * *Secret 提示：`SMTP_SERVER` 填 `smtp.gmail.com`，`SMTP_PORT` 填 `587`*

---

### 方式二：本地运行

```bash
# 1. 克隆仓库
git clone https://github.com/YOUR_USERNAME/met-bot.git
cd met-bot

# 2. 安装依赖
pip install -r requirements.txt

# 3. 设置环境变量
export TELEGRAM_BOT_TOKEN="your_bot_token"
export TELEGRAM_CHAT_ID="your_chat_id"
export AI_PROVIDER="gemini"
export GEMINI_API_KEY="your_gemini_api_key"

# 4. 运行
python main.py
```

**Windows PowerShell:**

```powershell
$env:TELEGRAM_BOT_TOKEN="your_bot_token"
$env:TELEGRAM_CHAT_ID="your_chat_id"
$env:AI_PROVIDER="gemini"
$env:GEMINI_API_KEY="your_gemini_api_key"
python main.py
```

---

## ⚙️ 配置指南

### 环境变量一览

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `TELEGRAM_BOT_TOKEN` | - | Telegram Bot Token |
| `TELEGRAM_CHAT_ID` | - | 推送目标 Chat ID |
| `AI_PROVIDER` | `gemini` | AI 提供商：`gemini` / `deepseek` / `doubao` / `qwen` |
| `GEMINI_API_KEY` | - | Google Gemini API Key |
| `DEEPSEEK_API_KEY` | - | DeepSeek API Key |
| `DOUBAO_API_KEY` | - | 字节豆包 API Key |
| `QWEN_API_KEY` | - | 阿里通义千问 API Key |
| `AI_MODEL_NAME` | 自动选择 | 指定具体模型名称（可选） |

### 🔄 切换 AI 模型

#### 使用 Gemini（默认，免费额度）

```bash
AI_PROVIDER=gemini
GEMINI_API_KEY=your_key
```

获取 API Key: [Google AI Studio](https://aistudio.google.com/app/apikey)

#### 使用 DeepSeek（高性价比）

```bash
AI_PROVIDER=deepseek
DEEPSEEK_API_KEY=your_key
AI_MODEL_NAME=deepseek-chat  # 可选，默认 deepseek-chat
```

获取 API Key: [DeepSeek Platform](https://platform.deepseek.com/)

#### 使用豆包

```bash
AI_PROVIDER=doubao
DOUBAO_API_KEY=your_key
AI_MODEL_NAME=ep-xxxx  # 必填！填写你的接入点 ID
```

获取 API Key: [火山引擎控制台](https://console.volcengine.com/ark)

#### 使用通义千问

```bash
AI_PROVIDER=qwen
QWEN_API_KEY=your_key
AI_MODEL_NAME=qwen-plus  # 可选，默认 qwen-plus
```

获取 API Key: [阿里云 DashScope](https://dashscope.console.aliyun.com/)

---

## 📁 项目结构

```
met-bot/
├── main.py                 # 核心逻辑
├── requirements.txt        # Python 依赖
├── history.json            # 已推送文章记录（自动生成）
├── README.md               # 项目文档
└── .github/
    └── workflows/
        └── daily.yml       # GitHub Actions 配置
```

---

## 🔧 工作流程

```
┌──────────────────┐
│  ⏰ 定时触发      │  每天 UTC 00:00
└────────┬─────────┘
         ▼
┌──────────────────┐
│  📡 获取 RSS     │  PubMed + ClinicalTrials
└────────┬─────────┘
         ▼
┌──────────────────┐
│  🔍 智能去重     │  对比 history.json
└────────┬─────────┘
         ▼
┌──────────────────┐
│  🤖 AI 总结      │  Gemini / DeepSeek / ...
└────────┬─────────┘
         ▼
┌──────────────────┐
│  📱 Telegram     │  推送中文日报
└────────┬─────────┘
         ▼
┌──────────────────┐
│  💾 保存历史     │  更新 history.json
└──────────────────┘
```

---

## 📝 输出示例

```
风湿免疫科医学文献日报
日期：2026年1月14日
主题：幼年皮肌炎 (JDM)

【重磅】
1. 利妥昔单抗治疗幼年皮肌炎的有效性：一项多中心研究
   解读：对于难治性幼年皮肌炎患儿，使用利妥昔单抗治疗6个月后，
         近八成患儿的肌力和皮肤症状得到显著改善。
   链接：https://pubmed.ncbi.nlm.nih.gov/12345678/

【临床】
1. 幼年皮肌炎的长期预后：一项10年随访研究
   解读：一项长达10年的追踪研究发现，约三分之二的幼年皮肌炎患儿
         可实现完全缓解，而早期积极治疗与更好的长期预后密切相关。
   链接：https://pubmed.ncbi.nlm.nih.gov/11223344/

【基础】
1. 用于幼年皮肌炎早期检测的新型生物标志物
   解读：研究发现三种新型自身抗体在诊断幼年皮肌炎方面具有很高的
         敏感性和特异性，有望用于早期识别。
   链接：https://pubmed.ncbi.nlm.nih.gov/87654321/
```

---

## 📧 提供订阅服务

如果你想让更多人订阅这个医疗情报服务，推荐使用以下方案：

### 方案一：Telegram 公开频道（推荐）

创建一个公开的 Telegram 频道，用户点击链接即可订阅：

1. 创建 Telegram 公开频道
2. 将 Bot 添加为管理员
3. 设置 `TELEGRAM_CHAT_ID` 为频道 ID
4. 分享频道链接：`https://t.me/your_channel`

**优点**：完全免费、无限订阅者、用户自助订阅

### 方案二：Google Groups 邮件列表

创建 Google Groups 邮件列表，自动管理订阅：

1. 在 [groups.google.com](https://groups.google.com) 创建群组
2. 设置 `EMAIL_RECEIVER` 为群组邮箱
3. 用户发送邮件到 `群组+subscribe@googlegroups.com` 即可订阅

**优点**：免费、自助订阅/退订、支持无限订阅者

📖 **详细部署指南**：查看 [SUBSCRIPTION_GUIDE.md](SUBSCRIPTION_GUIDE.md)

---

## ❓ 常见问题

<details>
<summary><b>Q: 如何修改运行时间？</b></summary>

编辑 `.github/workflows/daily.yml` 中的 cron 表达式：

```yaml
schedule:
  - cron: '30 23 * * *'  # UTC 23:30 = 北京时间 07:30
  # 改成 '0 0 * * *' 就是 UTC 00:00 = 北京时间 08:00
```

</details>

<details>
<summary><b>Q: 如何获取 Telegram Chat ID？</b></summary>

1. 将 Bot 加入群组
2. 在群组中发送任意消息
3. 访问 `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
4. 在返回的 JSON 中找到 `chat.id`（群组 ID 通常是负数）

</details>

<details>
<summary><b>Q: 邮件收不到怎么办？</b></summary>

1. 检查垃圾邮件文件夹
2. 确认 `EMAIL_PASSWORD` 是授权码，不是登录密码
3. 确认 SMTP 服务器和端口正确
4. 查看 GitHub Actions 日志是否有报错

</details>

<details>
<summary><b>Q: 支持多个收件人吗？</b></summary>

支持！`EMAIL_RECEIVER` 用逗号分隔多个邮箱：

```
EMAIL_RECEIVER=user1@163.com,user2@gmail.com,user3@qq.com
```

</details>

---

## 🙏 鸣谢

本项目基于 [@onesky2015](https://github.com/onesky2015) 的 [met-bot](https://github.com/onesky2015/met-bot) 项目改进而来。

> **致敬原作者**
> 
> 感谢原作者为患者家属提供了如此优秀的开源工具和宝贵的思路。这个项目的诞生源于一位父亲对孩子的爱，为了抗击儿童罕见病，他开发了这个自动化医疗情报收集系统，让每一位患者和家属都能平等地、及时地获取救命的信息。
>
> 正如原作者所说：**"Information is hope."** （信息即希望）
>
> 这种无私的分享精神，让更多家庭在与疾病抗争的路上不再孤单。我们在此基础上进行了适配和优化，希望能帮助到更多需要的人。

**主要改进：**
- ✨ 适配幼年皮肌炎（Juvenile Dermatomyositis）文献监控
- 📧 优化邮件推送，支持多收件人和纯文本格式
- 🔧 简化部署流程，降低使用门槛
- 📖 完善文档，添加详细的配置指南和订阅服务方案

---

## 📄 许可证

本项目基于 [MIT License](LICENSE) 开源。

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

如果这个项目对你有帮助，请给个 ⭐️ Star 支持一下！

---

<p align="center">
  Made with ❤️ for Pediatric Rheumatology Research<br>
  <sub>每天北京时间 07:30 自动运行 | 完全免费 | 开源</sub>
</p>
