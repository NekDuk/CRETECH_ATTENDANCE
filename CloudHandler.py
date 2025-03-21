import datetime from datetime, delta

utc_time = datetime.utcnow()  # Get UTC time
local_time = utc_time + timedelta(hours=8)  # Convert to Philippine Time
timestamp = local_time.strftime("%H:%M")
date_today = time.strftime("%d%b%Y")  # Format: 5mar2025

spreadsheet = client.open("attendance")

try:
    worksheet = spreadsheet.worksheet(date_today)  # Try to access it
except gspread.WorksheetNotFound:
    print(f"Error: Worksheet {date_today} not found. Is it created automatically?")
    raise  # Stop execution if it's missing

print("Worksheet found:", worksheet.title)

# Find next empty row in column B
next_row = len(worksheet.col_values(2)) + 1  # Get the next empty row

worksheet.update(range_name=f"A{next_row}", values=[[name]], value_input_option="USER_ENTERED")
worksheet.update(range_name=f"C{next_row}", values=[[timestamp]], value_input_option="USER_ENTERED")
