import socket
import threading
import logging
import os
import sys
import time

# 🚀 導入全新版的 Google GenAI SDK
from google import genai
from google.genai import types

# 確保路徑正確
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.auth.security import hash_password
from src.database.db_manager import DatabaseManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

active_clients = {}
db = DatabaseManager()

# 讀取 API Key 並用 strip() 清除任何不小心複製到的空白與換行
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()

if GEMINI_API_KEY:
    logging.info("[+] Gemini API 金鑰已載入！NovaBot 準備就緒。")
else:
    logging.warning("[-] 未偵測到 GEMINI_API_KEY，NovaBot 將降級為本地模式。")

def generate_nova_response(query):
    """呼叫最新版 Gemini 大語言模型進行智能客服回覆"""
    query = query.replace("@Nova", "").strip()
    
    if not query:
        return "您好！我是 DataNova 智能助理。請問需要什麼協助？"
    
    if not GEMINI_API_KEY:
        return "本地模式：收到您的訊息！(請從 Web 後台綁定 API Key 以啟動真實 LLM 大腦)"

    try:
        # 使用最新版 SDK 建立客戶端
        client = genai.Client(api_key=GEMINI_API_KEY)
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=query,
            config=types.GenerateContentConfig(
                system_instruction=(
                    "你是一個名為 NovaBot 的 AI 客服助理，由虛擬新創公司 DataNova Tech 所開發。"
                    "你正在為公司的產品『AI 資料服務平台 (AI Data Service Platform)』提供客戶支援。"
                    "請保持專業、親切、幽默的態度，且必須完全使用台灣習慣的【繁體中文】回答。"
                    "回答內容請精簡扼要，控制在 3 句話以內，適合聊天室閱讀。"
                )
            )
        )
        return response.text.strip()

    except Exception as e:
        # 將真實的錯誤原因抓出來，直接印在終端機與聊天室裡！
        error_msg = str(e)
        logging.error(f"Gemini API 呼叫失敗: {error_msg}")
        return f"【系統提示】NovaBot 發生錯誤: {error_msg}"

# 伺服器核心網路邏輯
def broadcast(message, sender_socket=None):
    for client in list(active_clients.keys()):
        if client != sender_socket:
            try:
                client.send(message.encode('utf-8'))
            except Exception:
                remove_client(client)

def remove_client(client_socket):
    if client_socket in active_clients:
        username = active_clients[client_socket]
        del active_clients[client_socket]
        client_socket.close()
        broadcast(f"[系統廣播] {username} 已離開客服聊天室。")
        logging.info(f"使用者 {username} 斷線。目前線上人數: {len(active_clients)}")

def handle_client(client_socket, address):
    logging.info(f"新連線來自: {address}")
    username = None

    try:
        client_socket.send("歡迎來到 DataNova 即時客服！請輸入帳號: ".encode('utf-8'))
        username = client_socket.recv(1024).decode('utf-8').strip()
        
        client_socket.send("請輸入密碼: ".encode('utf-8'))
        password = client_socket.recv(1024).decode('utf-8').strip()
        
        if password == "FACEID_VERIFIED_TOKEN":
            logging.info(f"[{username}] 透過 Face ID 生物辨識授權登入。")
        elif not db.verify_login(username, hash_password(password)):
            client_socket.send("[錯誤] 帳號或密碼錯誤，連線中斷。\n".encode('utf-8'))
            client_socket.close()
            return
            
        active_clients[client_socket] = username
        client_socket.send(f"[成功] 登入成功！歡迎 {username}，您現在可以開始傳送訊息了。\n".encode('utf-8'))
        broadcast(f"[系統廣播] {username} 加入了聊天室！", sender_socket=client_socket)
        logging.info(f"{username} 登入成功。目前線上人數: {len(active_clients)}")

        while True:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break 
                
            formatted_msg = f"[{username}]: {message}"
            logging.info(formatted_msg)
            
            broadcast(formatted_msg, client_socket)

            # 🤖 [攔截機制] 呼叫真實 LLM
            if message.strip().startswith("@Nova"):
                broadcast("\n[🤖 NovaBot]: 正在思考中...\n")
                
                bot_reply = generate_nova_response(message)
                bot_msg = f"\n[🤖 NovaBot]: {bot_reply}\n"
                logging.info(bot_msg.strip())
                
                broadcast(bot_msg, sender_socket=None) 

    except ConnectionResetError:
        logging.warning(f"來自 {address} 的連線異常中斷。")
    except Exception as e:
        logging.error(f"發生未預期錯誤: {e}")
    finally:
        if client_socket in active_clients:
            remove_client(client_socket)
        else:
            client_socket.close()

def start_server(host='127.0.0.1', port=9000):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen(5)
    logging.info(f"[*] 即時客服伺服器已啟動於 {host}:{port}，等待連線中...")

    try:
        while True:
            client_sock, addr = server.accept()
            client_thread = threading.Thread(target=handle_client, args=(client_sock, addr))
            client_thread.daemon = True 
            client_thread.start()
    except KeyboardInterrupt:
        logging.info("伺服器手動關閉。")
    finally:
        server.close()

if __name__ == "__main__":
    start_server()