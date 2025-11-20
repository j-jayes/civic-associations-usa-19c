"""Similarity metrics for verification."""

from typing import List
from ..models import AssociationRecord


def compute_similarity(record1: AssociationRecord, record2: AssociationRecord) -> float:
    """
    Compute similarity between two association records.
    
    Args:
        record1: First record
        record2: Second record
        
    Returns:
        Similarity score between 0.0 and 1.0
    """
    # Simple placeholder - would use fuzzy string matching in practice
    name_match = 1.0 if record1.name.lower() == record2.name.lower() else 0.0
    type_match = 1.0 if record1.association_type == record2.association_type else 0.5
    
    # Average similarity
    similarity = (name_match + type_match) / 2.0
    return similarity


def aggregate_records(
    records: List[AssociationRecord],
    min_similarity: float = 0.9
) -> AssociationRecord:
    """
    Aggregate multiple extraction runs into a single record.
    
    Args:
        records: List of records from different runs
        min_similarity: Minimum similarity threshold
        
    Returns:
        Aggregated AssociationRecord
    """
    # Simple placeholder - would implement majority voting in practice
    if not records:
        raise ValueError("No records to aggregate")
    
    # For now, just return the first record
    return records[0]
