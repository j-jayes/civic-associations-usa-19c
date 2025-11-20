"""Tests for manifest builder."""

import pytest
from pathlib import Path
from civic_associations.ingestion import ManifestBuilder
from civic_associations.models import Page


def test_manifest_builder_init():
    """Test ManifestBuilder initialization."""
    builder = ManifestBuilder(
        city="Boston",
        state="MA",
        year=1855,
        source_collection="boston_directory_1855"
    )
    
    assert builder.city == "Boston"
    assert builder.state == "MA"
    assert builder.year == 1855
    assert builder.source_collection == "boston_directory_1855"


def test_generate_page_id():
    """Test page ID generation."""
    builder = ManifestBuilder(
        city="Boston",
        state="MA",
        year=1855,
        source_collection="boston_directory_1855"
    )
    
    # Test with page number
    page_id = builder._generate_page_id("page_001", 1)
    assert page_id == "boston_directory_1855_p001"
    
    # Test with existing page ID pattern
    page_id = builder._generate_page_id("boston_1855_p012", 12)
    assert page_id == "boston_1855_p012"
