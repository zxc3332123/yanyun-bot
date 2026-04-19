import os
import requests
from bs4 import BeautifulSoup
import time

# --- 設定區 ---
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK")
TARGET_URL = "https://www.wherewindsmeetgame.com/hmt/news/" # 新聞列表頁
# 為了避免被網站擋掉，模擬真人瀏覽器的 Header
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def fetch_yanyun_news():
    print(f"正在檢查《燕雲十六聲》官網公告...")
    try:
        response = requests.get(TARGET_URL, headers=HEADERS)
        response.encoding = 'utf-8' # 確保中文不亂碼
        soup = BeautifulSoup(response.text, 'html.parser')

        # 根據官網結構定位新聞 (這部分可能隨官網更新調整)
        # 假設新聞標題在 class 為 'news-item' 的 a 標籤中
        news_list = soup.find_all('a', class_='item') # 燕雲官網常見的標籤結構

        if not news_list:
            # 如果找不到，嘗試另一種常見的選擇器
            news_list = soup.select('.news_list li a')

        if news_list:
            latest = news_list[0]
            title = latest.find('p', class_='title').text.strip() if latest.find('p', class_='title') else "新公告"
            link = latest['href']
            
            # 處理相對路徑連結
            if link.startswith('/'):
                link = "https://www.wherewindsmeetgame.com" + link
            
            # 嘗試抓取預覽圖
            img_tag = latest.find('img')
            img_url = img_tag['src'] if img_tag else ""

            return title, link, img_url
    except Exception as e:
        print(f"抓取發生錯誤: {e}")
    
    return None, None, None

def send_to_discord(title, link, img_url):
    payload = {
        "embeds": [{
            "title": "🏮 《燕雲十六聲》最新情報",
            # 將紅線的台詞放在描述最上方，並與標題 {title} 做區隔
            "description": f"「老大，我又給你帶來新消息了，說好要給我松子糖的，你該不會又忘記了吧？🍬」\n\n**{title}**",
            "url": link,
            "color": 16711680,  # 燕雲風的紅色
            "image": {"url": img_url},
            "footer": {"text": "紅線特派員 · 期待松子糖中"}
        }]
    }
    res = requests.post(WEBHOOK_URL, json=payload)
    if res.status_code == 204:
        print("✅ 成功發布到 Discord！")

if __name__ == "__main__":
    title, link, img_url = fetch_yanyun_news()
    
    if title and link:
        # 讀取上一次發送過的連結
        try:
            with open("last_link.txt", "r") as f:
                last_link = f.read().strip()
        except FileNotFoundError:
            last_link = ""

        # 比對連結，如果不同才發送
        if link != last_link:
            print(f"發現新公告：{title}，準備發送...")
            send_to_discord(title, link, img_url)
            
            # 更新記憶體
            with open("last_link.txt", "w") as f:
                f.write(link)
        else:
            print("新聞已發送過，暫無新情報。")
    else:
        print("❌ 抓取失敗，請檢查網路或網頁結構。")
