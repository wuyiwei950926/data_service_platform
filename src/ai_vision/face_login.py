import cv2
import sys
import os
import numpy as np
import time
import subprocess

# 確保路徑正確
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.database.db_manager import DatabaseManager

class FaceLoginSystem:
    def __init__(self):
        self.cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(self.cascade_path)
        self.db = DatabaseManager()
        
        # 建立 LBPH 人臉辨識模型
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.model_path = 'data/face_model.yml'
        
        # 若已經有訓練好的模型，就載入它
        if os.path.exists(self.model_path):
            self.recognizer.read(self.model_path)

    def get_user_info(self, identifier, search_by="username"):
        """透過帳號找 ID，或透過 ID 找帳號 (用於模型標籤對應)"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            if search_by == "username":
                cursor.execute("SELECT id FROM users WHERE username = ?", (identifier,))
                row = cursor.fetchone()
                return row['id'] if row else None
            else:
                cursor.execute("SELECT username FROM users WHERE id = ?", (identifier,))
                row = cursor.fetchone()
                return row['username'] if row else "Unknown"

    def register_face(self, username):
        """[Face ID 註冊階段] 收集人臉樣本並訓練模型"""
        user_id = self.get_user_info(username, search_by="username")
        if not user_id:
            print(f"[-] 錯誤：找不到帳號 '{username}'，請先在系統註冊帳號。")
            input("按 Enter 鍵結束...")
            return

        print(f"[*] 開始為 '{username}' 建立 Face ID...")
        print("[*] 🎥 請正對鏡頭，並稍微轉動頭部。系統將自動擷取 30 張臉部特徵樣本。")
        
        cap = cv2.VideoCapture(0)
        faces_data = []
        labels = []
        sample_count = 0

        while True:
            ret, frame = cap.read()
            if not ret: break
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

            for (x, y, w, h) in faces:
                sample_count += 1
                faces_data.append(gray[y:y+h, x:x+w])
                labels.append(user_id) 
                
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                cv2.putText(frame, f"Scanning: {sample_count}/30", (x, y-10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                
                cv2.imshow('Face ID Setup', frame)
                time.sleep(0.1) 

            cv2.imshow('Face ID Setup', frame)
            
            # 支援大小寫 'q' 退出
            key = cv2.waitKey(1) & 0xFF
            if key in [ord('q'), ord('Q')] or sample_count >= 30:
                break

        cap.release()
        cv2.destroyAllWindows()

        if sample_count >= 30:
            print("\n[*] 樣本擷取完畢，正在訓練 AI 辨識模型...")
            if os.path.exists(self.model_path):
                self.recognizer.update(faces_data, np.array(labels))
            else:
                self.recognizer.train(faces_data, np.array(labels))
            
            self.recognizer.write(self.model_path)
            print(f"[+] 🎉 {username} 的 Face ID 註冊成功！資料庫已更新。")
        else:
            print("[-] 樣本擷取數量不足，註冊中斷。")
        
        input("按 Enter 鍵關閉視窗...")

    def start_vision_login(self):
        """[Face ID 登入階段] 即時比對人臉並辨識身分"""
        if not os.path.exists(self.model_path):
            print("[-] 系統尚未建立任何 Face ID，請先進行註冊。")
            input("按 Enter 鍵結束...")
            return False

        print("[*] 啟動 AI 影像登入服務...")
        print("[*] 🎥 請看著鏡頭，綠框代表辨識成功。按下 'L' 進行登入，'Q' 離開。")
        
        cap = cv2.VideoCapture(0)
        
        while True:
            ret, frame = cap.read()
            if not ret: break
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.2, 5)

            recognized_name = "Unknown"
            
            for (x, y, w, h) in faces:
                id_, conf = self.recognizer.predict(gray[y:y+h, x:x+w])
                
                if conf < 80:
                    recognized_name = self.get_user_info(id_, search_by="id")
                    match_percent = round(100 - conf)
                    color = (0, 255, 0)
                    text = f"{recognized_name} ({match_percent}%)"
                else:
                    recognized_name = "Unknown"
                    color = (0, 0, 255)
                    text = "Unknown Face"

                cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                cv2.putText(frame, text, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

            cv2.putText(frame, "Press 'L' to Login | 'Q' to Quit", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.imshow('DataNova - AI Face Login', frame)

            # 監聽鍵盤按鍵 (支援大小寫 L 與 Q)
            key = cv2.waitKey(1) & 0xFF
            if key in [ord('q'), ord('Q')]:
                break
            elif key in [ord('l'), ord('L')]:
                if recognized_name != "Unknown":
                    print(f"\n[+] 影像分析成功！已比對到特徵。")
                    print(f"[+] 歡迎回來，{recognized_name}！Face ID 登入成功。")
                    
                    # 登入成功，先關閉鏡頭
                    cap.release()
                    cv2.destroyAllWindows()
            
                    # 啟動聊天室並傳遞通行證
                    print("[*] 正在為您轉接至 DataNova 智能聊天室...")
                    subprocess.Popen(['start', 'cmd', '/k', 'python', '-m', 'src.chat.client', str(recognized_name), 'FACEID_BYPASS'], shell=True)
            
                    # 結束這個函式
                    return recognized_name
                
                else:
                    # 如果按下 L，但臉部辨識是 Unknown 時的防呆機制
                    print("\n[-] 登入失敗：無法辨識此人臉，或未對準鏡頭。")

        # 這裡處理的是按下 'Q' 或發生意外退出迴圈時的收尾
        cap.release()
        cv2.destroyAllWindows()
        return None

if __name__ == "__main__":
    ai_system = FaceLoginSystem()
    
    if len(sys.argv) >= 3 and sys.argv[1] == 'register':
        ai_system.register_face(sys.argv[2])
    else:
        ai_system.start_vision_login()