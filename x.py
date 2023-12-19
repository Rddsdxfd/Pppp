import telebot
from telebot import types
import cv2
import numpy as np
import pytesseract
import re

# Create a Telebot object
bot = telebot.TeleBot("6503263167:AAFLTBgytJpQ4FegGlUI2qGaHaHrXFL9rs8")

# Define the command handler for '/start'
@bot.message_handler(commands=['start'])
def start(message):
    # Send a welcome message to the user
    bot.send_message(message.chat.id, "Hello! I am a bot that can read text from videos. Send me a video and I will highlight the text and send it to you.")

# Define the message handler for video messages
@bot.message_handler(content_types=['video'])
def handle_video(message):
    try:
        # Download the video file
        file_info = bot.get_file(message.video.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        # Check if the video is too large
        if file_info.file_size > 10 * 1024 * 1024:
            bot.send_message(message.chat.id, "The video is too large. Please send a video that is less than 10 MB.")
            return

        # Read the video file
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

            # Apply thresholding to the grayscale image
            thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

            # Perform OCR on the thresholded image
            text = pytesseract.image_to_string(thresh, lang='eng')

            # If text is detected, highlight it and send it to the user
            if text:
                # Highlight the text in the frame
                frame = cv2.putText(frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                # Send the highlighted frame to the user
                bot.send_video(message.chat.id, frame)
    except Exception as e:
        # Handle any errors that may occur
        bot.send_message(message.chat.id, "An error occurred while processing the video. Please try again.")

# Start the bot
bot.polling()