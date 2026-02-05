# from seleniumbase import SB
import pytz
from datetime import datetime as dt
from datetime import time
import pandas as pd
import telegram
import asyncio
import os
import multiprocessing

from utils.scraping_utils import process_keyword_multi, \
    get_first_link, generate_message_string

from dotenv import load_dotenv

load_dotenv(override=True)

# Environment variables setup
user = os.environ['PROXY_USER']
password = os.environ['PROXY_PASSWORD']
proxy_host = os.environ['PROXY_HOST']
proxy_port = os.environ['PROXY_PORT']
proxy_string = f"{user}:{password}@{proxy_host}:{proxy_port}"

keywords = ['material -sosial', 'HMETD', 'aksi korporasi -dividen',
            'Penandatanganan', 'Penambahan Modal', 'Insidentil',
            'Pengambilalihan', 'perubahan  -kepemilikan -audit',
            'luar biasa -iklan', 'PMHMETD', 'negoisasi', 'media massa',
            'pengendali', 'penggabungan', 'peningkatan modal',
            'kontrak penting', 'restrukturisasi', 'pendirian entitas',
            'prospektus', 'tender', 'anak usaha']

if __name__ == "__main__":
    # Calculate date-related variables
    raw_today_data = dt.now(pytz.timezone('Asia/Jakarta'))
    today_date = raw_today_data.strftime("%Y-%m-%d")

    today_month_year = raw_today_data.strftime("%b %Y")

    # Create list of arguments for each keyword
    args = [(keyword, today_date, today_month_year, proxy_string)
            for keyword in keywords]
    # print("procesingg....")
    # Process keywords in parallel
    # with multiprocessing.Pool(processes=4) as pool:
    #     results = pool.starmap(process_keyword_multi, args)

    with multiprocessing.Pool(processes=4) as pool:
        async_results = [pool.apply_async(process_keyword_multi, arg)
                         for arg in args]

        results = []
        for i, async_result in enumerate(async_results):
            try:
                result = async_result.get(timeout=300)
                results.append(result)
                print(f"Successfully processed keyword: {keywords[i]}")
            except multiprocessing.TimeoutError:
                print(f"Timeout: Keyword '{keywords[i]}' took too long"
                      " - skipping")
            except Exception as e:
                print(f"Error processing keyword '{keywords[i]}': {e}")

    print("Processing completed.")

    # print("Result:")
    # print(results)
    # Combine results
    try:
        final_df = pd.concat([df for df in results if df is not None],
                             ignore_index=True)
    except Exception as e:
        print(e)
        final_df = None

    if raw_today_data.time() < time(10, 00):
        run_time_type = 'Morning'
    elif raw_today_data.time() > time(10, 00) and \
            raw_today_data.time() < time(14, 00):
        run_time_type = 'Afternoon'
    else:
        run_time_type = 'Evening'

    string = (f"<b>{today_date} - {raw_today_data.strftime('%A').upper()}"
              f"- {run_time_type.upper()} RUN SUMMARY</b>")
    string += '\n\n'

    print(final_df)

    if final_df.shape[0] > 0 and final_df is not None:
        print("Final data is not none before filtering time")

        final_df['time'] = pd.to_datetime(final_df['time'], format='%H:%M:%S')\
            .dt.time

        if raw_today_data.time() < time(10, 00):
            final_df = final_df
        elif raw_today_data.time() > time(10, 00) and \
                raw_today_data.time() < time(14, 00):
            final_df = final_df[final_df.time > time(8, 45)].\
                reset_index(drop=True)
        else:
            final_df = final_df[final_df.time > time(13, 15)].\
                reset_index(drop=True)

        if final_df.shape[0] > 0 and final_df is not None:
            final_df['first_link'] = final_df.apply(lambda x:
                                                    get_first_link(x),
                                                    axis=1)

            final_df['message_string'] = final_df.apply(
                lambda x: generate_message_string(x),
                axis=1)

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
    else:
        string += 'No Result Available'

    BOT_TOKEN = os.environ['BOT_TOKEN']

    TARGET_CHAT_ID = "1415309056"
    TARGET_CHAT_ID = "-1003386345668"

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
                print("Hint: Make sure the TARGET_CHAT_ID is correct")
            elif "bot was blocked by the user" in str(e):
                print("Hint: The target user has blocked this bot.")

    asyncio.run(main())
