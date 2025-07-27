import json
import openai
import numpy as np
from telegram import Update
from telegram.ext import CallbackContext

from config import OPENAI_API_KEY

def get_embedding(text, model="text-embedding-ada-002"):
   text = text.replace("\n", " ")
   return openai.Embedding.create(input = [text], model=model)['data'][0]['embedding']

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def load_knowledge_base():
    with open('knowledge_base.json', 'r') as f:
        return json.load(f)

def generate_embeddings():
    with open('knowledge_base_guide.json', 'r', encoding='utf-8') as f:
        guide_data = json.load(f)

    knowledge_base = []
    for category in guide_data['guide']['categories']:
        for subsection in category.get('subsections', []):
            text = subsection['title']['en'] + "\n" + "\n".join(subsection.get('content', {}).get('en', []))
            knowledge_base.append({
                "text": text,
                "embedding": get_embedding(text)
            })

    with open('knowledge_base.json', 'w') as f:
        json.dump(knowledge_base, f)

async def search(update: Update, context: CallbackContext) -> None:
    """Performs a semantic search on the knowledge base."""
    if not OPENAI_API_KEY:
        await update.message.reply_text("Search service is not configured.")
        return

    query = update.message.text
    query_embedding = get_embedding(query)

    knowledge_base = load_knowledge_base()

    similarities = [cosine_similarity(query_embedding, item['embedding']) for item in knowledge_base]

    most_similar_index = np.argmax(similarities)

    await update.message.reply_text(knowledge_base[most_similar_index]['text'])
