import logging
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, 
    AudioMessage, ImageMessage, FileMessage
)
import tempfile
import traceback
from config import LINE_CHANNEL_SECRET, LINE_CHANNEL_ACCESS_TOKEN, FAMILY_USER_IDS
from gsheet_manager import GSheetManager
from line_handler import LineHandler
from gemini_manager import GeminiManager

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = app.logger

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)
gsheet = GSheetManager()
gemini = GeminiManager()

@app.route("/", methods=['GET'])
def index():
    return "Bookeep server is running! Please use /callback for LINE Webhook.", 200

@app.errorhandler(Exception)
def handle_error(e):
    logger.error(f"!!! Unhandled Exception: {str(e)}")
    logger.error(traceback.format_exc())
    return "Internal Server Error", 500

@app.route("/callback", methods=['POST'])
def callback():
    # 獲取 X-Line-Signature 標頭值
    signature = request.headers.get('X-Line-Signature')

    # 獲取請求實體
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # 處理 Webhook 本體
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    user_id = event.source.user_id
    text = event.message.text
    
    # 優先嘗試處理系統指令
    if "使用教學" in text:
        reply = "🌸 Bookeep 使用小撇步：\n1. 直接打字「早餐 100」\n2. 對我說話「今天吃大餐花了一千」\n3. 拍收據或上傳帳單 PDF\n4. 點下方選單看「報表」唷！"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        return

    if "查詢ID" in text or "my id" in text.lower():
        reply = f"你的 LINE User ID 是：\n{user_id}\n\n(請將此 ID 提供給管理員以設定家庭共享)"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        return

    if any(keyword in text for keyword in ["全家", "全家報表", "家庭報表"]):
        if not FAMILY_USER_IDS:
            reply = "尚未設定家庭成員 ID。請在環境變數中設定 FAMILY_USER_IDS。"
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
            return
        
        summary = gsheet.get_summary(FAMILY_USER_IDS, is_family=True)
        if isinstance(summary, dict):
            reply_message = LineHandler.get_summary_flex(summary)
            line_bot_api.reply_message(event.reply_token, reply_message)
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=summary))
        return

    if any(keyword in text for keyword in ["摘要", "總額", "報表", "本月"]):
        summary = gsheet.get_summary(user_id)
        if isinstance(summary, dict):
            reply_message = LineHandler.get_summary_flex(summary)
            line_bot_api.reply_message(event.reply_token, reply_message)
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=summary))
        return
    else:
        # 使用 Gemini 解析文字
        records = gemini.parse_bookkeeping_content(text_content=text)
        
        if records:
            success = gsheet.add_records(records, user_id)
            if success:
                if len(records) > 1:
                    reply_message = LineHandler.get_batch_summary_flex(records)
                else:
                    reply_message = LineHandler.get_flex_message(records[0])
                line_bot_api.reply_message(event.reply_token, reply_message)
                return
            else:
                reply = "❌ 記錄失敗，請檢查 Google Sheets 設定。"
        else:
            reply = "抱歉，我看不懂這筆帳。請嘗試輸入例如：\n「晚餐 100」\n「150 交通費」"

    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))

@handler.add(MessageEvent, message=(AudioMessage, ImageMessage, FileMessage))
def handle_content_message(event):
    user_id = event.source.user_id
    message_content = line_bot_api.get_message_content(event.message.id)
    
    # 決定副檔名與 MIME 類型
    if isinstance(event.message, AudioMessage):
        ext = "m4a"
        mime_type = "audio/x-m4a"
    elif isinstance(event.message, ImageMessage):
        ext = "jpg"
        mime_type = "image/jpeg"
    elif isinstance(event.message, FileMessage):
        ext = event.message.file_name.split('.')[-1]
        mime_type = "application/pdf" if ext.lower() == 'pdf' else "application/octet-stream"
    else:
        return

    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tf:
        for chunk in message_content.iter_content():
            tf.write(chunk)
        temp_path = tf.name

    # 使用 Gemini 解析多媒體內容
    records = gemini.parse_bookkeeping_content(content_path=temp_path, mime_type=mime_type)
    
    # 刪除暫存檔
    if os.path.exists(temp_path):
        os.remove(temp_path)

    if records:
        success = gsheet.add_records(records, user_id)
        if success:
            if len(records) > 1:
                reply_message = LineHandler.get_batch_summary_flex(records)
            else:
                reply_message = LineHandler.get_flex_message(records[0])
            line_bot_api.reply_message(event.reply_token, reply_message)
            return
        else:
            reply = "❌ 辨識成功但記錄失敗。"
    else:
        reply = "抱歉，我無法從這段內容中提取記帳資訊。"

    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
