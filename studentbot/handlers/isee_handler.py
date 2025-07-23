from telegram import Update
from telegram.ext import CallbackContext

async def isee_calculator(update: Update, context: CallbackContext) -> None:
    """Starts the ISEE calculator conversation."""
    # This will be implemented later
    await update.message.reply_text("Let's calculate your ISEE.")
