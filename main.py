# filename: main.py
"""
医疗情报自动收集与推送机器人 (v3.0 多模型版)

功能: 从 RSS 源获取医学文献，使用 AI 总结，推送到 Telegram
支持: Gemini, DeepSeek, 豆包(Doubao), 通义千问(Qwen)
"""

# ============================================================
# 导入模块
# ============================================================

# 标准库
import json
import logging
import os
import time
from datetime import datetime
from typing import Optional

# 第三方库
import feedparser
import google.generativeai as genai
import requests
from openai import OpenAI

# ============================================================
# 配置区域
# ============================================================

# --- Telegram 配置 ---
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

# --- AI 提供商配置 ---
# 可选值: gemini, deepseek, doubao, qwen (默认 gemini)
AI_PROVIDER = os.environ.get("AI_PROVIDER", "gemini").lower()

# 各 AI 提供商的 API Key
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DOUBAO_API_KEY = os.environ.get("DOUBAO_API_KEY", "")
QWEN_API_KEY = os.environ.get("QWEN_API_KEY", "")

# 自定义模型名称 (可选，用于指定具体模型或豆包的接入点 ID)
AI_MODEL_NAME = os.environ.get("AI_MODEL_NAME", "")

# --- RSS 源列表 ---
RSS_SOURCES = [
    {
        "name": "PubMed - Pediatric SLE",
        # 搜索关键词: Systemic Lupus Erythematosus AND Child
        "url": "https://pubmed.ncbi.nlm.nih.gov/rss/search/14_xQ7JEOWXDuopaPahtu8vYOV9ttMUxoq8IeKOLBpA7Zak9UG/?limit=15&utm_campaign=pubmed-2&fc=20260103215413",
    },
    {
        "name": "Top Journals (NEJM/Lancet/Nature/ARD)",
        # 顶级期刊红斑狼疮研究
        "url": "https://pubmed.ncbi.nlm.nih.gov/rss/search/1houoX_LGC3Y5rpUnbir5VljX_fEj1HoolaYuUt4RMxsPBbkIL/?limit=15&utm_campaign=pubmed-2&fc=20260106101820",
    },
    {
        "name": "ClinicalTrials - Pediatric Lupus",
        # 搜索关键词: SLE (Condition) + Child (Term)
        "url": "https://clinicaltrials.gov/api/rss?cond=Systemic+Lupus+Erythematosus&term=Child",
    },
]

# --- 历史记录配置 ---
HISTORY_FILE = "history.json"
MAX_HISTORY_SIZE = 1000  # 最大历史记录数量，防止文件无限增大

# --- 日志配置 ---
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
        已处理过的文章 ID 集合
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
    保存历史记录到文件，自动截断至最大数量。

    Args:
        history: 文章 ID 集合
    """
    history_list = list(history)
    if len(history_list) > MAX_HISTORY_SIZE:
        history_list = history_list[-MAX_HISTORY_SIZE:]

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
    从 RSS 源获取文章列表，包含反爬虫策略。

    Args:
        sources: RSS 源配置列表

    Returns:
        文章列表，每篇包含 id, title, link, summary, source, published
    """
    articles = []
    session = requests.Session()

    for source in sources:
        source_name = source.get("name", "Unknown")
        url = source.get("url", "")

        if not url:
            continue

        logger.info(f"正在获取: {source_name}")

        # 针对不同来源定制 Headers
        if "pubmed" in url.lower():
            headers = {
                "User-Agent": "MedicalIntelligenceBot/1.0 (Research Purpose)",
                "Referer": "https://pubmed.ncbi.nlm.nih.gov/",
                "Accept": "*/*",
            }
        else:
            # ClinicalTrials 等其他网站模拟浏览器
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            }

        try:
            # 延时避免封禁
            time.sleep(2)
            response = session.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            feed = feedparser.parse(response.content)

            current_count = 0
            for entry in feed.entries:
                article_id = entry.get("id") or entry.get("link") or entry.get("title", "")
                if not article_id:
                    continue

                articles.append({
                    "id": article_id,
                    "title": entry.get("title", "无标题"),
                    "link": entry.get("link", ""),
                    "summary": entry.get("summary", entry.get("description", "无摘要")),
                    "source": source_name,
                    "published": entry.get("published", ""),
                })
                current_count += 1

            logger.info(f"从 '{source_name}' 获取了 {current_count} 篇文章")

        except Exception as e:
            logger.error(f"获取 '{source_name}' 失败: {e}")

    session.close()
    return articles


def filter_new_articles(articles: list, history: set) -> list:
    """
    过滤出新文章（不在历史记录中的）。

    Args:
        articles: 全部文章列表
        history: 历史记录 ID 集合

    Returns:
        新文章列表
    """
    new_articles = [a for a in articles if a.get("id") and a.get("id") not in history]
    logger.info(f"发现 {len(new_articles)} 篇新文章")
    return new_articles


# ============================================================
# AI 总结 (多模型支持)
# ============================================================

