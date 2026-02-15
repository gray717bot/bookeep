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

    def get_summary(self, user_id, month=None):
        """
        獲取摘要。如果指定 month (格式 YYYY-MM)，則只計算該月。
        """
        if not self.client:
            return "Error: Could not connect to Google Sheets."
        
        try:
            sheet = self.client.open_by_key(self.spreadsheet_id).sheet1
            records = sheet.get_all_records()
            
            user_total = 0
            category_totals = {}
            count = 0
            
            # 如果沒指定月份，預設為本月
            target_month = month if month else datetime.now().strftime("%Y-%m")

            for r in records:
                r_user_id = r.get('User ID') or r.get('user_id')
                r_amount = r.get('Amount') or r.get('amount')
                r_date = r.get('Date') or r.get('date', '')
                
                # 檢查使用者 ID 與月份
                if str(r_user_id) == str(user_id) and r_date.startswith(target_month):
                    try:
                        amt = float(r_amount)
                        user_total += amt
                        count += 1
                        
                        # 按類別統計
                        cat = r.get('Category') or r.get('category') or '未分類'
                        category_totals[cat] = category_totals.get(cat, 0) + amt
                    except (ValueError, TypeError):
                        continue
            
            if count == 0:
                return f"你目前在 {target_month} 還沒有任何記帳紀錄喔！"
            
            # 準備類別詳細資訊文字版 (或供 Flex 使用)
            cat_details = "\n".join([f"• {k}: {v}元" for k, v in category_totals.items()])
            
            return {
                "month": target_month,
                "total": user_total,
                "count": count,
                "category_details": category_totals,
                "text_summary": f"📊 {target_month} 報表：\n━━━━━━━━━━\n總支出：{user_total} 元\n筆數：{count} 筆\n\n類別明細：\n{cat_details}"
            }
        except Exception as e:
            print(f"Error getting summary: {e}")
            return "無法獲取摘要資料，請確認試算表格式。"
