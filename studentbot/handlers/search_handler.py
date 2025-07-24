import json
import numpy as np
from sentence_transformers import SentenceTransformer
from telegram import Update
from telegram.ext import ContextTypes
import pickle
import gc
from config import logger, get_db_connection
from handlers.cmd_start import get_translation

# بارگذاری مدل یک بار در سطح ماژول
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def load_knowledge_base():
    """Loads the knowledge base from JSON file."""
    try:
        with open('studentbot/knowledge_base_guide.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info("Successfully loaded knowledge_base_guide.json")
        return data
    except FileNotFoundError:
        logger.warning("knowledge_base_guide.json not found")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON format in knowledge_base_guide.json: {e}")
        raise
    except Exception as e:
        logger.error(f"Failed to load knowledge_base_guide.json: {e}")
        raise

def create_embeddings_table():
    """Creates a table for storing embeddings in PostgreSQL."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS embeddings (
                id VARCHAR(255) PRIMARY KEY,
                category_id VARCHAR(255),
                embedding BYTEA
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()
        logger.info("Embeddings table created successfully")
    except Exception as e:
        logger.error(f"Failed to create embeddings table: {e}")
        raise

def save_embeddings(embeddings):
    """Saves embeddings to PostgreSQL database."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM embeddings")  # پاک کردن داده‌های قدیمی
        for item in embeddings:
            cursor.execute(
                "INSERT INTO embeddings (id, category_id, embedding) VALUES (%s, %s, %s)",
                (item['id'], item['category_id'], pickle.dumps(item['embedding']))
            )
        conn.commit()
        cursor.close()
        conn.close()
        logger.info("Embeddings saved to database")
    except Exception as e:
        logger.error(f"Failed to save embeddings to database: {e}")
        raise

def load_embeddings():
    """Loads embeddings from PostgreSQL database."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, category_id, embedding FROM embeddings")
        rows = cursor.fetchall()
        embeddings = [
            {'id': row[0], 'category_id': row[1], 'embedding': pickle.loads(row[2])}
            for row in rows
        ]
        cursor.close()
        conn.close()
        logger.info("Embeddings loaded from database")
        return embeddings if embeddings else None
    except Exception as e:
        logger.error(f"Failed to load embeddings from database: {e}")
        return None

def generate_embeddings():
    """Generates embeddings for the knowledge base using Sentence Transformers."""
    embeddings = load_embeddings()
    if embeddings:
        return embeddings

    try:
        knowledge_base = load_knowledge_base()
        embeddings = []

        def process_subsection(subsection, category_id, parent_id=None):
            subsection_id = subsection.get('id', subsection.get('name', {}).get('en', 'unnamed'))
            if parent_id:
                subsection_id = f"{parent_id}_{subsection_id}"

            if 'subsections' in subsection:
                for sub in subsection['subsections']:
                    process_subsection(sub, category_id, subsection_id)
            else:
                content_key = 'content' if 'content' in subsection else 'details'
                if content_key in subsection:
                    text = ' '.join(subsection[content_key]['en'])
                    embedding = model.encode(text, batch_size=1)
                    embeddings.append({
                        'id': subsection_id,
                        'category_id': category_id,
                        'embedding': embedding
                    })
                    gc.collect()  # آزادسازی حافظه

        for category in knowledge_base['guide']['categories']:
            for subsection in category['subsections']:
                process_subsection(subsection, category['id'])

        save_embeddings(embeddings)
        logger.info("Successfully generated and saved embeddings")
        return embeddings
    except Exception as e:
        logger.error(f"خطا در تولید embeddings: {e}")
        raise

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the search command."""
    lang = context.user_data.get('lang', 'fa')
    query = update.message.text.replace('/search ', '')
    try:
        query_embedding = model.encode(query, batch_size=1)

        embeddings = generate_embeddings()
        similarities = []
        for item in embeddings:
            similarity = np.dot(query_embedding, item['embedding']) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(item['embedding'])
            )
            similarities.append({
                'id': item['id'],
                'category_id': item['category_id'],
                'similarity': similarity
            })

        top_result = max(similarities, key=lambda x: x['similarity'])
        knowledge_base = load_knowledge_base()

        def find_content(subsection, target_id, parent_id=None):
            subsection_id = subsection.get('id', subsection.get('name', {}).get('en', 'unnamed'))
            if parent_id:
                subsection_id = f"{parent_id}_{subsection_id}"

            if subsection_id == target_id:
                content_key = 'content' if 'content' in subsection else 'details'
                if content_key in subsection:
                    return subsection[content_key][lang]
                else:
                    logger.warning(f"هیچ 'content' یا 'details' در زیربخش پیدا نشد: {subsection_id}")
                    return None
            if 'subsections' in subsection:
                for sub in subsection['subsections']:
                    result = find_content(sub, target_id, subsection_id)
                    if result:
                        return result
            return None

        for category in knowledge_base['guide']['categories']:
            if category['id'] == top_result['category_id']:
                for subsection in category['subsections']:
                    content = find_content(subsection, top_result['id'])
                    if content:
                        await update.message.reply_text(
                            get_translation(lang, 'search_result') + '\n' + '\n'.join(content),
                            parse_mode='MarkdownV2'
                        )
                        logger.info(f"نتیجه جستجو برای کاربر با شناسه {update.effective_user.id} ارسال شد")
                        return
        await update.message.reply_text(
            get_translation(lang, 'error_no_guide_data'),
            parse_mode='MarkdownV2'
        )
        logger.info(f"نتیجه جستجویی برای کاربر با شناسه {update.effective_user.id} پیدا نشد")
    except Exception as e:
        logger.error(f"خطا در پردازش جستجو برای کاربر با شناسه {update.effective_user.id}: {e}")
        await update.message.reply_text(
            get_translation(lang, 'voice_error'),  # Reuse error message
            parse_mode='MarkdownV2'
        )
