import os
import sys

def print_menu():
    print("="*50)
    print(" 🚀 DataNova Tech - 系統控制台 (單一進入點) ")
    print("="*50)
    print(" [1] 執行 M3+M4: 啟動爬蟲並清洗資料寫入資料庫")
    print(" [2] 執行 M5: 啟動 Web 服務與 API (包含前端整合面板)")
    print(" [3] 執行 M6: 啟動 Socket 即時客服伺服器")
    print(" [4] 執行 M7: 啟動 AI 影像人臉登入系統")
    print(" [Q] 離開系統")
    print("="*50)

def main():
    while True:
        print_menu()
        choice = input("請輸入欲啟動的模組代碼 (1-4): ").strip().upper()

        if choice == '1':
            print("\n[*] 正在啟動資料爬蟲與清洗管線...")
            os.system(f"{sys.executable} -m src.crawler.scraper")
            os.system(f"{sys.executable} -m src.cleaner.data_cleaner")
            print("[+] 資料管線執行完畢。\n")
        
        elif choice == '2':
            print("\n[*] 正在啟動 Web 服務... 請開啟瀏覽器前往 http://127.0.0.1:5000")
            print("[*] 按 Ctrl+C 可關閉伺服器。")
            os.system(f"{sys.executable} -m src.api.app")
            
        elif choice == '3':
            print("\n[*] 正在啟動即時客服伺服器...")
            print("[*] 請開啟新的終端機，執行 python -m src.chat.client 來連線測試。")
            print("[*] 按 Ctrl+C 可關閉伺服器。")
            os.system(f"{sys.executable} -m src.chat.server")
            
        elif choice == '4':
            print("\n[*] 正在啟動 AI 影像登入服務...")
            os.system(f"{sys.executable} -m src.ai_vision.face_login")
            
        elif choice == 'Q':
            print("感謝使用 DataNova 系統，再見！")
            break
        else:
            print("[-] 無效的輸入，請重新選擇。")

if __name__ == "__main__":
    main()