#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简易网页爬虫脚本
用法：
    python scraper.py [URL]
    如果不提供 URL，程序会提示输入。
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import sys
import time

def scrape(url):
    """爬取指定 URL，返回标题、正文预览和链接列表"""
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
    }

    try:
        print(f"⏳ 正在请求：{url}")
        resp = requests.get(url, timeout=15, headers=headers)
        resp.raise_for_status()
        resp.encoding = resp.apparent_encoding  # 自动检测编码
    except requests.exceptions.Timeout:
        return {'error': '请求超时，请检查网络或目标服务器响应慢。'}
    except requests.exceptions.ConnectionError:
        return {'error': '连接失败，请检查网址或网络。'}
    except requests.exceptions.HTTPError as e:
        return {'error': f'HTTP 错误：{e.response.status_code}'}
    except Exception as e:
        return {'error': f'请求出错：{str(e)}'}

    try:
        soup = BeautifulSoup(resp.text, 'html.parser')
        title = soup.title.string.strip() if soup.title else '无标题'
        text = ' '.join(soup.get_text().split())
        text_preview = text[:500] + ('...' if len(text) > 500 else '')

        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            full_url = urljoin(url, href)
            text_link = a.get_text(strip=True) or '[无文字]'
            # 过滤常见的非网页链接（如 javascript:、mailto: 等）
            if full_url.startswith(('http://', 'https://')):
                links.append({'text': text_link, 'href': full_url})

        # 去重并限制数量
        unique_links = []
        seen = set()
        for link in links:
            if link['href'] not in seen:
                seen.add(link['href'])
                unique_links.append(link)
        links = unique_links[:30]  # 最多显示30个

        return {
            'title': title,
            'text_preview': text_preview,
            'links': links,
            'link_count': len(links)
        }
    except Exception as e:
        return {'error': f'解析失败：{str(e)}'}


def main():
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = input("请输入要爬取的网址（如 https://example.com）：").strip()
        if not url:
            print("❌ 未输入网址，退出。")
            return

    result = scrape(url)

    if 'error' in result:
        print(f"❌ {result['error']}")
        return

    print("\n" + "=" * 60)
    print(f"📄 标题：{result['title']}")
    print("=" * 60)
    print(f"📝 正文预览（前500字符）：\n{result['text_preview']}")
    print("=" * 60)
    print(f"🔗 找到 {result['link_count']} 个链接（显示前30个）：")
    for idx, link in enumerate(result['links'], 1):
        print(f"{idx}. {link['text']} → {link['href']}")
    print("=" * 60)
    print("✅ 爬取完成。")


if __name__ == '__main__':
    main()