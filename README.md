# 🏥 医疗情报自动收集机器人

**Pediatric SLE Intelligence Bot**

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![GitHub Actions](https://img.shields.io/badge/CI-GitHub%20Actions-2088FF?logo=github-actions&logoColor=white)](https://github.com/features/actions)
[![Telegram](https://img.shields.io/badge/Push-Telegram-26A5E4?logo=telegram&logoColor=white)](https://telegram.org/)

># 🏥 Pediatric SLE Intelligence Bot (儿童红斑狼疮医疗情报机器人)

> **❤️ 写在前面 / Our Mission**
>
> 这个项目的诞生源于一位父亲对孩子的爱。为了抗击儿童红斑狼疮 (Systemic Lupus Erythematosus, SLE)，我们需要时刻关注全球最新的医疗进展。
>
> 我将这个自动化工具开源，是希望**每一位患者和家属都能平等地、及时地获取救命的信息**。希望这些最新的科研成果能为治疗带来新思路，为处于焦虑中的家庭带去希望。
>
> _"Information is hope."_

---
> 🔬 专为**儿童系统性红斑狼疮 (Pediatric SLE)** 研究设计的自动化文献监控机器人。  
> 每日自动抓取 PubMed 和 ClinicalTrials 最新文献，通过 AI 生成中文日报，推送至 Telegram或者邮箱。

## 📖 项目简介
这是一个基于 AI 的医疗情报自动收集机器人。它每天定时从全球权威医学数据库（PubMed, Top Journals, ClinicalTrials）抓取关于 **Pediatric SLE (儿童红斑狼疮)** 的最新研究，利用大语言模型（DeepSeek/Gemini等）进行深度总结，并推送给用户。

### ✨ 核心功能

| 🤖 **多模型支持** | 支持 Google Gemini (免费)、DeepSeek (高性价比)、豆包、通义千问，一键切换 |
| ⚙️ **配置驱动** | 无需改代码，通过环境变量即可切换 AI 模型和运行逻辑 |
| 📡 **稳定情报源** | 直连 PubMed / ClinicalTrials 官方 RSS，已解决反爬虫问题 |
| 🔄 **智能去重** | 自动记录已推送文章，避免重复推送 |
| 🌐 **双语支持** | 支持生成 **中文 (CN)** 或 **英文 (EN)** 版本的日报 |
| ⏰ **全自动化** | 专为 GitHub Actions 设计，每日定时运行，零维护 |
| 📱 **多渠道推送** | 支持 **Telegram** 及 **邮件** 推送 (自动长消息分段, Markdown 降级保护) |

---

## 📊 信息源

| 来源 | 描述 |
|------|------|
| **PubMed - Pediatric SLE** | 儿童红斑狼疮相关文献 |
| **Top Journals** | NEJM / Lancet / Nature / ARD 顶级期刊 SLE 研究 |
| **ClinicalTrials** | 儿童狼疮相关临床试验 |

---

## 🚀 快速开始

### 方式一：GitHub Actions 部署（推荐）

1. **Fork 本仓库** 到你的 GitHub 账号

2. **配置 Secrets**  
   进入仓库 → `Settings` → `Secrets and variables` → `Actions` → `New repository secret`，添加以下变量：

   | Secret 名称 | 必填 | 说明 |
   |------------|:----:|------|
   | `TELEGRAM_BOT_TOKEN` | ✅ | Telegram Bot Token，通过 [@BotFather](https://t.me/BotFather) 获取 |
   | `TELEGRAM_CHAT_ID` | ✅ | 目标群组/频道 ID |
   | `AI_PROVIDER` | ❌ | AI 提供商，可选 `gemini` / `deepseek` / `doubao` / `qwen`，默认 `gemini` |
   | `GEMINI_API_KEY` | ⚠️ | Google Gemini API Key，使用 Gemini 时必填 |
   | `DEEPSEEK_API_KEY` | ⚠️ | DeepSeek API Key，使用 DeepSeek 时必填 |
   | `DOUBAO_API_KEY` | ⚠️ | 豆包 API Key，使用豆包时必填 |
   | `QWEN_API_KEY` | ⚠️ | 通义千问 API Key，使用 Qwen 时必填 |
   | `AI_MODEL_NAME` | ❌ | 自定义模型名称（豆包必填接入点 ID） |

3. **启用 Actions**  
   进入仓库 → `Actions` → 点击 `I understand my workflows, go ahead and enable them`

4. **手动测试**  
   点击 `医疗情报日报` → `Run workflow` → `Run workflow` 手动触发

5. **等待推送** 🎉  
   每天 UTC 00:00（北京时间 08:00）自动运行

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
📅 2026-01-07 儿童红斑狼疮研究日报

【重磅】
📌 新型 B 细胞靶向疗法在儿童 SLE 中的突破性进展
💡 一种新药能有效控制狼疮活动，副作用比传统方案更少
🔗 https://pubmed.ncbi.nlm.nih.gov/xxxxx

【临床】
📌 儿童狼疮性肾炎的长期预后研究
💡 早期规范治疗的患儿，10 年后肾功能保持良好的比例超过 80%
🔗 https://pubmed.ncbi.nlm.nih.gov/xxxxx

【基础】
📌 Treg 细胞在儿童 SLE 发病中的作用机制
💡 发现调节性 T 细胞功能障碍与疾病活动密切相关
🔗 https://pubmed.ncbi.nlm.nih.gov/xxxxx
```

---

## ❓ 常见问题

### Q: Telegram 收不到消息？

1. 确认 Bot 已加入目标群组/频道
2. 确认 `TELEGRAM_CHAT_ID` 正确（群组 ID 通常是负数）
3. 检查 GitHub Actions 日志是否有报错

### Q: 如何获取 Telegram Chat ID？

1. 将 Bot 加入群组
2. 在群组中发送任意消息
3. 访问 `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
4. 在返回的 JSON 中找到 `chat.id`

### Q: 如何修改运行时间？

编辑 `.github/workflows/daily.yml` 中的 cron 表达式：

```yaml
schedule:
  - cron: '0 0 * * *'  # UTC 时间，北京时间 +8 小时
```

### Q: 豆包提示模型不存在？

豆包必须通过 `AI_MODEL_NAME` 指定**接入点 ID**（不是模型名称），格式如 `ep-xxxxxxxxx`。

---

## 📄 许可证

本项目基于 [MIT License](LICENSE) 开源。

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

<p align="center">
  Made with ❤️ for Pediatric Rheumatology Research
</p>
