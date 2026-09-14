import os
import asyncio
import re
from bs4 import BeautifulSoup

try:
    import rubpy
    import curl_cffi
    import requests
except ImportError:
    os.system('pip install rubpy bs4 requests curl_cffi')
    import rubpy
    from curl_cffi import requests as c_requests
    import requests

from curl_cffi import requests as c_requests
from rubpy import BotClient

TARGET_SITES = [
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
    
    posted_list = list(posted)[-200:]
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

def get_teaser_url(post_soup):
    try:
        # ۱. بررسی تگ استاندارد video
        video_tag = post_soup.find('video')
        if video_tag:
            if video_tag.get('src'):
                return video_tag['src']
            source_tag = video_tag.find('source')
            if source_tag and source_tag.get('src'):
                return source_tag['src']
        
        # ۲. جستجوی دقیق لینک‌های مستقیم ویدیویی در صفحه
        for a in post_soup.find_all('a', href=True):
            href = a['href']
            lower_href = href.lower()
            # باید شامل پسوند ویدیو یا کلمات کلیدی تریلر باشد و به صفحات معمولی HTML ختم نشود
            if '.mp4' in lower_href or '.mkv' in lower_href or 'trailer' in lower_href or 'teaser' in lower_href:
                if not lower_href.endswith(('.html', '.php', '.aspx', '.htm', '/')):
                    return href
    except Exception:
        pass
    return None

def extract_movie_info(post_soup):
    meta_desc = post_soup.find('meta', property='og:description') or post_soup.find('meta', attrs={'name': 'description'})
    if meta_desc and meta_desc.get('content'):
        summary = meta_desc['content'].strip()
        if len(summary) > 30:
            return summary[:450] + "..."

    return "روایتی جذاب و تماشایی که شما را تا انتهای داستان مبهوت خود خواهد کرد..."

async def main():
    print("🚀 ربات هوشمند با فیلتر دقیق تریلر راه‌اندازی شد...")
    posted_history = get_posted_history()
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    }

    async with BotClient(token=RUBIKA_TOKEN) as bot:
        posted_successfully = False

        for target_site in TARGET_SITES:
            if posted_successfully:
                break
                
            try:
                print(f"🔍 در حال بررسی سایت: {target_site}")
                response = c_requests.get(target_site, impersonate="chrome", headers=headers, timeout=15)
                if response.status_code != 200:
                    continue
                    
                soup = BeautifulSoup(response.text, 'html.parser')
                posts = soup.find_all('div', class_='post') or soup.find_all('article') or soup.find_all('div', class_='item') or soup.find_all('div', class_='box')
                
                if not posts:
                    continue

                for p in posts[:15]:
                    if posted_successfully:
                        break

                    title_tag = p.find('h2') or p.find('h1') or p.find('h3') or p.find('a')
                    if not title_tag:
                        continue
                    
                    raw_title = title_tag.get_text(strip=True)
                    if len(raw_title) < 3:
                        continue
                        
                    title = raw_title.replace("دانلود فیلم", "").replace("دانلود سریال", "").replace("دانلود", "").strip()
                    
                    link_tag = p.find('a', href=True)
                    if not link_tag:
                        continue
                    post_url = link_tag['href']
                    
                    if not post_url.startswith('http'):
                        continue
                        
                    if post_url in posted_history:
                        continue
                    
                    print(f"🎯 فیلم جدید پیدا شد: {title}")
                    post_response = c_requests.get(post_url, impersonate="chrome", headers=headers, timeout=15)
                    if post_response.status_code != 200:
                        continue
                        
                    post_soup = BeautifulSoup(post_response.text, 'html.parser')
                    trailer_url = get_teaser_url(post_soup)
                    
                    if not trailer_url or trailer_url in posted_history:
                        print("⏭️ این فیلم لینک تریلر مستقیم نداشت یا تکراری بود.")
                        continue
                    
                    print(f"📥 در حال دانلود تریلر از لینک: {trailer_url}")
                    
                    vid_headers = headers.copy()
                    vid_headers['Referer'] = post_url
                    
                    vid_res = c_requests.get(trailer_url, impersonate="chrome", headers=vid_headers, stream=True, timeout=30)
                    if vid_res.status_code != 200:
                        print(f"❌ دانلود تریلر ناموفق بود (کد وضعیت: {vid_res.status_code})")
                        continue
                        
                    trailer_file = "Movie_Trailer.mp4"
                    with open(trailer_file, 'wb') as f:
                        for chunk in vid_res.iter_content(chunk_size=8192):
                            f.write(chunk)
                    
                    # بررسی سلامت فایل ویدیویی (حجم باید بیشتر از ۵۰۰ کیلوبایت باشد)
                    file_size = os.path.getsize(trailer_file)
                    if file_size < 500 * 1024:
                        print(f"⚠️ فایل دانلود شده ویدیوی معتبری نبود (حجم: {file_size} بایت). رد کردن...")
                        if os.path.exists(trailer_file):
                            os.remove(trailer_file)
                        continue

                    page_text = post_soup.get_text()
                    
                    if "دوبله فارسی" in page_text or "صوت دوبله" in page_text:
                        version_tag = "🎙️ #دوبله_فارسی"
                    else:
                        version_tag = "📄 #زیرنویس_چسبیده_فارسی"

                    is_comedy = "کمدی" in title or "طنز" in title or "Comedy" in page_text
                    genre = "#کمدی #طنز" if is_comedy else "#اکشن #جنایی #درام"
                    
                    imdb_match = re.search(r'IMDb[:\s]*([0-9.]+)', page_text, re.IGNORECASE)
                    imdb_score = imdb_match.group(1) if imdb_match else "۷.۵"

                    summary_text = extract_movie_info(post_soup)
                    
                    caption = (
                        f"🎬 {title}\n"
                        f"⚡️ IMDb: {imdb_score}\n\n"
                        f"{version_tag}\n"
                        f"🎭 ژانر: {genre}\n\n"
                        f"📚 خلاصه داستان:\n"
                        f"{summary_text}\n\n"
                        f"🔗 لینک دانلود و تماشا:\n"
                        f"{post_url}\n\n"
                        f"@moarefi_film_ir"
                    )
                    
                    try:
                        print("📤 در حال آپلود و ارسال ویدیوی سالم به همراه متن در کانال...")
                        await bot.send_file(chat_id=CHAT_ID, file=trailer_file, text=caption)
                        
                        if os.path.exists(trailer_file):
                            os.remove(trailer_file)
                        
                        print("✅ پست با موفقیت، متن کامل و ویدیوی قابل پخش در کانال منتشر شد!")
                        save_to_history(post_url, trailer_url)
                        posted_successfully = True
                        break
                    except Exception as e:
                        print(f"❌ خطا در ارسال به روبیکا: {e}")
                        if os.path.exists(trailer_file):
                            os.remove(trailer_file)
                    
            except Exception as e:
                print(f"⚠️ خطا در بررسی سایت: {e}")
                continue

if __name__ == "__main__":
    asyncio.run(main())
