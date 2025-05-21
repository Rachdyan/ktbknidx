import os
import fitz
import pandas as pd
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from oauth2client.service_account import ServiceAccountCredentials
from openai import OpenAI
from seleniumbase import SB

from utils.google_utils import get_folder_list_from_drive, create_folder, \
    upload_to_drive
from utils.ai_summary_utils import summarize


def generate_pdf_name(row):
    title = row['title']
    if (len(title) > 200):
        title = title[:200]

    today_date = row['date']

    stock_code = row['stock']

    pdf_name = f"{today_date}_{stock_code}_{title}.pdf"
    return pdf_name


def upload_pdf_and_generate_summary(sb, df, drive, parent_folder_id,
                                    upload, generate_summary, client):
    print(f"Getting {df['pdf_name']}....")
    all_links = eval(df['document_links'])
    # all_links

    all_filenames = [link.split('/')[-1] for link in all_links]
    # all_filenames

    download_folder = sb.get_downloads_folder()
    full_combined_pdf_path = os.path.join(download_folder, df['pdf_name'])

    text_content = ""
    combined_pdf = fitz.open()
    success_flag = False  # Track if at least 1 file downloaded

    for i in range(0, len(all_links)):
        link = all_links[i]
        filename = all_filenames[i]
        downloaded = False

        try:
            print(f"Downloading {link}")
            sb.uc_open(link)
            sb.assert_downloaded_file(filename, timeout=60)
            downloaded = True
            success_flag = True  # Mark success if downloaded
        except Exception as e:
            print(f"⚠️ Failed to download {filename}: {str(e)}")
            sb.delete_downloaded_file_if_present(filename)  # Clean up
            continue  # Skip to next file

        if downloaded:
            try:
                downloaded_filepath = sb.get_path_of_downloaded_file(filename)
                current_pdf = fitz.open(downloaded_filepath)
                # Process text content
                for page in current_pdf:
                    if len(text_content) < 62000:
                        text_content += page.get_text("text")
                # Add to combined PDF
                combined_pdf.insert_pdf(current_pdf)
            finally:
                sb.delete_downloaded_file_if_present(filename)

    # Return None if all downloads failed
    if not success_flag:
        print("❌ All downloads failed. Returning None.")
        combined_pdf.close()
        df['drive_link'] = 'Failed Downloading PDF'
        df['summary'] = 'Failed Downloading PDF'
        return df

    # Save combined PDF only if content exists
    if combined_pdf.page_count > 0:
        combined_pdf.save(full_combined_pdf_path)
        combined_pdf.close()
    else:
        print("❌ No valid PDF content. Returning None.")
        combined_pdf.close()
        df['drive_link'] = 'Failed Downloading PDF'
        df['summary'] = 'Failed Downloading PDF'
        return df
    #     downloaded_filepath = sb.get_path_of_downloaded_file(filename)
    #     current_pdf = fitz.open(downloaded_filepath)
    #     for page in current_pdf:
    #         if len(text_content) < 62000:
    #             text_content += page.get_text("text")

    #     combined_pdf.insert_pdf(current_pdf)

    #     sb.delete_downloaded_file_if_present(filename)

    # combined_pdf.save(full_combined_pdf_path)

    # Upload to Drive

    if upload:
        existing_drive_folder_df = get_folder_list_from_drive(drive,
                                                              parent_folder_id)

        if df['stock'] in existing_drive_folder_df.title.tolist():
            print(f"{df['stock']} folder already exist in drive")
            to_be_upload_folder_id = existing_drive_folder_df[
                existing_drive_folder_df.title == df['stock']]\
                .get('id').tolist()[0]
        else:
            print(f"{df['stock']} folder not exist in drive."
                  "Creating folder..")
            new_stock_folder = create_folder(
                drive, parent_folder_id, df['stock'])
            to_be_upload_folder_id = new_stock_folder['id']

            # local_file_path = full_combined_pdf_path

        drive_file_name = df['pdf_name']
        try:
            uploaded_file = upload_to_drive(
                drive,
                folder_id=to_be_upload_folder_id,
                local_file_path=full_combined_pdf_path,
                drive_file_name=drive_file_name)

            uploaded_file_link = uploaded_file['alternateLink']
        except Exception as e:
            print(f"Error uploading file because of {e}")
            uploaded_file_link = 'Error uploading file'
    else:
        uploaded_file_link = 'Doc not uploaded to drive'

    # Generate Summary
    if generate_summary:
        try:
            print(f"Summarizing {df['pdf_name']}")
            pdf_summary = summarize(text_content, client,
                                    detail=0,
                                    model='deepseek-chat',
                                    verbose=True,
                                    )
        except Exception as error:
            print("Error generating summary:", error)
            pdf_summary = 'Error generating summary because of {e}'

    else:
        pdf_summary = 'Summary is not generated'

    df['drive_link'] = uploaded_file_link
    df['summary'] = pdf_summary

    return pd.DataFrame([df])


def upload_pdf_and_generate_summary_multi(row, proxy_string,
                                          service_account_dict,
                                          parent_folder_id,
                                          scope, deepseek_api_key):
    """Process a single row with its own browser instance and services"""
    try:
        # Reinitialize services inside the process
        gauth = GoogleAuth()
        gauth.credentials = ServiceAccountCredentials.from_json_keyfile_dict(
            service_account_dict, scope
        )
        drive = GoogleDrive(gauth)
        client = OpenAI(api_key=deepseek_api_key,
                        base_url="https://api.deepseek.com")

        with SB(uc=True, headless=True, xvfb=True,
                proxy=proxy_string,
                maximize=True, external_pdf=True) as sb:
            # Configure browser settings
            sb.driver.execute_cdp_cmd(
                    "Network.setExtraHTTPHeaders",
                    {
                        "headers": {
                            'Accept': 'text/html,application/xhtml+xml,\
                                application\
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

            return upload_pdf_and_generate_summary(
                sb=sb,
                df=row.to_dict(),
                drive=drive,
                parent_folder_id=parent_folder_id,
                upload=True,
                generate_summary=True,
                client=client
            )
    except Exception as e:
        print(f"Error processing row: {e}")
        return None
