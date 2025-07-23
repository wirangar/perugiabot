from telegram import Update
from telegram.ext import CallbackContext

async def send_pdf(update: Update, context: CallbackContext) -> None:
    """Sends a sample PDF file."""
    await update.message.reply_document(open('assets/pdfs/sample.pdf', 'rb'))

async def send_video(update: Update, context: CallbackContext) -> None:
    """Sends a sample video file."""
    await update.message.reply_video(open('assets/videos/sample.mp4', 'rb'))
