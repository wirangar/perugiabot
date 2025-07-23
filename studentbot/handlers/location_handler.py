from telegram import Update
from telegram.ext import CallbackContext

async def send_university_location(update: Update, context: CallbackContext) -> None:
    """Sends the location of the University of Perugia."""
    # Coordinates for the University of Perugia
    lat, lon = 43.1107, 12.3908
    await update.message.reply_location(latitude=lat, longitude=lon)
