import requests
import os
from datetime import datetime
from zoneinfo import ZoneInfo
import jdatetime

def get_crypto_prices():
    """گرفتن قیمت ارزها از CoinGecko API"""
    coins = {
        'ton': 'the-open-network',
        'btc': 'bitcoin',
        'trx': 'tron',
        'xrp': 'ripple',
        'ada': 'cardano',
        'usdt': 'tether'
    }
    
    coin_ids = ','.join(coins.values())
    
    # گرفتن قیمت همه ارزها به USDT
    url_usdt = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_ids}&vs_currencies=usdt"
    response_usdt = requests.get(url_usdt, timeout=15).json()
    
    # گرفتن قیمت تتر به تومان (IRT)
    url_irt = "https://api.coingecko.com/api/v3/simple/price?ids=tether&vs_currencies=irt"
    response_irt = requests.get(url_irt, timeout=15).json()
    
    # استخراج قیمت‌ها
    ton_price = response_usdt.get('the-open-network', {}).get('usdt', 0)
    btc_price = response_usdt.get('bitcoin', {}).get('usdt', 0)
    trx_price = response_usdt.get('tron', {}).get('usdt', 0)
    xrp_price = response_usdt.get('ripple', {}).get('usdt', 0)
    ada_price = response_usdt.get('cardano', {}).get('usdt', 0)
    usdt_irt = response_irt.get('tether', {}).get('irt', 0)
    
    # ساخت متن پیام
    lines = []
    lines.append(f"1 Ton = {ton_price:.2f} USDT")
    lines.append(f"1 BTC = {int(btc_price):,} USDT")
    lines.append(f"1 TRX = {trx_price:.6f} USDT")
    lines.append(f"1 XRP = {xrp_price:.2f} USDT")
    lines.append(f"1 ADA = {ada_price:.6f} USDT")
    
    # قیمت تتر به تومان
    if usdt_irt:
        lines.append(f"1 USDT = {int(usdt_irt):,} IRT")
    else:
        lines.append("1 USDT = ناموجود IRT")
    
    return '\n'.join(lines)

def get_persian_datetime():
    """گرفتن تاریخ و ساعت شمسی با timezone تهران"""
    # ✨ تنظیم timezone به تهران (UTC+3:30)
    tehran_tz = ZoneInfo('Asia/Tehran')
    now = datetime.now(tehran_tz)
    
    # تبدیل به تاریخ شمسی
    jalali_now = jdatetime.datetime.fromgregorian(datetime=now)
    
    # نام روز هفته به فارسی
    weekdays = ['دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنج‌شنبه', 'جمعه', 'شنبه', 'یکشنبه']
    day_name = weekdays[jalali_now.weekday()]
    
    # نام ماه به فارسی
    months = ['فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
              'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند']
    month_name = months[jalali_now.month - 1]
    
    # فرمت: چهارشنبه 8 تیر 1405 - 11:10
    formatted = f"{day_name} {jalali_now.day} {month_name} {jalali_now.year} - {jalali_now.strftime('%H:%M')}"
    
    return formatted

def send_to_telegram(text):
    """ارسال پیام به کانال تلگرام"""
    bot_token = os.getenv('BOT_TOKEN')
    chat_id = os.getenv('CHAT_ID')
    
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

def main():
    """تابع اصلی"""
    try:
        prices = get_crypto_prices()
        persian_date = get_persian_datetime()
        
        message = f"""{prices}

{persian_date}

📢 @Dollar_Alert"""
        
        send_to_telegram(message)
        print("✅ اجرا با موفقیت انجام شد")
        
    except Exception as e:
        print(f"❌ خطا: {e}")
        raise

if __name__ == "__main__":
    main()
