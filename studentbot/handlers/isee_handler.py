import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

from utils.db import save_isee_calculation
from utils.sheets import save_isee_to_sheet
from handlers.cmd_start import get_translation
from config import logger  # اضافه کردن logger برای لاگ‌گیری

# States for conversation
FAMILY_MEMBERS, ANNUAL_INCOME, PROPERTY_STATUS, PROPERTY_SIZE = range(4)

async def start_isee_calculation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the ISEE calculation conversation."""
    lang = context.user_data.get('lang', 'fa')
    context.user_data['isee'] = {}
    await update.callback_query.message.reply_text(get_translation(lang, 'isee_intro'))
    await update.callback_query.message.reply_text(get_translation(lang, 'ask_family_members'))
    logger.info(f"Started ISEE calculation for user {update.effective_user.id}")
    return FAMILY_MEMBERS

async def get_family_members(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the number of family members and asks for the annual income."""
    lang = context.user_data.get('lang', 'fa')
    try:
        family_members = int(update.message.text)
        if family_members <= 0:
            await update.message.reply_text(get_translation(lang, 'invalid_number_positive'))
            return FAMILY_MEMBERS
        context.user_data['isee']['family_members'] = family_members
        await update.message.reply_text(get_translation(lang, 'ask_annual_income'))
        logger.info(f"User {update.effective_user.id} entered family members: {family_members}")
        return ANNUAL_INCOME
    except ValueError:
        await update.message.reply_text(get_translation(lang, 'invalid_number'))
        logger.warning(f"User {update.effective_user.id} entered invalid family members: {update.message.text}")
        return FAMILY_MEMBERS

async def get_annual_income(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the annual income and asks for the property status."""
    lang = context.user_data.get('lang', 'fa')
    try:
        annual_income = float(update.message.text)
        if annual_income < 0:
            await update.message.reply_text(get_translation(lang, 'invalid_number_non_negative'))
            return ANNUAL_INCOME
        context.user_data['isee']['annual_income'] = annual_income
        keyboard = [
            [
                InlineKeyboardButton(get_translation(lang, 'property_owner'), callback_data='owner'),
                InlineKeyboardButton(get_translation(lang, 'property_tenant'), callback_data='tenant'),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(get_translation(lang, 'ask_property_status'), reply_markup=reply_markup)
        logger.info(f"User {update.effective_user.id} entered annual income: {annual_income}")
        return PROPERTY_STATUS
    except ValueError:
        await update.message.reply_text(get_translation(lang, 'invalid_number'))
        logger.warning(f"User {update.effective_user.id} entered invalid annual income: {update.message.text}")
        return ANNUAL_INCOME

async def get_property_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the property status and asks for the property size if owner."""
    query = update.callback_query
    await query.answer()
    context.user_data['isee']['property_status'] = query.data
    lang = context.user_data.get('lang', 'fa')
    logger.info(f"User {update.effective_user.id} selected property status: {query.data}")
    if query.data == 'owner':
        await query.message.reply_text(get_translation(lang, 'ask_property_size'))
        return PROPERTY_SIZE
    else:
        context.user_data['isee']['property_size'] = 0
        return await calculate_and_show_isee(update, context)

async def get_property_size(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the property size and calculates the ISEE."""
    lang = context.user_data.get('lang', 'fa')
    try:
        property_size = float(update.message.text)
        if property_size < 0:
            await update.message.reply_text(get_translation(lang, 'invalid_number_non_negative'))
            return PROPERTY_SIZE
        context.user_data['isee']['property_size'] = property_size
        logger.info(f"User {update.effective_user.id} entered property size: {property_size}")
        return await calculate_and_show_isee(update, context)
    except ValueError:
        await update.message.reply_text(get_translation(lang, 'invalid_number'))
        logger.warning(f"User {update.effective_user.id} entered invalid property size: {update.message.text}")
        return PROPERTY_SIZE

async def calculate_and_show_isee(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Calculates the ISEE and shows the result."""
    isee_data = context.user_data['isee']
    family_members = isee_data['family_members']
    annual_income = isee_data['annual_income']
    property_size = isee_data.get('property_size', 0)

    property_value = property_size * 500 * 0.2
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

    await update.effective_message.reply_text(result_text, parse_mode='MarkdownV2')
    logger.info(f"User {update.effective_user.id} calculated ISEE: {isee:.2f}, Status: {scholarship_status_key}")

    # Save the calculation to the database and Google Sheets
    try:
        isee_data['isee_value'] = isee
        isee_data['scholarship_status'] = get_translation(lang, scholarship_status_key)
        isee_data['scholarship_amount'] = scholarship_amount
        save_isee_calculation(update.effective_user.id, isee_data)
        save_isee_to_sheet(update.effective_user.id, isee_data)
        logger.info(f"Successfully saved ISEE calculation for user {update.effective_user.id}")
    except Exception as e:
        logger.error(f"Failed to save ISEE calculation for user {update.effective_user.id}: {e}")

    return ConversationHandler.END

async def cancel_isee_calculation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels the ISEE calculation."""
    lang = context.user_data.get('lang', 'fa')
    await update.message.reply_text(get_translation(lang, 'calculation_cancelled'), parse_mode='MarkdownV2')
    logger.info(f"User {update.effective_user.id} cancelled ISEE calculation")
    return ConversationHandler.END
