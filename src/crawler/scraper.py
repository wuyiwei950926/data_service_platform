import requests
import json
import logging
from src.database.db_manager import DatabaseManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class MarketDataScraper:
    def __init__(self):
        self.db = DatabaseManager()
        # 這裡設定一個目標 API。在真實專案中，可能會是 Yahoo Finance 或證交所 API。
        # 為了確保你的期末專案在 Demo 時絕對不會因為外部 API 掛掉而崩潰（符合 Exception Handling 要求），
        # 我們會加入一個備用的模擬資料源。
        self.api_url = "https://api.example.com/v1/ev-financial-news" 

    def fetch_data(self):
        """使用 requests 發出 HTTP 請求抓取資料"""
        logging.info(f"準備從 {self.api_url} 抓取最新市場數據...")
        
        try:
            # 設定 timeout 避免伺服器無回應導致程式卡死
            response = requests.get(self.api_url, timeout=5)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logging.warning(f"API 連線失敗: {e}。系統將自動切換至本地備用財報資料庫以確保服務不中斷。")
            # [Exception Handling] 發生網路錯誤時，回傳備用的模擬真實財報資料，確保管線持續運作
            return self._get_fallback_data()

    def _get_fallback_data(self):
        """備用資料：包含需要被清洗的髒資料（Dirty Data）"""
        return [
            {"source": "EV_Weekly", "content": "Tesla Q3 updates: Total automotive revenue reached $ 21,300m. The R&D spending was roughly 1,160 m. Gross margin is stable."},
            {"source": "Asia_Tech_News", "content": "BYD breaks record! Revenue hits 28,500 m (RMB). R&D expenses increased to 3,200m. <script>alert('ad')</script>"},
            {"source": "Startup_Daily", "content": "Rivian Q3 financial report: Revenue is currently at 1,337m. R&D spending stands at 450 m USD. Contact pr@rivian.com for details."},
            {"source": "Market_Watch", "content": "   The overall EV market shows a 15% growth... \n\n "}
        ]

    def run_pipeline(self):
        """執行抓取並存入 M2 資料庫的完整流程"""
        raw_data_list = self.fetch_data()
        
        if not raw_data_list:
            logging.error("沒有抓取到任何資料。")
            return

        success_count = 0
        for item in raw_data_list:
            source = item.get("source", "Unknown API")
            # 將資料轉為字串格式存入資料庫
            content = item.get("content", json.dumps(item)) 
            
            # 呼叫 M2 的 DatabaseManager 寫入資料庫
            inserted_id = self.db.create_raw_data(source, content)
            if inserted_id:
                success_count += 1
                
        logging.info(f"抓取任務完成！共成功將 {success_count} 筆原始資料存入 raw_data 資料表。")

if __name__ == "__main__":
    scraper = MarketDataScraper()
    scraper.run_pipeline()