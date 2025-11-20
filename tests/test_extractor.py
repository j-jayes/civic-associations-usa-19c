"""Tests for extractor."""

import pytest
from civic_associations.extraction import LLMClient, Extractor
from civic_associations.models import Section, AssociationRecord


def test_llm_client_init():
    """Test LLMClient initialization."""
    client = LLMClient()
    assert client.model_name == "gemini-2.5-flash"
    assert client.temperature == 0.1


def test_extractor_init():
    """Test Extractor initialization."""
    client = LLMClient()
    extractor = Extractor(client)
    assert extractor.client == client


def test_extract_from_section():
    """Test extraction from a section."""
    client = LLMClient()
    extractor = Extractor(client)
    
    section = Section(
        section_id="test_section",
        page_ids=["test_p001"],
        city="Boston",
        state="MA",
        year=1855,
        start_page_number=1,
        end_page_number=1,
        section_type="associations",
        raw_text="Boston Temperance Society - President: John Smith"
    )
    
    records = extractor.extract_from_section(section, run_id="test_run")
    assert isinstance(records, list)
    assert len(records) > 0
    assert isinstance(records[0], AssociationRecord)
