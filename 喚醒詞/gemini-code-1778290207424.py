import os
import time
import numpy as np
import pyaudio
import speech_recognition as sr
from edge_impulse_linux.audio import AudioImpulseRunner

# 1. 載入模型 (Windows 原生環境請使用下載的 .wasm 檔案)
model_file = "喚醒詞\edge-impulse-standalone.wasm" 

def perform_stt():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print(">>> 偵測到喚醒詞！請說出您的指令...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        try:
            # 設定超時以避免程式卡死
            audio_data = recognizer.listen(source, timeout=5, phrase_time_limit=5)
            text = recognizer.recognize_google(audio_data, language="zh-TW")
            print(f">>> 您說的是: {text}")
        except sr.UnknownValueError:
            print(">>> 無法辨識音訊內容")
        except Exception as e:
            print(f">>> STT 錯誤: {e}")

def main():
    # 使用 WASM Runner
    with AudioImpulseRunner(model_file) as runner:
        model_info = runner.init()
        print(f"模型已啟動: {model_info['project']['name']}")
        
        # 設定 Windows 音訊參數
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000,
                        input=True, frames_per_buffer=1600)

        print("正在監聽喚醒詞...")

        try:
            while True:
                # 讀取麥克風數據並轉換為模型需要的格式
                data = stream.read(1600, exception_on_overflow=False)
                audio_features = np.frombuffer(data, dtype=np.int16).tolist()
                
                res, _ = runner.classify(audio_features)
                
                if 'classification' in res['result']:
                    score = res['result']['classification'].get('nxp_wake', 0)
                    if score > 0.8:
                        print(f"喚醒詞匹配！ 信心值: {score:.2f}")
                        stream.stop_stream() # 暫停監聽以進行 STT
                        perform_stt()
                        stream.start_stream()
                        print("\n繼續監聽喚醒詞...")
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()

if __name__ == "__main__":
    main()