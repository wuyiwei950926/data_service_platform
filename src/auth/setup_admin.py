# src/auth/setup_admin.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from werkzeug.security import generate_password_hash
from src.database.db_core import get_connection

def create_test_user():
    """建立期末專題指定的驗收帳號"""
    username = "yungchen"
    # 這是教授指定的驗收密碼
    password = r"teed6Vu [b)oa" 
    
    # 密碼必須以 hash 方式儲存
    password_hash = generate_password_hash(password)
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)", 
            (username, password_hash)
        )
        conn.commit()
        print(f"✅ 成功建立驗收帳號: {username}")
    except Exception as e:
        print(f"⚠️ 帳號建立失敗 (可能已存在): {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    create_test_user()