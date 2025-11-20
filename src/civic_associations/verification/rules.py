"""Verification rules for checking record quality."""

from typing import Tuple
from ..models import AssociationRecord, VerificationResult


def verify_record(
    record: AssociationRecord,
    min_name_length: int = 3
) -> Tuple[bool, str]:
    """
    Verify that a record meets basic quality standards.
    
    Args:
        record: Record to verify
        min_name_length: Minimum association name length
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check name
    if not record.name or len(record.name) < min_name_length:
        return False, f"Association name too short: {record.name}"
    
    # Check required fields
    if not record.city or not record.state or not record.year:
        return False, "Missing required location/date fields"
    
    if not record.source_pages:
        return False, "No source pages specified"
    
    return True, ""


def create_verification_result(
    association_id: str,
    num_runs: int,
    exact_matches: int,
    similarity: float,
    min_similarity: float = 0.9,
    min_exact_matches: int = 2
) -> VerificationResult:
    """
    Create a verification result based on multi-run consistency.
    
    Args:
        association_id: Association ID
        num_runs: Total number of extraction runs
        exact_matches: Number of runs that exactly matched
        similarity: Average similarity score
        min_similarity: Minimum similarity threshold
        min_exact_matches: Minimum exact matches required
        
    Returns:
        VerificationResult object
    """
    # Determine status
    if exact_matches >= min_exact_matches and similarity >= min_similarity:
        status = "accepted"
    elif similarity >= min_similarity * 0.8:
        status = "needs_review"
    else:
        status = "rejected"
    
    notes = None
    if status == "needs_review":
        notes = f"Low consistency: {exact_matches}/{num_runs} exact matches, {similarity:.2f} similarity"
    elif status == "rejected":
        notes = f"Failed verification: {exact_matches}/{num_runs} exact matches, {similarity:.2f} similarity"
    
    return VerificationResult(
        association_id=association_id,
        num_runs=num_runs,
        exact_match_runs=exact_matches,
        similarity_score=similarity,
        status=status,
        notes=notes
    )
