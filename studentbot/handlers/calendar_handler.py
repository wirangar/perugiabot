from telegram import Update
from telegram.ext import CallbackContext
from telegram_inline_calendar import InlineCalendar

calendar = InlineCalendar()

async def show_calendar(update: Update, context: CallbackContext) -> None:
    """Shows the calendar."""
    await update.message.reply_text("Please select a date:", reply_markup=calendar.markup)

async def calendar_callback(update: Update, context: CallbackContext) -> None:
    """Handles the calendar callback."""
    query = update.callback_query
    await query.answer()

    selected, date = calendar.process_selection(update, context)

    if selected:
        await query.edit_message_text(
            text=f"You selected {date.strftime('%Y-%m-%d')}",
            reply_markup=None
        )
