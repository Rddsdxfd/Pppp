import telebot
from telebot import types
import cv2
import numpy as np
import pytesseract
import re

bot = telebot.TeleBot("6503263167:AAFLTBgytJpQ4FegGlUI2qGaHaHrXFL9rs8")

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Hello! I am a bot that can read text from videos. Send me a video and I will highlight the text and send it to you.")

@bot.message_handler(content_types=['video'])
def handle_video(message):
    try:
        file_info = bot.get_file(message.video.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        if file_info.file_size > 10 * 1024 * 1024:
            bot.send_message(message.chat.id, "The video is too large. Please send a video that is less than 10 MB.")
            return

        nparr = np.frombuffer(downloaded_file, np.uint8)

        cap = cv2.VideoCapture(cv2.imdecode(nparr, cv2.IMREAD_COLOR))

        extracted_text = []

        while cap.isOpened():
            ret, frame = cap.read()

            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

            labels = cv2.connectedComponentsWithStats(thresh, connectivity=4)[1]

            for label in np.unique(labels)[1:]:
                x, y, w, h = cv2.boundingRect(labels == label)

                cropped_thresh = thresh[y:y+h, x:x+w]

                text = pytesseract.image_to_string(cropped_thresh, lang='rus')

                if text:
                    extracted_text.append(text)

        cap.release()

        if not extracted_text:
            bot.send_message(message.chat.id, "No text was found in the video.")
        else:
            bot.send_message(message.chat.id, '\n'.join(extracted_text))

    except Exception as e:
        error_message = f"An error occurred while processing the video. Error details: {str(e)}"
        bot.send_message(message.chat.id, error_message)

bot.polling()
