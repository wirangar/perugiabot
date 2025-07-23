import openai
from telegram import Update
from telegram.ext import CallbackContext

from config import OPENAI_API_KEY
from .cmd_start import get_translation

async def transcribe_voice(update: Update, context: CallbackContext) -> None:
    """Transcribes a voice message using OpenAI's Whisper API."""
    lang = context.user_data.get('lang', 'fa')

    if not OPENAI_API_KEY:
        await update.message.reply_text("Voice transcription service is not configured.")
        return

    try:
        file = await context.bot.get_file(update.message.voice.file_id)
        file_path = await file.download_to_drive()

        with open(file_path, "rb") as audio_file:
            transcript = openai.Audio.transcribe("whisper-1", audio_file)

        transcribed_text = transcript['text']

        response_text = f"{get_translation(lang, 'voice_transcribed')}\n\n{transcribed_text}"
        await update.message.reply_text(response_text)

    except Exception as e:
        print(f"Error transcribing voice: {e}")
        await update.message.reply_text(get_translation(lang, 'voice_error'))
