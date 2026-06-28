from flask import Flask, request, jsonify, render_template
import sqlite3
import os
import sys
import subprocess
# 確保路徑正確
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.database.db_manager import DatabaseManager
from src.auth.security import hash_password
from src.crawler.scraper import MarketDataScraper
from src.cleaner.data_cleaner import DataCleaner

app = Flask(__name__, template_folder='templates')
db = DatabaseManager()

@app.route('/')
def index():
    """回傳前端整合介面 (Dashboard)"""
    return render_template('index.html')

# ==========================================
# M5 原有資料 API
# ==========================================
@app.route('/api/data', methods=['GET'])
def get_clean_data():
    category = request.args.get('category')
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            if category:
                cursor.execute("SELECT * FROM clean_data WHERE category = ?", (category,))
            else:
                cursor.execute("SELECT * FROM clean_data ORDER BY id DESC")
            rows = cursor.fetchall()
            return jsonify({"status": "success", "count": len(rows), "data": [dict(row) for row in rows]}), 200
    except sqlite3.Error as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/data/<int:data_id>', methods=['DELETE'])
def delete_clean_data(data_id):
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM clean_data WHERE id = ?", (data_id,))
            conn.commit()
            return jsonify({"status": "success", "message": f"ID {data_id} 刪除成功"}), 200
    except sqlite3.Error as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/trigger/pipeline', methods=['POST'])
def trigger_pipeline():
    """一鍵執行 M3 爬蟲與 M4 清洗"""
    try:
        scraper = MarketDataScraper()
        scraper.run_pipeline()
        
        cleaner = DataCleaner()
        cleaner.run_pipeline()
        return jsonify({"status": "success", "message": "資料管線執行完畢，資料庫已更新！"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/trigger/chat-server', methods=['POST'])
def trigger_chat_server():
    """自動彈出新視窗啟動 M6 伺服器"""
    # 使用 Windows 專用指令啟動新命令提示字元
    subprocess.Popen(['start', 'cmd', '/k', f'{sys.executable} -m src.chat.server'], shell=True)
    return jsonify({"status": "success", "message": "已在新視窗啟動即時客服伺服器！"})

@app.route('/api/trigger/chat-client', methods=['POST'])
def trigger_chat_client():
    """自動彈出新視窗啟動 M6 客戶端"""
    subprocess.Popen(['start', 'cmd', '/k', f'{sys.executable} -m src.chat.client'], shell=True)
    return jsonify({"status": "success", "message": "已彈出客服連線視窗！"})

@app.route('/api/trigger/face-login', methods=['POST'])
def trigger_face_login():
    """自動彈出新視窗啟動 M6 客戶端，並啟用 Face ID 模式"""
    subprocess.Popen(['start', 'cmd', '/k', f'{sys.executable} -m src.chat.client faceid'], shell=True)
    return jsonify({"status": "success", "message": "啟動成功！請看向攝影機進行 Face ID 登入，成功後將自動進入聊天室。"})

@app.route('/api/auth/register', methods=['POST'])
def api_register():
    """接收前端傳來的註冊請求"""
    req_data = request.get_json()
    username = req_data.get('username', '').strip()
    password = req_data.get('password', '').strip()

    if not username or not password:
        return jsonify({"status": "error", "message": "帳號與密碼不可為空！"}), 400

    # 密碼必須以 hash 方式儲存 (不可存明文)
    hashed_pw = hash_password(password)
    
    if db.register_user(username, hashed_pw):
        return jsonify({"status": "success", "message": f"🎉 帳號 '{username}' 註冊成功！您現在可以開啟客服連線了。"})
    else:
        return jsonify({"status": "error", "message": f"[-] 註冊失敗：帳號 '{username}' 可能已被使用。"}), 400

@app.route('/api/trigger/face-register', methods=['POST'])
def trigger_face_register():
    """先驗證密碼，成功後才自動彈出新視窗進行 Face ID 註冊"""
    req_data = request.get_json()
    username = req_data.get('username', '').strip()
    password = req_data.get('password', '').strip()
    
    if not username or not password:
        return jsonify({"status": "error", "message": "帳號與密碼不可為空！"}), 400
    
    hashed_password = hash_password(password)
    # 🔐 【安全性關鍵】先進行密碼 Hash 驗證
    if not db.verify_login(username, hashed_password):
        return jsonify({"status": "error", "message": "密碼錯誤，安全驗證失敗！"})
        
    # 驗證成功，允許開啟 OpenCV 鏡頭擷取人臉
    subprocess.Popen(['start', 'cmd', '/k', f'{sys.executable} -m src.ai_vision.face_login register {username}'], shell=True)
    return jsonify({"status": "success", "message": f" Verified！密碼驗證成功，正在開啟 {username} 的 Face ID 註冊視窗。"})

#設定 Gemini API Key 
@app.route('/api/config/gemini', methods=['POST'])
def config_gemini():
    """接收前端傳來的 API Key，並設定為系統環境變數"""
    req_data = request.get_json()
    api_key = req_data.get('api_key', '').strip()
    
    if not api_key:
        return jsonify({"status": "error", "message": "API Key 不能為空！"}), 400
        
    # 動態寫入環境變數。之後由 Flask 啟動的 M6 伺服器會自動繼承這個變數！
    os.environ["GEMINI_API_KEY"] = api_key
    
    return jsonify({
        "status": "success", 
        "message": "🧠 大腦綁定成功！系統已記住您的金鑰。\n請點擊下方【1. 啟動 Socket 伺服器】來喚醒 NovaBot！"
    })

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)