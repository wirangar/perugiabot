from telegram import Update
from telegram.ext import CallbackContext

async def profile(update: Update, context: CallbackContext) -> None:
    """Displays the user's profile."""
    # This will be implemented later
    await update.message.reply_text("This is your profile.")

async def edit_profile(update: Update, context: CallbackContext) -> None:
    """Starts the conversation to edit the user's profile."""
    # This will be implemented later
    await update.message.reply_text("Let's edit your profile.")
