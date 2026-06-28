import socket
import threading
import sys
import getpass  # 🛑 引入專門用來隱藏終端機密碼的模組

def receive_messages(client_socket):
    """處理接收來自伺服器與其他使用者的訊息"""
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
            
            # 清除目前這一行的輸入提示，印出訊息後再補上新的提示
            sys.stdout.write('\r' + ' ' * 50 + '\r') 
            print(message)
            print("輸入訊息: ", end="", flush=True)
            
        except Exception as e:
            print(f"\n[系統] 連線異常中斷。")
            client_socket.close()
            break

def start_client(host='127.0.0.1', port=9000):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((host, port))
    except Exception as e:
        print(f"[系統] 無法連線至伺服器: {e}")
        return

    try:
        # --- 登入驗證流程 ---
        # 1. 接收「請輸入帳號」並回傳
        prompt_user = client.recv(1024).decode('utf-8')
        username = input(prompt_user)
        client.send(username.encode('utf-8'))

        # 2. 接收「請輸入密碼」
        prompt_pass = client.recv(1024).decode('utf-8')
        
        # 🛑 【關鍵升級】使用 getpass 取代 input，打字時螢幕上完全不會顯示字元！
        password = getpass.getpass(prompt_pass)
        client.send(password.encode('utf-8'))

        # 3. 接收登入結果
        result = client.recv(1024).decode('utf-8')
        print(result)

        # 如果被伺服器拒絕，就自動關閉程式
        if "錯誤" in result:
            client.close()
            return

        print("\n--- 開始聊天 (輸入 'exit' 離開) ---")

        # 啟動背景執行緒負責接收廣播訊息
        receive_thread = threading.Thread(target=receive_messages, args=(client,))
        receive_thread.daemon = True
        receive_thread.start()

        # 主執行緒負責發送訊息
        while True:
            message = input("輸入訊息: ")
            if message.lower() == 'exit':
                break
            if message.strip():
                client.send(message.encode('utf-8'))

    except KeyboardInterrupt:
        print("\n[系統] 手動離開聊天室。")
    finally:
        client.close()

if __name__ == "__main__":
    start_client()