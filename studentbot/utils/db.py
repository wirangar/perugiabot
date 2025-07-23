import psycopg2
import redis
from config import DATABASE_URL, REDIS_URL

def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    conn = psycopg2.connect(DATABASE_URL)
    return conn

def get_redis_connection():
    """Establishes a connection to the Redis server."""
    r = redis.from_url(REDIS_URL)
    return r
