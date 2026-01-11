import telebot
from google import genai
from google.genai import types
from config import TELEGRAM_TOKEN, GEMINI_API_KEY
import os
import io
import time
from PIL import Image
from gtts import gTTS

# Configure Gemini Client
client = genai.Client(api_key=GEMINI_API_KEY)

# Initialize Bot
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Dictionary to store chat sessions
# Format: {chat_id: chat_object}
chat_sessions = {}

def get_chat_session(chat_id):
    if chat_id not in chat_sessions:
        # Create a new chat session using the client
        chat_sessions[chat_id] = client.chats.create(model="gemini-2.0-flash")
    return chat_sessions[chat_id]

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Это бот на базе Gemini AI, можешь отправить ему текст/видео и он ответит тебе что на нем, также ты можешь спросить у него любой вопрос и он даст тебе ответ, еще есть функция превращения текста в голос :)" )

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        # Get the highest resolution photo
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        image = Image.open(io.BytesIO(downloaded_file))
        
        # New SDK supports passing images directly in many cases, or we can use PIL image
        prompt = message.caption if message.caption else "Опиши это изображение."
        
        # Use models.generate_content for single turn with image + text
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[prompt, image]
        )
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, f"Ошибка при обработке фото: {e}")

@bot.message_handler(content_types=['video'])
def handle_video(message):
    temp_filename = ""
    try:
        reply = bot.reply_to(message, "Загружаю видео на сервер...")
        
        file_info = bot.get_file(message.video.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        # Save temp file
        temp_filename = f"video_{message.chat.id}.mp4"
        with open(temp_filename, 'wb') as new_file:
            new_file.write(downloaded_file)
            
        bot.edit_message_text("Отправляю видео в Gemini...", chat_id=message.chat.id, message_id=reply.message_id)
        
        # Upload file using new SDK
        video_file = client.files.upload(file=temp_filename)
        
        # Wait for processing
        while video_file.state == "PROCESSING":
            time.sleep(2)
            video_file = client.files.get(name=video_file.name)
            
        if video_file.state == "FAILED":
            bot.edit_message_text("Не удалось обработать видео.", chat_id=message.chat.id, message_id=reply.message_id)
            if os.path.exists(temp_filename):
                os.remove(temp_filename)
            return

        bot.edit_message_text("Видео обработано. Генерирую ответ...", chat_id=message.chat.id, message_id=reply.message_id)

        prompt = message.caption if message.caption else "Describe this video."
        
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[prompt, video_file]
        )
        bot.reply_to(message, response.text)
        
    except Exception as e:
        bot.reply_to(message, f"Ошибка при обработке видео: {e}")
    finally:
        if temp_filename and os.path.exists(temp_filename):
            os.remove(temp_filename)

@bot.message_handler(commands=['tts', 'voice'])
def handle_tts(message):
    text = message.text.replace('/tts', '').replace('/voice', '').strip()
    if not text:
        if message.reply_to_message and message.reply_to_message.text:
            text = message.reply_to_message.text
        else:
            bot.reply_to(message, "Пожалуйста, укажите текст или ответьте на сообщение (реплаем), которое нужно озвучить. Пример: /tts Привет")
            return

    try:
        reply = bot.reply_to(message, "Создаю голосовое сообщение...")
        tts = gTTS(text, lang='ru')
        filename = f"voice_{message.chat.id}.mp3"
        tts.save(filename)
        
        with open(filename, 'rb') as audio:
            bot.send_audio(message.chat.id, audio, title=f"Voice for {message.chat.first_name}")
        
        os.remove(filename)
        bot.delete_message(message.chat.id, reply.message_id)
    except Exception as e:
        bot.reply_to(message, f"Ошибка озвучки: {e}")


@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_text(message):
    try:
        chat_session = get_chat_session(message.chat.id)
        # In new SDK, chat.send_message is the same
        response = chat_session.send_message(message.text)
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка: {e}")

if __name__ == '__main__':
    print("Bot is running...")
    bot.polling(none_stop=True)
