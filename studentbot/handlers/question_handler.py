from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

from config import ADMIN_CHAT_ID
from utils.sheets import get_sheet
from .cmd_start import get_translation

ASK_QUESTION = range(1)

async def start_ask_question(update: Update, context: CallbackContext) -> int:
    """Starts the ask a question conversation."""
    lang = context.user_data.get('lang', 'fa')
    await update.callback_query.message.reply_text(get_translation(lang, 'ask_question_prompt'))
    return ASK_QUESTION

async def save_question(update: Update, context: CallbackContext) -> int:
    """Saves the question to Google Sheets and sends it to the admin."""
    question = update.message.text
    user_id = update.effective_user.id

    # Save to Google Sheets
    sheet = get_sheet("Questions")
    sheet.append_row([user_id, question])

    # Send to admin
    if ADMIN_CHAT_ID:
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=f"New question from {user_id}:\n\n{question}")

    lang = context.user_data.get('lang', 'fa')
    await update.message.reply_text(get_translation(lang, 'question_sent'))

    return ConversationHandler.END

async def cancel_question(update: Update, context: CallbackContext) -> int:
    """Cancels the ask a question process."""
    lang = context.user_data.get('lang', 'fa')
    await update.message.reply_text(get_translation(lang, 'question_cancelled'))
    return ConversationHandler.END
