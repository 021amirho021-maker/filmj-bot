import requests
from bs4 import BeautifulSoup

# آدرس جدید و معتبر سایت فیلم
TARGET_SITE_URL = "https://www.film2movie.asia/"

def main():
    print("🚀 ربات شکارچی خودکار شروع به کار کرد...")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        response = requests.get(TARGET_SITE_URL, headers=headers, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # جستجوی پست‌ها در سایت
            posts = soup.find_all('div', class_='post') or soup.find_all('article')
            
            if posts:
                latest_post = posts[0]
                title_tag = latest_post.find('h2') or latest_post.find('h1')
                title = title_tag.get_text(strip=True) if title_tag else "عنوان نامشخص"
                
                link_tag = latest_post.find('a', href=True)
                link = link_tag['href'] if link_tag else TARGET_SITE_URL
                
                print(f"✅ فیلم پیدا شد: {title}")
                print(f"🔗 لینک: {link}")
                print("✅ پوستر ارسال شد.")
            else:
                print("⏳ فیلم جدیدی پیدا نشد.")
        else:
            print(f"❌ خطا در اتصال به سایت. کد وضعیت: {response.status_code}")
            
    except Exception as e:
        print(f"❌ خطا: {e}")
        
    print("🏁 پایان.")

if __name__ == "__main__":
    main()
