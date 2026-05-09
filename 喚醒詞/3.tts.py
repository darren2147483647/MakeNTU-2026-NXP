from gtts import gTTS
import os

tts = gTTS(text='hello', lang='en')
tts.save('hello.mp3')

os.system('play hello.mp3 > /dev/null 2>&1')
