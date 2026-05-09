import os
import time
from edge_impulse_linux.audio import AudioImpulseRunner
import speech_recognition as sr

# # 安裝系統底層套件
# sudo apt update
# sudo apt install libasound2-dev python3-pyaudio flac -y

# # 安裝 Python 套件
# pip install edge-impulse-linux speech_recognition

# 如果沒有eim
# edge-impulse-linux-runner --download my_model.eim

# 1. 載入模型路徑
model_file = "長者喚醒詞-runner-linux-aarch64-ethos-v1-impulse-#1.eim"

# 2. 定義語音轉文字函數 (STT)
def perform_stt():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print(">>> 偵測到喚醒詞！請說出您的指令...")
        # 環境降噪處理
        recognizer.adjust_for_ambient_noise(source, duration=1)
        audio_data = recognizer.listen(source)
    
    try:
        # 使用 Google 辨識引擎 (需聯網)
        text = recognizer.recognize_google(audio_data, language="zh-TW")
        print(f">>> 您說的是: {text}")
    except sr.UnknownValueError:
        print(">>> 無法辨識音訊內容")
    except sr.RequestError as e:
        print(f">>> 無法從辨識服務取得結果: {e}")

# 3. 主循環：喚醒詞偵測 (Edge Impulse)
def main():
    with AudioImpulseRunner(model_file) as runner:
        model_info = runner.init()
        print(f"模型已啟動，正在監聽喚醒詞...")

        # 這裡會持續監聽流式音訊
        for res, audio in runner.classifier():
            # 假設您的喚醒詞標籤是 'nxp_wake'
            score = res['result']['classification']['nxp_wake']
            
            if score > 0.8: # 信心值門檻
                print(f"喚醒詞匹配！ 信心值: {score:.2f}")
                # 暫停偵測，進入 STT 階段
                perform_stt()
                # 處理完後繼續偵測喚醒詞
                print("\n繼續監聽喚醒詞...")

if __name__ == "__main__":
    main()