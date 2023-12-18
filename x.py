import telebot
import cv2
import numpy as np
import requests

bot = telebot.TeleBot('6503263167:AAFLTBgytJpQ4FegGlUI2qGaHaHrXFL9rs8')

@bot.message_handler(content_types=['video'])
def handle_video(message):
    try:
        file_id = message.video.file_id
        file_path = bot.get_file(file_id).file_path
        downloaded_file = bot.download_file(file_path)

        with open('video.mp4', 'wb') as f:
            f.write(downloaded_file)

        cap = cv2.VideoCapture('video.mp4')
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        frames = []
        for i in range(frame_count):
            ret, frame = cap.read()
            if ret:
                frames.append(frame)

        # Move the cap.release() statement here
        cap.release()

        text_frames = []
        for frame in frames:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                if w * h > 1000:
                    text_frames.append(frame[y:y+h, x:x+w])

        merged_frame = np.zeros((frame_height, frame_width, 3), np.uint8)
        for frame in text_frames:
            merged_frame[0:frame.shape[0], 0:frame.shape[1]] = frame

        cv2.imwrite('merged_frame.jpg', merged_frame)

        with open('merged_frame.jpg', 'rb') as f:
            files = {'image': f}

        headers = {
            'X-RapidAPI-Key': '60efa71f10msh430e82a841e2baap1390eejsnff1bda884297',
            'X-RapidAPI-Host': 'image-to-text9.p.rapidapi.com'
        }

        response = requests.request("GET", "https://image-to-text9.p.rapidapi.com/ocr?url=https://i.imgur.com/ZP0jV1H.png", headers=headers, files=files)

        text = response.text

        bot.send_message(message.chat.id, text)

    except Exception as e:
        bot.send_message(message.chat.id, f"An error occurred: {str(e)}")

bot.polling()