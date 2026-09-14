from datetime import datetime
import os
import random
import requests
from bs4 import BeautifulSoup

# آدرس سایت منبع فیلم و سریال
TARGET_SITE_URL = "https://www.film2movie.asia/"

# اطلاعات ربات روبیکا
RUBIKA_TOKEN = "CEEDJE0NSCPVLWRZSPQCCGYNLTWTKOKYHYVAIBGSKSVRJGHTXVPXXHXOZQLWXRTT"
CHANNEL_USERNAME = "@moarefi_film_ir"
LAST_URL_FILE = "last_url.txt"

# متن‌های کوتاه و ادمین‌طوری با چاشنی طنز و سینما
ADMIN_SHORT_POSTS = [
    "پیشنهاد فیلم امشب 🎬 آماده یک خنده حسابی و پاپ‌کورن باشید 😂🍿",
    "یه کمدی ایرانی باحال برای اینکه خستگی امروزتون در بره 👇",
    "اگه امشب حوصله‌ات سر رفته، این فیلم طنز رو از دست نده 🔥",
    "معرفی فیلم جدید روی سایت قرار گرفت، بترکونید 🎬🍿"
]

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
            if response.status_code == 200:
                print("✅ تریلر با موفقیت در کانال ارسال شد.")
            else:
                print(f"❌ خطا در ارسال ویدیو: {response.text}")
    except Exception as e:
        print(f"❌ خطا در ارسال فایل ویدیو: {e}")

def send_text_to_rubika(message):
    url = f"https://botapi.rubika.ir/v3/{RUBIKA_TOKEN}/sendMessage"
    payload = {'chat_id': CHANNEL_USERNAME, 'text': message}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception:
        pass

def main():
    print("🚀 ربات هوشمند مدیریت کانال شروع به کار کرد...")
    
    current_hour = datetime.utcnow().hour
    if 11 <= current_hour <= 12:
        selected_msg = random.choice(ADMIN_SHORT_POSTS) + f"\n\n#کمدی_ایرانی #فیلم_طنز\n\n📌 {CHANNEL_USERNAME}"
        send_text_to_rubika(selected_msg)
        return

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        response = requests.get(TARGET_SITE_URL, headers=headers, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            posts = soup.find_all('div', class_='post') or soup.find_all('article')
            
            if posts:
                # 🎯 جستجوی هوشمند: اولویت با کمدی‌ها و آثار جدید ایرانی در بین پست‌های اخیر
                selected_post = posts[0]
                for p in posts[:8]:
                    t_tag = p.find('h2') or p.find('h1')
                    t_text = t_tag.get_text(strip=True) if t_tag else ""
                    # اگر اثر کمدی یا ایرانی بود، شانس بالاتری برای انتخاب دارد
                    if "کمدی" in t_text or "طنز" in t_text or "ایرانی" in t_text:
                        selected_post = p
                        break

                title_tag = selected_post.find('h2') or selected_post.find('h1')
                title = title_tag.get_text(strip=True) if title_tag else "عنوان نامشخص"
                
                link_tag = selected_post.find('a', href=True)
                post_url = link_tag['href'] if link_tag else TARGET_SITE_URL
                
                # 🛑 سیستم ضد تکرار
                last_url = get_last_posted_url()
                if post_url == last_url:
                    print("⏳ این اثر قبلاً در کانال منتشر شده است.")
                    return
                
                print(f"🔍 انتخاب‌شده برای انتشار: {title}")
                post_response = requests.get(post_url, headers=headers, timeout=15)
                
                short_desc = "پیشنهاد ویژه امروز، کیفیت عالی و ترافیک نیم‌بها."
                trailer_url = None
                
                if post_response.status_code == 200:
                    post_soup = BeautifulSoup(post_response.text, 'html.parser')
                    
                    content_div = post_soup.find('div', class_='content') or post_soup.find('div', class_='post-content')
                    if content_div:
                        paragraph = content_div.find('p')
                        if paragraph and len(paragraph.get_text(strip=True)) > 20:
                            short_desc = paragraph.get_text(strip=True)[:180] + "..."
                    
                    for a in post_soup.find_all('a', href=True):
                        href = a['href']
                        if 'trailer' in href.lower() or (href.endswith('.mp4') and 'teaser' in href.lower()):
                            trailer_url = href
                            break
                
                # تشخیص اینکه آیا فیلم کمدی/طنز است یا خیر برای هشتگ‌گذاری هوشمند
                is_comedy = "کمدی" in title or "طنز" in title or "خنده‌دار" in short_desc
                extra_tags = "#کمدی_ایرانی #فیلم_طنز #خنده" if is_comedy else "#سینمای_روز #فیلم_جدید"
                
                # 💎 کپشن لوکس و جذب‌کننده
                caption = (
                    f"🎬 **نام اثر:** {title}\n"
                    f"━━━━━━━━━━━━━━━━━━━\n"
                    f"📝 **خلاصه داستان:**\n"
                    f"{short_desc}\n\n"
                    f"🔥 **ویژگی‌های اثر:**\n"
                    f"✨ کیفیت بلوری و فول‌اچ‌دی (نسخه اورجینال)\n"
                    f"⚡️ ترافیک نیم‌بها و سرعت دانلود بالا\n"
                    f"🎙️ با زیرنویس فارسی چسبیده / نسخه کامل\n\n"
                    f"📥 **لینک دانلود مستقیم و نیم‌بها:**\n"
                    f"🔗 {post_url}\n"
                    f"━━━━━━━━━━━━━━━━━━━\n"
                    f"🌟 برای تماشای ترندترین فیلم و سریال‌های روز 👇\n\n"
                    f"#فیلم #سریال #معرفی_فیلم #تریلر #دانلود_فیلم {extra_tags}\n\n"
                    f"📌 {CHANNEL_USERNAME}"
                )
                
                if trailer_url:
                    print(f"📥 در حال دانلود تریلر...")
                    trailer_res = requests.get(trailer_url, stream=True, timeout=30)
                    if trailer_res.status_code == 200:
                        video_path = "trailer.mp4"
                        with open(video_path, 'wb') as f:
                            for chunk in trailer_res.iter_content(chunk_size=8192):
                                if chunk:
                                    f.write(chunk)
                        
                        print("📤 در حال آپلود در کانال...")
                        send_video_to_rubika(video_path, caption)
                        
                        if os.path.exists(video_path):
                            os.remove(video_path)
                            
                        save_last_posted_url(post_url)
                    else:
                        send_text_to_rubika(caption)
                        save_last_posted_url(post_url)
                else:
                    send_text_to_rubika(caption)
                    save_last_posted_url(post_url)
                    
            else:
                print("⏳ موردی پیدا نشد.")
        else:
            print(f"❌ خطا در اتصال. کد: {response.status_code}")
            
    except Exception as e:
        print(f"❌ خطا: {e}")
        
    print("🏁 پایان چرخه.")

if __name__ == "__main__":
    main()
