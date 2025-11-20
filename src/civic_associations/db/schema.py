"""SQLite database schema definition."""

import sqlite3
from pathlib import Path
from ..utils import setup_logger

logger = setup_logger(__name__)


SCHEMA_SQL = """
-- Associations table
CREATE TABLE IF NOT EXISTS associations (
    association_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    association_type TEXT,
    city TEXT,
    county TEXT,
    state TEXT,
    year INTEGER,
    source_directory_title TEXT,
    source_collection TEXT,
    raw_section_text TEXT,
    extraction_run_id TEXT,
    metadata_json TEXT
);

-- Association pages junction table
CREATE TABLE IF NOT EXISTS association_pages (
    association_id TEXT,
    page_id TEXT,
    PRIMARY KEY (association_id, page_id),
    FOREIGN KEY (association_id) REFERENCES associations(association_id)
);

-- Members table
CREATE TABLE IF NOT EXISTS members (
    member_id INTEGER PRIMARY KEY AUTOINCREMENT,
    association_id TEXT,
    full_name TEXT NOT NULL,
    role TEXT,
    notes TEXT,
    FOREIGN KEY (association_id) REFERENCES associations(association_id)
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_associations_city_year ON associations(city, year);
CREATE INDEX IF NOT EXISTS idx_associations_type ON associations(association_type);
CREATE INDEX IF NOT EXISTS idx_members_association ON members(association_id);
CREATE INDEX IF NOT EXISTS idx_members_name ON members(full_name);
"""


def create_schema(db_path: str) -> None:
    """
    Create the database schema.
    
    Args:
        db_path: Path to SQLite database file
    """
    db_file = Path(db_path)
    db_file.parent.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Creating database schema: {db_path}")
    
    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(SCHEMA_SQL)
        conn.commit()
        logger.info("Database schema created successfully")
    finally:
        conn.close()
