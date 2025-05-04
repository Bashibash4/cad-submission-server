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
        file_urls = []

        # Upload files to Drive
        drive_service = build('drive', 'v3', credentials=credentials)
        for f in files:
            if f:
                filename = secure_filename(f.filename)
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                f.save(filepath)

                media = MediaFileUpload(filepath)
                file_meta = {'name': filename, 'parents': [DRIVE_FOLDER_ID]}
                uploaded = drive_service.files().create(body=file_meta, media_body=media, fields='id').execute()
                file_id = uploaded['id']
                file_urls.append(f"https://drive.google.com/file/d/{file_id}/view")
                os.remove(filepath)

        # Append row to Sheet
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
            ", ".join(file_urls)
        ]]
        sheets_service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{SHEET_NAME}!A1",
            valueInputOption="USER_ENTERED",
            body={"values": row}
        ).execute()

        return jsonify({"status": "success"}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

