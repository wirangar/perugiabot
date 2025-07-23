import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,  # جایگزین CallbackContext
    ConversationHandler,
)

from config import TELEGRAM_TOKEN, logger  # اضافه کردن logger
from utils.db import create_user_table, create_isee_calculations_table
from handlers.cmd_start import start, button
from handlers.isee_handler import (
    start_isee_calculation,
    get_family_members,
    get_annual_income,
    get_property_status,
    get_property_size,
    cancel_isee_calculation,
    FAMILY_MEMBERS,
    ANNUAL_INCOME,
    PROPERTY_STATUS,
    PROPERTY_SIZE,
)
from handlers.search_handler import search, generate_embeddings
from handlers.live_chat_handler import (
    start_live_chat,
    forward_to_admin,
    forward_to_user,
    cancel_live_chat,
    LIVE_CHAT,
)
from handlers.location_handler import send_university_location
from handlers.calendar_handler import show_calendar, calendar_callback
from handlers.voice_handler import transcribe_voice
from handlers.question_handler import (
    start_ask_question,
    save_question,
    cancel_question,
    ASK_QUESTION,
)
from handlers.weather_handler import get_weather
from handlers.file_handler import send_pdf, send_video
from handlers.menu_handler import (
    guide_menu,
    guide_category_menu,
    guide_subsection_content,
)
from handlers.profile_handler import (
    start_registration,
    get_name,
    get_family_name,
    get_age,
    get_email,
    get_field_of_study,
    get_country,
    cancel_registration,
    show_profile,
    start_edit_profile,
    ask_for_new_value,
    update_field,
    cancel_edit,
    NAME,
    FAMILY_NAME,
    AGE,
    EMAIL,
    FIELD_OF_STUDY,
    COUNTRY,
    EDIT_PROFILE,
    EDIT_FIELD,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

def main() -> None:
    """Start the bot."""
    try:
        # Create the user table if it doesn't exist
        logger.info("Creating database tables...")
        create_user_table()
        create_isee_calculations_table()
        logger.info("Generating embeddings...")
        generate_embeddings()

        logger.info("Initializing Telegram bot application...")
        application = Application.builder().token(TELEGRAM_TOKEN).build()

        # Register conversation handlers
        reg_handler = ConversationHandler(
            entry_points=[CommandHandler("register", start_registration)],
            states={
                NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
                FAMILY_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_family_name)],
                AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_age)],
                EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_email)],
                FIELD_OF_STUDY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_field_of_study)],
                COUNTRY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_country)],
            },
            fallbacks=[CommandHandler("cancel", cancel_registration)],
        )
        application.add_handler(reg_handler)

        isee_handler = ConversationHandler(
            entry_points=[CallbackQueryHandler(start_isee_calculation, pattern='^isee_calculator$')],
            states={
                FAMILY_MEMBERS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_family_members)],
                ANNUAL_INCOME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_annual_income)],
                PROPERTY_STATUS: [CallbackQueryHandler(get_property_status)],
                PROPERTY_SIZE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_property_size)],
            },
            fallbacks=[CommandHandler("cancel", cancel_isee_calculation)],
        )
        application.add_handler(isee_handler)

        edit_profile_handler = ConversationHandler(
            entry_points=[CallbackQueryHandler(start_edit_profile, pattern='^edit_profile$')],
            states={
                EDIT_PROFILE: [CallbackQueryHandler(ask_for_new_value)],
                EDIT_FIELD: [MessageHandler(filters.TEXT & ~filters.COMMAND, update_field)],
            },
            fallbacks=[CommandHandler("cancel", cancel_edit)],
        )
        application.add_handler(edit_profile_handler)

        question_handler = ConversationHandler(
            entry_points=[CallbackQueryHandler(start_ask_question, pattern='^ask_question$')],
            states={
                ASK_QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_question)],
            },
            fallbacks=[CommandHandler("cancel", cancel_question)],
        )
        application.add_handler(question_handler)

        # Register other handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CallbackQueryHandler(button, pattern='^lang_'))
        application.add_handler(CallbackQueryHandler(show_profile, pattern='^profile$'))
        application.add_handler(CallbackQueryHandler(guide_menu, pattern='^guide$'))
        application.add_handler(CallbackQueryHandler(guide_category_menu, pattern='^guide_category_'))
        application.add_handler(CallbackQueryHandler(guide_subsection_content, pattern='^guide_subsection_'))
        application.add_handler(CommandHandler("pdf", send_pdf))
        application.add_handler(CommandHandler("video", send_video))
        application.add_handler(CommandHandler("weather", get_weather))
        application.add_handler(MessageHandler(filters.VOICE, transcribe_voice))
        application.add_handler(CommandHandler("calendar", show_calendar))
        application.add_handler(CallbackQueryHandler(calendar_callback, pattern='^calendar-'))
        application.add_handler(CommandHandler("university", send_university_location))

        live_chat_handler = ConversationHandler(
            entry_points=[CommandHandler("livechat", start_live_chat)],
            states={
                LIVE_CHAT: [MessageHandler(filters.TEXT & ~filters.COMMAND, forward_to_admin)],
            },
            fallbacks=[CommandHandler("cancel", cancel_live_chat)],
        )
        application.add_handler(live_chat_handler)

        application.add_handler(MessageHandler(filters.REPLY, forward_to_user))
        application.add_handler(CommandHandler("search", search))

        # Start the Bot
        logger.info("Starting bot with polling...")
        application.run_polling()
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise

if __name__ == "__main__":
    main()
