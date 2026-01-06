# filename: main.py
"""
医疗情报自动收集与推送机器人 (全能版)
支持: Google Gemini, DeepSeek, 豆包 (Doubao), 通义千问 (Qwen)
"""

import os
import json
import logging
import time
from datetime import datetime
from typing import Optional

import feedparser
import requests
import google.generativeai as genai
from openai import OpenAI

# ============================================================
# 配置区域
# ============================================================

# 基础配置
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

# AI 提供商选择: "gemini", "deepseek", "doubao", "qwen"
AI_PROVIDER = os.environ.get("AI_PROVIDER", "gemini").lower()

# 各家 API Key
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DOUBAO_API_KEY = os.environ.get("DOUBAO_API_KEY", "")
QWEN_API_KEY = os.environ.get("QWEN_API_KEY", "")

# 模型名称配置
# DeepSeek 默认: deepseek-chat
# 豆包: 填接入点ID (如 ep-202406...)
# 通义千问: qwen-plus (性价比高) 或 qwen-max (能力强)
AI_MODEL_NAME = os.environ.get("AI_MODEL_NAME", "")

# RSS 源列表
RSS_SOURCES = [
    {
        "name": "PubMed - Pediatric SLE",
        "url": "https://pubmed.ncbi.nlm.nih.gov/rss/search/14_xQ7JEOWXDuopaPahtu8vYOV9ttMUxoq8IeKOLBpA7Zak9UG/?limit=15&utm_campaign=pubmed-2&fc=20260103215413",
    },
    {
        "name": "ClinicalTrials - Pediatric Lupus",
        "url": "https://clinicaltrials.gov/api/rss?cond=Systemic+Lupus+Erythematosus&term=Child",
    },
]

HISTORY_FILE = "history_new.json"
MAX_HISTORY_SIZE = 1000

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# ============================================================
# 核心功能：AI 总结 (通用适配器)
# ============================================================

def get_ai_summary(text_content: str) -> Optional[str]:
    """根据配置的 AI_PROVIDER 调用不同的 AI"""
    
    prompt = f"""你是一个风湿免疫科专家，请将以下关于"儿童红斑狼疮"的最新文献整理成中文日报。
日期: {datetime.now().strftime('%Y-%m-%d')}
要求：
1. 分为【重磅】、【临床】、【基础】三类。
2. 每个条目包含：中文标题、一句话通俗解读、原文链接。
3. 保持专业且易读。

待处理文献：
{text_content}
"""

    try:
        # ---------------------------------------
        # 分支 1: 使用 Google Gemini
        # ---------------------------------------
        if AI_PROVIDER == "gemini":
            logger.info("正在调用 Google Gemini...")
            if not GEMINI_API_KEY:
                logger.error("缺少 GEMINI_API_KEY")
                return None
            
            genai.configure(api_key=GEMINI_API_KEY)
            # 如果没指定模型，默认用 flash
            model_name = AI_MODEL_NAME if AI_MODEL_NAME else "gemini-1.5-flash"
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            return response.text if response else None

        # ---------------------------------------
        # 分支 2: 使用 DeepSeek
        # ---------------------------------------
        elif AI_PROVIDER == "deepseek":
            model_use = AI_MODEL_NAME if AI_MODEL_NAME else "deepseek-chat"
            logger.info(f"正在调用 DeepSeek ({model_use})...")
            if not DEEPSEEK_API_KEY:
                logger.error("缺少 DEEPSEEK_API_KEY")
                return None

            client = OpenAI(
                api_key=DEEPSEEK_API_KEY, 
                base_url="https://api.deepseek.com"
            )
            
            response = client.chat.completions.create(
                model=model_use,
                messages=[
                    {"role": "system", "content": "你是一个专业的医学情报助手。"},
                    {"role": "user", "content": prompt},
                ],
                stream=False
            )
            return response.choices[0].message.content

        # ---------------------------------------
        # 分支 3: 使用 豆包 (Doubao)
        # ---------------------------------------
        elif AI_PROVIDER == "doubao":
            logger.info(f"正在调用 豆包 (接入点: {AI_MODEL_NAME})...")
            if not DOUBAO_API_KEY:
                logger.error("缺少 DOUBAO_API_KEY")
                return None
            if not AI_MODEL_NAME:
                logger.error("豆包必须在 Secrets 里配置 AI_MODEL_NAME (接入点ID)")
                return None

            client = OpenAI(
                api_key=DOUBAO_API_KEY,
                base_url="https://ark.cn-beijing.volces.com/api/v3"
            )
            
            response = client.chat.completions.create(
                model=AI_MODEL_NAME, # 豆包这里填接入点 ID
                messages=[
                    {"role": "system", "content": "你是一个专业的医学情报助手。"},
                    {"role": "user", "content": prompt},
                ],
            )
            return response.choices[0].message.content

        # ---------------------------------------
        # 分支 4: 使用 通义千问 (Qwen) - 新增！
        # ---------------------------------------
        elif AI_PROVIDER == "qwen":
            model_use = AI_MODEL_NAME if AI_MODEL_NAME else "qwen-plus"
            logger.info(f"正在调用 通义千问 ({model_use})...")
            if not QWEN_API_KEY:
                logger.error("缺少 QWEN_API_KEY")
                return None

            # 阿里云 DashScope 兼容 OpenAI 协议
            client = OpenAI(
                api_key=QWEN_API_KEY,
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
            )
            
            response = client.chat.completions.create(
                model=model_use,
                messages=[
                    {"role": "system", "content": "你是一个专业的医学情报助手。"},
                    {"role": "user", "content": prompt},
                ],
            )
            return response.choices[0].message.content

        else:
            logger.error(f"未知的 AI_PROVIDER: {AI_PROVIDER}")
            return None

    except Exception as e:
        logger.error(f"AI 调用失败 ({AI_PROVIDER}): {e}")
        return None

