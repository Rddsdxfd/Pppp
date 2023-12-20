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
        extracted_text = set()  # Use a set to store unique text fragments
        frame_count = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Process every 15th frame
            if frame_count % 15 == 0:
                # Preprocess the frame
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
                edges = cv2.Canny(thresh, 100, 200)

                # Consider adding frame resizing if the frames are large
                # to speed up processing and decrease memory usage

                text = pytesseract.image_to_string(edges, lang='rus')  # Change to the correct language if not 'rus'
                cleaned_text = text.strip()

                if cleaned_text:  # Checks if text is non-empty and not just whitespace
                    # Check if the cleaned text is not already in the set
                    if cleaned_text not in extracted_text:
                        extracted_text.add(cleaned_text)

            frame_count += 1

        cap.release()
        os.unlink(temp_filename)  # Delete the temporary file

        if not extracted_text:
            bot.send_message(message.chat.id, "No unique text was found in the video.")
        else:
            # Post-process the extracted text
            result_text = ' '.join(extracted_text)
            result_text = re.sub(r'[^а-яА-ЯёЁa-zA-Z0-9\s]', '', result_text)  # Remove non-alphanumeric characters
            result_text = re.sub(r'\s+', ' ', result_text)  # Remove extra whitespace

            bot.send_message(message.chat.id, result_text)
    except Exception as e:
        error_message = f"An error occurred while processing the video. Error details: {str(e)}"
        bot.send_message(message.chat.id, error_message)

# ... (rest of your code)

# Start bot polling
bot.polling(non_stop=True, interval=0)
                                         
