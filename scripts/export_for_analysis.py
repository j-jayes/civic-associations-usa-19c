#!/usr/bin/env python3
"""Export data for analysis."""

import argparse
import sqlite3
import csv
import json
from pathlib import Path
from civic_associations.utils import setup_logger

logger = setup_logger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description="Export association data for analysis"
    )
    parser.add_argument(
        "--db-path",
        required=True,
        help="Path to SQLite database"
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Directory to save export files"
    )
    parser.add_argument(
        "--format",
        choices=["csv", "jsonl"],
        default="csv",
        help="Output format (default: csv)"
    )
    
    args = parser.parse_args()
    
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Exporting data from: {args.db_path}")
    
    # Connect to database
    conn = sqlite3.connect(args.db_path)
    conn.row_factory = sqlite3.Row
    
    try:
        # Export associations
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM associations")
        associations = cursor.fetchall()
        
        logger.info(f"Exporting {len(associations)} associations")
        
        if args.format == "csv":
            output_file = output_dir / "associations.csv"
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                if associations:
                    writer = csv.DictWriter(f, fieldnames=associations[0].keys())
                    writer.writeheader()
                    for row in associations:
                        writer.writerow(dict(row))
        else:  # jsonl
            output_file = output_dir / "associations.jsonl"
            with open(output_file, 'w', encoding='utf-8') as f:
                for row in associations:
                    f.write(json.dumps(dict(row)) + '\n')
        
        logger.info(f"Exported associations to: {output_file}")
        
        # Export members
        cursor.execute("SELECT * FROM members")
        members = cursor.fetchall()
        
        logger.info(f"Exporting {len(members)} members")
        
        if args.format == "csv":
            output_file = output_dir / "members.csv"
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                if members:
                    writer = csv.DictWriter(f, fieldnames=members[0].keys())
                    writer.writeheader()
                    for row in members:
                        writer.writerow(dict(row))
        else:  # jsonl
            output_file = output_dir / "members.jsonl"
            with open(output_file, 'w', encoding='utf-8') as f:
                for row in members:
                    f.write(json.dumps(dict(row)) + '\n')
        
        logger.info(f"Exported members to: {output_file}")
        
    finally:
        conn.close()
    
    logger.info("Export completed successfully")


if __name__ == "__main__":
    main()
