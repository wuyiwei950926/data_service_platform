import requests
import json
import time

# 設定你 Flask 伺服器的網址
BASE_URL = "http://127.0.0.1:5000/api/data"

def run_api_tests():
    print("=== 🚀 開始測試 DataNova Tech API 服務 ===")

    # --- 測試 1: POST 新增資料 ---
    print("\n[測試 1] POST - 新增一筆測試資料...")
    test_payload = {
        "raw_id": None,
        "clean_content": "這是一筆由測試腳本自動寫入的乾淨財報數據：Revenue 500m",
        "category": "API_Auto_Test"
    }
    
    response = requests.post(BASE_URL, json=test_payload)
    print(f"狀態碼: {response.status_code}")
    print(f"回應內容: {response.json()}")
    
    # 抓出剛剛新增的資料 ID，留給後面的刪除測試使用
    inserted_id = response.json().get("inserted_id")

    # --- 測試 2: GET 查詢資料 ---
    print("\n[測試 2] GET - 查詢剛剛新增的資料 (篩選 category=API_Auto_Test)...")
    time.sleep(1) # 暫停 1 秒，模擬真實呼叫情境
    
    # 利用 params 傳遞查詢條件
    response = requests.get(BASE_URL, params={"category": "API_Auto_Test"})
    print(f"狀態碼: {response.status_code}")
    # 將回傳的 JSON 格式化印出，方便閱讀
    print(f"回應內容:\n{json.dumps(response.json(), indent=2, ensure_ascii=False)}")

    # --- 測試 3: DELETE 刪除資料 ---
    if inserted_id:
        print(f"\n[測試 3] DELETE - 刪除剛剛新增的資料 (ID: {inserted_id})...")
        delete_url = f"{BASE_URL}/{inserted_id}"
        
        response = requests.delete(delete_url)
        print(f"狀態碼: {response.status_code}")
        print(f"回應內容: {response.json()}")
    else:
        print("\n[!] 略過 DELETE 測試，因為 POST 未成功取得 ID。")

    print("\n=== ✨ API 測試流程結束 ===")

if __name__ == "__main__":
    try:
        run_api_tests()
    except requests.exceptions.ConnectionError:
        print("\n[-] 連線失敗！請確認你的 Flask 伺服器 (app.py) 已經在另一個終端機啟動，且運行在 port 5000。")