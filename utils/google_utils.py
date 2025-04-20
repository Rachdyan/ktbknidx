import pandas as pd
from gspread_dataframe import get_as_dataframe, set_with_dataframe


def get_folder_list_from_drive(drive, parent_folder_id):
    list_query = f"'{parent_folder_id}' in parents and trashed=false"
    print(f"Querying for items inside folder ID: {parent_folder_id}")

    try:
        # Execute the query
        file_list = drive.ListFile({'q': list_query}).GetList()
        file_list_df = pd.DataFrame(file_list)
        file_list_df = file_list_df[['kind', 'title', 'mimeType', 'id']]
        folder_list_df = file_list_df[
            file_list_df.mimeType == 'application/vnd.google-apps.folder']
    except Exception as e:
        print(f"\nAn error occurred while listing files: {e}")
        print("Possible reasons: Invalid folder ID, insufficient permissions"
              "for the service account on the folder, Drive API issue.")
        folder_list_df = pd.DataFrame()

    return folder_list_df


def create_folder(drive, parent_folder_id, folderName):
    file_metadata = {
        'title': folderName,
        'parents': [{'id': parent_folder_id}],
        'mimeType': 'application/vnd.google-apps.folder'
        }

    folder = drive.CreateFile(file_metadata)
    folder.Upload()
    return folder


def upload_to_drive(drive, folder_id, local_file_path, drive_file_name):
    try:
        file_metadata = {'title': drive_file_name}
        file_metadata['parents'] = [{'id': folder_id}]
        # print(f"Creating Google Drive file object for: {drive_file_name}")
        drive_file = drive.CreateFile(file_metadata)

        # print(f"Setting content from local file: {local_file_path}")
        drive_file.SetContentFile(local_file_path)

        # print("Starting upload...")
        drive_file.Upload()  # This performs the actual upload

        print(f"Successfully uploaded '{drive_file['title']}'")
        # print(f"File ID: {drive_file['id']}")

    except Exception as e:
        print(f"An error occurred during upload: {e}")
        drive_file = None

    return drive_file


def export_to_sheets(spreadsheet, sheet_name, df, mode='r'):
    ws = spreadsheet.worksheet(f'{sheet_name}')
    if (mode == 'w'):
        ws.clear()
        set_with_dataframe(worksheet=ws, dataframe=df, include_index=False,
                           include_column_header=True, resize=False)
        return True
    elif (mode == 'a'):
        ws.add_rows(df.shape[0])
        max_rows = len(ws.get_all_values(major_dimension='rows'))
        set_with_dataframe(worksheet=ws, dataframe=df, include_index=False,
                           include_column_header=False, row=max_rows + 1,
                           resize=False)
        return True
    else:
        return get_as_dataframe(worksheet=ws)
