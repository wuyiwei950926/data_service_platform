import socket
import threading
import sys
import os

# 讓 Python 找得到 AI Vision 模組
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.ai_vision.face_login import FaceLoginSystem

def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                print("\n[系統] 與伺服器的連線已中斷。")
                client_socket.close()
                break
            print(message)
        except Exception as e:
            print(f"\n[系統] 發生錯誤: {e}")
            client_socket.close()
            break

def start_client(host='127.0.0.1', port=9000, use_faceid=False):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((host, port))
    except ConnectionRefusedError:
        print("[-] 無法連線至伺服器，請確認伺服器 (server.py) 是否已啟動。")
        return

    # --- 登入流程 ---
    print(client.recv(1024).decode('utf-8'), end="") # 接收 "請輸入帳號:"
    
    if use_faceid:
        print("\n[*] 正在啟動 Face ID 系統...")
        ai_system = FaceLoginSystem()
        # 呼叫 M7 開啟鏡頭，並取得辨識成功的帳號
        username = ai_system.start_vision_login()
        
        if not username:
            print("[-] Face ID 登入取消或失敗，連線中斷。")
            client.close()
            return
            
        # 自動幫使用者輸入帳號
        print(f"{username} (已透過 Face ID 自動帶入)")
        client.send(username.encode('utf-8'))
        
        print(client.recv(1024).decode('utf-8'), end="") # 接收 "請輸入密碼:"
        print("******** (Face ID 快速通關授權)")
        # 發送 Face ID 專用憑證給伺服器
        client.send("FACEID_VERIFIED_TOKEN".encode('utf-8'))
        
    else:
        # 傳統手動輸入模式
        username = input()
        client.send(username.encode('utf-8'))
        print(client.recv(1024).decode('utf-8'), end="")
        password = input()
        client.send(password.encode('utf-8'))

    # 接收登入結果
    login_result = client.recv(1024).decode('utf-8')
    print(login_result)
    
    if "[錯誤]" in login_result:
        client.close()
        return

    # --- 聊天流程 ---
    receive_thread = threading.Thread(target=receive_messages, args=(client,))
    receive_thread.daemon = True
    receive_thread.start()

    print("\n--- 開始聊天 (輸入 'exit' 離開) ---")
    while True:
        try:
            message = input()
            if message.lower() == 'exit':
                client.close()
                sys.exit()
            client.send(message.encode('utf-8'))
        except KeyboardInterrupt:
            client.close()
            sys.exit()

if __name__ == "__main__":
    # 若指令後面加上 faceid，就啟動人臉辨識登入模式
    use_faceid = len(sys.argv) > 1 and sys.argv[1] == "faceid"
    start_client(use_faceid=use_faceid)