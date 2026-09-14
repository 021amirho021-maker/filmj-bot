import os
import random
import asyncio
import requests
from bs4 import BeautifulSoup

# نصب خودکار کتابخانه‌های مورد نیاز
try:
    import rubpy
except ImportError:
    os.system('pip install rubpy bs4 requests')
    import rubpy

from rubpy import BotClient

TARGET_SITES = [
    "https://www.film2movie.asia/",
    "https://www.doostihaa.com/",
    "https://salamdl.info/"
]

RUBIKA_TOKEN = "CEEDJE0NSCPVLWRZSPQCCGYNLTWTKOKYHYVAIBGSKSVRJGHTXVPXXHXOZQLWXRTT"
CHAT_ID = "@moarefi_film_ir"
HISTORY_FILE = "posted_urls.txt"
MODE_FILE = "post_mode.txt"

# بانک جامع و متنوع از متن‌های ادمین‌طوری (کاملاً غیرتکراری و جذاب)
ADMIN_MESSAGES = [
    "سلام بچه‌ها! 👋 امشب وقتشه یکم فیلم‌بازی دراریم؛ به نظرتون بهترین فیلم اکشن سال کدوم بود؟ اسمشو بگین بقیه هم استفاده کنن! 🔥",
    "🎬 بچه‌ها بین فیلم‌های درام و روان‌شناختی با فیلم‌های کمدی و حال‌خوب‌کن، کدوم رو برای آخر هفته ترجیح میدید؟",
    "🍿 یه سوال سینمایی: بازیگر مرد یا زن ایرانی و خارجی که همیشه با دیدن فیلمهاش کیف می‌کنید کیه؟ برامون کامنت کنید 👇",
    "✨ راستی کیفیت فایل‌ها و لینک‌های دانلود نیم‌بها چطوره؟ اگر ژانر خاصی مد نظرتونه بگید تا بیشتر از اون سبک بذاریم.",
    "توصیه ادمین برای امشب: چرا چراغ‌ها رو خاموش نکنید و یه فیلم ترسناک یا معمایی سنگین نمی‌بینید؟ کیا پایه‌ان؟ 👻",
    "بچه‌ها سریال در حال پخشی هست که دارین دنبالش می‌کنید و واقعاً جذاب باشه؟ اسمشو تو نظرات بگین تا بررسی‌ش کنیم 📺",
    "صدا، تصویر، داستان... به نظرتون کدوم فاکتور تو یک فیلم از همه مهم‌تره که شمارو تا آخر پای فیلم میخکوب کنه؟ 🤔",
    "یه چالش کوتاه: اگر قرار باشه فقط تا آخر عمرت بتونی فیلم‌های یک ژانر رو تماشا کنی، کدوم ژانر رو انتخاب می‌کنی؟ (کمدی، اکشن، ترسناک، علمی‌تخیلی؟)",
    "بچه‌ها نظرتون درباره فیلم‌های زیرنویس‌چسبیده چیه راحت‌ترید یا دوبله فارسی؟ برامون بنویسید 💬",
    "آخر هفته‌تون چطور گذشت؟ فیلم خوبی دیدید که ارزش معرفی داشته باشه و ما نذاریم توی کانال؟ معرفی کنید بقیه هم ببینن! 🎬"
]

def get_posted_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f if line.strip())
    return set()

def save_to_history(item_str):
    posted = get_posted_history()
    posted.add(item_str)
    
    posted_list = list(posted)[-150:]  # نگهداری ۱۵۰ مورد آخر برای امنیت بیشتر در برابر تکرار
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(posted_list) + "\n")

def get_next_mode():
    if os.path.exists(MODE_FILE):
        with open(MODE_FILE, "r", encoding="utf-8") as f:
            current = f.read().strip()
            return "text" if current == "trailer" else "trailer"
    return "trailer"

def save_next_mode(mode):
    with open(MODE_FILE, "w", encoding="utf-8") as f:
        f.write(mode)

def commit_changes():
    try:
        os.system('git config --global user.name "github-actions[bot]"')
        os.system('git config --global user.email "github-actions[bot]@users.noreply.github.com"')
        os.system(f'git add {HISTORY_FILE} {MODE_FILE}')
        os.system('git commit -m "Update schedule state [skip ci]"')
        os.system('git push')
    except Exception:
        pass

def download_video_file(trailer_url):
    try:
        print(f"📥 در حال دانلود تیزر از: {trailer_url}")
        headers = {'User-Agent': 'Mozilla/5.0'}
        vid_res = requests.get(trailer_url, headers=headers, stream=True, timeout=20)
        if vid_res.status_code == 200:
            trailer_path = "temp_trailer.mp4"
            with open(trailer_path, 'wb') as f:
                for chunk in vid_res.iter_content(chunk_size=8192):
                    f.write(chunk)
            return trailer_path
    except Exception as e:
        print(f"⚠️ خطا در دانلود تیزر: {e}")
    return None

