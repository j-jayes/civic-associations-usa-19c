"""Tests for verification."""

import pytest
from civic_associations.models import AssociationRecord, Member
from civic_associations.verification import compute_similarity, verify_record


def test_verify_record_valid():
    """Test verification of a valid record."""
    record = AssociationRecord(
        association_id="test_id",
        name="Boston Temperance Society",
        city="Boston",
        state="MA",
        year=1855,
        source_pages=["test_p001"],
        raw_section_text="Test text",
        extraction_run_id="test_run"
    )
    
    is_valid, error = verify_record(record)
    assert is_valid
    assert error == ""


def test_verify_record_invalid_name():
    """Test verification with invalid name."""
    record = AssociationRecord(
        association_id="test_id",
        name="",  # Empty name
        city="Boston",
        state="MA",
        year=1855,
        source_pages=["test_p001"],
        raw_section_text="Test text",
        extraction_run_id="test_run"
    )
    
    is_valid, error = verify_record(record)
    assert not is_valid
    assert "name" in error.lower()


def test_verify_record_missing_location():
    """Test verification with missing location."""
    record = AssociationRecord(
        association_id="test_id",
        name="Boston Society",
        city="",  # Missing city
        state="MA",
        year=1855,
        source_pages=["test_p001"],
        raw_section_text="Test text",
        extraction_run_id="test_run"
    )
    
    is_valid, error = verify_record(record)
    assert not is_valid
    assert "location" in error.lower() or "fields" in error.lower()


def test_compute_similarity_exact_match():
    """Test similarity computation with exact match."""
    record1 = AssociationRecord(
        association_id="test_id",
        name="Boston Society",
        association_type="temperance",
        city="Boston",
        state="MA",
        year=1855,
        source_pages=["test_p001"],
        raw_section_text="Test",
        extraction_run_id="run1"
    )
    
    record2 = AssociationRecord(
        association_id="test_id",
        name="Boston Society",
        association_type="temperance",
        city="Boston",
        state="MA",
        year=1855,
        source_pages=["test_p001"],
        raw_section_text="Test",
        extraction_run_id="run2"
    )
    
    similarity = compute_similarity(record1, record2)
    assert similarity == 1.0
