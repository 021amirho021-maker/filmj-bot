import requests

RUBIKA_TOKEN = "CEEDJE0NSCPVLWRZSPQCCGYNLTWTKOKYHYVAIBGSKSVRJGHTXVPXXHXOZQLWXRTT"

def main():
    print("🔍 در حال تست متدهای مختلف برای دریافت شناسه‌ها از روبیکا...")
    url = f"https://botapi.rubika.ir/v3/{RUBIKA_TOKEN}/getChats"
    
    # تست متد GET
    try:
        print("\n--- تست با متد GET ---")
        res_get = requests.get(url, timeout=10)
        print("پاسخ GET:", res_get.text)
    except Exception as e:
        print("خطا در GET:", e)

    # تست متد POST
    try:
        print("\n--- تست با متد POST ---")
        res_post = requests.post(url, json={}, timeout=10)
        print("پاسخ POST:", res_post.text)
    except Exception as e:
        print("خطا در POST:", e)

if __name__ == "__main__":
    main()
