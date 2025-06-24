from seleniumbase import SB
import pytz
from datetime import datetime as dt
import pandas as pd
import telegram
import asyncio
import os
# import requests
from dotenv import load_dotenv
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from oauth2client.service_account import ServiceAccountCredentials
import gspread
from openai import OpenAI


from utils.scraping_utils import scrape_data
from utils.detailed_scraping_utils import generate_pdf_name, \
    upload_pdf_and_generate_summary
from utils.google_utils import export_to_sheets
from utils.telegram_utils import send_summary_message

load_dotenv(override=True)

user = os.environ['PROXY_USER']
password = os.environ['PROXY_PASSWORD']
proxy_host = os.environ['PROXY_HOST']
proxy_port = os.environ['PROXY_PORT']

proxy_string = f"{user}:{password}@{proxy_host}:{proxy_port}"
# print(proxy_string)

private_key_id = os.environ['SA_PRIVKEY_ID']
sa_client_email = os.environ['SA_CLIENTMAIL']
sa_client_x509_url = os.environ['SA_CLIENT_X509_URL']

private_key = os.environ['SA_PRIVKEY']

private_key = private_key.replace('\\n', '\n')
full_private_key = f"-----BEGIN PRIVATE KEY-----\n"\
                   f"{private_key}\n-----END PRIVATE KEY-----\n"

parent_folder_id = '1_jCMdbv409mtEYTu8JyGW_cmSzezZ-7r'

# --- Build the dictionary directly ---
service_account_dict = {
    "type": "service_account",
    "project_id": "keterbukaan-informasi-idx",
    "private_key_id": private_key_id,
    "private_key": full_private_key,
    "client_email": sa_client_email,
    "client_id": "116805150468350492730",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url":
    "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": sa_client_x509_url,
    "universe_domain": "googleapis.com"
}

scope = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/spreadsheets'
]

gauth = GoogleAuth()

# Load credentials from the dictionary and specify scope
try:
    gauth.credentials = ServiceAccountCredentials.from_json_keyfile_dict(
        service_account_dict, scope
    )
except Exception as e:
    print(f"Error loading credentials from dictionary: {e}")
    # Handle error appropriately, maybe exit
    exit(1)

drive = GoogleDrive(gauth)

parent_folder_id = '1_jCMdbv409mtEYTu8JyGW_cmSzezZ-7r'

# Authenticate Deepseek
deepseek_api_key = os.environ['DEEPSEEK_APIKEY']
client = OpenAI(
        api_key=deepseek_api_key,
        base_url="https://api.deepseek.com"
    )

BOT_TOKEN = os.environ['BOT_TOKEN']

TARGET_CHAT_ID = "1415309056"
bot = telegram.Bot(token=BOT_TOKEN)

creds = gauth.credentials
gc = None
spreadsheet = None
worksheet = None
try:
    gc = gspread.authorize(creds)
    print("Google Sheets client (gspread) initialized successfully.")

    sheet_key = "1NZYsh_JVkSIhbcZwV0gfhm8J3v9gmElxSXS7RT_KbFs"
    spreadsheet = gc.open_by_key(sheet_key)

    print(f"Successfully opened spreadsheet: '{spreadsheet.title}'")

except gspread.exceptions.SpreadsheetNotFound:
    print("Error: Spreadsheet not found. \n"
          "1. Check if the name/key/URL is correct.\n")
    # Decide if you want to exit or continue without sheet access
    exit(1)
except gspread.exceptions.APIError as e:
    print(f"Google Sheets API Error: {e}")
    exit(1)
except Exception as e:
    # Catch other potential errors during gspread initialization/opening
    print(f"An error occurred during Google Sheets setup: {e}")
    exit(1)


keywords = ['material -sosial', 'HMETD', 'aksi korporasi -dividen',
            'Penandatanganan', 'Penambahan Modal', 'Insidentil',
            'Pengambilalihan', 'perubahan  -kepemilikan -audit',
            'luar biasa -iklan', 'PMHMETD', 'negoisasi', 'media massa',
            'pengendali', 'penggabungan', 'peningkatan modal',
            'kontrak penting', 'restrukturisasi', 'pendirian entitas',
            'prospektus', 'tender', 'anak usaha']

# keywords = ['Pengambilalihan', 'penandatanganan']

# keywords = ['penandatanganan', 'tender']

raw_today_data = dt.now(pytz.timezone('Asia/Jakarta'))
today_date = raw_today_data.strftime("%Y-%m-%d")
# today_date = '2025-06-08'

today_month_year = raw_today_data.strftime("%b %Y")
# today_month_year = 'Apr 2025'

