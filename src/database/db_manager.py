import sqlite3
import os

class DatabaseManager:
    def __init__(self, db_path="data/ai_platform.db"):
        """初始化資料庫連線與路徑"""
        self.db_path = db_path
        # 確保 data 資料夾存在
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_db()

    def get_connection(self):
        """建立並回傳資料庫連線"""
        # check_same_thread=False 是為了讓之後 M6 的多執行緒(Threading)也能共用連線
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row # 讓查詢結果可以用字典的方式存取欄位
        return conn

    def init_db(self):
        """初始化建立 3 張核心資料表"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # 1. 使用者表 (保留密碼 hash 欄位給 M6 使用)
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password_hash TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # 2. 原始資料表 (給 M3 爬蟲存放用)
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS raw_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        source TEXT NOT NULL,
                        content TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # 3. 清洗後資料表 (給 M4 清洗器與 M5 API 使用)
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS clean_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        raw_id INTEGER,
                        clean_content TEXT NOT NULL,
                        category TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (raw_id) REFERENCES raw_data (id)
                    )
                ''')
                conn.commit()
                print("[*] 資料庫與資料表初始化完成！")
        except sqlite3.Error as e:
            print(f"[-] 資料庫初始化失敗: {e}")
    # M6 帳號安全與登入驗證操作
    def register_user(self, username, password_hash):
        """[Auth] 註冊新使用者"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password_hash))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            # 捕捉帳號重複的錯誤
            return False 
        except sqlite3.Error as e:
            print(f"[-] 註冊失敗: {e}")
            return False

    def verify_login(self, username, password_hash):
        """[Auth] 驗證登入帳密"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE username = ? AND password_hash = ?", (username, password_hash))
                return cursor.fetchone() is not None
        except sqlite3.Error as e:
            print(f"[-] 登入驗證失敗: {e}")
            return False
        
    # CRUD 基礎操作實作 (Create, Read, Update, Delete)
    def create_raw_data(self, source, content):
        """[Create] 新增一筆原始資料"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO raw_data (source, content) VALUES (?, ?)", (source, content))
                conn.commit()
                return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"[-] 新增資料失敗: {e}")
            return None

    def read_all_raw_data(self):
        """[Read] 讀取所有原始資料"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM raw_data")
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"[-] 查詢資料失敗: {e}")
            return []

    def create_clean_data(self, raw_id, clean_content, category="Financial"):
        """[Create] 新增一筆清洗後的資料到 clean_data 表"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO clean_data (raw_id, clean_content, category) VALUES (?, ?, ?)", 
                    (raw_id, clean_content, category)
                )
                conn.commit()
                return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"[-] 新增清洗資料失敗: {e}")
            return None

if __name__ == "__main__":
    # 本地測試 CRUD 功能
    db = DatabaseManager()
    
    # 測試 Create
    inserted_id = db.create_raw_data("Test_API", '{"title": "測試數據", "value": 100}')
    print(f"[+] 成功新增資料，ID: {inserted_id}")
    
    # 測試 Read
    records = db.read_all_raw_data()
    print(f"[+] 目前資料庫共有 {len(records)} 筆 raw_data")
    if records:
        print(f"最新一筆資料內容: {records[-1]}")