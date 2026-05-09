
import idna
print(idna.__file__)
import asyncio
import edge_tts
import os
import random
from pydub import AudioSegment

# python -m pip install --upgrade --force-reinstall idna
# conda install -c conda-forge ffmpeg -y
# pip install edge-tts pydub
# python -c "import idna; import pydub; import edge_tts; print('✅ 所有模組載入成功！')"

# --- 設定區 ---
# 你的四個喚醒詞
TARGET_WORDS = ["沒事", "取消", "救命", "啊"] 
UNKNOWN_WORDS = ["你好", "今天天氣", "吃飯", "打開", "謝謝", "嘿", "喂"]
VOICES = [
    "zh-TW-HsiaoChenNeural", "zh-TW-YunJheNeural", "zh-TW-HsiaoYuNeural",
    "zh-CN-XiaoxiaoNeural", "zh-CN-YunxiNeural"
]

OUTPUT_DIR = "ei_dataset_multi"
SAMPLES_PER_WORD = 15  # 每個聲音生成的變體數量 (15*5聲=75條/每詞)

async def generate_speech(text, label, filename, voice):
    rate = f"{random.randint(-20, 20):+d}%"
    pitch = f"{random.randint(-10, 10):+d}Hz"
    
    communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    temp_file = f"temp_{random.randint(0,999)}.mp3"
    await communicate.save(temp_file)
    
    # 轉換格式 (16000Hz, Mono, 16-bit WAV)
    audio = AudioSegment.from_mp3(temp_file)
    audio = audio.set_frame_rate(16000).set_channels(1)
    
    # 統一長度為 1000ms (1秒)
    if len(audio) > 1000:
        audio = audio[:1000]
    else:
        # 對於像「啊」這種短音，隨機放置在 1 秒內的某個位置，增加模型魯棒性
        silence_total = 1000 - len(audio)
        before = random.randint(0, silence_total)
        after = silence_total - before
        audio = AudioSegment.silent(duration=before) + audio + AudioSegment.silent(duration=after)
        
    audio.export(f"{OUTPUT_DIR}/{label}/{filename}.wav", format="wav")
    if os.path.exists(temp_file):
        os.remove(temp_file)

async def main():
    print(f"🚀 開始生成多標籤語音資料集...")
    
    # 1. 生成四個目標喚醒詞
    for word in TARGET_WORDS:
        os.makedirs(f"{OUTPUT_DIR}/{word}", exist_ok=True)
        count = 0
        for voice in VOICES:
            for i in range(SAMPLES_PER_WORD):
                await generate_speech(word, word, f"{word}_{voice}_{i}", voice)
                count += 1
        print(f"✅ 已完成標籤 [{word}]: {count} 個樣本")

    # 2. 生成無關詞 (Unknown)
    os.makedirs(f"{OUTPUT_DIR}/unknown", exist_ok=True)
    count = 0
    for word in UNKNOWN_WORDS:
        for voice in VOICES:
            await generate_speech(word, "unknown", f"unk_{word}_{voice}", voice)
            count += 1
    print(f"✅ 已完成標籤 [unknown]: {count} 個樣本")
    
    print(f"\n🎉 完成！資料夾: {os.path.abspath(OUTPUT_DIR)}")

if __name__ == "__main__":
    asyncio.run(main())