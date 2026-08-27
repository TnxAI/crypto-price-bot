import requests
import os
from datetime import datetime
from zoneinfo import ZoneInfo
import jdatetime
import base64

def format_price(price, decimals=2, use_comma=False):
    """فرمت‌بندی قیمت - اگر 0 یا None بود، 'ناموجود' برمی‌گرداند"""
    if not price or price == 0:
        return "ناموجود"
    
    if use_comma:
        return f"{int(price):,}"
    elif decimals == 0:
        return f"{int(price):,}"
    else:
        return f"{price:.{decimals}f}"

def get_crypto_prices():
    """گرفتن قیمت ارزها از CoinGecko API"""
    coins = {
        'ton': 'the-open-network',
        'btc': 'bitcoin',
        'trx': 'tron',
        'xrp': 'ripple',
        'ada': 'cardano',
        'xaut': 'tether-gold'
    }
    
    coin_ids = ','.join(coins.values())
    
    # گرفتن قیمت به USD
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_ids}&vs_currencies=usd"
    
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"خطا در دریافت قیمت‌ها: {e}")
        data = {}
    
    # استخراج قیمت‌ها
    ton_price = data.get('the-open-network', {}).get('usd', 0)
    btc_price = data.get('bitcoin', {}).get('usd', 0)
    trx_price = data.get('tron', {}).get('usd', 0)
    xrp_price = data.get('ripple', {}).get('usd', 0)
    ada_price = data.get('cardano', {}).get('usd', 0)
    xaut_price = data.get('tether-gold', {}).get('usd', 0)
    
    # استفاده از XAUT به عنوان قیمت اونس جهانی طلا
    gold_ounce_price = xaut_price if xaut_price else 0
    
    # گرفتن قیمت تتر از نوبیتکس
    usdt_irt = get_usdt_price_from_nobitex()
    
    # محاسبه قیمت طلای 18 عیار
    gold_18_price = calculate_gold_18_price(gold_ounce_price, usdt_irt)
    
    # ساخت متن پیام (بدون ایموجی، بدون اونس طلا، تتر در آخر)
    lines = []
    
    # TON
    ton_formatted = format_price(ton_price, decimals=2)
    lines.append(f"1 Ton = {ton_formatted} USDT")
    
    # BTC
    btc_formatted = format_price(btc_price, decimals=0, use_comma=True)
    lines.append(f"1 BTC = {btc_formatted} USDT")
    
    # TRX
    trx_formatted = format_price(trx_price, decimals=6)
    lines.append(f"1 TRX = {trx_formatted} USDT")
    
    # XRP
    xrp_formatted = format_price(xrp_price, decimals=2)
    lines.append(f"1 XRP = {xrp_formatted} USDT")
    
    # ADA
    ada_formatted = format_price(ada_price, decimals=6)
    lines.append(f"1 ADA = {ada_formatted} USDT")
    
    # XAUT (Tether Gold)
    xaut_formatted = format_price(xaut_price, decimals=2, use_comma=True)
    lines.append(f"1 XAU = {xaut_formatted} USDT")
    
    # طلای 18 عیار
    if gold_18_price and gold_18_price > 0:
        gold_18_formatted = f"{int(gold_18_price):,}"
    else:
        gold_18_formatted = "ناموجود"
    lines.append(f"1g Gold 18K = {gold_18_formatted} Toman")
    
    # USDT به تومان (آخرین آیتم)
    if usdt_irt and usdt_irt > 0:
        usdt_toman = usdt_irt / 10
        usdt_formatted = f"{int(usdt_toman):,}"
    else:
        usdt_formatted = "ناموجود"
    lines.append(f"1 USDT = {usdt_formatted} Toman")
    
    return '\n'.join(lines)

def calculate_gold_18_price(xaut_price, usdt_irt):
    """
    محاسبه قیمت طلای 18 عیار
    فرمول: (قیمت اونس جهانی × نرخ دلار در ایران) ÷ 41.4713
    """
    if xaut_price and usdt_irt and usdt_irt > 0:
        try:
            usd_to_toman = usdt_irt / 10
            gold_18_price = (xaut_price * usd_to_toman) / 41.4713
            return gold_18_price
        except Exception as e:
            print(f"خطا در محاسبه طلای 18 عیار: {e}")
            return None
    return None

def get_usdt_price_from_nobitex():
    """گرفتن قیمت تتر از نوبیتکس (API v3)"""
    try:
        url = "https://apiv2.nobitex.ir/v3/orderbook/USDTIRT"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        last_price = data.get('lastTradePrice', 0)
        
        if last_price:
            return float(last_price)
    except Exception as e:
        print(f"خطا در دریافت قیمت تتر از نوبیتکس: {e}")
    
    return None

