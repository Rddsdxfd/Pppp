import telebot
import cv2
import numpy as np
import pytesseract
import tempfile
import os
import re

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
        last_text = ""
        subtitle_region = None  # This is the region where subtitles are expected

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Define the region of interest where subtitles are expected to be.
            # These values depend on the resolution and the position of the subtitles in the video.
            # (startY, startX, endY, endX)
            if subtitle_region is None:
                height, width, _ = frame.shape
                startY = int(height * 0.85)
                endY = int(height * 0.95)
                startX = int(width * 0.1)
                endX = int(width * 0.9)
                subtitle_region = (startY, endY, startX, endX)

            startY, endY, startX, endX = subtitle_region
            subtitle_frame = frame[startY:endY, startX:endX]

            # Preprocess the region for better readability:
            # Convert to grayscale
            gray = cv2.cvtColor(subtitle_frame, cv2.COLOR_BGR2GRAY)
            # Apply thresholding
            _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)

            # Use tesseract to do OCR on the preprocessed image
            text = pytesseract.image_to_string(thresh, lang='eng')  # You can change the lang parameter

            if text.strip() and text.strip() != last_text:  # Checks for non-empty, non-repeated text
                filtered_text = re.sub(r'\s+', ' ', text.strip())  # Filter out extra whitespace
                extracted_text.append(filtered_text)
                last_text = filtered_text

        cap.release()
        os.unlink(temp_filename)  # Delete the temporary file

        if not extracted_text:
            bot.send_message(message.chat.id, "No subtitles were found in the video.")
        else:
            bot.send_message(message.chat.id, '\n\n'.join(set(extracted_text)))  # Using set to remove duplicates

    except Exception as e:
        error_message = f"An error occurred while processing the video: {str(e)}"
        bot.send_message(message.chat.id, error_message)

# ... (rest of your code)

# Start bot polling
bot.polling(non_stop=True, interval=0)
