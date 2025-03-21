from datetime import datetime, timedelta
import io
import gspread
import os
import cv2
import numpy as np
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2 import service_account
from FacialRecognition import get_faces  # Ensure this function can accept an image array

# Authenticate Google APIs
SCOPES = ["https://www.googleapis.com/auth/drive"]
SERVICE_ACCOUNT_FILE = "key.json"

creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
drive_service = build("drive", "v3", credentials=creds)
gc = gspread.authorize(creds)

# Get current time in Philippine Time
utc_time = datetime.utcnow()
local_time = utc_time + timedelta(hours=8)
timestamp = local_time.strftime("%H:%M")
date_today = local_time.strftime("%d%b%Y")  # Example: 21Mar2025

# Open Google Sheet
spreadsheet = gc.open_by_key("1yvfKS2yLGoQ85SnbAeTUMgxEkYYmYbumg6i6akLJkRU")

def init_sheet():
    """Ensure today's attendance sheet exists."""
    today = datetime.now().strftime("%d%b%Y")
    existing_sheets = [sheet.title for sheet in spreadsheet.worksheets()]

    if today not in existing_sheets:
        try:
            template_sheet = spreadsheet.worksheet("TEMPLATE")
            new_sheet = spreadsheet.duplicate_sheet(source_sheet_id=template_sheet.id)
            new_sheet.update_title(today)
            print(f"✅ Created new attendance sheet: {today}")
        except gspread.exceptions.WorksheetNotFound:
            print("⚠️ Error: TEMPLATE sheet not found! Please create one.")

init_sheet()
worksheet = spreadsheet.worksheet(date_today)  # Access today's sheet

# **Step 1: Get Image Files from Google Drive**
FOLDER_ID = "1jHjsIHfzNCVMoI7ArI8eWSBCHL6ef7G0"

query = f"'{FOLDER_ID}' in parents and mimeType contains 'image/'"
results = drive_service.files().list(q=query, fields="files(id, name, createdTime)").execute()
files = results.get("files", [])


if not files:
    print("No images found in the Google Drive folder.")
    exit()


existing_entries = worksheet.col_values(1)
# **Step 2: Process Each Image**
for file in files:
    file_id = file["id"]
    file_name = file["name"]
    upload_time_utc = file["createdTime"]  # Example: '2025-03-21T12:34:56.789Z'

    # Convert UTC time to Philippine Time (UTC+8)
    upload_time_obj = datetime.strptime(upload_time_utc, "%Y-%m-%dT%H:%M:%S.%fZ")
    upload_time_pht = upload_time_obj + timedelta(hours=8)
    upload_timestamp = upload_time_pht.strftime("%H:%M")  # Format: HH:MM

    print(f"Processing: {file_name} (Uploaded at {upload_timestamp} PHT)")

    # Stream image into memory
    request = drive_service.files().get_media(fileId=file_id)
    image_data = io.BytesIO()
    downloader = MediaIoBaseDownload(image_data, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()

    image_data.seek(0)

    # Convert to NumPy array for OpenCV processing
    np_image = np.frombuffer(image_data.read(), np.uint8)
    img = cv2.imdecode(np_image, cv2.IMREAD_COLOR)

    # **Step 3: Run Face Recognition**
    name = get_faces(img)  # Pass the image directly, not the path

    if not name:
        name = "Unknown"
        print("No face detected.")

    if name in existing_entries:
        print(f"⚠️ Duplicate detected: {name} already exists in the attendance sheet. Skipping.")
        continue  # Skip this entry

    # **Step 4: Add to Google Sheet**
    if not name == "Unknown":


        next_row = len(worksheet.col_values(2)) + 1  # Find next empty row
        worksheet.update(f"A{next_row}", range_name=[[name]], value_input_option="USER_ENTERED")
        worksheet.update(f"C{next_row}", range_name=[[upload_timestamp]], value_input_option="USER_ENTERED")

        print(f"Added {name} to attendance sheet.")
    else:
        print("Unknown person detected! Requesting permission for elimination of target...")

print("Processing complete!")
