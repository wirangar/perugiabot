import json
import numpy as np
from openai import OpenAI
from telegram import Update
from telegram.ext import ContextTypes
from config import logger, OPENAI_API_KEY
from handlers.cmd_start import get_translation

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

def generate_embeddings():
    """Generates embeddings for the knowledge base."""
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        knowledge_base = load_knowledge_base()
        embeddings = []
        for category in knowledge_base['guide']['categories']:
            for subsection in category['subsections']:
                text = ' '.join(subsection['content']['en'])  # Use English content for embeddings
                response = client.embeddings.create(input=text, model="text-embedding-ada-002")
                embeddings.append({
                    'id': subsection['id'],
                    'category_id': category['id'],
                    'embedding': response.data[0].embedding
                })
        logger.info("Successfully generated embeddings")
        return embeddings
    except Exception as e:
        logger.error(f"Failed to generate embeddings: {e}")
        raise

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the search command."""
    lang = context.user_data.get('lang', 'fa')
    query = update.message.text.replace('/search ', '')
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.embeddings.create(input=query, model="text-embedding-ada-002")
        query_embedding = response.data[0].embedding

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
        for category in knowledge_base['guide']['categories']:
            if category['id'] == top_result['category_id']:
                for subsection in category['subsections']:
                    if subsection['id'] == top_result['id']:
                        content = subsection['content'][lang]
                        await update.message.reply_text(
                            get_translation(lang, 'search_result') + '\n' + '\n'.join(content),
                            parse_mode='MarkdownV2'
                        )
                        logger.info(f"Search result sent for user_id: {update.effective_user.id}")
                        return
        await update.message.reply_text(
            get_translation(lang, 'error_no_guide_data'),
            parse_mode='MarkdownV2'
        )
        logger.info(f"No search result found for user_id: {update.effective_user.id}")
    except Exception as e:
        logger.error(f"Failed to process search for user_id {update.effective_user.id}: {e}")
        await update.message.reply_text(
            get_translation(lang, 'voice_error'),  # Reuse error message
            parse_mode='MarkdownV2'
        )
