import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext

def get_translation(lang, key):
    with open(f'lang/{lang}.json', 'r', encoding='utf-8') as f:
        translations = json.load(f)
    return translations.get(key, "Translation not found")

async def start(update: Update, context: CallbackContext) -> None:
    """Sends a message with three inline buttons attached."""
    keyboard = [
        [
            InlineKeyboardButton("🇮🇷 فارسی", callback_data="lang_fa"),
            InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
            InlineKeyboardButton("🇮🇹 Italiano", callback_data="lang_it"),
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Please choose your language:", reply_markup=reply_markup)
