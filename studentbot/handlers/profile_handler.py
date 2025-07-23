import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler

from utils.db import save_user, get_user
from utils.sheets import save_user_to_sheet
from .cmd_start import get_translation

# States for conversation
(
    NAME,
    FAMILY_NAME,
    AGE,
    EMAIL,
    FIELD_OF_STUDY,
    COUNTRY,
    EDIT_PROFILE,
    EDIT_FIELD,
) = range(8)

async def start_registration(update: Update, context: CallbackContext) -> int:
    """Starts the registration conversation."""
    lang = context.user_data.get('lang', 'fa')
    await update.message.reply_text(get_translation(lang, 'ask_name'))
    return NAME

async def get_name(update: Update, context: CallbackContext) -> int:
    """Stores the name and asks for the family name."""
    context.user_data['name'] = update.message.text
    lang = context.user_data.get('lang', 'fa')
    await update.message.reply_text(get_translation(lang, 'ask_family_name'))
    return FAMILY_NAME

async def get_family_name(update: Update, context: CallbackContext) -> int:
    """Stores the family name and asks for the age."""
    context.user_data['family_name'] = update.message.text
    lang = context.user_data.get('lang', 'fa')
    await update.message.reply_text(get_translation(lang, 'ask_age'))
    return AGE

async def get_age(update: Update, context: CallbackContext) -> int:
    """Stores the age and asks for the email."""
    context.user_data['age'] = update.message.text
    lang = context.user_data.get('lang', 'fa')
    await update.message.reply_text(get_translation(lang, 'ask_email'))
    return EMAIL

async def get_email(update: Update, context: CallbackContext) -> int:
    """Stores the email and asks for the field of study."""
    context.user_data['email'] = update.message.text
    lang = context.user_data.get('lang', 'fa')
    await update.message.reply_text(get_translation(lang, 'ask_field_of_study'))
    return FIELD_OF_STUDY

async def get_field_of_study(update: Update, context: CallbackContext) -> int:
    """Stores the field of study and asks for the country."""
    context.user_data['field_of_study'] = update.message.text
    lang = context.user_data.get('lang', 'fa')
    await update.message.reply_text(get_translation(lang, 'ask_country'))
    return COUNTRY

async def get_country(update: Update, context: CallbackContext) -> int:
    """Stores the country and ends the conversation."""
    context.user_data['country'] = update.message.text
    context.user_data['user_id'] = update.message.from_user.id
    lang = context.user_data.get('lang', 'fa')
    save_user(context.user_data)
    save_user_to_sheet(context.user_data)
    await update.message.reply_text(get_translation(lang, 'registration_complete'))
    return ConversationHandler.END

async def cancel_registration(update: Update, context: CallbackContext) -> int:
    """Cancels the registration."""
    lang = context.user_data.get('lang', 'fa')
    await update.message.reply_text(get_translation(lang, 'registration_cancelled'))
    return ConversationHandler.END

async def show_profile(update: Update, context: CallbackContext) -> None:
    """Shows the user's profile."""
    user_id = update.effective_user.id
    lang = context.user_data.get('lang', 'fa')
    user = get_user(user_id)

    if user:
        profile_text = f"""
        {get_translation(lang, 'profile_title')}

        {get_translation(lang, 'name')} {user['name']}
        {get_translation(lang, 'family_name')} {user['family_name']}
        {get_translation(lang, 'age')} {user['age']}
        {get_translation(lang, 'email')} {user['email']}
        {get_translation(lang, 'field_of_study')} {user['field_of_study']}
        {get_translation(lang, 'country')} {user['country']}
        {get_translation(lang, 'registration_date')} {user['created_at'].strftime('%Y-%m-%d %H:%M')}
        """
        keyboard = [
            [InlineKeyboardButton(get_translation(lang, "edit_profile"), callback_data="edit_profile")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.message.reply_text(profile_text, reply_markup=reply_markup)
    else:
        await update.callback_query.message.reply_text(get_translation(lang, 'user_not_found'))

async def start_edit_profile(update: Update, context: CallbackContext) -> int:
    """Starts the edit profile conversation."""
    lang = context.user_data.get('lang', 'fa')
    keyboard = [
        [InlineKeyboardButton(get_translation(lang, "edit_name"), callback_data="edit_name")],
        [InlineKeyboardButton(get_translation(lang, "edit_family_name"), callback_data="edit_family_name")],
        [InlineKeyboardButton(get_translation(lang, "edit_age"), callback_data="edit_age")],
        [InlineKeyboardButton(get_translation(lang, "edit_email"), callback_data="edit_email")],
        [InlineKeyboardButton(get_translation(lang, "edit_field_of_study"), callback_data="edit_field_of_study")],
        [InlineKeyboardButton(get_translation(lang, "edit_country"), callback_data="edit_country")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.reply_text(get_translation(lang, 'edit_profile_prompt'), reply_markup=reply_markup)
    return EDIT_PROFILE

async def ask_for_new_value(update: Update, context: CallbackContext) -> int:
    """Asks for the new value for the selected field."""
    query = update.callback_query
    await query.answer()
    context.user_data['edit_field'] = query.data.split('_')[1]
    lang = context.user_data.get('lang', 'fa')
    await query.message.reply_text(get_translation(lang, 'ask_new_value'))
    return EDIT_FIELD

async def update_field(update: Update, context: CallbackContext) -> int:
    """Updates the selected field in the database."""
    new_value = update.message.text
    field_to_edit = context.user_data['edit_field']
    user_id = update.effective_user.id

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"UPDATE users SET {field_to_edit} = %s WHERE user_id = %s", (new_value, user_id))
    conn.commit()
    cur.close()
    conn.close()

    lang = context.user_data.get('lang', 'fa')
    await update.message.reply_text(get_translation(lang, 'profile_updated'))

    # Show the updated profile
    await show_profile(update, context)

    return ConversationHandler.END

async def cancel_edit(update: Update, context: CallbackContext) -> int:
    """Cancels the edit process."""
    lang = context.user_data.get('lang', 'fa')
    await update.message.reply_text(get_translation(lang, 'edit_cancelled'))
    return ConversationHandler.END
