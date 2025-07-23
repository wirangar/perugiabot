import psycopg2
import redis
from config import logger, DATABASE_URL, REDIS_URL

def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        logger.info("Successfully connected to PostgreSQL database")
        return conn
    except Exception as e:
        logger.error(f"Failed to connect to PostgreSQL database: {e}")
        raise

def create_user_table():
    """Creates the users table in the database if it doesn't exist."""
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                user_id BIGINT UNIQUE NOT NULL,
                name VARCHAR(255),
                family_name VARCHAR(255),
                age INTEGER,
                email VARCHAR(255),
                field_of_study VARCHAR(255),
                country VARCHAR(255),
                language VARCHAR(10),
                points INTEGER DEFAULT 0,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        logger.info("User table created successfully")
    except Exception as e:
        logger.error(f"Failed to create user table: {e}")
        raise
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def create_isee_calculations_table():
    """Creates the isee_calculations table in the database if it doesn't exist."""
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS isee_calculations (
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL,
                family_members INTEGER,
                annual_income FLOAT,
                property_status VARCHAR(255),
                property_size FLOAT,
                isee_value FLOAT,
                scholarship_status VARCHAR(255),
                scholarship_amount FLOAT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            );
        """)
        conn.commit()
        logger.info("ISEE calculations table created successfully")
    except Exception as e:
        logger.error(f"Failed to create ISEE calculations table: {e}")
        raise
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def save_user(user_data):
    """Saves user data to the database."""
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO users (user_id, name, family_name, age, email, field_of_study, country, language)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (user_id) DO UPDATE SET
                name = EXCLUDED.name,
                family_name = EXCLUDED.family_name,
                age = EXCLUDED.age,
                email = EXCLUDED.email,
                field_of_study = EXCLUDED.field_of_study,
                country = EXCLUDED.country,
                language = EXCLUDED.language;
        """, (
            user_data['user_id'],
            user_data['name'],
            user_data['family_name'],
            user_data['age'],
            user_data['email'],
            user_data['field_of_study'],
            user_data['country'],
            user_data['lang']
        ))
        conn.commit()
        logger.info(f"User data saved for user_id: {user_data['user_id']}")
    except Exception as e:
        logger.error(f"Failed to save user data for user_id {user_data['user_id']}: {e}")
        raise
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def save_isee_calculation(user_id, isee_data):
    """Saves an ISEE calculation to the database."""
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO isee_calculations (user_id, family_members, annual_income, property_status, property_size, isee_value, scholarship_status, scholarship_amount)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            user_id,
            isee_data['family_members'],
            isee_data['annual_income'],
            isee_data['property_status'],
            isee_data.get('property_size', 0),
            isee_data['isee_value'],
            isee_data['scholarship_status'],
            isee_data['scholarship_amount']
        ))
        conn.commit()
        logger.info(f"ISEE calculation saved for user_id: {user_id}")
    except Exception as e:
        logger.error(f"Failed to save ISEE calculation for user_id {user_id}: {e}")
        raise
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def get_user(user_id):
    """Retrieves user data from the database."""
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT name, family_name, age, email, field_of_study, country, language, points, created_at FROM users WHERE user_id = %s", (user_id,))
        user = cur.fetchone()
        if user:
            logger.info(f"Retrieved user data for user_id: {user_id}")
            return {
                "name": user[0],
                "family_name": user[1],
                "age": user[2],
                "email": user[3],
                "field_of_study": user[4],
                "country": user[5],
                "language": user[6],
                "points": user[7],
                "created_at": user[8]
            }
        logger.info(f"No user found for user_id: {user_id}")
        return None
    except Exception as e:
        logger.error(f"Failed to retrieve user data for user_id {user_id}: {e}")
        raise
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def add_points(user_id, points):
    """Adds points to a user's score."""
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE users SET points = points + %s WHERE user_id = %s", (points, user_id))
        conn.commit()
        logger.info(f"Added {points} points to user_id: {user_id}")
    except Exception as e:
        logger.error(f"Failed to add points for user_id {user_id}: {e}")
        raise
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def get_redis_connection():
    """Establishes a connection to the Redis server."""
    try:
        r = redis.from_url(REDIS_URL)
        logger.info("Successfully connected to Redis server")
        return r
    except Exception as e:
        logger.error(f"Failed to connect to Redis server: {e}")
        raise
