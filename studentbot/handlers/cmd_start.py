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

async def button(update: Update, context: CallbackContext) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    await query.answer()

    lang = query.data.split('_')[1]
    context.user_data['lang'] = lang

    translation = get_translation(lang, "language_changed")
    await query.edit_message_text(text=translation)

    # Show the main menu
    keyboard = [
        [InlineKeyboardButton(get_translation(lang, "profile"), callback_data="profile")],
        [InlineKeyboardButton(get_translation(lang, "isee_calculator"), callback_data="isee_calculator")],
        [InlineKeyboardButton(get_translation(lang, "scholarships"), callback_data="scholarships")],
        [InlineKeyboardButton(get_translation(lang, "ask_question"), callback_data="ask_question")],
        [InlineKeyboardButton(get_translation(lang, "about"), callback_data="about")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.reply_text(get_translation(lang, "main_menu"), reply_markup=reply_markup)
