import requests

RUBIKA_TOKEN = "CEEDJE0NSCPVLWRZSPQCCGYNLTWTKOKYHYVAIBGSKSVRJGHTXVPXXHXOZQLWXRTT"

def main():
    print("🔍 در حال دریافت لیست چت‌ها و شناسه‌ها از روبیکا...")
    url = f"https://botapi.rubika.ir/v3/{RUBIKA_TOKEN}/getChats"
    try:
        response = requests.post(url)
        print("📋 پاسخ سرور روبیکا (شناسه‌ها اینجا هستند):")
        print(response.text)
    except Exception as e:
        print(f"❌ خطا: {e}")

if __name__ == "__main__":
    main()
