import google.generativeai as genai
import os
from datetime import datetime
import json
from dotenv import load_dotenv

load_dotenv()

class GeminiManager:
    def __init__(self):
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model = genai.GenerativeModel('gemini-flash-latest')

    def parse_bookkeeping_content(self, content_path=None, text_content=None, mime_type=None):
        """
        使用 Gemini 解析記帳內容。
        支援文字、圖片 (Receipts)、語音 (Voice notes)。
        """
        prompt = """
        你是一位專業的記帳助理。請從提供的內容中提取記帳資訊。
        請務必以 JSON 格式回傳，包含以下欄位：
        {
            "category": "類別 (例如：晚餐, 交通, 購物...)",
            "amount": 金額 (數字),
            "note": "備註 (如果沒有則留空)",
            "date": "YYYY-MM-DD HH:MM:SS (當前時間為: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """)"
        }
        如果是收據圖片，請抓取總金額。
        如果是語音或文字，請從語句中提取。
        """

        contents = [prompt]
        
        if content_path and os.path.exists(content_path):
            with open(content_path, "rb") as f:
                data = f.read()
            contents.append({
                "mime_type": mime_type,
                "data": data
            })
        
        if text_content:
            contents.append(text_content)

        try:
            response = self.model.generate_content(contents)
            # 提取 JSON 部分
            text_response = response.text
            json_str = text_response.split('```json')[1].split('```')[0].strip() if '```json' in text_response else text_response
            return json.loads(json_str)
        except Exception as e:
            print(f"Gemini Parsing Error: {e}")
            return None

if __name__ == "__main__":
    # 簡單測試合法性
    gm = GeminiManager()
    print("Gemini Manager 載入成功")
