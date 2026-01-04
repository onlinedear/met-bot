# filename: main.py
"""
医疗情报自动收集与推送机器人
功能: 从RSS源获取医学文献，使用AI总结，推送到Telegram
"""

import os
import json
import logging
from datetime import datetime
from typing import Optional

import feedparser
import requests
import google.generativeai as genai

# ============================================================
# 配置区域
# ============================================================

# 从环境变量读取敏感配置
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# RSS 源列表
RSS_SOURCES = [
    {
        "name": "PubMed - Pediatric SLE",
        # 需替换为用户生成的PubMed链接
        # 生成方法: 访问 https://pubmed.ncbi.nlm.nih.gov/，搜索关键词后点击 "Create RSS"
        "url": "https://pubmed.ncbi.nlm.nih.gov/rss/search/14_xQ7JEOWXDuopaPahtu8vYOV9ttMUxoq8IeKOLBpA7Zak9UG/?limit=15&utm_campaign=pubmed-2&fc=20260103215413",
    },
    {
        "name": "ClinicalTrials - Pediatric Lupus",
        # ✅ 修正点：将 'apirss' 改为 'api/rss' (加了斜杠)
        # 链接逻辑：搜索红斑狼疮(SLE) + 儿童(child) + 过去60天(in_last=60)
        "url": "https://clinicaltrials.gov/api/rss?cond=Systemic+Lupus+Erythematosus&aggFilters=ages%3Achild%2Cstatus%3Arec+not&in_last=60",
    },
]

# 历史记录文件路径
HISTORY_FILE = "history.json"

# 最大历史记录数量（防止文件无限增大）
MAX_HISTORY_SIZE = 1000

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ============================================================
# 历史记录管理
# ============================================================


def load_history() -> set:
    """
    加载历史记录文件。

    Returns:
        set: 已处理过的文章ID集合
    """
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                logger.info(f"已加载 {len(data)} 条历史记录")
                return set(data)
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"读取历史记录失败: {e}，将使用空记录")
            return set()
    else:
        logger.info("历史记录文件不存在，创建新记录")
        return set()


def save_history(history: set) -> None:
    """
    保存历史记录到文件。只保留最近的 MAX_HISTORY_SIZE 条记录。

    Args:
        history: 文章ID集合
    """
    # 转换为列表并只保留最后 MAX_HISTORY_SIZE 条
    history_list = list(history)
    if len(history_list) > MAX_HISTORY_SIZE:
        history_list = history_list[-MAX_HISTORY_SIZE:]
        logger.info(f"历史记录已截断至 {MAX_HISTORY_SIZE} 条")

    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history_list, f, ensure_ascii=False, indent=2)
        logger.info(f"已保存 {len(history_list)} 条历史记录")
    except IOError as e:
        logger.error(f"保存历史记录失败: {e}")


# ============================================================
# RSS 解析
# ============================================================


