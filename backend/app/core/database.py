import os
import sqlite3
from typing import Generator
from contextlib import contextmanager
from backend.app.core.config import get_config
from backend.app.logger import get_logger

config = get_config()
logger = get_logger()

# Database File Path
DB_FILE_PATH = os.path.join(config.BASE_DIR, "downloader.db")

def get_db_connection() -> sqlite3.Connection:
    """Creates and returns a configured SQLite database connection."""
    conn = sqlite3.connect(DB_FILE_PATH, check_same_thread=False, timeout=30.0)
    conn.row_factory = sqlite3.Row
    
    # Performance & Data Integrity Pragmas
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    
    return conn

@contextmanager
def get_db() -> Generator[sqlite3.Connection, None, None]:
    """Context manager for thread-safe SQLite database transactions."""
    conn = get_db_connection()
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Database transaction error: {str(e)}")
        raise e
    finally:
        conn.close()

def init_db() -> None:
    """Initializes SQLite database schemas, tables, and indexes."""
    logger.info(f"Initializing SQLite database at: {DB_FILE_PATH}")
    with get_db() as conn:
        # 1. Download Jobs Table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS download_jobs (
                id TEXT PRIMARY KEY,
                url TEXT NOT NULL,
                format_id TEXT NOT NULL,
                media_type TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                progress REAL DEFAULT 0.0,
                speed TEXT DEFAULT '',
                eta TEXT DEFAULT '',
                title TEXT DEFAULT '',
                thumbnail TEXT DEFAULT '',
                file_name TEXT DEFAULT '',
                file_path TEXT DEFAULT '',
                file_size INTEGER DEFAULT 0,
                error_message TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # 2. Download History Table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS download_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT NOT NULL,
                title TEXT NOT NULL,
                url TEXT NOT NULL,
                media_type TEXT NOT NULL,
                file_name TEXT NOT NULL,
                file_size INTEGER DEFAULT 0,
                download_url TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # 3. Application Settings Table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS app_settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # Indexes for Fast Searching & Sorting
        conn.execute("CREATE INDEX IF NOT EXISTS idx_jobs_status ON download_jobs(status, created_at);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_history_created ON download_history(created_at DESC);")
        
    logger.info("SQLite database schema initialized successfully.")

# Run schema initialization on module load
init_db()
