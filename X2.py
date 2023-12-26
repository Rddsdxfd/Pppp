import telebot 
import requests
import tempfile
from moviepy.editor import VideoFileClip
import os

API_KEY = "e2202adb69a843dc84e20792f7b2f7e2" 

bot = telebot.TeleBot("6503263167:AAFLTBgytJpQ4FegGlUI2qGaHaHrXFL9rs8")

@bot.message_handler(content_types=['video']) 
def handle_video(message):

    try:
        file_info = bot.get_file(message.video.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        with tempfile.NamedTemporaryFile(suffix='.mp4') as video_file:
            video_file.write(downloaded_file)
    
            clip = VideoFileClip(video_file.name)
            audio = clip.audio
            audio.write_audiofile("audio.wav")

        upload_response = upload_audio("audio.wav")
transcript_id = upload_response["upload"]["id"] 

poller = Poller(API_KEY, transcript_id)
# rest of code...
        poller = Poller(API_KEY, transcript_id)
        transcript = poller.poll_for_transcription()
        
        text = transcript['text']
        text_chunks = chunk_text(text) 

        first_msg = None
        for chunk in text_chunks:
            if not first_msg:
               first_msg = bot.send_message(message.chat.id, chunk) 
            else:
               bot.send_message(message.chat.id, chunk, reply_to_message_id=first_msg.message_id)
       
    finally:
        os.remove("audio.wav")
        
# Helper functions        
def upload_audio(filename):
   with open(filename, 'rb') as fin:
      file_data = fin.read()

   url = "https://api.assemblyai.com/v2/upload"
   headers = {'authorization': API_KEY} 
   response = requests.post(url, headers=headers, data=file_data)
   return response.json()

def chunk_text(text, max_chars=3500):
   return [text[i:i+max_chars] for i in range(0, len(text), max_chars)] 
   
# AssemblyAI poller class   
class Poller:
    def __init__(self, api_key, transcript_id):
        self.api_key = api_key
        self.transcript_id = transcript_id
        self.polling_interval = 30
        self.status = ""

    def poll_for_transcription(self):
       url = f"https://api.assemblyai.com/v2/transcript/{self.transcript_id}"
       headers = {'authorization': self.api_key}
       response = requests.get(url, headers=headers).json()
       self.status = response['status']

       while self.status != 'completed':
          sleep(self.polling_interval)
          response = requests.get(url, headers=headers).json() 
          self.status = response['status']

       return response
       
bot.polling()
