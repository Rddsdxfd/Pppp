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

        # Convert the downloaded file to a NumPy array
        nparr = np.frombuffer(downloaded_file, np.uint8)

        # Create a VideoCapture object from the decoded array
        cap = cv2.VideoCapture(cv2.imdecode(nparr, cv2.IMREAD_COLOR))

        # Initialize an empty list to store the extracted text
        extracted_text = []

        # Loop over the frames in the video
        while cap.isOpened():
            # Read the next frame
            ret, frame = cap.read()

            # If the frame is empty, break the loop
            if not ret:
                break

            # Convert the frame to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Apply thresholding to the grayscale image
            thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

            # Perform connected component analysis
            labels = cv2.connectedComponentsWithStats(thresh, connectivity=8)[1]

            # Loop over the connected components
            for label in np.unique(labels)[1:]:
                # Get the bounding box of the connected component
                x, y, w, h = cv2.boundingRect(labels == label)

                # Crop the connected component from the thresholded image
                cropped_thresh = thresh[y:y+h, x:x+w]

                # Perform OCR on the cropped thresholded image
                text = pytesseract.image_to_string(cropped_thresh, lang='rus')

                # If text is detected, add it to the list
                if text:
                    extracted_text.append(text)

        # Release the video capture object
        cap.release()

        # Send the extracted text to the user
        bot.send_message(message.chat.id, '\n'.join(extracted_text))

    except Exception as e:
        # Send a detailed error message with the exception information
        error_message = f"An error occurred while processing the video. Error details: {str(e)}"
        bot.send_message(message.chat.id, error_message)

# Start the bot
bot.polling()
