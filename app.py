from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os
from config import LINE_CHANNEL_SECRET, LINE_CHANNEL_ACCESS_TOKEN
from gsheet_manager import GSheetManager
from line_handler import LineHandler
from gemini_manager import GeminiManager
import tempfile
from linebot.models import MessageEvent, TextMessage, TextSendMessage, AudioMessage, ImageMessage

app = Flask(__name__)

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)
gsheet = GSheetManager()
gemini = GeminiManager()

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
    if "摘要" in text or "總額" in text:
        reply = gsheet.get_summary()
    else:
        # 使用 Gemini 解析文字
        record = gemini.parse_bookkeeping_content(text_content=text)
        
        if record and record.get('amount'):
            success = gsheet.add_record(
                record['date'],
                record['category'],
                record['amount'],
                record['note'],
                user_id
            )
            if success:
                # 使用 Flex Message 回覆
                reply_message = LineHandler.get_flex_message(record)
                line_bot_api.reply_message(event.reply_token, reply_message)
                return
            else:
                reply = "❌ 記錄失敗，請檢查 Google Sheets 設定。"
        else:
            reply = "抱歉，我看不懂這筆帳。請嘗試輸入例如：\n「晚餐 100」\n「150 交通費」"

    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))

@handler.add(MessageEvent, message=(AudioMessage, ImageMessage))
def handle_content_message(event):
    user_id = event.source.user_id
    message_content = line_bot_api.get_message_content(event.message.id)
    
    # 決定 MIME 類型
    if isinstance(event.message, AudioMessage):
        ext = "m4a"
        mime_type = "audio/x-m4a"
    else:
        ext = "jpg"
        mime_type = "image/jpeg"

    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tf:
        for chunk in message_content.iter_content():
            tf.write(chunk)
        temp_path = tf.name

    # 使用 Gemini 解析多媒體內容
    record = gemini.parse_bookkeeping_content(content_path=temp_path, mime_type=mime_type)
    
    # 刪除暫存檔
    if os.path.exists(temp_path):
        os.remove(temp_path)

    if record and record.get('amount'):
        success = gsheet.add_record(
            record['date'],
            record['category'],
            record['amount'],
            record['note'],
            user_id
        )
        if success:
            # 使用 Flex Message 回覆
            reply_message = LineHandler.get_flex_message(record)
            line_bot_api.reply_message(event.reply_token, reply_message)
            return
        else:
            reply = "❌ 辨識成功但記錄失敗。"
    else:
        reply = "抱歉，我無法從這段語音或照片中提取記帳資訊。"

    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