def fetch_rss_articles(sources: list) -> list:
    """
    从RSS源获取文章列表。

    Args:
        sources: RSS源配置列表

    Returns:
        list: 文章列表，每个文章包含 id, title, link, summary, source
    """
    articles = []

    # ==============================================================================
    # 完整的浏览器伪装 Headers
    # 作用：模拟真实 Chrome 浏览器访问，绕过 ClinicalTrials.gov 等网站的反爬虫机制
    # ==============================================================================
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/rss+xml, application/xml, text/xml, */*',
        'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Cache-Control': 'no-cache',
    }

    for source in sources:
        source_name = source.get("name", "Unknown")
        url = source.get("url", "")

        if not url:
            logger.warning(f"源 '{source_name}' 没有配置URL，跳过")
            continue

        logger.info(f"正在获取: {source_name}")

        try:
            # ==============================================================================
            # 步骤1: 使用 requests 下载 RSS 内容
            # 优势：比 feedparser 直接请求更灵活，可以完整控制 headers 和错误处理
            # ==============================================================================
            response = requests.get(url, headers=headers, timeout=30)

            # 步骤2: 检查 HTTP 状态码，捕获 403/404 等错误
            response.raise_for_status()

            logger.info(f"成功下载 '{source_name}'，状态码: {response.status_code}，内容长度: {len(response.content)} bytes")

            # ==============================================================================
            # 步骤3: 使用 feedparser 解析下载到的二进制内容
            # 注意：使用 response.content (bytes) 而不是 response.text (str)
            # feedparser 可以自动处理编码问题
            # ==============================================================================
            feed = feedparser.parse(response.content)

            # 错误检查逻辑
            if feed.bozo and feed.bozo_exception:
                # 某些 XML 可能有轻微格式问题但不影响读取，这里做记录
                logger.warning(f"解析 '{source_name}' 时收到警告 (可能是格式问题): {feed.bozo_exception}")

            for entry in feed.entries:
                # 生成唯一ID (优先使用id，否则使用link)
                article_id = entry.get("id") or entry.get("link") or entry.get("title", "")

                if not article_id:
                    continue

                article = {
                    "id": article_id,
                    "title": entry.get("title", "无标题"),
                    "link": entry.get("link", ""),
                    "summary": entry.get("summary", entry.get("description", "无摘要")),
                    "source": source_name,
                    "published": entry.get("published", ""),
                }
                articles.append(article)

            logger.info(f"从 '{source_name}' 获取了 {len(feed.entries)} 篇文章")

        except requests.exceptions.HTTPError as e:
            # 捕获 403/404/500 等 HTTP 错误
            logger.error(f"获取 '{source_name}' 失败 - HTTP错误: {e.response.status_code} {e.response.reason}")
            continue
        except requests.exceptions.Timeout:
            logger.error(f"获取 '{source_name}' 失败 - 请求超时 (30秒)")
            continue
        except requests.exceptions.ConnectionError as e:
            logger.error(f"获取 '{source_name}' 失败 - 连接错误: {e}")
            continue
        except requests.exceptions.RequestException as e:
            logger.error(f"获取 '{source_name}' 失败 - 请求异常: {e}")
            continue
        except Exception as e:
            logger.error(f"获取 '{source_name}' 失败 - 未知错误: {e}")
            continue

    return articles


def filter_new_articles(articles: list, history: set) -> list:
    """
    过滤出新文章（不在历史记录中的）。

    Args:
        articles: 全部文章列表
        history: 历史记录ID集合

    Returns:
        list: 新文章列表
    """
    new_articles = []

    for article in articles:
        article_id = article.get("id", "")
        if article_id and article_id not in history:
            new_articles.append(article)

    logger.info(f"发现 {len(new_articles)} 篇新文章")
    return new_articles


# ============================================================
# AI 总结
# ============================================================


def generate_ai_summary(articles: list) -> Optional[str]:
    """
    使用 Gemini AI 生成文献总结。

    Args:
        articles: 新文章列表

    Returns:
        str: AI生成的中文总结，失败返回None
    """
    if not GEMINI_API_KEY:
        logger.error("未配置 GEMINI_API_KEY，无法进行AI总结")
        return None

    if not articles:
        logger.info("没有新文章，无需AI总结")
        return None

    # 准备发送给AI的内容
    articles_text = ""
    for i, article in enumerate(articles, 1):
        articles_text += f"""
---
文章 {i}:
标题: {article['title']}
来源: {article['source']}
摘要: {article['summary'][:500]}...
链接: {article['link']}
"""

    prompt = f"""你是一个风湿免疫科专家，请将以下关于"儿童红斑狼疮"的最新文献整理成中文日报。

请按以下格式输出：
1. 分为【重磅】、【临床】、【基础】三类
2. 每条内容包含：
   - 📌 中文标题
   - 💡 一句话通俗解读（让非专业人士也能理解）
   - 🔗 原文链接

如果某个分类没有相关文章，可以省略该分类。
在开头加上日期标题，格式如：📅 {datetime.now().strftime('%Y年%m月%d日')} 儿童红斑狼疮研究日报

以下是今日收集的文献：
{articles_text}
"""

    try:
        # 配置 Gemini
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")

        logger.info("正在调用 Gemini AI 生成总结...")
        response = model.generate_content(prompt)

        if response and response.text:
            logger.info("AI总结生成成功")
            return response.text
        else:
            logger.error("AI返回内容为空")
            return None

    except Exception as e:
        logger.error(f"AI总结失败: {e}")
        return None


# ============================================================
# Telegram 推送
# ============================================================


def send_telegram_message(text: str) -> bool:
    """
    发送消息到 Telegram。

    Args:
        text: 要发送的消息文本

    Returns:
        bool: 发送成功返回True
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.error("未配置 TELEGRAM_BOT_TOKEN 或 TELEGRAM_CHAT_ID")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    # Telegram 消息有长度限制 (4096 字符)，需要分段发送
    max_length = 4000
    messages = []

    if len(text) <= max_length:
        messages.append(text)
    else:
        # 按段落分割，尽量保持完整性
        paragraphs = text.split("\n\n")
        current_message = ""

        for para in paragraphs:
            if len(current_message) + len(para) + 2 <= max_length:
                current_message += para + "\n\n"
            else:
                if current_message:
                    messages.append(current_message.strip())
                current_message = para + "\n\n"

        if current_message:
            messages.append(current_message.strip())

    success = True
    for i, msg in enumerate(messages, 1):
        try:
            payload = {
                "chat_id": TELEGRAM_CHAT_ID,
                "text": msg,
                "parse_mode": "Markdown",
                "disable_web_page_preview": True,
            }

            response = requests.post(url, json=payload, timeout=30)

            if response.status_code == 200:
                logger.info(f"消息 {i}/{len(messages)} 发送成功")
            else:
                # 如果 Markdown 解析失败，尝试纯文本
                payload["parse_mode"] = None
                response = requests.post(url, json=payload, timeout=30)

                if response.status_code == 200:
                    logger.info(f"消息 {i}/{len(messages)} 以纯文本发送成功")
                else:
                    logger.error(f"消息发送失败: {response.text}")
                    success = False

        except requests.RequestException as e:
            logger.error(f"发送Telegram消息失败: {e}")
            success = False

    return success


# ============================================================
# 主流程
# ============================================================


def main():
    """主函数：协调整个工作流程"""
    logger.info("=" * 50)
    logger.info("医疗情报收集机器人启动")
    logger.info("=" * 50)

    # 验证必要配置
    missing_configs = []
    if not TELEGRAM_BOT_TOKEN:
        missing_configs.append("TELEGRAM_BOT_TOKEN")
    if not TELEGRAM_CHAT_ID:
        missing_configs.append("TELEGRAM_CHAT_ID")
    if not GEMINI_API_KEY:
        missing_configs.append("GEMINI_API_KEY")

    if missing_configs:
        logger.warning(f"缺少以下环境变量配置: {', '.join(missing_configs)}")
        logger.warning("部分功能可能无法正常工作")

    # 1. 加载历史记录
    history = load_history()

    # 2. 获取RSS文章
    all_articles = fetch_rss_articles(RSS_SOURCES)
    logger.info(f"共获取 {len(all_articles)} 篇文章")

    # 3. 过滤新文章
    new_articles = filter_new_articles(all_articles, history)

    if not new_articles:
        logger.info("没有新文章，任务结束")
        return

    # 4. 更新历史记录
    for article in new_articles:
        history.add(article["id"])

    # 5. AI总结
    summary = generate_ai_summary(new_articles)

    if summary:
        # 6. 发送到 Telegram
        send_telegram_message(summary)
    else:
        # 如果AI总结失败，发送简单的文章列表
        fallback_message = f"📅 {datetime.now().strftime('%Y年%m月%d日')} 新文献通知\n\n"
        fallback_message += f"今日发现 {len(new_articles)} 篇新文献:\n\n"
        for article in new_articles[:10]:  # 限制数量
            fallback_message += f"• {article['title']}\n  {article['link']}\n\n"

        send_telegram_message(fallback_message)

    # 7. 保存历史记录（关键步骤，必须执行）
    save_history(history)

    logger.info("=" * 50)
    logger.info("任务完成")
    logger.info("=" * 50)


if __name__ == "__main__":
    main()