# ============================================================
# 辅助函数 (Send Message Fix)
# ============================================================

def load_history() -> set:
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except: return set()
    return set()

def save_history(history: set) -> None:
    history_list = list(history)[-MAX_HISTORY_SIZE:]
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history_list, f, ensure_ascii=False, indent=2)

def fetch_rss_articles(sources: list) -> list:
    articles = []
    session = requests.Session()
    
    # 🕵️‍♂️ 强力伪装：模拟真实的 Chrome 浏览器
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    for source in sources:
        url = source.get("url")
        logger.info(f"正在连接: {source['name']} ...")
        
        try:
            # 增加超时时间到 60秒
            resp = session.get(url, headers=headers, timeout=60)
            
            # 🔍 关键调试日志：告诉我们对方服务器到底返回了什么
            if resp.status_code == 200:
                feed = feedparser.parse(resp.content)
                if feed.entries:
                    logger.info(f" -> ✅ 成功抓取 {len(feed.entries)} 篇文章")
                    for entry in feed.entries:
                        articles.append({
                            "id": entry.get("id") or entry.get("link"),
                            "title": entry.get("title", ""),
                            "link": entry.get("link", ""),
                            "summary": entry.get("summary", ""),
                            "source": source.get("name")
                        })
                else:
                    logger.warning(f" -> ⚠️ 连接成功(200)但内容为空。可能链接已失效，或返回了非RSS格式。")
                    logger.info(f" -> 页面前50个字符: {resp.text[:50]}") # 看看是不是报错页面
            else:
                logger.error(f" -> ❌ 抓取失败，状态码: {resp.status_code} (可能是IP被封锁)")
                
        except Exception as e:
            logger.error(f" -> 💥 网络错误: {e}")
            
    return articles

def send_telegram_message(text: str) -> bool:
    """发送消息到 Telegram，失败时自动降级为纯文本"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID: 
        logger.error("未配置 TELEGRAM_BOT_TOKEN 或 TELEGRAM_CHAT_ID")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    max_length = 4000
    messages = []
    while len(text) > 0:
        if len(text) > max_length:
            split_idx = text.rfind('\n', 0, max_length)
            if split_idx == -1: split_idx = max_length
            messages.append(text[:split_idx])
            text = text[split_idx:]
        else:
            messages.append(text)
            text = ""

    all_success = True
    for i, msg in enumerate(messages, 1):
        # 方案 A: Markdown
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": msg,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True
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

        # 方案 B: 纯文本降级
        payload.pop("parse_mode", None) 
        
        try:
            resp = requests.post(url, json=payload, timeout=30)
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
# 主入口
# ============================================================

def main():
    logger.info(f"启动医疗情报机器人 - 当前AI模型: {AI_PROVIDER}")
    
    history = load_history()
    all_articles = fetch_rss_articles(RSS_SOURCES)
    logger.info(f"🔍 调试: 共抓取到 {len(all_articles)} 篇原始文章")
    
    # ⚠️ 强制模式：无视历史记录，强制发送所有文章（测试用）
    new_articles = all_articles 
    # new_articles = [a for a in all_articles if a["id"] not in history] # 原代码先注释掉
    
    if not new_articles:
        logger.info("无新文章")
        # send_telegram_message(f"📅 {datetime.now().strftime('%Y-%m-%d')} 日报\n今日暂无新文献。")
        return

    articles_text = ""
    for i, a in enumerate(new_articles, 1):
        articles_text += f"\n--- 文章 {i} ---\n标题: {a['title']}\n摘要: {a['summary'][:500]}\n链接: {a['link']}\n"

    summary = get_ai_summary(articles_text)

    if summary:
        if send_telegram_message(summary):
            for a in new_articles: history.add(a["id"])
            save_history(history)
            logger.info("任务完成")
        else:
            logger.error("消息发送失败，不保存历史记录")
    else:
        logger.error("AI 总结失败")

if __name__ == "__main__":
    main()