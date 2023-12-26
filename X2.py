import telebot
import requests
import tempfile
from moviepy.editor import VideoFileClip 
import time
import os

ASSEMBLYAI_API_KEY = "e2202adb69a843dc84e20792f7b2f7e2"
TELEGRAM_BOT_TOKEN = "6503263167:AAFLTBgytJpQ4FegGlUI2qGaHaHrXFL9rs8"

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

@bot.message_handler(content_types=['video'])
def handle_video(message):
    try:
        file_info = bot.get_file(message.video.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        with tempfile.NamedTemporaryFile(suffix='.mp4') as temp_video:
            temp_video.write(downloaded_file)
      
            video = VideoFileClip(temp_video.name)
            audio = video.audio
            audio.write_audiofile("video.wav")

        upload_response = upload_audio("video.wav")
        transcript_id = upload_response["upload"]["id"]

        poller = TranscriptPoller(ASSEMBLYAI_API_KEY, transcript_id)
        transcript = poller.poll_for_completion()
        
        text = transcript["text"]
        chunks = chunk_text(text)

        first_msg = None
        for chunk in chunks:
            if not first_msg:
                first_msg = bot.send_message(message.chat.id, chunk)  
            else:
                bot.send_message(message.chat.id, chunk, reply_to_message_id=first_msg.message_id)

    finally:
        os.remove("video.wav")
        
def upload_audio(filename):
    with open(filename, 'rb') as f:
        file_data = f.read()

    url = "https://api.assemblyai.com/v2/upload"
    headers = {
        "authorization": ASSEMBLYAI_API_KEY,
    }
    response = requests.post(url, headers=headers, data=file_data)
    return response.json()

def chunk_text(text, max_chars=3500):
    return [text[i:i+max_chars] for i in range(0, len(text), max_chars)]

class TranscriptPoller:
    def __init__(self, api_key, transcript_id):
        self.api_key = api_key
        self.transcript_id = transcript_id
        self.polling_interval = 30

    def poll_for_completion(self):
        while True:
            url = f"https://api.assemblyai.com/v2/transcript/{self.transcript_id}"
            headers = {
                "authorization": self.api_key,
            }
            response = requests.get(url, headers=headers).json() 
            status = response["status"]
            
            if status == "completed":
                return response
                
            time.sleep(self.polling_interval)
            
bot.polling()
