import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import logger  # وارد کردن logger از config.py در ریشه پروژه
from handlers.cmd_start import get_translation  # اصلاح مسیر وارد کردن get_translation
from utils.text_formatter import sanitize_markdown  # وارد کردن sanitize_markdown از utils/

def load_guide_data():
    """Load guide data from knowledge_base_guide.json."""
    try:
        # مسیر فایل نسبت به موقعیت فایل menu_handler.py
        file_path = os.path.join(os.path.dirname(__file__), '..', 'knowledge_base_guide.json')
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info(f"Successfully loaded knowledge_base_guide.json from {file_path}")
        return data
    except FileNotFoundError as e:
        logger.error(f"Failed to load knowledge_base_guide.json: {e}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON format in knowledge_base_guide.json: {e}")
        raise

try:
    guide_data = load_guide_data()
except Exception as e:
    logger.error(f"Failed to initialize guide_data: {e}")
    guide_data = {}  # برای جلوگیری از کرش، اما باید فایل را اضافه کنید

async def guide_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays the main guide menu."""
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get('lang', 'fa')

    if not guide_data:
        error_msg = get_translation(lang, 'error_no_guide_data')
        await query.message.reply_text(error_msg, parse_mode='MarkdownV2')
        return

    keyboard = []
    for category in guide_data.get('guide', {}).get('categories', []):
        button = InlineKeyboardButton(
            category['title'].get(lang, category['title']['fa']),
            callback_data=f"guide_category_{category['id']}"
        )
        keyboard.append([button])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text(
        text=guide_data['guide']['title'].get(lang, guide_data['guide']['title']['fa']),
        reply_markup=reply_markup,
        parse_mode='MarkdownV2'
    )
    await query.message.delete()

async def guide_category_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays the subsections of a guide category."""
    query = update.callback_query
    await query.answer()
    category_id = query.data.split('_')[-1]
    lang = context.user_data.get('lang', 'fa')

    category = next((cat for cat in guide_data.get('guide', {}).get('categories', []) if cat['id'] == category_id), None)

    if not category:
        error_msg = get_translation(lang, 'error_category_not_found')
        await query.message.edit_text(error_msg, parse_mode='MarkdownV2')
        return

    keyboard = []
    for subsection in category.get('subsections', []):
        button = InlineKeyboardButton(
            subsection['title'].get(lang, subsection['title']['fa']),
            callback_data=f"guide_subsection_{category_id}_{subsection['id']}"
        )
        keyboard.append([button])

    # Add a back button
    back_text = get_translation(lang, 'back_button')
    keyboard.append([InlineKeyboardButton(back_text, callback_data="guide")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.edit_text(
        text=category['description'].get(lang, category['description']['fa']),
        reply_markup=reply_markup,
        parse_mode='MarkdownV2'
    )

async def guide_subsection_content(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays the content of a guide subsection."""
    query = update.callback_query
    await query.answer()
    _, _, category_id, subsection_id = query.data.split('_')
    lang = context.user_data.get('lang', 'fa')

    category = next((cat for cat in guide_data.get('guide', {}).get('categories', []) if cat['id'] == category_id), None)
    if not category:
        error_msg = get_translation(lang, 'error_category_not_found')
        await query.message.edit_text(error_msg, parse_mode='MarkdownV2')
        return

    subsection = next((sub for sub in category.get('subsections', []) if sub['id'] == subsection_id), None)
    if not subsection:
        error_msg = get_translation(lang, 'error_subsection_not_found')
        await query.message.edit_text(error_msg, parse_mode='MarkdownV2')
        return

    # Build content
    content = "\n".join(subsection.get('content', {}).get(lang, subsection.get('content', {}).get('fa', [])))

    resources = ""
    if subsection.get('resources'):
        if subsection['resources'].get('links'):
            resources += "\n\n" + get_translation(lang, 'resources_links') + "\n" + "\n".join(subsection['resources']['links'])
        if subsection['resources'].get('apps'):
            resources += "\n\n" + get_translation(lang, 'resources_apps') + "\n" + "\n".join(subsection['resources']['apps'])
        if subsection['resources'].get('contacts'):
            resources += "\n\n" + get_translation(lang, 'resources_contacts') + "\n" + "\n".join(subsection['resources']['contacts'])

    tips = ""
    if subsection.get('tips'):
        tips = "\n\n" + get_translation(lang, 'tips') + "\n" + "\n".join(subsection['tips'].get(lang, subsection['tips'].get('fa', [])))

    faqs = ""
    if subsection.get('faqs'):
        faqs = "\n\n" + get_translation(lang, 'faqs') + "\n" + "\n".join(subsection['faqs'].get(lang, subsection['faqs'].get('fa', [])))

    tips_for_iranians = ""
    if subsection.get('tips_for_iranians'):
        tips_for_iranians = "\n\n" + get_translation(lang, 'tips_for_iranians') + "\n" + "\n".join(subsection['tips_for_iranians'].get(lang, subsection['tips_for_iranians'].get('fa', [])))

    # Escape special characters for MarkdownV2
    content_text = sanitize_markdown(
        f"**{subsection['title'].get(lang, subsection['title']['fa'])}**\n\n{content}{resources}{tips}{faqs}{tips_for_iranians}"
    )

    # Add back button
    back_text = get_translation(lang, 'back_button')
    keyboard = [[InlineKeyboardButton(back_text, callback_data=f"guide_category_{category_id}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(
        text=content_text,
        parse_mode='MarkdownV2',
        reply_markup=reply_markup
    )
