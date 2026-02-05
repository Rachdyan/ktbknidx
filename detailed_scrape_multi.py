# from seleniumbase import SB
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
from gspread_dataframe import get_as_dataframe
from openai import OpenAI
import multiprocessing


from utils.scraping_utils import process_keyword_multi
from utils.detailed_scraping_utils import generate_pdf_name, \
    upload_pdf_and_generate_summary_multi
from utils.google_utils import export_to_sheets
from utils.telegram_utils import send_summary_message

load_dotenv(override=True)

user = os.environ['PROXY_USER']
password = os.environ['PROXY_PASSWORD']
proxy_host = os.environ['PROXY_HOST']
proxy_port = os.environ['PROXY_PORT']

proxy_string = f"{user}:{password}@{proxy_host}:{proxy_port}"

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
TARGET_CHAT_ID = "-1003386345668"
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


# keywords = ['material -sosial', 'HMETD']

if __name__ == "__main__":

    # Check if proxy is working
    print("Checking proxy connection...")
    try:
        import requests
        proxies = {
            'http': f'http://{proxy_string}',
            'https': f'http://{proxy_string}'
        }
        response = requests.get('https://www.idx.co.id/',
                                proxies=proxies, timeout=10)
        print(f"Proxy working. Response code: {response.status_code}")
    except Exception as e:
        print(f"Proxy check failed: {e}")
        print("Continuing anyway...")

    # Calculate date-related variables
    raw_today_data = dt.now(pytz.timezone('Asia/Jakarta'))
    today_date = raw_today_data.strftime("%Y-%m-%d")
    # today_date = '2025-11-13'
    today_month_year = raw_today_data.strftime("%b %Y")
    # today_month_year = 'June 2025'

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
        print("Combining results...")
        final_df = pd.concat([df for df in results if df is not None],
                             ignore_index=True)
    except Exception as e:
        print(e)
        final_df = None

    if (final_df is not None and final_df.shape[0] > 0):
        final_df['pdf_name'] = final_df.apply(generate_pdf_name, axis=1)
        final_df['identifier'] = final_df.apply(
            # lambda x: f"{x['time']}_{x['pdf_name']}",
            lambda x: f"{x['pdf_name']}",
            axis=1)

        data_sheet = spreadsheet.worksheet('Data')
        previous_data_df = get_as_dataframe(data_sheet)
        previous_data_df = previous_data_df[['date', 'time', 'pdf_name']]
        previous_data_df['identifier'] = previous_data_df.apply(
            # lambda x: f"{x['time']}_{x['pdf_name']}",
            lambda x: f"{x['pdf_name']}",
            axis=1)

        final_df_filtered = final_df[
            ~final_df.identifier.isin(previous_data_df.identifier.tolist())]
        final_df_filtered.drop('identifier', axis=1,
                               inplace=True)

        print(f"There are a total of {final_df_filtered.shape[0]}"
              " filtered records")

        rows = [row for _, row in final_df_filtered.iterrows()]
        process_args = [(row, proxy_string, service_account_dict,
                         parent_folder_id, scope, deepseek_api_key)
                        for row in rows]

        # Process rows in parallel
        with multiprocessing.Pool(processes=4) as pool:
            processed_results = pool.starmap(
                upload_pdf_and_generate_summary_multi, process_args)

        # Combine results
        final_processed_df = pd.concat(
            [res for res in processed_results if res is not None],
            ignore_index=True)
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

        async def send_no_results_notification():
            try:
                # Create a bot instance
                bot = telegram.Bot(token=BOT_TOKEN)
                print(
                    f"Attempting to send message to chat ID: {TARGET_CHAT_ID}")

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

        asyncio.run(send_no_results_notification())

        result_dict = {'date': dt.strptime(today_date, '%Y-%m-%d').
                       strftime("%d-%m-%Y"),
                       'time': '', 'stock': 'No Result', 'keyword': '',
                       'title': '', 'n_doc': 'No Result', 'document_links': '',
                       'pdf_name': '', 'drive_link': '', 'summary': ''}
        final_processed_df = pd.DataFrame([result_dict])

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

        print("Updating Google Sheet..")
        export_to_sheets(spreadsheet=spreadsheet, sheet_name='Data',
                         df=final_processed_df, mode='a')

        export_to_sheets(spreadsheet=spreadsheet, sheet_name='Date Summary',
                         df=date_summary_result, mode='a')

        export_to_sheets(spreadsheet=spreadsheet, sheet_name='Keyword Summary',
                         df=keyword_summary_result, mode='a')

        print("Finished Updating Sheet")
