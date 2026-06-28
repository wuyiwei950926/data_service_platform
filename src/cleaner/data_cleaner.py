import re
import logging
from src.database.db_manager import DatabaseManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DataCleaner:
    def __init__(self):
        self.db = DatabaseManager()

    def process_cleaning_rules(self, text):
        """套用 3 種正規表達式清洗規則"""
        if not text:
            return ""

        # 規則 1: 去除 HTML 標籤 
        # 尋找以 < 開頭，> 結尾的任何內容並替換為空字串
        cleaned_text = re.sub(r'<.*?>', '', text)
        
        # 規則 2: 統一金額格式，精確提取數字並以 "m" 為單位 
        # 先清除多餘的貨幣符號 ($ 或 RMB 或 USD)
        cleaned_text = re.sub(r'[\$]|USD|\(RMB\)', '', cleaned_text)
        # 尋找數字(包含逗號)後面跟著 0 或多個空白再加上 m/M 的格式，強制轉換為緊湊的 "數字m"
        cleaned_text = re.sub(r'(\d[\d,]*(\.\d+)?)\s*[mM]', r'\1m', cleaned_text)
        
        # 規則 3: 去除特殊符號與多餘空白 
        # 將多個連續的空白、換行符號替換為單一空格，並去除頭尾空白
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
        
        return cleaned_text

    def run_pipeline(self):
        """執行從 raw_data 讀取、清洗並存入 clean_data 的完整資料管線"""
        logging.info("啟動資料清洗管線...")
        
        # 讀取 M3 存下來的所有原始資料
        raw_records = self.db.read_all_raw_data()
        if not raw_records:
            logging.warning("目前 raw_data 中沒有資料可供清洗。")
            return
            
        success_count = 0
        for record in raw_records:
            raw_id = record['id']
            original_content = record['content']
            
            # 執行清洗
            clean_content = self.process_cleaning_rules(original_content)
            
            # 存入 clean_data 表
            if self.db.create_clean_data(raw_id, clean_content, category="EV_Finance"):
                success_count += 1
                
        logging.info(f"清洗完成！共 {success_count} 筆資料已標準化並存入 clean_data。")

if __name__ == "__main__":
    # 本地端測試與展示清洗結果
    cleaner = DataCleaner()
    cleaner.run_pipeline()
    
    # 印出最新一筆清洗後的資料來驗收
    with cleaner.db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT clean_content FROM clean_data ORDER BY id DESC LIMIT 1")
        result = cursor.fetchone()
        if result:
            print("\n[✅ 驗收] 清洗後的最新資料格式:")
            print(result['clean_content'])