import telebot
from telebot import types
import cv2
import numpy as np
import pytesseract
import re
import tempfile
import os

# Configure pytesseract to work with Russian
# Presuming that 'rus' is the correct Tesseract language code for Russian
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

bot = telebot.TeleBot("6503263167:AAFLTBgytJpQ4FegGlUI2qGaHaHrXFL9rs8")

@bot.message_handler(content_types=['video'])
def handle_video(message):
    try:
        # ... (rest of your existing code for downloading and video handling remains unchanged) ...

        # New Step: Image preprocessing
        def preprocess_image(img):
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            _, thresh_img = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            return thresh_img

        # New Step: Post-processing improvements
        def clean_text(text):
            # Normalize hyphenated words at the end of lines
            text = re.sub(r'(\w)-\n(\w)', r'\1\2', text)
            # Insert additional regex replacements here
            return text

        # ... (rest of existing video capture loop) ...

        processed_text = []
        last_text = ""

        while cap.isOpened():
            # ... (reading frames remains unchanged) ...

            # Preprocessing step before OCR
            preprocessed_frame = preprocess_image(frame)

            # OCR on the preprocessed frame
            text = pytesseract.image_to_string(preprocessed_frame, lang='rus')

            # Post-processing on the extracted text
            clean = clean_text(text)
            if clean.strip() and clean.strip() != last_text:
                processed_text.append(clean.strip())
                last_text = clean.strip()

        # ... (closing the video and temporary files remains unchanged) ...
        
        # Send the cleaned and processed text to the user
        if not processed_text:
            bot.send_message(message.chat.id, "No text was found in the video.")
        else:
            bot.send_message(message.chat.id, '\n'.join(processed_text))
    
    except Exception as e:
        error_message = f"An error occurred while processing the video. Error details: {str(e)}"
        bot.send_message(message.chat.id, error_message)

bot.polling(non_stop=True, interval=0)
