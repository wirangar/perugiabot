from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

from config import ADMIN_CHAT_ID
from .cmd_start import get_translation

LIVE_CHAT = range(1)

async def start_live_chat(update: Update, context: CallbackContext) -> int:
    """Starts the live chat conversation."""
    lang = context.user_data.get('lang', 'fa')
    await update.message.reply_text(get_translation(lang, 'live_chat_prompt'))

    if ADMIN_CHAT_ID:
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=f"{get_translation(lang, 'new_live_chat')} {update.effective_user.id}"
        )

    return LIVE_CHAT

async def forward_to_admin(update: Update, context: CallbackContext) -> None:
    """Forwards user messages to the admin."""
    if ADMIN_CHAT_ID:
        await context.bot.forward_message(
            chat_id=ADMIN_CHAT_ID,
            from_chat_id=update.effective_chat.id,
            message_id=update.message.message_id
        )

async def forward_to_user(update: Update, context: CallbackContext) -> None:
    """Forwards admin messages to the user."""
    user_id = update.message.reply_to_message.forward_from.id
    await context.bot.send_message(
        chat_id=user_id,
        text=update.message.text
    )

async def cancel_live_chat(update: Update, context: CallbackContext) -> int:
    """Cancels the live chat conversation."""
    lang = context.user_data.get('lang', 'fa')
    await update.message.reply_text(get_translation(lang, 'live_chat_disconnected'))
    return ConversationHandler.END
