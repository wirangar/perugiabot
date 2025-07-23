from telegram import Update
from telegram.ext import CallbackContext

from .cmd_start import get_translation

async def scholarships_menu(update: Update, context: CallbackContext) -> None:
    """Handles the scholarships menu."""
    lang = context.user_data.get('lang', 'fa')
    # This is a placeholder. In a real application, you would fetch this from a database or a file.
    scholarships_info = {
        "fa": "اطلاعات بورسیه‌ها در اینجا نمایش داده می‌شود.",
        "en": "Scholarships information will be displayed here.",
        "it": "Le informazioni sulle borse di studio verranno visualizzate qui."
    }
    await update.callback_query.message.reply_text(scholarships_info[lang])

async def immigration_menu(update: Update, context: CallbackContext) -> None:
    """Handles the immigration menu."""
    lang = context.user_data.get('lang', 'fa')
    immigration_info = {
        "fa": "اطلاعات مراحل مهاجرت در اینجا نمایش داده می‌شود.",
        "en": "Immigration process information will be displayed here.",
        "it": "Le informazioni sul processo di immigrazione verranno visualizzate qui."
    }
    await update.callback_query.message.reply_text(immigration_info[lang])

async def housing_menu(update: Update, context: CallbackContext) -> None:
    """Handles the housing menu."""
    lang = context.user_data.get('lang', 'fa')
    housing_info = {
        "fa": "اطلاعات مسکن در پروجا در اینجا نمایش داده می‌شود.",
        "en": "Housing information in Perugia will be displayed here.",
        "it": "Le informazioni sugli alloggi a Perugia verranno visualizzate qui."
    }
    await update.callback_query.message.reply_text(housing_info[lang])
