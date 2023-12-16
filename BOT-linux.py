import os
import time
import telebot
from googlesearch import search
from telebot import types
import platform
import logging
import requests
import qrcode
from io import BytesIO
from telebot.types import Message
from googlesearch import search
from telebot.types import Message
import wikipediaapi
from bs4 import BeautifulSoup
import yt_dlp
from pydub import AudioSegment
TOKEN = '6896380150:AAFVVRSHi6CRUaFShL1MGYtnCIUUrI4_wdM'
OWNER_USER_ID = 6426928410
OPENWEATHERMAP_API_KEY = '8e238375b0ed5d203301c1c6e0ba961f'
YTDL_API_KEY = 'AIzaSyBB0TXBzzv3nZMc7a6LcKBQFUzpdlYFa2U'
bot = telebot.TeleBot(TOKEN)
yt_dl = yt_dlp.YoutubeDL()
LOG_FILE_PATH = 'bot.log'
GIF_FILE_PATH = 'bot.gif'
WIKIPEDIA_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
logging.basicConfig(filename=os.path.abspath(LOG_FILE_PATH), level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
def remove_html_tags(text):
    soup = BeautifulSoup(text, 'html.parser')
    return soup.get_text()

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    log_user_interaction(message)
    
    if message.text.startswith('/ping'):
        handle_ping(message)
    elif message.text.startswith('/help'):
        handle_help(message)
    elif message.text.startswith('/systeminfo'):
        handle_system_info(message)
    elif message.text.startswith('/start'):
        send_gif(message)
    elif message.text.startswith('/viewlog'):
        handle_view_log(message)
    elif message.text.startswith('/generateqr'):
        handle_generate_qr(message)
    elif message.text.startswith('/weather'):
        handle_weather(message)
    elif message.text.startswith('/google'):
        handle_google_search(message, bot)
    elif message.text.startswith('/wikipedia'):
        handle_wikipedia_search(message)
    elif message.text.startswith('/download'):
        handle_download(message)
    else:
        handle_unrecognized_command(message)

def handle_google_search(message: Message, bot, num_results=5):
    try:
        query = message.text.split(' ', 1)[1]
        search_results = list(search(query, num_results=num_results))
        results_text = "\n".join(search_results)
        bot.reply_to(message, f"Google Search Results:\n{results_text}")
    except Exception as e:
        bot.reply_to(message, f"Error performing Google search: {e}")

def log_user_interaction(message):
    user_info = f"User ID: {message.from_user.id}, Username: {message.from_user.username}, Chat ID: {message.chat.id}"
    logging.info(f"User Interaction: {user_info}, Message: {message.text}")

def send_gif(message):
    user_name = message.from_user.first_name
    gif = open(os.path.abspath(GIF_FILE_PATH), 'rb')
    caption = f"Hello {user_name}! Use /help to see available commands"
    bot.send_animation(message.chat.id, gif, caption=caption)

def handle_ping(message):
    start_time = time.time()
    reply = bot.send_message(message.chat.id, "Pinging...")
    end_time = time.time()
    
    elapsed_time = end_time - start_time
    bot.edit_message_text(f"Pong! Response time: {elapsed_time:.2f} seconds", message.chat.id, reply.message_id)

def handle_help(message):
    help_text = (
        "Available commands:\n"
        "/ping - Check if the bot is responsive\n"
        "/help - Display this help message\n"
        "/systeminfo - Show system information\n"
        "/generateqr <text> - Generate QR code from text\n"
        "/weather <city> - Get current weather information for a city\n"
        "/wikipedia <query> - Search Wikipedia for information\n"
        "/download <video_url> - Download audio from a YouTube video"
    )
    bot.reply_to(message, help_text)

def handle_system_info(message):
    system_info = f"System: {platform.system()} {platform.version()}\nMachine: {platform.machine()}\nProcessor: {platform.processor()}"
    bot.reply_to(message, system_info)

def handle_unrecognized_command(message):
    bot.reply_to(message, "Sorry, I didn't recognize that command. Use /help to see available commands.")

@bot.message_handler(commands=['viewlog'])
def handle_view_log(message):
    if message.from_user.id == OWNER_USER_ID:
        try:
            with open(os.path.abspath(LOG_FILE_PATH), 'rb') as log_file:
                bot.send_document(message.chat.id, log_file, caption="Here is the log file.")
        except Exception as e:
            bot.reply_to(message, f"Error sending the log file: {e}")
    else:
        bot.reply_to(message, "You do not have permission to view the log.")

@bot.message_handler(commands=['generateqr'])
def handle_generate_qr(message):
    try:
        text_to_encode = message.text.split(' ', 1)[1]
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(text_to_encode)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        bot.send_photo(message.chat.id, img_bytes, caption=f"Generated QR code for:\n{text_to_encode}")
    except Exception as e:
        bot.reply_to(message, f"Error generating QR code: {e}")

@bot.message_handler(commands=['weather'])
def handle_weather(message):
    try:
        city_name = message.text.split(' ', 1)[1]
        weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={OPENWEATHERMAP_API_KEY}&units=metric"
        response = requests.get(weather_url)
        data = response.json()

        if response.status_code == 200:
            weather_description = data['weather'][0]['description']
            temperature = data['main']['temp']
            humidity = data['main']['humidity']
            wind_speed = data['wind']['speed']

            weather_info = (
                f"Weather in {city_name}:\n"
                f"Description: {weather_description}\n"
                f"Temperature: {temperature} C\n"
                f"Humidity: {humidity}%\n"
                f"Wind Speed: {wind_speed} m/s"
            )
            bot.reply_to(message, weather_info)
        else:
            bot.reply_to(message, f"Error fetching weather information: {data['message']}")
    except Exception as e:
        bot.reply_to(message, f"Error fetching weather information: {e}")

@bot.message_handler(commands=['wikipedia'])
def handle_wikipedia_search(message):
    try:
        query = message.text.split(' ', 1)[1]
        headers = {'User-Agent': WIKIPEDIA_USER_AGENT}
        wikipedia_url = f"https://en.wikipedia.org/w/api.php?action=query&format=json&titles={query}&prop=extracts&exintro=1"
        response = requests.get(wikipedia_url, headers=headers)
        data = response.json()

        if 'pages' in data['query']:
            page = next(iter(data['query']['pages'].values()))
            raw_html = page.get('extract', 'No information available')
            plain_text = remove_html_tags(raw_html)
            bot.reply_to(message, f"Wikipedia Summary for '{query}':\n{plain_text}")
        else:
            bot.reply_to(message, f"No Wikipedia page found for '{query}'")
    except Exception as e:
        bot.reply_to(message, f"Error performing Wikipedia search: {e}")

@bot.message_handler(commands=['download'])
def handle_download(message):
    try:
        video_url = message.text.split(' ', 1)[1]
        info = yt_dl.extract_info(video_url, download=False)
        audio_url = info['formats'][0]['url']
        audio_content = requests.get(audio_url).content
        audio_ogg = AudioSegment.from_ogg(BytesIO(audio_content))
        audio_mp3 = BytesIO()
        audio_ogg.export(audio_mp3, format="mp3")
        bot.send_voice(message.chat.id, audio_mp3.getvalue(), caption="Audio")
    except Exception as e:
        bot.reply_to(message, f"Error downloading YouTube audio: {e}")

if __name__ == "__main__":
    print("Starting the bot...")
    print("Press Ctrl+C to stop")
    print("----------")
    print("Bot started")
    print("----------")
    print(f"Bot username: @{bot.get_me().username}")
    print(f"Bot ID: {bot.get_me().id}")
    print("----------")
    print("Created by: HARAJIT")
    print("Follow me on Instagram: @harajit.exe")
    print("----------")
    print("Enjoy!") 
    bot.polling(none_stop=True)
