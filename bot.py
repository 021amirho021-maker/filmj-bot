from datetime import datetime
import os
import re
from bs4 import BeautifulSoup
import requests

TARGET_SITES = [
    "https://www.film2movie.asia/",
    "https://www.doostihaa.com/"
]

RUBIKA_TOKEN = "CEEDJE0NSCPVLWRZSPQCCGYNLTWTKOKYHYVAIBGSKSVRJGHTXVPXXHXOZQLWXRTT"
CHAT_ID = "c0ECYaE0b68c6a209e2060cceebd2bd9" 
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

def clean_text(text):
    if not text:
        return ""
    # پاک کردن کاراکترهای خاصی که ممکن است باعث خطای INVALID_INPUT در روبیکا شوند
    text = re.sub(r'[^\w\s\-\.\,\!\?\(\)\ا-يآأإؤئبپتثجحخدذرزسشصضطظعغفقكگلمنوهيیچپژکگءۀة]', '', text)
    return text.strip()

def send_post_to_rubika(caption):
    url = f"https://botapi.rubika.ir/v3/{RUBIKA_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": caption
    }
    try:
        response = requests.post(url, json=payload, timeout=30)
        res_json = response.json()
        print(f"📥 پاسخ سرور روبیکا: {res_json}")
        
        if res_json.get('status') == 'OK' or 'message_id' in str(res_json):
            print("✅ پست معرفی فیلم با موفقیت در کانال ارسال شد.")
            return True
        else:
            print(f"❌ سرور روبیکا درخواست را رد کرد: {res_json}")
            return False
    except Exception as e:
        print(f"❌ خطا در ارسال پیام: {e}")
        return False

def main():
    print("🚀 ربات در حال بررسی سایت‌ها و انتشار پست...")
    
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
                
                print(f"🎯 بررسی فیلم: {title}")
                post_response = requests.get(post_url, headers=headers, timeout=15)
                if post_response.status_code != 200:
                    continue
                    
                post_soup = BeautifulSoup(post_response.text, 'html.parser')
                
                short_desc = "بدون اسپویل | کیفیت عالی و ترافیک نیم بها."
                content_div = post_soup.find('div', class_='content') or post_soup.find('div', class_='post-content')
                if content_div:
                    paragraph = content_div.find('p')
                    if paragraph and len(paragraph.get_text(strip=True)) > 20:
                        short_desc = paragraph.get_text(strip=True)[:160] + "..."
                
                clean_title = clean_text(title)
                clean_desc = clean_text(short_desc)
                if not clean_title:
                    clean_title = "فیلم جدید"
                
                is_comedy = "کمدی" in title or "طنز" in title
                genre = "کمدی / طنز" if is_comedy else "سینمایی روز"
                
                caption = (
                    f"🎬 {clean_title}\n\n"
                    f"امتیاز: ویژه | سال: جدید | ژانر: {genre}\n\n"
                    f"معرفی کوتاه:\n"
                    f"{clean_desc}\n\n"
                    f"لینک دانلود مستقیم و نیم بها:\n"
                    f"{post_url}\n\n"
                    f"ترند این روزها\n"
                    f"#فیلم #سریال #معرفی_فیلم #تریلر\n\n"
                    f"@moarefi_film_ir"
                )
                
                success = send_post_to_rubika(caption)
                if success:
                    save_last_posted_url(post_url)
                    posted_successfully = True
                    break
                
        except Exception as e:
            print(f"⚠️ خطا: {e}")
            continue

if __name__ == "__main__":
    main()
