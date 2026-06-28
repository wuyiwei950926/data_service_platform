import os
import sys

# 確保 Python 能找到 src 目錄
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.database.db_manager import DatabaseManager
from src.auth.security import hash_password

def create_new_user():
    print("="*40)
    print(" 🚀 DataNova Tech - 新使用者註冊系統 ")
    print("="*40)
    
    username = input("請輸入您想要註冊的新帳號: ").strip()
    password = input("請輸入您的新密碼: ").strip()

    if not username or not password:
        print("[-] 錯誤：帳號與密碼不可為空！")
        return

    db = DatabaseManager()
    
    # 密碼必須以 hash 方式儲存 (不可存明文)
    hashed_pw = hash_password(password)

    # 呼叫我們在 M2 寫好的註冊函式
    if db.register_user(username, hashed_pw):
        print(f"\n[+] 太棒了！帳號 '{username}' 註冊成功！")
        print("[+] 您現在可以使用此帳號登入 M6 即時客服系統了。")
    else:
        print(f"\n[-] 註冊失敗：帳號 '{username}' 可能已經存在資料庫中。")

if __name__ == "__main__":
    create_new_user()