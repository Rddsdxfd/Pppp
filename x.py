import telebot
from telebot import types
import cv2
import numpy as np
import pytesseract
import re
import tempfile
import os

bot = telebot.TeleBot("6503263167:AAFLTBgytJpQ4FegGlUI2qGaHaHrXFL9rs8")

# ... (other parts of your code)

@bot.message_handler(content_types=['video'])
def handle_video(message):
    try:
        file_info = bot.get_file(message.video.file_id)
        
        if message.video.file_size > 10 * 1024 * 1024:
            bot.send_message(message.chat.id, "The video is too large. Please send a video that is less than 10 MB.")
            return
        
        downloaded_file = bot.download_file(file_info.file_path)
        nparr = np.frombuffer(downloaded_file, np.uint8)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
            temp_file.write(nparr)
            temp_filename = temp_file.name

        cap = cv2.VideoCapture(temp_filename)
        extracted_text = []

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Preprocess the frame here, if necessary

            # Consider adding frame resizing if the frames are large
            # to speed up processing and decrease memory usage

            text = pytesseract.image_to_string(frame, lang='rus')  # Change to the correct language if not 'rus'
            if text.strip():  # Checks if text is non-empty and not just whitespace
                extracted_text.append(text.strip())

        cap.release()
        os.unlink(temp_filename)  # Delete the temporary file

        if not extracted_text:
            bot.send_message(message.chat.id, "No text was found in the video.")
        else:
            bot.send_message(message.chat.id, '\n'.join(extracted_text))
    except Exception as e:
        error_message = f"An error occurred while processing the video. Error details: {str(e)}"
        bot.send_message(message.chat.id, error_message)

# ... (rest of your code)

# Start bot polling
bot.polling(non_stop=True, interval=0)
