import telebot
from telebot import types
import cv2
import numpy as np
import pytesseract
import re

# Create a Telegram bot
bot = telebot.TeleBot("6503263167:AAFLTBgytJpQ4FegGlUI2qGaHaHrXFL9rs8")

# Define the command handler for the bot
@bot.message_handler(commands=['start'])
def start(message):
    # Send a welcome message to the user
    bot.send_message(message.chat.id, "Hello! I am a bot that can read text from videos. Send me a video and I will send you the text that I find.")

# Define the message handler for the bot
@bot.message_handler(content_types=['video'])
def handle_video(message):
    try:
        # Download the video from Telegram
        file_info = bot.get_file(message.video.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        # Read the video using OpenCV
        cap = cv2.VideoCapture(downloaded_file)

        # Loop over the frames in the video
        while True:
            # Read the next frame
            ret, frame = cap.read()

            # If the frame is empty, break the loop
            if not ret:
                break

            # Convert the frame to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Perform OCR on the frame
            text = pytesseract.image_to_string(gray, lang='rus')

            # If there is text in the frame, send it to the user
            if text:
                bot.send_message(message.chat.id, text)

        # Release the video capture object
        cap.release()

    except Exception as e:
        # Send an error message to the user
        bot.send_message(message.chat.id, "An error occurred while processing the video. Please try again.")

# Start the bot
bot.polling()