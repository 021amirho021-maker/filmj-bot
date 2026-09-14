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

# لیست سایت‌های فعال و سازگار
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
        video_tag = post_soup.find('video')
        if video_tag:
            if video_tag.get('src'):
                return video_tag['src']
            source_tag = video_tag.find('source')
            if source_tag and source_tag.get('src'):
                return source_tag['src']
        
        for a in post_soup.find_all('a', href=True):
            href = a['href']
            lower_href = href.lower()
            if any(ext in lower_href for ext in ['.mp4', '.mkv', 'trailer', 'teaser', 'dl']):
                return href
    except Exception:
        pass
    return None

def extract_movie_info(post_soup):
    text_content = post_soup.get_text()
    imdb_match = re.search(r'IMDb[:\s]*([0-9.]+)', text_content, re.IGNORECASE)
    imdb_score = imdb_match.group(1) if imdb_match else "۸.۲"
    return imdb_score

async def main():
    print("🚀 ربات هوشمند با موفقیت راه‌اندازی شد...")
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

                for p in posts[:12]:
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
                        print("⏭️ این فیلم تریلر معتبر نداشت یا تکراری بود.")
                        continue
                    
                    print(f"📥 در حال دانلود تریلر: {trailer_url}")
                    
                    vid_headers = headers.copy()
                    vid_headers['Referer'] = post_url
                    
                    vid_res = c_requests.get(trailer_url, impersonate="chrome", headers=vid_headers, stream=True, timeout=30)
                    if vid_res.status_code != 200:
                        print(f"❌ دانلود تریلر ناموفق بود (کد وضعیت: {vid_res.status_code})")
                        continue
                        
                    trailer_file = "temp_trailer.mp4"
                    with open(trailer_file, 'wb') as f:
                        for chunk in vid_res.iter_content(chunk_size=8192):
                            f.write(chunk)
                    
                    summary_text = "روایتی جذاب و تماشایی که شما را تا انتهای داستان مبهوت خود خواهد کرد..."
                    content_div = post_soup.find('div', class_='content') or post_soup.find('div', class_='post-content') or post_soup.find('div', class_='entry-content')
                    if content_div:
                        paragraphs = [elem.get_text(strip=True) for elem in content_div.find_all('p') if len(elem.get_text(strip=True)) > 30]
                        if paragraphs:
                            summary_text = " ".join(paragraphs[:2])[:400] + "..."

                    is_comedy = "کمدی" in title or "طنز" in title
                    genre = "#کمدی #طنز" if is_comedy else "#جنایی #اکشن #درام"
                    imdb_score = extract_movie_info(post_soup)
                    
                    caption = (
                        f"🎬 {title}\n"
                        f"⚡️ IMDb: {imdb_score}\n\n"
                        f"🎙️ #دوبله_اختصاصی\n"
                        f"🎭 ژانر: {genre}\n\n"
                        f"📚 خلاصه داستان:\n"
                        f"{summary_text}\n\n"
                        f"🔗 لینک تماشا:\n"
                        f"{post_url}\n\n"
                        f"@moarefi_film_ir"
                    )
                    
                    try:
                        print("📤 در حال آپلود و ارسال ویدیو به همراه کپشن در کانال...")
                        # استفاده از متد استاندارد send_file در روبای برای ارسال ویدیوی پلیردار
                        await bot.send_file(chat_id=CHAT_ID, file=trailer_file, caption=caption)
                        
                        if os.path.exists(trailer_file):
                            os.remove(trailer_file)
                        
                        print("✅ پست با موفقیت در کانال منتشر شد!")
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
