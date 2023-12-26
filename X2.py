import telebot
from telebot import types
from moviepy.editor import VideoFileClip
import speech_recognition as sr
import tempfile
import os

bot = telebot.TeleBot("6503263167:AAFLTBgytJpQ4FegGlUI2qGaHaHrXFL9rs8")

@bot.message_handler(content_types=['video'])
def handle_video(message):
    try:
        file_info = bot.get_file(message.video.file_id)
        
        downloaded_file = bot.download_file(file_info.file_path)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_video_file, \
             tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_audio_file:
            temp_video_file.write(downloaded_file)
            temp_video_filename = temp_video_file.name
            temp_audio_filename = temp_audio_file.name

        # Extract audio from video
        video_clip = VideoFileClip(temp_video_filename)
        audio_clip = video_clip.audio
        audio_clip.write_audiofile(temp_audio_filename)

        # Recognize audio
        recognizer = sr.Recognizer()
        with sr.AudioFile(temp_audio_filename) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)
        
        # Split text into chunks to avoid long message errors
        text_chunks = [text[i:i+3500] for i in range(0, len(text), 3500)]
        
        for chunk in text_chunks:
            bot.reply_to(message, chunk)

    except Exception as e:
        bot.reply_to(message, f"An error occurred: {str(e)}")

    finally:
        # Cleanup temporary files
        for temp_file in [temp_video_filename, temp_audio_filename]:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
                
# Rest of bot code...

bot.polling()
