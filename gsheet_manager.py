import gspread
from google.oauth2.service_account import Credentials
import os
from dotenv import load_dotenv

load_dotenv()

class GSheetManager:
    def __init__(self):
        self.scope = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        self.credentials_file = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE', 'service_account.json')
        self.spreadsheet_id = os.getenv('GOOGLE_SHEETS_ID')
        self.client = self._authenticate()

    def _authenticate(self):
        try:
            creds = Credentials.from_service_account_file(self.credentials_file, scopes=self.scope)
            return gspread.authorize(creds)
        except Exception as e:
            print(f"Error authenticating with Google Sheets: {e}")
            return None

    def add_record(self, date, category, amount, note, user_id):
        if not self.client:
            return False
        
        try:
            sheet = self.client.open_by_key(self.spreadsheet_id).sheet1
            sheet.append_row([date, category, amount, note, user_id])
            return True
        except Exception as e:
            print(f"Error adding record to Google Sheets: {e}")
            return False

    def get_summary(self):
        # Implementation for basic summary/report
        if not self.client:
            return "Error: Could not connect to Google Sheets."
        
        try:
            sheet = self.client.open_by_key(self.spreadsheet_id).sheet1
            records = sheet.get_all_records()
            # Basic logic to sum amounts
            total = sum(float(r.get('Amount', 0)) for r in records if str(r.get('Amount')).replace('.', '', 1).isdigit())
            return f"目前的總支出為: {total}"
        except Exception as e:
            print(f"Error getting summary: {e}")
            return "無法獲取摘要資料。"
