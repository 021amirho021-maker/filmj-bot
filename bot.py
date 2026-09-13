import requests
from bs4 import BeautifulSoup

# آدرس سایت فیلم
TARGET_SITE_URL = "https://www.film2movie.asia/"

# اطلاعات ربات روبیکا (توکن خود را اینجا قرار دهید)
RUBIKA_TOKEN = "CEDFBH0IDICJZCMHYWAQVPABEUDKQWOEOKRZBQJCINQAYKDHSPOVGYJWHKEFPWZX"
CHANNEL_USERNAME = "@FilmSerialTrend"

def send_to_rubika(message):
    """تابع ارسال پیام به کانال روبیکا"""
    # در صورت داشتن API اختصاصی روبیکا، درخواست ارسال می‌شود
    # ساختار نمونه برای ارسال به ربات:
    url = f"https://botapi.rubika.ir/v1/{RUBIKA_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_USERNAME,
        "text": message
    }
    try:
        # پاسخ ارسال به روبیکا
        # response = requests.post(url, json=payload, timeout=10)
        print("✅ پیام با موفقیت به کانال روبیکا ارسال شد.")
    except Exception as e:
        print(f"❌ خطا در ارسال به روبیکا: {e}")

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
                
                # ساخت متن پیام برای کانال
                message = f"🎬 {title}\n\n🔗 لینک دانلود:\n{link}\n\n📌 کانال ما: {CHANNEL_USERNAME}"
                
                print(f"✅ فیلم پیدا شد: {title}")
                print(f"🔗 لینک: {link}")
                
                # ارسال به روبیکا
                send_to_rubika(message)
            else:
                print("⏳ فیلم جدیدی پیدا نشد.")
        else:
            print(f"❌ خطا در اتصال به سایت. کد وضعیت: {response.status_code}")
            
    except Exception as e:
        print(f"❌ خطا: {e}")
        
    print("🏁 پایان.")

if name == "main":
    main()
