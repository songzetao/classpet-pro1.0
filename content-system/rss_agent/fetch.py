#!/usr/bin/env python3
"""
RSS Agent
任务：抓取RSS源，获取每日热点信息
输入：RSS源列表 + RSSHub公众号源
输出：raw_feeds_{date}.json
"""

import json
import feedparser
from datetime import datetime
import os

# RSSHub官方实例
RSSHUB_BASE = "https://rsshub.app"

RSS_SOURCES = {
    "hotel_ota": [
        {"name": "Skift", "url": "https://skift.com/feed/"},
        {"name": "环球旅讯", "url": "https://www.traveldaily.cn/rss"},
        {"name": "品橙旅游", "url": "https://www.pinchain.com/rss"},
    ],
    "business": [
        {"name": "虎嗅", "url": "https://www.huxiu.com/rss/0.xml"},
        {"name": "36氪", "url": "https://36kr.com/feed"},
    ],
    "news": [
        {"name": "Reuters", "url": "https://www.reuters.com/rssFeed/businessNews"},
    ],
    "wechat_hotel": [
        # 酒店行业公众号（通过RSSHub）
        {"name": "酒店高参", "url": f"{RSSHUB_BASE}/wechat/official/酒店高参"},
        {"name": "酒店评论", "url": f"{RSSHUB_BASE}/wechat/official/酒店评论"},
        {"name": "酒管财经", "url": f"{RSSHUB_BASE}/wechat/official/酒管财经"},
    ],
    "wechat_business": [
        # 商业观察公众号
        {"name": "刘润", "url": f"{RSSHUB_BASE}/wechat/official/刘润"},
        {"name": "远川研究所", "url": f"{RSSHUB_BASE}/wechat/official/远川研究所"},
        {"name": "笔记侠", "url": f"{RSSHUB_BASE}/wechat/official/笔记侠"},
    ]
}

def fetch_rss():
    """抓取所有RSS源"""
    results = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "sources": []
    }
    
    for category, sources in RSS_SOURCES.items():
        for source in sources:
            try:
                print(f"   📡 抓取: {source['name']}...")
                feed = feedparser.parse(source["url"])
                
                # 检查是否成功
                if hasattr(feed, 'status') and feed.status >= 400:
                    raise Exception(f"HTTP {feed.status}")
                
                items = []
                for entry in feed.entries[:10]:  # 每个源取前10条
                    items.append({
                        "title": entry.get("title", ""),
                        "summary": entry.get("summary", entry.get("description", ""))[:200],
                        "link": entry.get("link", ""),
                        "pubDate": entry.get("published", "")
                    })
                
                results["sources"].append({
                    "name": source["name"],
                    "category": category,
                    "status": "success",
                    "items": items,
                    "item_count": len(items)
                })
                print(f"      ✅ 成功: {len(items)}条")
                
            except Exception as e:
                print(f"      ❌ 失败: {e}")
                results["sources"].append({
                    "name": source["name"],
                    "category": category,
                    "status": "failed",
                    "error": str(e),
                    "items": [],
                    "item_count": 0
                })
    
    # 统计
    total_items = sum(s.get("item_count", 0) for s in results["sources"])
    success_count = sum(1 for s in results["sources"] if s["status"] == "success")
    
    results["summary"] = {
        "total_sources": len(results["sources"]),
        "success_sources": success_count,
        "total_items": total_items
    }
    
    # 保存结果
    output_dir = "/Users/yr/.openclaw/workspace/data"
    os.makedirs(output_dir, exist_ok=True)
    
    filename = f"{output_dir}/raw_feeds_{datetime.now().strftime('%Y-%m-%d')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n📊 抓取完成: {success_count}/{len(results['sources'])} 个源, {total_items} 条内容")
    print(f"💾 已保存: {filename}")
    
    return results

if __name__ == "__main__":
    print(f"{'='*50}")
    print("📡 RSS Agent 启动")
    print(f"{'='*50}")
    fetch_rss()