if __name__ == "__main__":
    with SB(uc=True, headless=False, xvfb=True,
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

if (final_df is not None and final_df.shape[0] > 0):
    final_df['pdf_name'] = final_df.apply(generate_pdf_name, axis=1)
    final_df
    if __name__ == "__main__":
        with SB(uc=True, headless=True, xvfb=True,
                proxy=proxy_string, maximize=True,
                external_pdf=True
                ) as sb:
            sb.driver.execute_cdp_cmd(
                    "Network.setExtraHTTPHeaders",
                    {
                        "headers": {
                            'Accept':
                            'text/html,application/xhtml+xml,application\
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

            final_processed_df = pd.concat([
                upload_pdf_and_generate_summary(
                    sb=sb, df=row,
                    drive=drive, parent_folder_id=parent_folder_id,
                    upload=True, generate_summary=True,
                    client=client)
                for index, row in final_df.iterrows()
            ], ignore_index=True)

        # Summarize
        # final_processed_df.drop('new_pdf_name', axis = 1, inplace = True)
        keyword_summary_result = (
            final_processed_df.groupby(['date', 'keyword'], as_index=False)
            .agg(
                    n_unique_stock=('stock', 'nunique'),
                    unique_stock=('stock',
                                  lambda x: ', '.join(sorted(x.unique()))),
                    n_document=('pdf_name', 'nunique')
                )
        )

        date_summary_result = (
            final_processed_df.groupby(['date'], as_index=False)
            .agg(
                unique_keyword=('keyword', lambda x: ', '
                                .join(sorted(x.unique()))),
                n_unique_stock=('stock', 'nunique'),
                unique_stock=('stock',
                              lambda x: ', '.join(sorted(x.unique()))),
                n_document=('pdf_name', 'nunique')
                )
        )

        summary_string = (f"<b>{raw_today_data.strftime('%A').upper()}"
                          f" - {today_date} - "
                          f"{raw_today_data.strftime('%H:%M')}"
                          f" -  DAILY RUN SUMMARY</b>")
        summary_string += '\n\n'

        summary_string += '<b>• Unique Keywords:</b> '
        summary_string += f'{date_summary_result.unique_keyword.tolist()[0]}'
        summary_string += '\n\n'
        summary_string += '<b>• n Unique Stocks:</b> '
        summary_string += f'{date_summary_result.n_unique_stock.tolist()[0]}'
        summary_string += '\n\n'
        summary_string += '<b>• Unique Stocks:</b> '
        summary_string += f'{date_summary_result.unique_stock.tolist()[0]}'
        summary_string += '\n\n'
        summary_string += '<b>• n Documents:</b> '
        summary_string += f'{date_summary_result.n_document.tolist()[0]}'
        summary_string += '\n\n'

        async def main():
            try:
                # Create a bot instance
                print("Attempting to send summary message to chat ID: "
                      f"{TARGET_CHAT_ID}")

                await bot.send_message(
                    chat_id=TARGET_CHAT_ID,
                    text=summary_string,
                    parse_mode='HTML'
                )
                print("Summary Message sent successfully!")

            except telegram.error.TelegramError as e:
                # Handle potential errors
                print(f"Telegram Error: {e}")
                if "chat not found" in str(e):
                    print("Hint: Make sure the TARGET_CHAT_ID is correct"
                          "and the user"
                          "has started a chat with the bot first.")
                elif "bot was blocked by the user" in str(e):
                    print("Hint: The target user has blocked this bot.")

        asyncio.run(main())

        final_processed_df['time'] = pd.to_datetime(
            final_df['time'], format='%H:%M:%S')\
            .dt.time

        final_processed_df['message_string'] = final_processed_df.apply(
            lambda x: (f"<b>{x['stock']}</b> - {x['time'].strftime('%H:%M')}"
                       f" - <a href='{x['drive_link']}' target='_blank'>"
                       f"{x['title']}</a>"), axis=1)

        async def main():
            for index, row in final_processed_df.iterrows():
                print(f"Processing row {index}...")

                # Use 'await' directly when calling the async function
                success = await send_summary_message(row_data=row,
                                                     bot=bot,
                                                     chat_id=TARGET_CHAT_ID)

                if not success:
                    print(f"Failed to send message for row {index}."
                          "Continuing...")
                # else:
                #    print(f"Successfully sent for row {index}.") # Optional

                # Use 'await asyncio.sleep' directly for the non-blocking pause
                await asyncio.sleep(0.5)

        asyncio.run(main())

        print("Updating Google Sheet..")
        export_to_sheets(spreadsheet=spreadsheet, sheet_name='Data',
                         df=final_processed_df, mode='a')

        export_to_sheets(spreadsheet=spreadsheet, sheet_name='Date Summary',
                         df=date_summary_result, mode='a')

        export_to_sheets(spreadsheet=spreadsheet, sheet_name='Keyword Summary',
                         df=keyword_summary_result, mode='a')

        print("Finished Updating Sheet")

else:
    print(f"No result for {today_date}")
    summary_string = (f"<b>{raw_today_data.strftime('%A').upper()}"
                      f" - {today_date} - "
                      f"{raw_today_data.strftime('%H:%M')}"
                      f" -  DAILY RUN SUMMARY</b>")
    summary_string += '\n\n'
    summary_string += 'No Results'

    async def main():
        try:
            # Create a bot instance
            bot = telegram.Bot(token=BOT_TOKEN)
            print(f"Attempting to send message to chat ID: {TARGET_CHAT_ID}")

            await bot.send_message(
                chat_id=TARGET_CHAT_ID,
                text=summary_string,
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
