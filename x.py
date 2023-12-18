import telebot
import cv2
import numpy as np
import requests
import os

bot = telebot.TeleBot('6503263167:AAFLTBgytJpQ4FegGlUI2qGaHaHrXFL9rs8')

@bot.message_handler(content_types=['video'])
def handle_video(message):
    try:
        file_id = message.video.file_id
        file_info = bot.get_file(file_id)
        file_path = file_info.file_path

        # Download the video file
        downloaded_file = bot.download_file(file_path)
        with open('video.mp4', 'wb') as f:
            f.write(downloaded_file)

        # Read video frames
        cap = cv2.VideoCapture('video.mp4')
        frames = [cap.read()[1] for _ in range(int(cap.get(cv2.CAP_PROP_FRAME_COUNT)))]
        cap.release()

        # Extract frames with text
        text_frames = []
        for frame in frames:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                if w * h > 1000:
                    text_frames.append(frame[y:y+h, x:x+w])

        # Merge text frames
        frame_height, frame_width, _ = frames[0].shape
        merged_frame = np.zeros((frame_height, frame_width, 3), np.uint8)
        for frame in text_frames:
            merged_frame[:frame.shape[0], :frame.shape[1]] = frame

        # Validate merged_frame
        if not isinstance(merged_frame, np.ndarray) or merged_frame.ndim != 3 or merged_frame.shape[2] != 3 or merged_frame.dtype != np.uint8:
            raise ValueError("Invalid merged_frame format")

        # Save merged frame as an image
        cv2.imwrite('merged_frame.jpg', merged_frame)

        # Prepare image for OCR
        with open('merged_frame.jpg', 'rb') as f:
            files = {'image': f}

        # Set headers for OCR API
        headers = {
            'X-RapidAPI-Key': '60efa71f10msh430e82a841e2baap1390eejsnff1bda884297',
            'X-RapidAPI-Host': 'image-to-text9.p.rapidapi.com'
        }

        # Construct OCR API URL
        url = 'https://image-to-text9.p.rapidapi.com/ocr?url=' + file_path

        # Make OCR API request
        response = requests.get(url, headers=headers, files=files)
        text = response.text

        # Send OCR result as a message
        bot.send_message(message.chat.id, text)

    except Exception as e:
        bot.send_message(message.chat.id, f"An error occurred: {str(e)}")
    finally:
        # Cleanup: Delete the downloaded video and merged frame files
        os.remove('video.mp4')
        os.remove('merged_frame.jpg')

bot.polling()