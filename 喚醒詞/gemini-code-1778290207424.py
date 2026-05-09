import numpy as np
import pyaudio
import speech_recognition as sr
from wasmtime import Engine, Store, Module, Instance, Memory

# --- 配置區 ---
WASM_PATH = "edge-impulse-standalone.wasm"
TARGET_LABELS = ["救命", "啊", "沒事", "取消"] # 您的模型標籤
THRESHOLD = 0.8
SAMPLING_RATE = 16000
CHUNK_SIZE = 1600 # 每次讀取 100ms 的音訊

def perform_stt():
    """ 觸發 STT 辨識 """
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("\n>>> [系統] 偵測到關鍵字！請說出您的指令...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        try:
            audio_data = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio_data, language="zh-TW")
            print(f">>> 辨識結果: {text}")
        except Exception as e:
            print(f">>> 辨識失敗: {e}")

class WASMInference:
    def __init__(self, wasm_path):
        # 1. 初始化 WASM 引擎
        self.engine = Engine()
        self.store = Store(self.engine)
        self.module = Module.from_file(self.engine, wasm_path)
        self.instance = Instance(self.store, self.module, [])
        
        # 2. 取得 WASM 導出的函數與記憶體
        self.exports = self.instance.exports(self.store)
        self.memory = self.exports["memory"]
        
        # 假設 Edge Impulse WASM 導出的核心函數名稱 (依版本可能略有不同)
        self.run_classifier = self.exports.get("run_classifier")
        
    def infer(self, audio_data):
        """ 將音訊餵入 WASM 進行推論 """
        # 這裡需要將音訊數據寫入 WASM 記憶體並執行模型
        # 注意：實際模型通常需要 DSP 處理 (MFCC/MFE)
        # 本腳本示範邏輯結構，具體 Offset 需視模型 Export 介面而定
        return {label: 0.0 for label in TARGET_LABELS}

def main():
    # 檢查 Python 架構是否為 64bit
    import platform
    if "64" not in platform.architecture()[0]:
        print("警告: 請確保使用 64 位元 Python 以相容 wasmtime")
    
    # 1. 初始化 WASM 模型
    try:
        model = WASMInference(WASM_PATH)
        print(f"成功載入模型: {WASM_PATH}")
    except Exception as e:
        print(f"模型載入失敗: {e}")
        return

    # 2. 開啟麥克風串流
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, 
                    channels=1, 
                    rate=SAMPLING_RATE, 
                    input=True, 
                    frames_per_buffer=CHUNK_SIZE)

    print("正在監聽喚醒詞... (Ctrl+C 停止)")
    
    try:
        while True:
            # 讀取音訊並轉換為模型需要的格式
            data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
            audio_np = np.frombuffer(data, dtype=np.int16).astype(np.float32)

            # 進行推論
            # 註：在方案一中，您必須手動處理 DSP 特徵提取
            results = model.infer(audio_np)
            
            # 檢查是否觸發
            for label in TARGET_LABELS:
                if results.get(label, 0) > THRESHOLD:
                    print(f"\n[觸發] 偵測到: {label}")
                    stream.stop_stream()
                    perform_stt()
                    stream.start_stream()
                    break
                    
    except KeyboardInterrupt:
        print("\n停止程式。")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

if __name__ == "__main__":
    main()