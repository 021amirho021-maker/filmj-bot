import os
import asyncio
import requests
from bs4 import BeautifulSoup

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

def get_posted_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f if line.strip())
    return set()

def save_to_history(post_url, trailer_url):
    posted = get_posted_history()
    posted.add(post_url)
    if trailer_url:
        posted.add(trailer_url)
    
    posted_list = list(posted)[-150:]
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(posted_list) + "\n")
        
    try:
        os.system('git config --global user.name "github-actions[bot]"')
        os.system('git config --global user.email "github-actions[bot]@users.noreply.github.com"')
        os.system(f'git add {HISTORY_FILE}')
        os.system('git commit -m "Update posted history [skip ci]"')
        os.system('git push')
    except Exception:
        pass

def download_teaser(post_soup):
    """جستجو و دانلود اختصاصی تیزر ویدیویی (اگر تیزر نباشد، None برمی‌گرداند)"""
    try:
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
        
        if trailer_url:
            print(f"📥 تیزر ویدیویی پیدا شد، در حال دانلود از: {trailer_url}")
            headers = {'User-Agent': 'Mozilla/5.0'}
            vid_res = requests.get(trailer_url, headers=headers, stream=True, timeout=25)
            if vid_res.status_code == 200:
                trailer_path = "temp_trailer.mp4"
                with open(trailer_path, 'wb') as f:
                    for chunk in vid_res.iter_content(chunk_size=8192):
                        f.write(chunk)
                return trailer_url, trailer_path
    except Exception as e:
        print(f"⚠️ خطا در دانلود تیزر: {e}")
    return None, None

async def main():
    print("🚀 ربات جستجوی خود را برای پیدا کردن فیلم دارای تیزر آغاز کرد...")
    posted_history = get_posted_history()
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    async with BotClient(token=RUBIKA_TOKEN) as bot:
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

                for p in posts[:15]: # بررسی تعداد بیشتر برای پیدا کردن حتمی تیزر
                    if posted_successfully:
                        break

                    title_tag = p.find('h2') or p.find('h1') or p.find('h3')
                    if not title_tag:
                        continue
                    
                    raw_title = title_tag.get_text(strip=True)
                    title = raw_title.replace("دانلود فیلم", "").replace("دانلود سریال", "").replace("دانلود", "").strip()
                    
                    link_tag = p.find('a', href=True)
                    if not link_tag:
                        continue
                    post_url = link_tag['href']
                    
                    if post_url in posted_history:
                        continue
                    
                    print(f"🎯 بررسی فیلم: {title}")
                    post_response = requests.get(post_url, headers=headers, timeout=15)
                    if post_response.status_code != 200:
                        continue
                        
                    post_soup = BeautifulSoup(post_response.text, 'html.parser')
                    
                    # 1. تلاش برای پیدا کردن و دانلود تیزر (شرط حیاتی برای انتشار)
                    trailer_url, trailer_file = download_teaser(post_soup)
                    
                    # اگر تیزر نداشت یا تکراری بود، این فیلم رو رد کن و برو سراغ بعدی!
                    if not trailer_url or not trailer_file or trailer_url in posted_history:
                        print("⏭️ این فیلم تیزر ویدیویی نداشت یا تکراری بود، رد شد.")
                        if trailer_file and os.path.exists(trailer_file):
                            os.remove(trailer_file)
                        continue
                    
                    # 2. استخراج توضیحات همراه با جزئیات و کمی اسپویل جذاب داستان
                    spoiler_desc = "ماجرای این فیلم از جایی شروع می‌شود که کاراکتر اصلی درگیر یک چالش مرگبار و رازآلود شده و در نهایت... (پیشنهاد می‌کنیم حتماً تماشا کنید تا غافلگیر بشید!)"
                    content_div = post_soup.find('div', class_='content') or post_soup.find('div', class_='post-content')
                    if content_div:
                        paragraphs = [p.get_text(strip=True) for p in content_div.find_all('p') if len(p.get_text(strip=True)) > 40]
                        if paragraphs:
                            spoiler_desc = " ".join(paragraphs[:2])[:350] + "...\n🔥 (نکته دارک و بخش حساس داستان که نباید لو بره...)"

                    is_comedy = "کمدی" in title or "طنز" in title
                    genre = "کمدی / طنز" if is_comedy else "هیجان‌انگیز / اکشن / درام"
                    
                    caption = (
                        f"🎬 دانلود فیلم {title}\n\n"
                        f"✨ امتیاز: ویژه | ژانر: {genre}\n\n"
                        f"⚠️ **خلاصه داستان (همراه با کمی اسپویل):**\n"
                        f"{spoiler_desc}\n\n"
                        f"🔗 **لینک دانلود مستقیم و کامل فیلم:**\n"
                        f"{post_url}\n\n"
                        f"🔥 تریلر رسمی فیلم را بالا تماشا کنید و نظرتان را کامنت کنید!\n"
                        f"#فیلم #سریال #معرفی_فیلم #تریلر_فیلم #اسپویل\n\n"
                        f"@moarefi_film_ir"
                    )
                    
                    try:
                        print("📤 ارسال تیزر ویدیویی و کپشن اختصاصی به کانال...")
                        await bot.send_video(chat_id=CHAT_ID, video=trailer_file, caption=caption)
                        os.remove(trailer_file)
                        
                        print("✅ تیزر فیلم با موفقیت و کاملاً اصولی در کانال منتشر شد.")
                        save_to_history(post_url, trailer_url)
                        posted_successfully = True
                        break
                    except Exception as e:
                        print(f"❌ خطا در ارسال ویدیو به روبیکا: {e}")
                        if trailer_file and os.path.exists(trailer_file):
                            os.remove(trailer_file)
                    
            except Exception as e:
                print(f"⚠️ خطا در بررسی سایت: {e}")
                continue

if __name__ == "__main__":
    asyncio.run(main())
