import requests
import os
from datetime import datetime
import jdatetime

def get_crypto_prices():
    """گرفتن قیمت ارزها از CoinGecko API"""
    # لیست ارزها با آیدی CoinGecko
    coins = {
        'ton': 'the-open-network',
        'btc': 'bitcoin',
        'trx': 'tron',
        'xrp': 'ripple',
        'ada': 'cardano'
    }
    
    coin_ids = ','.join(coins.values())
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_ids}&vs_currencies=usd"
    
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        raise Exception(f"خطا در دریافت قیمت‌ها: {e}")
    
    # ساخت متن پیام
    lines = []
    
    # TON
    ton_price = data.get('the-open-network', {}).get('usd', 0)
    lines.append(f"1 Ton = {ton_price:.2f} USD")
    
    # BTC
    btc_price = data.get('bitcoin', {}).get('usd', 0)
    lines.append(f"1 BTC = {int(btc_price):,} USD")
    
    # TRX
    trx_price = data.get('tron', {}).get('usd', 0)
    lines.append(f"1 TRX = {trx_price:.6f} USD")
    
    # XRP
    xrp_price = data.get('ripple', {}).get('usd', 0)
    lines.append(f"1 XRP = {xrp_price:.2f} USD")
    
    # ADA
    ada_price = data.get('cardano', {}).get('usd', 0)
    lines.append(f"1 ADA = {ada_price:.6f} USD")
    
    # USDT (تتر معمولاً به IRT در نوبیتکس ناموجود است، پس همان فرمت شما)
    lines.append("1 USDT = ناموجود IRT")
    
    return '\n'.join(lines)

def get_persian_datetime():
    """گرفتن تاریخ و ساعت شمسی"""
    # گرفتن زمان فعلی
    now = datetime.now()
    
    # تبدیل به تاریخ شمسی
    jalali_now = jdatetime.datetime.fromgregorian(datetime=now)
    
    # نام روز هفته به فارسی
    weekdays = ['دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنج‌شنبه', 'جمعه', 'شنبه', 'یکشنبه']
    day_name = weekdays[jalali_now.weekday()]
    
    # نام ماه به فارسی
    months = ['فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
              'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند']
    month_name = months[jalali_now.month - 1]
    
    # فرمت: جمعه 22 مرداد 1404 - 00:15
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
        # گرفتن قیمت‌ها
        prices = get_crypto_prices()
        
        # گرفتن تاریخ شمسی
        persian_date = get_persian_datetime()
        
        # ساخت پیام کامل با فرمت دلخواه
        message = f"""{prices}

{persian_date}

📢 @Dollar_Alert"""
        
        # ارسال به تلگرام
        send_to_telegram(message)
        
        print("✅ اجرا با موفقیت انجام شد")
        
    except Exception as e:
        print(f"❌ خطا: {e}")
        raise

if __name__ == "__main__":
    main()
