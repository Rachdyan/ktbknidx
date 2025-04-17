from seleniumbase import SB
import pytz
from datetime import datetime as dt
from datetime import time
import pandas as pd
import telegram
import asyncio
import os
# import requests
from dotenv import load_dotenv

from utils.scraping_utils import scrape_data, truncate_with_ellipsis, \
    get_first_link

load_dotenv()

user = os.environ['PROXY_USER']
password = os.environ['PROXY_PASSWORD']
proxy_host = os.environ['PROXY_HOST']
proxy_port = os.environ['PROXY_PORT']

proxy_string = f"{user}:{password}@{proxy_host}:{proxy_port}"

# def internet_connection():
#    try:
#        response = requests.get("https://www.idx.co.id/id", timeout=5)
#        return True
#    except requests.ConnectionError:
#        return False


keywords = ['material -sosial', 'HMETD', 'aksi korporasi -dividen',
            'Penandatanganan', 'Penambahan Modal', 'Insidentil',
            'Pengambilalihan', 'perubahan -saham', 'luar biasa -iklan',
            'PMHMETD', 'negoisasi', 'media massa', 'pengendali',
            'penggabungan', 'peningkatan modal', 'kontrak penting',
            'restrukturisasi', 'pendirian entitas', 'prospektus', 'tender']

keywords = ['Pengambilalihan', 'perubahan -saham']

# keywords = ['penandatanganan', 'tender']

raw_today_data = dt.now(pytz.timezone('Asia/Jakarta'))
today_date = raw_today_data.strftime("%Y-%m-%d")
# today_date = '2025-04-09'

today_month_year = raw_today_data.strftime("%b %Y")
# today_month_year = 'Apr 2025'

if __name__ == "__main__":
    with SB(uc=True, headless=True, xvfb=True,
            proxy=proxy_string, maximize=True,
            ) as sb:
        sb.driver.execute_cdp_cmd(
                "Network.setExtraHTTPHeaders",
                {
                    "headers": {
                        'Accept': 'text/html,application/xhtml+xml,application\
                            /xml;q=0.9,image/avif,image/webp,image/apng,*/*;\
                                q=0.8,application/signed-exchange;v=b3;q=0.7',
                        'Accept-Encoding': 'gzip, deflate, br, zstd',
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Cache-Control': "no-cache",
                        'Pragma': "no-cache",
                        'Priority': "u=0, i",
                        'Sec-Ch-Ua': '"Chromium";v="134", \
                            "Not:A-Brand";v="24","Google Chrome";v="134"',
                        'Sec-Ch-Mobile': "?0",
                        'Sec-Ch-Ua-Platform': '"macOS"',
                        'Sec-Fetch-Dest': "document",
                        'Sec-Fetch-Mode': "navigate",
                        'Sec-Fetch-User': "?1",
                        'Upgrade-Insecure-Requests': '1',
                    }
                }
            )

        sb.driver.execute_cdp_cmd(
                "Network.setUserAgentOverride",
                {
                    "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X \
                        10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) \
                            Chrome/134.0.0.0 Safari/537.36"
                },
            )

        sb.driver.execute_script("Object.defineProperty(navigator, \
                                 'webdriver',{get: () => undefined})")

        final_df = pd.DataFrame()
        for keyword in keywords:
            print(f"Processing keyword: {keyword}")
            keyword_df = scrape_data(sb, keyword, today_date, today_month_year)
            if keyword_df is not None:
                final_df = pd.concat([final_df, keyword_df], ignore_index=True)


if final_df.shape[0] > 0:
    print("Final data is not none")
    is_evening = True if raw_today_data.time() > time(9, 00) else False
    print(f"Is Evening: {is_evening}")

    final_df['time'] = pd.to_datetime(final_df['time'], format='%H:%M:%S')\
        .dt.time

    if is_evening:
        final_df = final_df[final_df.time > time(9, 00)].reset_index(drop=True)

    final_df['first_link'] = final_df.apply(lambda x:
                                            get_first_link(x),
                                            axis=1)

    final_df['message_string'] = final_df.apply(
        lambda x: (f"•<b>{x['stock']}</b> - {x['time'].strftime('%H:%M')}"
                   f"- <a href='{x['first_link']}' target='_blank'>"
                   f"{truncate_with_ellipsis(x['title'], 75)}</a>"), axis=1)

    keyword_summary_result = (
        final_df.groupby(['date', 'keyword'], as_index=False)
        .agg(
            n_unique_stock=('stock', 'nunique'),
            unique_stock=('stock', lambda x: ', '.join(
                sorted(x.unique()))),
            # n_document=('pdf_name', 'nunique')
        )
    )

    date_summary_result = (
        final_df.groupby(['date'], as_index=False)
        .agg(
            unique_keyword=('keyword', lambda x: ', '.join(
                sorted(x.unique()))),
            n_unique_stock=('stock', 'nunique'),
            unique_stock=('stock', lambda x: ', '.join(
                sorted(x.unique()))),
            # n_document=('pdf_name', 'nunique')
        )
        )

    avail_keywords = final_df.keyword.unique().tolist()


if is_evening:
    run_type = 'EVENING RUN'
else:
    run_type = 'MORNING RUN'

string = (f"<b>{today_date} - {raw_today_data.strftime('%A').upper()}"
          f"- {run_type} SUMMARY</b>")
string += '\n\n'


if final_df.shape[0] > 0:
    string += f'n stock: {date_summary_result.n_unique_stock[0]}'
    # string += '\n'
    # string += date_summary_result.unique_stock[0]
    string += '\n'

    avail_keywords = final_df.keyword.unique().tolist()
    for keyword in avail_keywords:
        string += '\n'
        string += f'<b>{keyword}</b>:'
        string += '\n'

        keyword_df = final_df[final_df.keyword == keyword]\
            .reset_index(drop=True)
        print(keyword_df)
        for i in range(0, keyword_df.shape[0]):
            string += keyword_df.message_string[i]
            string += '\n'
else:
    string += 'No Result Available'


BOT_TOKEN = os.environ['BOT_TOKEN']

TARGET_CHAT_ID = "1415309056"


async def main():
    try:
        # Create a bot instance
        bot = telegram.Bot(token=BOT_TOKEN)
        print(f"Attempting to send message to chat ID: {TARGET_CHAT_ID}")

        await bot.send_message(
            chat_id=TARGET_CHAT_ID,
            text=string,
            parse_mode='HTML'
        )
        print("Message sent successfully!")

    except telegram.error.TelegramError as e:
        # Handle potential errors
        print(f"Telegram Error: {e}")
        if "chat not found" in str(e):
            print("Hint: Make sure the TARGET_CHAT_ID is correct and the user"
                  "has started a chat with the bot first.")
        elif "bot was blocked by the user" in str(e):
            print("Hint: The target user has blocked this bot.")

asyncio.run(main())
