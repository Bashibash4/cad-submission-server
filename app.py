from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os, datetime

# Setup
app = Flask(__name__)
UPLOAD_FOLDER = 'cad_uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load credentials from secret file
SERVICE_ACCOUNT_FILE = 'service_account.json'  # Render secret file mounts here
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=[
        'https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/spreadsheets'
    ]
)

# Google Config
DRIVE_FOLDER_ID = '1wOzYjnZ77ryz4wR6MeRa8Q6oFVGPHcc7'
SPREADSHEET_ID = '1g_odFKVOighAK59B0osOjfryN74xKGrcmhOTTWZ4gUU'
SHEET_NAME = 'CAD Orders'

@app.route('/submit-cad-idea', methods=['POST'])
def submit_cad_idea():
    try:
        form = request.form
        files = request.files.getlist("files")

        drive_service = build('drive', 'v3', credentials=credentials)

        # ✅ Step 1: Create customer folder
        customer_name = form.get("name", "Customer")
        folder_metadata = {
            'name': f"{customer_name} - CAD Idea",
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [DRIVE_FOLDER_ID]
        }
        folder = drive_service.files().create(body=folder_metadata, fields='id').execute()
        customer_folder_id = folder.get('id')

        # ✅ Step 2: Upload files to customer folder
        for f in files:
            if f:
                filename = secure_filename(f.filename)
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                f.save(filepath)

                media = MediaFileUpload(filepath)
                file_meta = {'name': filename, 'parents': [customer_folder_id]}
                drive_service.files().create(body=file_meta, media_body=media, fields='id').execute()
                os.remove(filepath)

        # ✅ Step 3: Build folder link to save
        folder_link = f"https://drive.google.com/drive/folders/{customer_folder_id}"

        # ✅ Step 4: Append to Sheets (start on A2)
        sheets_service = build('sheets', 'v4', credentials=credentials)
        row = [[
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            form.get("name", ""),
            form.get("email", ""),
            form.get("title", ""),
            form.get("description", ""),
            form.get("use", ""),
            form.get("format", ""),
            form.get("timeline", ""),
            form.get("notes", ""),
            folder_link
        ]]
        sheets_service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{SHEET_NAME}!A2",  # 👈 Starts from row 2 now
            valueInputOption="USER_ENTERED",
            body={"values": row}
        ).execute()

        return jsonify({"status": "success"}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