def build_prompt(articles: list) -> str:
    """
    构建发送给 AI 的 Prompt。

    Args:
        articles: 文章列表

    Returns:
        格式化的 Prompt 字符串
    """
    articles_text = ""
    for i, article in enumerate(articles, 1):
        summary_truncated = article["summary"][:500]
        articles_text += (
            f"\n--- 文章 {i} ---\n"
            f"标题: {article['title']}\n"
            f"摘要: {summary_truncated}...\n"
            f"链接: {article['link']}\n"
        )

    prompt = f"""你是一个风湿免疫科专家，请将以下关于"儿童红斑狼疮"的最新文献整理成中文日报。

日期: {datetime.now().strftime('%Y-%m-%d')}

要求：
1. 分为【重磅】、【临床】、【基础】三类。
2. 每个条目包含：中文标题、一句话通俗解读、原文链接。
3. 保持专业且易读。
4. 重要：请不要在输出中使用不闭合的 Markdown 符号（如单个 * 或 _），尽量避免使用复杂的格式，使用纯文本或简单的 emoji 即可。

待处理文献：
{articles_text}
"""
    return prompt


def generate_with_gemini(prompt: str) -> Optional[str]:
    """
    使用 Google Gemini 生成总结。

    Args:
        prompt: 提示词

    Returns:
        生成的文本，失败返回 None
    """
    if not GEMINI_API_KEY:
        logger.error("未配置 GEMINI_API_KEY")
        return None

    try:
        genai.configure(api_key=GEMINI_API_KEY)

        logger.info("正在自动选择最佳 Gemini 模型...")
        available_models = []
        try:
            for m in genai.list_models():
                if "generateContent" in m.supported_generation_methods:
                    available_models.append(m.name)
        except Exception as e:
            logger.warning(f"无法列出模型，尝试使用默认值: {e}")

        # 确定模型名称
        model_name = AI_MODEL_NAME if AI_MODEL_NAME else "models/gemini-pro"

        # 优先选择策略: Flash > Pro > 其他
        if available_models and not AI_MODEL_NAME:
            flash_models = [m for m in available_models if "flash" in m]
            pro_models = [m for m in available_models if "pro" in m]

            if flash_models:
                model_name = flash_models[0]
            elif pro_models:
                model_name = pro_models[0]

        logger.info(f"已选择 Gemini 模型: {model_name}")
        model = genai.GenerativeModel(model_name)

        response = model.generate_content(prompt)
        if response and response.text:
            logger.info("Gemini 总结生成成功")
            return response.text

    except Exception as e:
        logger.error(f"Gemini 总结失败: {e}")

    return None


def generate_with_openai_compatible(prompt: str, provider: str) -> Optional[str]:
    """
    使用 OpenAI 兼容模式调用 DeepSeek / 豆包 / 通义千问。

    Args:
        prompt: 提示词
        provider: 提供商名称 (deepseek, doubao, qwen)

    Returns:
        生成的文本，失败返回 None
    """
    # 提供商配置表
    config = {
        "deepseek": {
            "base_url": "https://api.deepseek.com",
            "api_key": DEEPSEEK_API_KEY,
            "default_model": "deepseek-chat",
        },
        "doubao": {
            "base_url": "https://ark.cn-beijing.volces.com/api/v3",
            "api_key": DOUBAO_API_KEY,
            "default_model": "",  # 豆包必须通过 AI_MODEL_NAME 指定接入点 ID
        },
        "qwen": {
            "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
            "api_key": QWEN_API_KEY,
            "default_model": "qwen-plus",
        },
    }

    if provider not in config:
        logger.error(f"未知的 AI 提供商: {provider}")
        return None

    cfg = config[provider]
    api_key = cfg["api_key"]
    base_url = cfg["base_url"]
    model_name = AI_MODEL_NAME if AI_MODEL_NAME else cfg["default_model"]

    if not api_key:
        logger.error(f"未配置 {provider.upper()}_API_KEY")
        return None

    if not model_name:
        logger.error(f"使用 {provider} 时必须通过 AI_MODEL_NAME 环境变量指定模型/接入点 ID")
        return None

    logger.info(f"正在调用 {provider.upper()} API (模型: {model_name})...")

    try:
        client = OpenAI(api_key=api_key, base_url=base_url)

        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "你是一个专业的风湿免疫科医学文献助手。"},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=4096,
        )

        if response and response.choices and response.choices[0].message:
            result = response.choices[0].message.content
            logger.info(f"{provider.upper()} 总结生成成功")
            return result

    except Exception as e:
        logger.error(f"{provider.upper()} 总结失败: {e}")

    return None


