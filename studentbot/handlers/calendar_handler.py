import calendar
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from utils.events import get_events_for_month

def create_calendar(year, month):
    markup = []
    # Header
    row = [InlineKeyboardButton(f"{calendar.month_name[month]} {year}", callback_data="ignore")]
    markup.append(row)
    row = [InlineKeyboardButton(day, callback_data="ignore") for day in ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]]
    markup.append(row)

    my_calendar = calendar.monthcalendar(year, month)
    events = get_events_for_month(year, month)
    event_days = [event['date'].day for event in events]

    for week in my_calendar:
        row = []
        for day in week:
            if day == 0:
                row.append(InlineKeyboardButton(" ", callback_data="ignore"))
            elif day in event_days:
                row.append(InlineKeyboardButton(f"*{day}*", callback_data=f"calendar-day-{year}-{month}-{day}"))
            else:
                row.append(InlineKeyboardButton(str(day), callback_data=f"calendar-day-{year}-{month}-{day}"))
        markup.append(row)

    # Navigation
    row = [
        InlineKeyboardButton("<", callback_data=f"calendar-prev-{year}-{month}"),
        InlineKeyboardButton(" ", callback_data="ignore"),
        InlineKeyboardButton(">", callback_data=f"calendar-next-{year}-{month}"),
    ]
    markup.append(row)

    return InlineKeyboardMarkup(markup)

async def show_calendar(update: Update, context: CallbackContext) -> None:
    """Shows the calendar."""
    now = datetime.now()
    await update.message.reply_text(
        "Please select a date:",
        reply_markup=create_calendar(now.year, now.month)
    )

async def calendar_callback(update: Update, context: CallbackContext) -> None:
    """Handles the calendar callback."""
    query = update.callback_query
    await query.answer()

    data = query.data.split('-')
    action = data[1]
    year = int(data[2])
    month = int(data[3])

    if action == "prev":
        month -= 1
        if month < 1:
            month = 12
            year -= 1
        await query.edit_message_text(
            text="Please select a date:",
            reply_markup=create_calendar(year, month)
        )
    elif action == "next":
        month += 1
        if month > 12:
            month = 1
            year += 1
        await query.edit_message_text(
            text="Please select a date:",
            reply_markup=create_calendar(year, month)
        )
    elif action == "day":
        day = int(data[4])
        await query.edit_message_text(
            text=f"You selected {year}-{month}-{day}",
            reply_markup=None
        )
