import hashlib
import logging
from src.database.db_manager import DatabaseManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def hash_password(password):
    """將密碼轉換為 SHA-256 Hash，絕對不存明文"""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def setup_professor_account():
    """建立期末專題指定的隱藏驗收帳號"""
    db = DatabaseManager()
    target_user = "yungchen"
    # 小心處理密碼中的特殊字元與空白
    target_pass = "teed6Vu [b)oa" 
    hashed_pass = hash_password(target_pass)
    
    # 嘗試註冊，如果帳號已存在會回傳 False，我們就不重複建立
    if db.register_user(target_user, hashed_pass):
        logging.info(f"[✅ 驗收條件達成] 已成功建立教授專屬驗收帳號: {target_user}")
    else:
        logging.info(f"[*] 驗收帳號 {target_user} 已存在資料庫中。")

if __name__ == "__main__":
    # 執行此檔案來初始化驗收帳號
    setup_professor_account()