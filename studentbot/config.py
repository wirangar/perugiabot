import logging
import json
from dotenv import load_dotenv
import os

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENWEATHERMAP_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")
REDIS_URL = os.getenv("REDIS_URL")
DATABASE_URL = os.getenv("DATABASE_URL")
GOOGLE_CREDS = os.getenv("GOOGLE_CREDS")
SPREADSHEET_NAME = os.getenv("SPREADSHEET_NAME")
SHEET_ID = os.getenv("SHEET_ID")
QUESTIONS_SHEET_NAME = os.getenv("QUESTIONS_SHEET_NAME")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")
BASE_URL = os.getenv("BASE_URL")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")

# تنظیم logger
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# لود کردن knowledge_base_guide.json
guide_data = {}
try:
    with open('studentbot/knowledge_base_guide.json', 'r', encoding='utf-8') as f:
        guide_data = json.load(f)
    logger.info("Successfully loaded knowledge_base_guide.json")
except FileNotFoundError:
    logger.warning("knowledge_base_guide.json not found, initializing with empty guide_data")
except json.JSONDecodeError as e:
    logger.error(f"Invalid JSON format in knowledge_base_guide.json: {e}")
except Exception as e:
    logger.error(f"Failed to initialize guide_data: {e}")
