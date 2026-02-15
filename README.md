# 🌸 Bookeep - AI 智慧記帳機器人

這是一個基於 LINE Messaging API、Google Gemini AI 與 Google Sheets 的智慧記帳解決方案。它能理解你的語音、辨識你的收據照片，並提供漂亮的視覺化月報表。

---

## ✨ 核心功能

### 1. 多模態智慧記帳
*   **打字記帳**：直接輸入白話文，例如「今天午餐在麥當勞花了 180 元」。
*   **語音記帳**：直接對著機器人說話，它會自動轉換成文字並記錄。
*   **圖片/帳單記帳**：拍攝收據、電子發票或**信用卡帳單截圖/PDF**，AI 會自動辨識多筆消費並批次存入。

### 2. 專業視覺化回饋 (Flex Message)
*   每筆記帳成功後，系統會回傳一張「可愛粉紅收據卡片」。
*   **批次彙總卡片**：當你上傳帳單時，系統會顯示總筆數與金額的彙總。

### 3. LINE Rich Menu 圖文選單
*   底部提供視覺化選單，包含：📊 報表、🏠 家庭報表、🔍 查詢ID、📖 使用教學。

---

## 🚀 快速上手教學

### 🛠 環境變數設定 (.env / Render)
... (略)

### 🎨 設定圖文選單
在本地端執行以下腳本即可啟動漂亮的選單：
```bash
python3 setup_rich_menu.py
```

### 📝 常用指令列表
... (略)
| 指令 | 說明 |
| :--- | :--- |
| **隨意說話/拍照** | 自動解析並記帳 |
| **摘要 / 報表 / 本月** | 查看個人當月統計卡片 |
| **家庭報表 / 全家** | 查看全家合併統計卡片 |
| **查詢ID** | 獲取個人的 LINE User ID |

---

## 📂 檔案結構說明

*   `app.py`: Webhook 核心引擎，處理 LINE 傳入的各種訊息。
*   `gemini_manager.py`: 負責與 Google Gemini AI 對接，執行 NLP 解析。
*   `gsheet_manager.py`: 負責對 Google Sheets 進行讀寫與報表統計。
*   `line_handler.py`: 負責 Flex Message (卡片介面) 的設計與產生。
*   `config.py`: 專案設定檔。
*   `service_account.json`: Google Cloud 服務帳號憑證。

---

## 👨‍💻 開發者備註
*   本專案使用 `gunicorn` 作為生產伺服器。
*   佈署至 Render 時請務必在 Environment 設定 `service_account.json` 為 Secret File。

---
祝你記帳愉快，早日達成財富自由！🌸💰
