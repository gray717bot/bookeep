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

    def get_summary(self, user_id):
        # Implementation for basic summary/report
        if not self.client:
            return "Error: Could not connect to Google Sheets."
        
        try:
            sheet = self.client.open_by_key(self.spreadsheet_id).sheet1
            records = sheet.get_all_records()
            
            # 使用列表推導式篩選屬於該使用者的金額
            # 假設試算表欄位名稱包含 'Amount' 和 'User ID' (或對應 index)
            # 由於 append_row 使用 [date, category, amount, note, user_id]
            # get_all_records 會將第一列視為 Header
            
            user_total = 0
            count = 0
            for r in records:
                # 這裡需要匹配你的試算表標頭名稱，如果是照我的程式碼產生的，標頭應該是：
                # Date | Category | Amount | Note | User ID
                # 我們用索引或名稱來抓取
                r_user_id = r.get('User ID') or r.get('user_id')
                r_amount = r.get('Amount') or r.get('amount')
                
                if str(r_user_id) == str(user_id):
                    try:
                        user_total += float(r_amount)
                        count += 1
                    except (ValueError, TypeError):
                        continue
            
            if count == 0:
                return "你目前還沒有任何記帳紀錄喔！"
                
            return f"💰 你目前的總支出共計：{user_total} 元（共 {count} 筆紀錄）"
        except Exception as e:
            print(f"Error getting summary: {e}")
            return "無法獲取摘要資料，請確認試算表格式是否正確。"
