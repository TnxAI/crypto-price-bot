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
        'xaut': 'tether-gold'  # ✨ اضافه شد
    }
    
    coin_ids = ','.join(coins.values())
    
    # گرفتن قیمت به USD
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_ids}&vs_currencies=usd"
    response = requests.get(url, timeout=15).json()
    
    # استخراج قیمت‌ها
    ton_price = response.get('the-open-network', {}).get('usd', 0)
    btc_price = response.get('bitcoin', {}).get('usd', 0)
    trx_price = response.get('tron', {}).get('usd', 0)
    xrp_price = response.get('ripple', {}).get('usd', 0)
    ada_price = response.get('cardano', {}).get('usd', 0)
    xaut_price = response.get('tether-gold', {}).get('usd', 0)  # ✨ اضافه شد
    
    # گرفتن قیمت تتر به تومان از نوبیتکس
    usdt_irt = get_usdt_price_from_nobitex()
    
    # ساخت متن پیام
    lines = []
    lines.append(f"1 Ton = {ton_price:.2f} USDT")
    lines.append(f"1 BTC = {int(btc_price):,} USDT")
    lines.append(f"1 TRX = {trx_price:.6f} USDT")
    lines.append(f"1 XRP = {xrp_price:.2f} USDT")
    lines.append(f"1 ADA = {ada_price:.6f} USDT")
    lines.append(f"1 XAU = {xaut_price:,.2f} USDT")  # ✨ اضافه شد
    
    # قیمت تتر به تومان
    if usdt_irt:
        lines.append(f"1 USDT = {int(usdt_irt):,} IRT")
    else:
        lines.append("1 USDT = ناموجود IRT")
    
    return '\n'.join(lines)

def get_usdt_price_from_nobitex():
    """گرفتن قیمت تتر از نوبیتکس"""
    try:
        url = "https://api.nobitex.ir/v2/orderbook/USDT-IRT"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if data.get('status') == 'ok':
            last_price = data.get('lastTradePrice', 0)
            return float(last_price)
    except Exception as e:
        print(f"خطا در دریافت قیمت تتر از نوبیتکس: {e}")
    
    return None

def get_persian_datetime():
    """گرفتن تاریخ و ساعت شمسی با timezone تهران"""
    tehran_tz = ZoneInfo('Asia/Tehran')
    now = datetime.now(tehran_tz)
    
    jalali_now = jdatetime.datetime.fromgregorian(datetime=now)
    
    weekdays = ['دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنج‌شنبه', 'جمعه', 'شنبه', 'یکشنبه']
    day_name = weekdays[jalali_now.weekday()]
    
    months = ['فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
              'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند']
    month_name = months[jalali_now.month - 1]
    
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
