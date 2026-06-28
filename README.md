# DataNova Tech - AI 資料服務平台 (AI Data Service Platform)

吳翊崴 (D1447108) | 人工智慧學系

## 📌 專案簡介與架構圖
本專案為一個全端 AI 資料服務平台，旨在提供自動化的市場財務數據抓取、清洗，並整合具備人臉辨識安全登入機制的即時智能客服系統。系統採用模組化設計，以單一 Web 戰情面板作為控制中心，串接所有後端服務。

**系統架構圖 (Text-based)：**
```text
[Web 戰情面板 (Flask + HTML/JS/Bootstrap)]
       │
       ├──> (M3/M4) 自動管線: [Requests/BS4 爬蟲] -> [Regex 清洗] -> [SQLite 資料庫]
       │
       ├──> (M5) 核心 API: [RESTful 端點 (GET/DELETE)] <-> [SQLite 資料庫]
       │
       ├──> (M6) 智能客服: [TCP Socket 伺服器] <-> [Gemini 2.5 Flash API]
       │
       └──> (M7) 視覺安全: [OpenCV Haar 偵測 + LBPH 辨識] <-> [Webcam 鏡頭]

環境安裝與執行步驟
mkdir data_service_platfrom
cd data_service_platfrom
uv init
uv venv
uv sync
.venv\Scripts
使用 uv run -m src.api.app
後進入 http://127.0.0.1:5000 即可開始使用
若使用ai智能客服(NovaBot)需先輸入api key
(API Key在pdf中)
各模組對應的技術主題說明

|  模組  |                     實作功能描述                 |           對應課程技術主題         |
================================================================================================
| M1/M2  |      系統基礎架構與使用者密碼 Hash 加密驗證       |   基礎 Python, SQLite 資料庫操作   |
|   M3   |  自動化抓取電動車產業 (Tesla, BYD, Rivian) 財報  | 網路爬蟲 (Requests, BeautifulSoup) |
|   M4   |           財務數據標準化處理與例外字元過濾        |         正規表達式 (Regex)         |
|   M5   |          提供前端撈取與刪除資料的 Web 服務        |     Flask Web 框架, RESTful API   |
|   M6   | 多人即時客服室，並串接 Google Gemini 提供 AI 回覆 |  TCP Socket 網路程式設計, 多執行緒  | 
|   M7   |     提供 Face ID 人臉註冊與雙因子驗證登入機制     |  OpenCV 電腦視覺, LBPH 機器學習模型 |