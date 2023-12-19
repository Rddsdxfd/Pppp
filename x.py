import telebot
import cv2
import pytesseract
import numpy as np

# Create a Telegram bot
bot = telebot.TeleBot('6503263167:AAFLTBgytJpQ4FegGlUI2qGaHaHrXFL9rs8')

# Define the function to split the video into pictures
def split_video(video_path, output_path):
    cap = cv2.VideoCapture(video_path)
    count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        cv2.imwrite(f'{output_path}/frame{count}.jpg', frame)
        count += 1
    cap.release()

# Define the function to detect text in an image
def detect_text(image_path):
    image = cv2.imread(image_path)
    text = pytesseract.image_to_string(image, lang='rus')
    return text

# Define the function to merge the pictures into one
def merge_pictures(images_path, output_path):
    images = []
    for image_path in images_path:
        image = cv2.imread(image_path)
        images.append(image)
    merged_image = np.concatenate(images, axis=1)
    cv2.imwrite(output_path, merged_image)

# Define the function to send the picture to the library
def send_picture_to_library(image_path):
    # Here you should implement the code to send the picture to the library
    # and get the text from the library
    text = 'Text from the library'
    return text

# Define the function to handle the Telegram bot commands
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Hello! Send me a video and I will extract the text from it.')

@bot.message_handler(content_types=['video'])
def handle_video(message):
    # Get the video file from the message
    video_file_id = message.video.file_id
    video_file = bot.get_file(video_file_id)
    video_file_path = f'videos/{video_file.file_path}'
    
    # Download the video file
    bot.download_file(video_file_path, video_file.file_path)
    
    # Split the video into pictures
    output_path = f'frames/{message.chat.id}'
    split_video(video_file_path, output_path)
    
    # Detect text in each picture
    images_path = [f'{output_path}/frame{i}.jpg' for i in range(10)]  # Here you can specify the number of pictures to process
    texts = []
    for image_path in images_path:
        text = detect_text(image_path)
        texts.append(text)
    
    # Merge the pictures into one
    merged_image_path = f'merged_images/{message.chat.id}.jpg'
    merge_pictures(images_path, merged_image_path)
    
    # Send the merged picture to the library
    text = send_picture_to_library(merged_image_path)
    
    # Send the text to the user
    bot.send_message(message.chat.id, text)

# Start the Telegram bot
bot.polling()