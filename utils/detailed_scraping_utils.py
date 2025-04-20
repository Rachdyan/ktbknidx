import os
import fitz
import pandas as pd

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

    for i in range(0, len(all_links)):
        link = all_links[i]
        filename = all_filenames[i]

        print(f"Downloading {link}")
        # sb.download_file(link)
        # sb.uc_open_with_disconnect(link, timeout = 10)
        # sb.uc_open_with_reconnect(link, reconnect_time = 5)
        # sb.activate_cdp_mode()
        sb.uc_open(link)

        sb.assert_downloaded_file(filename)

        downloaded_filepath = sb.get_path_of_downloaded_file(filename)
        current_pdf = fitz.open(downloaded_filepath)
        for page in current_pdf:
            if len(text_content) < 62000:
                text_content += page.get_text("text")

        combined_pdf.insert_pdf(current_pdf)

        sb.delete_downloaded_file_if_present(filename)

    combined_pdf.save(full_combined_pdf_path)

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
