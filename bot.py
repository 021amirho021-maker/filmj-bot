from datetime import datetime
import os
import random
import requests
from bs4 import BeautifulSoup

TARGET_SITES = [
    "https://www.film2movie.asia/",
    "https://www.doostihaa.com/",
    "https://salamcinema.ir/"
]

RUBIKA_TOKEN = "CEEDJE0NSCPVLWRZSPQCCGYNLTWTKOKYHYVAIBGSKSVRJGHTXVPXXHXOZQLWXRTT"
CHANNEL_USERNAME = "@moarefi_film_ir"  # اگر گاید کانال را دارید، اینجا به جای یوزرنیم قرار دهید
LAST_URL_FILE = "last_url.txt"

def get_last_posted_url():
    if os.path.exists(LAST_URL_FILE):
        with open(LAST_URL_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    return ""

def save_last_posted_url(url):
    with open(LAST_URL_FILE, "w", encoding="utf-8") as f:
        f.write(url)
    try:
        os.system('git config --global user.name "github-actions[bot]"')
        os.system('git config --global user.email "github-actions[bot]@users.noreply.github.com"')
        os.system(f'git add {LAST_URL_FILE}')
        os.system('git commit -m "Update last posted url [skip ci]"')
        os.system('git push')
    except Exception:
        pass

def send_video_to_rubika(video_path, caption):
    url = f"https://botapi.rubika.ir/v3/{RUBIKA_TOKEN}/sendVideo"
    try:
        with open(video_path, 'rb') as f:
            files = {'video': f}
            data = {'chat_id': CHANNEL_USERNAME, 'caption': caption}
            response = requests.post(url, files=files, data=data, timeout=60)
            
            # چاپ پاسخ دقیق سرور روبیکا برای عیب‌یابی
            print(f"📥 پاسخ سرور روبیکا: {response.text}")
            
            res_json = response.json()
            if res_json.get('status') == 'OK' or 'message_id' in str(res_json):
                print("✅ تریلر با موفقیت در کانال ارسال شد.")
                return True
            else:
                print(f"❌ سرور روبیکا درخواست را رد کرد: {response.text}")
                return False
    except Exception as e:
        print(f"❌ خطا در ارسال فایل ویدیو: {e}")
        return False

def main():
    print("🚀 ربات در حال بررسی و ارسال...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    last_url = get_last_posted_url()
    posted_successfully = False

    for target_site in TARGET_SITES:
        if posted_successfully:
            break
            
        try:
            response = requests.get(target_site, headers=headers, timeout=15)
            if response.status_code != 200:
                continue
                
            soup = BeautifulSoup(response.text, 'html.parser')
            posts = soup.find_all('div', class_='post') or soup.find_all('article') or soup.find_all('div', class_='item')
            
            if not posts:
                continue

            for p in posts[:5]:
                if posted_successfully:
                    break

                title_tag = p.find('h2') or p.find('h1') or p.find('h3')
                if not title_tag:
                    continue
                title = title_tag.get_text(strip=True)
                
                link_tag = p.find('a', href=True)
                if not link_tag:
                    continue
                post_url = link_tag['href']
                
                if post_url == last_url:
                    continue
                
                print(f"🎯 تست ارسال برای: {title}")
                post_response = requests.get(post_url, headers=headers, timeout=15)
                if post_response.status_code != 200:
                    continue
                    
                post_soup = BeautifulSoup(post_response.text, 'html.parser')
                
                short_desc = "بدون اسپویل | کیفیت عالی و ترافیک نیم‌بها."
                content_div = post_soup.find('div', class_='content') or post_soup.find('div', class_='post-content')
                if content_div:
                    paragraph = content_div.find('p')
                    if paragraph and len(paragraph.get_text(strip=True)) > 20:
                        short_desc = paragraph.get_text(strip=True)[:160] + "..."
                
                trailer_url = None
                for a in post_soup.find_all(['a', 'source'], href=True):
                    href = a.get('href') or a.get('src', '')
                    if href and ('trailer' in href.lower() or 'teaser' in href.lower() or href.endswith('.mp4')):
                        trailer_url = href
                        break
                
                if not trailer_url:
                    continue
                
                is_comedy = "کمدی" in title or "طنز" in title or "خنده‌دار" in short_desc
                genre = "کمدی / طنز 😂" if is_comedy else "سینمایی روز 🔥"
                
                caption = (
                    f"🎬 **{title}**\n\n"
                    f"⭐ امتیاز: ویژه 📅 سال: جدید 🎭 ژانر: {genre}\n\n"
                    f"📝 **معرفی کوتاه:**\n"
                    f"{short_desc}\n\n"
                    f"📥 **لینک دانلود مستقیم و نیم‌بها:**\n"
                    f"🔗 {post_url}\n\n"
                    f"🔥 ترند این روزها\n"
                    f"#فیلم #سریال #معرفی_فیلم #تریلر\n\n"
                    f"📌 {CHANNEL_USERNAME}"
                )
                
                trailer_res = requests.get(trailer_url, stream=True, timeout=30)
                if trailer_res.status_code == 200:
                    video_path = "trailer.mp4"
                    with open(video_path, 'wb') as f:
                        for chunk in trailer_res.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                    
                    success = send_video_to_rubika(video_path, caption)
                    
                    if os.path.exists(video_path):
                        os.remove(video_path)
                        
                    if success:
                        save_last_posted_url(post_url)
                        posted_successfully = True
                        break
                
        except Exception as e:
            print(f"⚠️ خطا: {e}")
            continue

if __name__ == "__main__":
    main()
