# CAD Submission Server

This Flask server accepts CAD idea submissions via a form, uploads user drawings to Google Drive, and logs submission data to Google Sheets.

## Endpoints

- `POST /submit-cad-idea`: Accepts form data and files

## Setup

1. Add your Google Service Account JSON to `etc/secrets/service_account.json`.
2. Update `DRIVE_FOLDER_ID` and `SPREADSHEET_ID` in `app.py`.
3. Run with: `python app.py`

## Dependencies

```bash
pip install -r requirements.txt
```