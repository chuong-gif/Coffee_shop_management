import datetime
import os
import pickle
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = [
    "https://www.googleapis.com/auth/drive.file"
]


def get_drive_service(client_secrets_path: str, token_path: str):
    """Khởi tạo Google Drive service với token lưu trên máy."""
    creds = None

    if os.path.exists(token_path):
        with open(token_path, "rb") as token_file:
            creds = pickle.load(token_file)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secrets_path, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(token_path, "wb") as token_file:
            pickle.dump(creds, token_file)

    return build("drive", "v3", credentials=creds)


def find_or_create_folder(service, folder_name: str, parent_id: Optional[str] = None) -> str:
    """Tìm hoặc tạo thư mục Google Drive theo tên và cha."""
    safe_name = folder_name.replace("'", "\\'")
    query = (
        f"mimeType='application/vnd.google-apps.folder' and trashed=false "
        f"and name='{safe_name}'"
    )
    if parent_id:
        query += f" and '{parent_id}' in parents"

    response = service.files().list(
        q=query,
        spaces="drive",
        fields="files(id, name)",
        pageSize=1,
    ).execute()
    files = response.get("files", [])
    if files:
        return files[0]["id"]

    metadata = {
        "name": folder_name,
        "mimeType": "application/vnd.google-apps.folder",
    }
    if parent_id:
        metadata["parents"] = [parent_id]

    created = service.files().create(body=metadata, fields="id").execute()
    return created.get("id")


def ensure_drive_folder_hierarchy(service, root_folder_id: str, year: str, month: str, day: str) -> str:
    """Tạo cấu trúc thư mục [root]/[Year]/[Month]/[Day]."""
    year_id = find_or_create_folder(service, year, parent_id=root_folder_id)
    month_id = find_or_create_folder(service, month, parent_id=year_id)
    day_id = find_or_create_folder(service, day, parent_id=month_id)
    return day_id


def upload_backup_to_drive(
    service,
    local_file_path: str,
    root_folder_id: str,
    backup_name: Optional[str] = None,
):
    """Upload file backup vào Drive theo cấu trúc thư mục ngày tháng."""
    if not os.path.exists(local_file_path):
        raise FileNotFoundError(f"Không tìm thấy file: {local_file_path}")

    backup_name = backup_name or os.path.basename(local_file_path)
    now = datetime.datetime.now()
    target_folder_id = ensure_drive_folder_hierarchy(
        service,
        root_folder_id,
        now.strftime("%Y"),
        now.strftime("%m"),
        now.strftime("%d"),
    )

    file_metadata = {
        "name": backup_name,
        "parents": [target_folder_id],
    }
    media = MediaFileUpload(local_file_path, mimetype="application/octet-stream", resumable=True)
    uploaded_file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id, name, parents",
    ).execute()

    return uploaded_file


def upload_database_backup(
    client_secrets_path: str,
    token_path: str,
    app_root_folder_name: str,
    local_db_path: str,
    backup_name: Optional[str] = None,
):
    """Chuẩn bị service và upload backup database vào thư mục Drive của app."""
    drive_service = get_drive_service(client_secrets_path, token_path)
    root_folder_id = find_or_create_folder(drive_service, app_root_folder_name)
    return upload_backup_to_drive(drive_service, local_db_path, root_folder_id, backup_name)
