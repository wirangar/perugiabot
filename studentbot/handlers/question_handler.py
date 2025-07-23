import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from config import logger, ADMIN_CHAT_ID
from utils.db import add_points
from utils.sheets import get_sheet
from handlers.cmd_start import get_translation

ASK_QUESTION = 0

async def start_ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the question submission process."""
    lang = context.user_data.get('lang', 'fa')
    await update.callback_query.message.reply_text(
        get_translation(lang, 'ask_question_prompt'),
        parse_mode='MarkdownV2'
    )
    logger.info(f"User {update.effective_user.id} started asking a question")
    return ASK_QUESTION

async def save_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Saves the user's question to Google Sheets and notifies admin."""
    lang = context.user_data.get('lang', 'fa')
    question = update.message.text
    user_id = update.effective_user.id

    try:
        sheet = get_sheet("Questions")
        sheet.append_row([user_id, question, str(update.message.date)])
        add_points(user_id, 5)  # Award 5 points for asking a question
        if ADMIN_CHAT_ID:
            await context.bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=f"{get_translation(lang, 'new_live_chat')} {user_id}\nQuestion: {question}",
                parse_mode='MarkdownV2'
            )
        await update.message.reply_text(
            get_translation(lang, 'question_sent'),
            parse_mode='MarkdownV2'
        )
        logger.info(f"Question saved for user_id: {user_id}")
    except Exception as e:
        logger.error(f"Failed to save question for user_id {user_id}: {e}")
        await update.message.reply_text(
            get_translation(lang, 'voice_error'),  # Reuse error message
            parse_mode='MarkdownV2'
        )
        return ASK_QUESTION

    return ConversationHandler.END

async def cancel_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels the question submission."""
    lang = context.user_data.get('lang', 'fa')
    await update.message.reply_text(
        get_translation(lang, 'question_cancelled'),
        parse_mode='MarkdownV2'
    )
    logger.info(f"User {update.effective_user.id} cancelled question submission")
    return ConversationHandler.END
