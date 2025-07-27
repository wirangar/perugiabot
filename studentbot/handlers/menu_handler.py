import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from .cmd_start import get_translation

def load_guide_data():
    with open('knowledge_base_guide.json', 'r', encoding='utf-8') as f:
        return json.load(f)

guide_data = load_guide_data()

async def guide_menu(update: Update, context: CallbackContext) -> None:
    """Displays the main guide menu."""
    lang = context.user_data.get('lang', 'fa')

    keyboard = []
    for category in guide_data['guide']['categories']:
        button = InlineKeyboardButton(
            category['title'][lang],
            callback_data=f"guide_category_{category['id']}"
        )
        keyboard.append([button])

    reply_markup = InlineKeyboardMarkup(keyboard)
    # It's better to send a new message here instead of editing,
    # because the user is coming from the main menu.
    await update.callback_query.message.reply_text(
        guide_data['guide']['title'][lang],
        reply_markup=reply_markup
    )
    await update.callback_query.message.delete()


async def guide_category_menu(update: Update, context: CallbackContext) -> None:
    """Displays the subsections of a guide category."""
    query = update.callback_query
    await query.answer()
    category_id = query.data.split('_')[-1]
    lang = context.user_data.get('lang', 'fa')

    category = next((cat for cat in guide_data['guide']['categories'] if cat['id'] == category_id), None)

    if category:
        keyboard = []
        for subsection in category['subsections']:
            button = InlineKeyboardButton(
                subsection['title'][lang],
                callback_data=f"guide_subsection_{category_id}_{subsection['id']}"
            )
            keyboard.append([button])

        # Add a back button
        keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="guide")])

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text=category['description'][lang],
            reply_markup=reply_markup
        )

async def guide_subsection_content(update: Update, context: CallbackContext) -> None:
    """Displays the content of a guide subsection."""
    query = update.callback_query
    await query.answer()
    _, _, category_id, subsection_id = query.data.split('_')
    lang = context.user_data.get('lang', 'fa')

    category = next((cat for cat in guide_data['guide']['categories'] if cat['id'] == category_id), None)
    if category:
        subsection = next((sub for sub in category['subsections'] if sub['id'] == subsection_id), None)
        if subsection:
            content = "\n".join(subsection['content'][lang])

            resources = ""
            if subsection.get('resources'):
                if subsection['resources'].get('links'):
                    resources += "\n\nLinks:\n" + "\n".join(subsection['resources']['links'])
                if subsection['resources'].get('apps'):
                    resources += "\n\nApps:\n" + "\n".join(subsection['resources']['apps'])
                if subsection['resources'].get('contacts'):
                    resources += "\n\nContacts:\n" + "\n".join(subsection['resources']['contacts'])

            tips = ""
            if subsection.get('tips'):
                tips = "\n\nTips:\n" + "\n".join(subsection['tips'][lang])

            faqs = ""
            if subsection.get('faqs'):
                faqs = "\n\nFAQs:\n" + "\n".join(subsection['faqs'][lang])

            tips_for_iranians = ""
            if subsection.get('tips_for_iranians'):
                tips_for_iranians = "\n\nTips for Iranians:\n" + "\n".join(subsection['tips_for_iranians'][lang])

            keyboard = [[InlineKeyboardButton("⬅️ Back", callback_data=f"guide_category_{category_id}")]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                text=f"**{subsection['title'][lang]}**\n\n{content}{resources}{tips}{faqs}{tips_for_iranians}",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