def get_persian_datetime():
    """گرفتن تاریخ و ساعت شمسی با timezone تهران"""
    tehran_tz = ZoneInfo('Asia/Tehran')
    now = datetime.now(tehran_tz)
    
    jalali_now = jdatetime.datetime.fromgregorian(datetime=now)
    
    # ✅ ترتیب صحیح روزهای هفته در jdatetime: شنبه=0، یکشنبه=1، ...، پنج‌شنبه=5، جمعه=6
    weekdays = ['شنبه', 'یکشنبه', 'دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنج‌شنبه', 'جمعه']
    day_name = weekdays[jalali_now.weekday()]
    
    months = ['فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
              'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند']
    month_name = months[jalali_now.month - 1]
    
    formatted = f"{day_name} {jalali_now.day} {month_name} {jalali_now.year} - {jalali_now.strftime('%H:%M')}"
    
    return formatted

def save_to_file(message):
    """ذخیره پیام در فایل TXT (محلی)"""
    with open('prices.txt', 'w', encoding='utf-8') as f:
        f.write(message)
    print("✅ قیمت‌ها در فایل prices.txt ذخیره شدند")

def send_to_telegram(text, chat_id):
    """ارسال پیام به کانال تلگرام"""
    bot_token = os.getenv('BOT_TOKEN')
    
    if not bot_token or not chat_id:
        raise Exception("توکن ربات یا آی‌دی کانال تنظیم نشده!")
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML'
    }
    
    try:
        response = requests.post(url, data=payload, timeout=15)
        response.raise_for_status()
        print("✅ پیام با موفقیت ارسال شد!")
    except Exception as e:
        raise Exception(f"خطا در ارسال به تلگرام: {e}")

def commit_to_github(file_path, message_content):
    """ارسال فایل به گیت‌هاب با استفاده از GitHub API"""
    repo = os.getenv('GITHUB_REPOSITORY')
    token = os.getenv('GITHUB_TOKEN')
    
    if not repo or not token:
        print("⚠️ اطلاعات گیت‌هاب تنظیم نشده! فایل فقط به صورت محلی ذخیره شد.")
        return False
    
    # دریافت SHA فایل فعلی (برای جایگزینی)
    api_url = f"https://api.github.com/repos/{repo}/contents/{file_path}"
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    try:
        # دریافت اطلاعات فایل فعلی
        response = requests.get(api_url, headers=headers)
        sha = None
        if response.status_code == 200:
            sha = response.json().get('sha')
        
        # آماده‌سازی محتوا
        content_base64 = base64.b64encode(message_content.encode('utf-8')).decode('utf-8')
        
        # ارسال درخواست commit
        data = {
            'message': f'Update prices - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
            'content': content_base64,
            'branch': 'main'  # یا 'master' بسته به مخزن شما
        }
        
        if sha:
            data['sha'] = sha
        
        if sha:
            # بروزرسانی فایل موجود
            response = requests.put(api_url, headers=headers, json=data)
        else:
            # ایجاد فایل جدید
            response = requests.put(api_url, headers=headers, json=data)
        
        if response.status_code in [200, 201]:
            print(f"✅ فایل {file_path} با موفقیت در گیت‌هاب بروزرسانی شد!")
            return True
        else:
            print(f"❌ خطا در ارسال به گیت‌هاب: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ خطا در ارتباط با گیت‌هاب: {e}")
        return False

def main():
    """تابع اصلی"""
    try:
        # دریافت قیمت‌ها و تاریخ
        prices = get_crypto_prices()
        persian_date = get_persian_datetime()
        chat_id = os.getenv('CHAT_ID')
        
        # ساخت پیام کامل (همان پیامی که به تلگرام میره)
        message = f"""{prices}

{persian_date}

📢 Channel ID: {chat_id}"""
        
        # 1. ذخیره در فایل محلی (همیشه انجام میشه)
        save_to_file(message)
        
        # 2. ارسال به تلگرام
        send_to_telegram(message, chat_id)
        
        # 3. ارسال به گیت‌هاب (فعال‌سازی مخزن)
        commit_to_github('prices.txt', message)
        
        print("✅ اجرا با موفقیت انجام شد")
        
    except Exception as e:
        print(f"❌ خطا: {e}")
        raise

if __name__ == "__main__":
    main()
