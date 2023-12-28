import telebot  
import tensorflow as tf
import numpy as np
import librosa
from sklearn.preprocessing import LabelEncoder
from telebot import types 

API_TOKEN = '6503263167:AAFLTBgytJpQ4FegGlUI2qGaHaHrXFL9rs8'
bot = telebot.TeleBot(API_TOKEN)

# Model definition
model = tf.keras.Sequential([
    tf.keras.layers.Dense(32),
    tf.keras.layers.Dense(32),
    tf.keras.layers.Dense(1, activation='softmax')])

# Data arrays
TRAIN_DATA = []
TRAIN_LABELS = []  

def preprocess_audio(audio_file):
    # MFCC extraction
    
    return mfccs, label  

TRAINING_MODE = False

@bot.message_handler(commands=['start'])
def start(message): 
    bot.reply_to(message, 'I understand "пальяниця", say it!')

@bot.message_handler(commands=['zsu']) 
def switch_training(message):
    global TRAINING_MODE
    TRAINING_MODE = not TRAINING_MODE
    text = "Switched to training mode" if TRAINING_MODE else "Evaluation mode"
    bot.reply_to(message, text)
    
@bot.message_handler(func=lambda m: True)  
def handle_message(message):
    if TRAINING_MODE:  
        # Add audio to dataset
    else:
        # Classify audio 

if __name__ == '__main__':
    
    # Load latest model
    # Bot polling
    
    while True:  
        if len(TRAIN_DATA)>1000:
            model.fit(TRAIN_DATA, TRAIN_LABELS)
            tf.saved_model.save(model, f'models/mdl_{time.time()}')
            
            TRAIN_DATA, TRAIN_LABELS = [], []
            
        time.sleep(3600)
