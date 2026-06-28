import socket
import threading
import sys
import os

# 確保系統能正確找到 src 模組
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.database.db_manager import DatabaseManager
from src.auth.security import hash_password

# 嘗試載入 Gemini AI (如果系統有安裝套件的話)
try:
    from google import genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# 存放目前連線的客戶端 { client_socket: username }
clients = {} 
db = DatabaseManager()

# 初始化 Gemini 客戶端 (從環境變數讀取 API Key)
api_key = os.environ.get("GEMINI_API_KEY")
gemini_client = genai.Client(api_key=api_key) if GEMINI_AVAILABLE and api_key else None


def broadcast(message, sender_socket=None):
    """將訊息廣播給聊天室內的所有人"""
    for client in list(clients.keys()):
        try:
            client.send(message.encode('utf-8'))
        except:
            client.close()
            if client in clients:
                del clients[client]


def handle_client(client_socket, addr):
    """處理單一連線使用者的登入與聊天"""
    try:
        # 1. 驗證階段：接收帳號
        client_socket.send("歡迎來到 DataNova 即時客服！請輸入帳號: ".encode('utf-8'))
        username = client_socket.recv(1024).decode('utf-8').strip()

        # 2. 驗證階段：接收密碼 (或 Face ID 通行證)
        client_socket.send("請輸入密碼: ".encode('utf-8'))
        password = client_socket.recv(1024).decode('utf-8').strip()

        # 🛑 【關鍵升級】Face ID 專屬放行條 (不需查資料庫，直接過關！)
        if password == "FACEID_BYPASS":
            client_socket.send(f"[成功] 登入成功！歡迎 {username} (Face ID 快速通關)".encode('utf-8'))
        else:
            # 一般手動登入，需與資料庫比對 Hash 密碼
            if not db.verify_login(username, hash_password(password)):
                client_socket.send("[錯誤] 密碼錯誤！連線中斷。".encode('utf-8'))
                client_socket.close()
                return
            client_socket.send(f"[成功] 登入成功！歡迎 {username}，您現在可以開始傳送訊息了。".encode('utf-8'))

        # 驗證通過，加入廣播清單並公告
        clients[client_socket] = username
        join_msg = f"[系統] {username} 加入了聊天室！"
        print(f"[*] {username} ({addr[0]}:{addr[1]}) 成功連線。")
        broadcast(join_msg)

        # 3. 聊天與 AI 互動階段
        while True:
            msg = client_socket.recv(1024).decode('utf-8')
            if not msg:
                break

            formatted_msg = f"[{username}]: {msg}"
            print(formatted_msg)
            broadcast(formatted_msg)

            # 🤖 M6 核心功能：當訊息包含 @Nova 時，觸發 Gemini AI
            if "@Nova" in msg and gemini_client:
                try:
                    prompt = msg.replace("@Nova", "").strip()
                    response = gemini_client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=prompt
                    )
                    ai_msg = f"[🤖 NovaBot]: {response.text}"
                    print(ai_msg)
                    broadcast(ai_msg)
                except Exception as e:
                    error_msg = f"[🤖 NovaBot]: 抱歉，AI 服務目前無法回應 ({e})"
                    broadcast(error_msg)

    except Exception as e:
        print(f"[-] {addr} 連線異常: {e}")
    finally:
        # 使用者離開時的收尾動作
        if client_socket in clients:
            user = clients[client_socket]
            del clients[client_socket]
            leave_msg = f"[系統] {user} 離開了聊天室。"
            print(f"[*] {user} 已斷線。")
            broadcast(leave_msg)
        client_socket.close()


def start_server(host='127.0.0.1', port=9000):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 解決 TCP Port 被占用的 TIME_WAIT 問題
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server.bind((host, port))
        server.listen(5)
        print(f"[*] 伺服器啟動於 {host}:{port}，等待連線中...")
        
        while True:
            client_socket, addr = server.accept()
            # 建立多執行緒 (Threading) 處理每位客戶端
            client_thread = threading.Thread(target=handle_client, args=(client_socket, addr))
            client_thread.daemon = True
            client_thread.start()
            
    except KeyboardInterrupt:
        print("\n[*] 伺服器關閉中...")
    finally:
        server.close()

if __name__ == "__main__":
    start_server()