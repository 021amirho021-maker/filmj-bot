import requests

RUBIKA_TOKEN = "CEEDJE0NSCPVLWRZSPQCCGYNLTWTKOKYHYVAIBGSKSVRJGHTXVPXXHXOZQLWXRTT"

def main():
    print("🔍 در حال دریافت آپدیت‌ها و شناسه‌های چت برای این توکن...")
    url = f"https://botapi.rubika.ir/v3/{RUBIKA_TOKEN}/getUpdates"
    try:
        response = requests.post(url, json={})
        print("📋 پاسخ سرور روبیکا:")
        print(response.text)
    except Exception as e:
        print(f"❌ خطا: {e}")

if __name__ == "__main__":
    main()
