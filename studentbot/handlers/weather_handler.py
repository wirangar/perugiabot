import requests
from telegram import Update
from telegram.ext import CallbackContext

from config import OPENWEATHERMAP_API_KEY
from .cmd_start import get_translation

async def get_weather(update: Update, context: CallbackContext) -> None:
    """Gets the weather for Perugia."""
    lang = context.user_data.get('lang', 'fa')

    if not OPENWEATHERMAP_API_KEY:
        await update.message.reply_text("Weather service is not configured.")
        return

    try:
        # Perugia's coordinates
        lat, lon = 43.1122, 12.3888
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHERMAP_API_KEY}&units=metric"
        response = requests.get(url)
        response.raise_for_status()
        weather_data = response.json()

        city = weather_data['name']
        temp = weather_data['main']['temp']
        description = weather_data['weather'][0]['description']

        weather_text = f"Weather in {city}:\nTemperature: {temp}°C\nDescription: {description}"

        await update.message.reply_text(weather_text)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather: {e}")
        await update.message.reply_text("Sorry, I couldn't fetch the weather information right now.")