async def main():
    print("🚀 بررسی وضعیت کانال برای ارسال پست جدید...")
    mode = get_next_mode()
    posted_history = get_posted_history()
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    async with BotClient(token=RUBIKA_TOKEN) as bot:
        
        # بخش اول: اگر نوبت متن صمیمی و ادمین‌طوری باشد (با فیلتر ضد تکرار)
        if mode == "text":
            print("💬 نوبت ارسال پیام صمیمی و ادمین‌طوری است...")
            
            # پیدا کردن متن‌هایی که تا حالا ارسال نشده‌اند
            available_messages = [m for m in ADMIN_MESSAGES if m not in posted_history]
            
            # اگر همه متن‌ها استفاده شده بودند، تاریخچه متن‌ها رو ریست می‌کنیم تا دوباره بچرخند
            if not available_messages:
                available_messages = ADMIN_MESSAGES
                
            selected_msg = random.choice(available_messages)
            caption = f"{selected_msg}\n\n@moarefi_film_ir"
            
            try:
                await bot.send_message(chat_id=CHAT_ID, text=caption)
                print("✅ پیام صمیمی ادمین با موفقیت ارسال شد.")
                save_to_history(selected_msg)
                save_next_mode("text")
                commit_changes()
                return
            except Exception as e:
                print(f"❌ خطا در ارسال پیام ادمین: {e}")

        # بخش دوم: اگر نوبت ارسال تیزر و معرفی فیلم جدید باشد
        print("🎬 نوبت بررسی و ارسال تیزر فیلم غیرتکراری است...")
        posted_successfully = False

        for target_site in TARGET_SITES:
            if posted_successfully:
                break
                
            try:
                print(f"🔍 بررسی سایت: {target_site}")
                response = requests.get(target_site, headers=headers, timeout=15)
                if response.status_code != 200:
                    continue
                    
                soup = BeautifulSoup(response.text, 'html.parser')
                posts = soup.find_all('div', class_='post') or soup.find_all('article') or soup.find_all('div', class_='item')
                
                if not posts:
                    continue

                for p in posts[:10]:
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
                    
                    # اگر لینک پست یا خود فیلم قبلاً ثبت شده بود، رد شو
                    if post_url in posted_history:
                        continue
                    
                    print(f"🎯 فیلم جدید پیدا شد: {title}")
                    post_response = requests.get(post_url, headers=headers, timeout=15)
                    if post_response.status_code != 200:
                        continue
                        
                    post_soup = BeautifulSoup(post_response.text, 'html.parser')
                    
                    # استخراج تریلر
                    video_tag = post_soup.find('video')
                    trailer_url = None
                    if video_tag and video_tag.get('src'):
                        trailer_url = video_tag['src']
                    else:
                        for a in post_soup.find_all('a', href=True):
                            href = a['href']
                            if 'trailer' in href.lower() or 'teaser' in href.lower() or (href.endswith('.mp4') and 'dl' in href):
                                trailer_url = href
                                break
                    
                    if trailer_url and trailer_url in posted_history:
                        continue
                    
                    trailer_file = download_video_file(trailer_url) if trailer_url else None
                    
                    short_desc = "بدون اسپویل | کیفیت عالی و ترافیک نیم بها."
                    content_div = post_soup.find('div', class_='content') or post_soup.find('div', class_='post-content')
                    if content_div:
                        paragraph = content_div.find('p')
                        if paragraph and len(paragraph.get_text(strip=True)) > 20:
                            short_desc = paragraph.get_text(strip=True)[:160] + "..."
                    
                    is_comedy = "کمدی" in title or "طنز" in title
                    genre = "کمدی / طنز" if is_comedy else "سینمایی روز / اکشن"
                    
                    caption = (
                        f"🎬 دانلود {title}\n\n"
                        f"✨ امتیاز: ویژه | سال: جدید | ژانر: {genre}\n\n"
                        f"📝 خلاصه داستان / معرفی:\n"
                        f"{short_desc}\n\n"
                        f"🔗 لینک دانلود مستقیم و کامل فیلم:\n"
                        f"{post_url}\n\n"
                        f"🔥 حتما تماشا کنید!\n"
                        f"#فیلم #سریال #معرفی_فیلم #تریلر_فیلم\n\n"
                        f"@moarefi_film_ir"
                    )
                    
                    try:
                        if trailer_file and os.path.exists(trailer_file):
                            print("📤 ارسال تیزر ویدیو همراه با کپشن به کانال...")
                            await bot.send_video(chat_id=CHAT_ID, video=trailer_file, caption=caption)
                            os.remove(trailer_file)
                        else:
                            print("📤 ارسال پست متنی کامل فیلم به کانال...")
                            await bot.send_message(chat_id=CHAT_ID, text=caption)
                        
                        print("✅ پست فیلم با موفقیت و کاملاً غیرتکراری منتشر شد.")
                        save_to_history(post_url)
                        if trailer_url:
                            save_to_history(trailer_url)
                        save_next_mode("trailer")
                        commit_changes()
                        posted_successfully = True
                        break
                    except Exception as e:
                        print(f"❌ خطا در ارسال به روبیکا: {e}")
                        if trailer_file and os.path.exists(trailer_file):
                            os.remove(trailer_file)
                    
            except Exception as e:
                print(f"⚠️ خطا در بررسی سایت: {e}")
                continue

if __name__ == "__main__":
    asyncio.run(main())
