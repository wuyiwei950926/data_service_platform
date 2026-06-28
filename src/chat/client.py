import socket
import threading
import sys
import getpass

def receive_messages(client_socket):
    """處理接收來自伺服器與其他使用者的訊息"""
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
            sys.stdout.write('\r' + ' ' * 50 + '\r') 
            print(message)
            print("輸入訊息: ", end="", flush=True)
        except Exception as e:
            print(f"\n[系統] 連線異常中斷。")
            client_socket.close()
            break

# 🛑 新增 auto_user 與 auto_pass 參數
def start_client(host='127.0.0.1', port=9000, auto_user=None, auto_pass=None):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((host, port))
    except Exception as e:
        print(f"[系統] 無法連線至伺服器: {e}")
        return

    try:
        # 1. 處理帳號輸入
        prompt_user = client.recv(1024).decode('utf-8')
        if auto_user:
            username = auto_user
            print(f"{prompt_user}{username} (Face ID 自動帶入)")
        else:
            username = input(prompt_user)
        client.send(username.encode('utf-8'))

        # 2. 處理密碼輸入
        prompt_pass = client.recv(1024).decode('utf-8')
        if auto_pass:
            password = auto_pass
            print(f"{prompt_pass}****** (生物辨識快速通關)")
        else:
            password = getpass.getpass(prompt_pass)
        client.send(password.encode('utf-8'))

        # 3. 接收結果
        result = client.recv(1024).decode('utf-8')
        print(result)

        if "錯誤" in result or "失敗" in result:
            client.close()
            return

        print("\n--- 開始聊天 (輸入 'exit' 離開) ---")
        receive_thread = threading.Thread(target=receive_messages, args=(client,))
        receive_thread.daemon = True
        receive_thread.start()

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
    # 🛑 判斷如果是從 Face ID 帶參數啟動的，就走自動登入
    if len(sys.argv) == 3:
        start_client(auto_user=sys.argv[1], auto_pass=sys.argv[2])
    else:
        start_client()