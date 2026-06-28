# src/database/db_core.py
import sqlite3
import os

# 設定資料庫檔案路徑 (存在專案根目錄的 data 資料夾下)
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'platform.db')

def get_connection():
    """取得資料庫連線"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row # 讓查詢結果可以用 dict 方式存取
    return conn

def init_db():
    """初始化資料庫與三張必要資料表"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 建立 users 表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            face_encoding BLOB
        )
    ''')
    
    # 建立 raw_data 表 (存放爬蟲抓取的原始資料)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS raw_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            raw_content TEXT NOT NULL,
            crawled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 建立 clean_data 表 (存放清洗後的資料)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clean_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            raw_id INTEGER,
            title TEXT,
            url TEXT,
            cleaned_content TEXT,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (raw_id) REFERENCES raw_data(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ 資料庫初始化完成！")

if __name__ == '__main__':
    init_db()