def generate_ai_summary(articles: list) -> Optional[str]:
    """
    根据 AI_PROVIDER 配置调用对应的 AI 服务生成总结。

    支持的提供商:
        - gemini: Google Gemini (默认)
        - deepseek: DeepSeek
        - doubao: 字节跳动豆包
        - qwen: 阿里通义千问

    Args:
        articles: 文章列表

    Returns:
        AI 生成的总结文本，失败返回 None
    """
    if not articles:
        logger.info("没有新文章，无需 AI 总结")
        return None

    prompt = build_prompt(articles)
    logger.info(f"当前 AI 提供商: {AI_PROVIDER.upper()}")

    if AI_PROVIDER == "gemini":
        return generate_with_gemini(prompt)
    elif AI_PROVIDER in ["deepseek", "doubao", "qwen"]:
        return generate_with_openai_compatible(prompt, AI_PROVIDER)
    else:
        logger.error(f"不支持的 AI 提供商: {AI_PROVIDER}，支持的值: gemini, deepseek, doubao, qwen")
        return None


# ============================================================
# Telegram 推送
# ============================================================

def escape_markdown(text: str) -> str:
    """
    转义 Telegram Markdown 中的特殊字符，防止解析错误。

    Args:
        text: 原始文本

    Returns:
        转义后的文本
    """
    def fix_unpaired(text: str, char: str) -> str:
        """修复不成对的特殊字符"""
        count = text.count(char)
        if count % 2 != 0:
            text = text.replace(char, "\\" + char)
        return text

    text = fix_unpaired(text, "*")
    text = fix_unpaired(text, "_")
    text = fix_unpaired(text, "`")

    # 转义 [ 但保留有效的链接格式 [text](url)
    result = []
    i = 0
    while i < len(text):
        if text[i] == "[":
            close_bracket = text.find("]", i)
            if close_bracket != -1 and close_bracket + 1 < len(text) and text[close_bracket + 1] == "(":
                result.append(text[i])
            else:
                result.append("\\[")
        else:
            result.append(text[i])
        i += 1

    return "".join(result)


def send_telegram_message(text: str) -> bool:
    """
    发送消息到 Telegram，失败时自动降级为纯文本。

    Args:
        text: 消息文本

    Returns:
        是否全部发送成功
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.error("未配置 TELEGRAM_BOT_TOKEN 或 TELEGRAM_CHAT_ID")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    # 切分长消息 (Telegram 单条消息限制 4096 字符)
    max_length = 4000
    messages = []
    remaining = text

    while len(remaining) > 0:
        if len(remaining) > max_length:
            split_idx = remaining.rfind("\n", 0, max_length)
            if split_idx == -1:
                split_idx = max_length
            messages.append(remaining[:split_idx])
            remaining = remaining[split_idx:].lstrip("\n")
        else:
            messages.append(remaining)
            remaining = ""

    all_success = True

    for i, msg in enumerate(messages, 1):
        # 方案 A: 尝试 Markdown 发送
        escaped_msg = escape_markdown(msg)
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": escaped_msg,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True,
        }

        try:
            resp = requests.post(url, json=payload, timeout=30)
            if resp.status_code == 200:
                logger.info(f"消息 {i}/{len(messages)} (Markdown) 发送成功")
                continue
            else:
                logger.warning(f"消息 {i} Markdown 发送失败 ({resp.text})，尝试纯文本重发...")
        except Exception as e:
            logger.warning(f"消息 {i} 网络异常: {e}")

        # 方案 B: 降级为纯文本发送
        payload_plain = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": msg,
            "disable_web_page_preview": True,
        }

        try:
            resp = requests.post(url, json=payload_plain, timeout=30)
            if resp.status_code == 200:
                logger.info(f"消息 {i}/{len(messages)} (纯文本) 发送成功")
            else:
                logger.error(f"消息 {i} 彻底失败: {resp.text}")
                all_success = False
        except Exception as e:
            logger.error(f"消息 {i} 纯文本重发异常: {e}")
            all_success = False

    return all_success


# ============================================================
# 主流程
# ============================================================

def main():
    """主函数：协调整个工作流程"""
    logger.info("=" * 50)
    logger.info("医疗情报收集机器人启动 (v3.0 多模型版)")
    logger.info(f"当前 AI 提供商: {AI_PROVIDER.upper()}")
    logger.info("=" * 50)

    # 1. 加载历史记录
    history = load_history()

    # 2. 获取 RSS 文章
    all_articles = fetch_rss_articles(RSS_SOURCES)

    # 3. 过滤新文章
    new_articles = filter_new_articles(all_articles, history)

    if not new_articles:
        logger.info("没有新文章，任务结束")
        return

    # 4. AI 总结
    summary = generate_ai_summary(new_articles)

    # 5. 推送消息
    if summary:
        send_telegram_message(summary)
    else:
        # AI 失败时的备选方案
        fallback = f"📅 {datetime.now().strftime('%Y-%m-%d')} 新文献通知 (AI 生成失败)\n\n"
        fallback += "\n".join([f"• {a['title']}\n  {a['link']}" for a in new_articles[:5]])
        send_telegram_message(fallback)

    # 6. 保存历史记录
    for a in new_articles:
        history.add(a["id"])
    save_history(history)

    logger.info("任务完成")


if __name__ == "__main__":
    main()
