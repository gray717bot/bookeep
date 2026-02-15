# 🌸 Bookeep - AI 智慧記帳機器人

這是一個基於 LINE Messaging API、Google Gemini AI 與 Google Sheets 的智慧記帳解決方案。它能理解你的語音、辨識你的收據照片，並提供漂亮的視覺化月報表。

---

## ✨ 核心功能

### 1. 多模態智慧記帳
*   **打字記帳**：直接輸入白話文，例如「今天午餐在麥當勞花了 180 元」。
*   **語音記帳**：直接對著機器人說話，它會自動轉換成文字並記錄。
*   **圖片記帳**：拍攝收據或電子發票，AI 會自動辨識品項與金額。

### 2. 專業視覺化回饋 (Flex Message)
*   每筆記帳成功後，系統會回傳一張「可愛粉紅收據卡片」，包含金額評價與打氣語錄。

### 3. 資料統計與月報
*   **個人報表**：輸入「報表」或「摘要」，查看當月個人消費統計。
*   **類別分析**：自動按類別（如餐飲、交通、購物）彙整支出。

### 4. 家庭共享空間
*   **家庭報表**：支援多人合併計帳，輸入「家庭報表」即可查看全家總支出。
*   **資料隔離**：一般情況下個人只能看到自己的帳目，兼顧隱私與共享。

---

## 🛠 技術架構

*   **後端框架**：Flask (Python)
*   **AI 大模型**：Google Gemini 1.5 Flash (用於處理文字、語音與影像)
*   **資料儲存**：Google Sheets API (雲端試算表)
*   **佈署平台**：Render (支援 24/7 運作)
*   **版本管理**：GitHub

---

## 🚀 快速上手教學

### 🛠 環境變數設定 (.env / Render)
請確保以下變數已正確設定：
*   `LINE_CHANNEL_SECRET`: LINE Developers 提供的 Secret。
*   `LINE_CHANNEL_ACCESS_TOKEN`: LINE Developers 提供的 Token。
*   `GOOGLE_SHEETS_ID`: 你的 Google 試算表 ID。
*   `GOOGLE_API_KEY`: Google AI Studio 提供的 Gemini API Key。
*   `FAMILY_USER_IDS`: (選填) 家庭成員的 ID，用半形逗號隔開。

### 📝 常用指令列表
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
