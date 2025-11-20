"""Database writer for storing association records."""

import sqlite3
import json
from typing import List
from pathlib import Path
from ..models import AssociationRecord
from ..utils import setup_logger
from .schema import create_schema

logger = setup_logger(__name__)


class DatabaseWriter:
    """Write association records to SQLite database."""
    
    def __init__(self, db_path: str):
        """
        Initialize database writer.
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        
        # Ensure schema exists
        if not Path(db_path).exists():
            create_schema(db_path)
    
    def write_record(self, record: AssociationRecord) -> None:
        """
        Write a single association record to the database.
        
        Args:
            record: AssociationRecord to write
        """
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            
            # Insert into associations table (or replace if exists)
            cursor.execute("""
                INSERT OR REPLACE INTO associations (
                    association_id, name, association_type, city, county, state, year,
                    source_directory_title, source_collection, raw_section_text,
                    extraction_run_id, metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                record.association_id,
                record.name,
                record.association_type,
                record.city,
                record.county,
                record.state,
                record.year,
                record.source_directory_title,
                record.source_collection,
                record.raw_section_text,
                record.extraction_run_id,
                json.dumps(record.metadata)
            ))
            
            # Insert association pages
            for page_id in record.source_pages:
                cursor.execute("""
                    INSERT OR IGNORE INTO association_pages (association_id, page_id)
                    VALUES (?, ?)
                """, (record.association_id, page_id))
            
            # Insert members
            for member in record.members:
                cursor.execute("""
                    INSERT INTO members (association_id, full_name, role, notes)
                    VALUES (?, ?, ?, ?)
                """, (record.association_id, member.full_name, member.role, member.notes))
            
            conn.commit()
            logger.debug(f"Wrote record {record.association_id} to database")
            
        except Exception as e:
            logger.error(f"Error writing record {record.association_id}: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def write_records(self, records: List[AssociationRecord]) -> None:
        """
        Write multiple association records to the database.
        
        Args:
            records: List of AssociationRecord objects
        """
        logger.info(f"Writing {len(records)} records to database")
        
        for record in records:
            self.write_record(record)
        
        logger.info(f"Successfully wrote {len(records)} records")
