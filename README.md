# CAD Submission Server (v2)

Handles idea submissions for custom CAD work via POST request. Uploads images to Google Drive and logs info in Google Sheets.

## Setup

1. Add your Google Service Account JSON to: `etc/secrets/service_account.json`
2. Replace `YOUR_DRIVE_FOLDER_ID` and `YOUR_SHEET_ID` in `app.py`
3. Install dependencies: `pip install -r requirements.txt`
4. Run the app: `python app.py`

## Endpoint

- `POST /submit-cad-idea`: Accepts form data and files