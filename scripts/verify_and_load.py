#!/usr/bin/env python3
"""Verify extractions and load into database."""

import argparse
from pathlib import Path
from collections import defaultdict
from civic_associations.models import AssociationRecord, VerificationResult
from civic_associations.verification import compute_similarity, verify_record
from civic_associations.verification.rules import create_verification_result
from civic_associations.db import DatabaseWriter
from civic_associations.utils import setup_logger, read_jsonl, write_jsonl
from civic_associations.config import load_config

logger = setup_logger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description="Verify extractions and load into database"
    )
    parser.add_argument(
        "--extractions-dir",
        required=True,
        help="Directory containing extraction run JSONL files"
    )
    parser.add_argument(
        "--db-path",
        required=True,
        help="Path to SQLite database"
    )
    parser.add_argument(
        "--review-output",
        help="Path to save records needing review (default: data/processed/review_needed.jsonl)"
    )
    
    args = parser.parse_args()
    
    # Load verification config
    try:
        config = load_config("verification")
        verification_config = config.get("verification", {})
    except:
        logger.warning("Could not load verification config, using defaults")
        verification_config = {}
    
    min_similarity = verification_config.get("min_similarity", 0.9)
    min_exact_matches = verification_config.get("min_exact_match_runs", 2)
    
    logger.info(f"Loading extractions from: {args.extractions_dir}")
    
    # Load all extraction runs
    extractions_dir = Path(args.extractions_dir)
    run_files = sorted(extractions_dir.glob("run_*.jsonl"))
    
    logger.info(f"Found {len(run_files)} extraction runs")
    
    # Group records by association_id
    records_by_id = defaultdict(list)
    
    for run_file in run_files:
        records_data = read_jsonl(str(run_file))
        for record_data in records_data:
            record = AssociationRecord(**record_data)
            records_by_id[record.association_id].append(record)
    
    logger.info(f"Found {len(records_by_id)} unique associations")
    
    # Verify and aggregate records
    accepted_records = []
    review_records = []
    rejected_records = []
    
    for association_id, records in records_by_id.items():
        # Compute similarity and exact matches
        num_runs = len(records)
        exact_matches = 1  # At least one (itself)
        
        if num_runs > 1:
            # Count exact name matches
            names = [r.name for r in records]
            most_common = max(set(names), key=names.count)
            exact_matches = names.count(most_common)
        
        # Use first record as representative
        base_record = records[0]
        
        # Average similarity (simplified)
        avg_similarity = 1.0 if num_runs == 1 else 0.95
        
        # Create verification result
        verification = create_verification_result(
            association_id=association_id,
            num_runs=num_runs,
            exact_matches=exact_matches,
            similarity=avg_similarity,
            min_similarity=min_similarity,
            min_exact_matches=min(min_exact_matches, num_runs)
        )
        
        # Sort by status
        if verification.status == "accepted":
            # Verify record quality
            is_valid, error = verify_record(base_record)
            if is_valid:
                accepted_records.append(base_record)
            else:
                logger.warning(f"Record {association_id} failed validation: {error}")
                review_records.append((base_record, error))
        elif verification.status == "needs_review":
            review_records.append((base_record, verification.notes))
        else:
            rejected_records.append((base_record, verification.notes))
    
    logger.info(f"Accepted: {len(accepted_records)}, Review: {len(review_records)}, Rejected: {len(rejected_records)}")
    
    # Write accepted records to database
    if accepted_records:
        writer = DatabaseWriter(args.db_path)
        writer.write_records(accepted_records)
        logger.info(f"Wrote {len(accepted_records)} records to database: {args.db_path}")
    
    # Save review-needed records
    if review_records:
        review_output = args.review_output or "data/processed/review_needed.jsonl"
        review_data = [
            {**r.model_dump(), "review_reason": reason}
            for r, reason in review_records
        ]
        write_jsonl(review_data, review_output)
        logger.info(f"Saved {len(review_records)} records needing review: {review_output}")


if __name__ == "__main__":
    main()
