from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler

from utils.db import save_isee_calculation
from utils.sheets import save_isee_to_sheet
from .cmd_start import get_translation

# States for conversation
FAMILY_MEMBERS, ANNUAL_INCOME, PROPERTY_STATUS, PROPERTY_SIZE = range(4)

async def start_isee_calculation(update: Update, context: CallbackContext) -> int:
    """Starts the ISEE calculation conversation."""
    lang = context.user_data.get('lang', 'fa')
    context.user_data['isee'] = {}
    await update.callback_query.message.reply_text(get_translation(lang, 'isee_intro'))
    await update.callback_query.message.reply_text(get_translation(lang, 'ask_family_members'))
    return FAMILY_MEMBERS

async def get_family_members(update: Update, context: CallbackContext) -> int:
    """Stores the number of family members and asks for the annual income."""
    lang = context.user_data.get('lang', 'fa')
    try:
        context.user_data['isee']['family_members'] = int(update.message.text)
    except ValueError:
        await update.message.reply_text(get_translation(lang, 'invalid_number'))
        return FAMILY_MEMBERS
    await update.message.reply_text(get_translation(lang, 'ask_annual_income'))
    return ANNUAL_INCOME

async def get_annual_income(update: Update, context: CallbackContext) -> int:
    """Stores the annual income and asks for the property status."""
    lang = context.user_data.get('lang', 'fa')
    try:
        context.user_data['isee']['annual_income'] = float(update.message.text)
    except ValueError:
        await update.message.reply_text(get_translation(lang, 'invalid_number'))
        return ANNUAL_INCOME
    keyboard = [
        [
            InlineKeyboardButton(get_translation(lang, 'property_owner'), callback_data='owner'),
            InlineKeyboardButton(get_translation(lang, 'property_tenant'), callback_data='tenant'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(get_translation(lang, 'ask_property_status'), reply_markup=reply_markup)
    return PROPERTY_STATUS

async def get_property_status(update: Update, context: CallbackContext) -> int:
    """Stores the property status and asks for the property size if owner."""
    query = update.callback_query
    await query.answer()
    context.user_data['isee']['property_status'] = query.data
    lang = context.user_data.get('lang', 'fa')
    if query.data == 'owner':
        await query.message.reply_text(get_translation(lang, 'ask_property_size'))
        return PROPERTY_SIZE
    else:
        context.user_data['isee']['property_size'] = 0
        return await calculate_and_show_isee(update, context)

async def get_property_size(update: Update, context: CallbackContext) -> int:
    """Stores the property size and calculates the ISEE."""
    lang = context.user_data.get('lang', 'fa')
    try:
        context.user_data['isee']['property_size'] = float(update.message.text)
    except ValueError:
        await update.message.reply_text(get_translation(lang, 'invalid_number'))
        return PROPERTY_SIZE
    return await calculate_and_show_isee(update, context)

async def calculate_and_show_isee(update: Update, context: CallbackContext) -> int:
    """Calculates the ISEE and shows the result."""
    isee_data = context.user_data['isee']
    family_members = isee_data['family_members']
    annual_income = isee_data['annual_income']
    property_size = isee_data.get('property_size', 0)

    property_value = property_size * 500 * 0.2

    # This is a simplified version of the formula
    family_coefficient = 1 + (family_members - 1) * 0.5

    isee = (annual_income + property_value) / family_coefficient

    isee_limit = 27948.60

    if isee <= isee_limit * 0.55:
        scholarship_status_key = "full_scholarship"
        scholarship_amount = 5192
    elif isee <= isee_limit * 0.715:
        scholarship_status_key = "medium_scholarship"
        scholarship_amount = 3634
    elif isee <= isee_limit:
        scholarship_status_key = "partial_scholarship"
        scholarship_amount = 2000
    else:
        scholarship_status_key = "no_scholarship"
        scholarship_amount = 0

    lang = context.user_data.get('lang', 'fa')

    result_text = f"""
    {get_translation(lang, 'isee_result')}

    {get_translation(lang, 'isee_value')} {isee:.2f}
    {get_translation(lang, 'scholarship_status')} {get_translation(lang, scholarship_status_key)}
    {get_translation(lang, 'scholarship_amount')} {scholarship_amount} €
    """

    await update.effective_message.reply_text(result_text)

    # Save the calculation to the database
    isee_data['isee_value'] = isee
    isee_data['scholarship_status'] = get_translation(lang, scholarship_status_key)
    isee_data['scholarship_amount'] = scholarship_amount
    save_isee_calculation(update.effective_user.id, isee_data)
    save_isee_to_sheet(update.effective_user.id, isee_data)

    return ConversationHandler.END

async def cancel_isee_calculation(update: Update, context: CallbackContext) -> int:
    """Cancels the ISEE calculation."""
    lang = context.user_data.get('lang', 'fa')
    await update.message.reply_text(get_translation(lang, 'calculation_cancelled'))
    return ConversationHandler.END
