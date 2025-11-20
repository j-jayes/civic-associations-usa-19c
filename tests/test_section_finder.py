"""Tests for section finder."""

import pytest
from civic_associations.ocr import SectionFinder
from civic_associations.models import PageOCR, Section


def test_section_finder_init():
    """Test SectionFinder initialization."""
    finder = SectionFinder()
    assert len(finder.keywords) > 0
    assert "associations" in finder.keywords


def test_section_finder_with_custom_keywords():
    """Test SectionFinder with custom keywords."""
    keywords = ["societies", "clubs"]
    finder = SectionFinder(keywords=keywords)
    assert finder.keywords == keywords


def test_find_sections_empty():
    """Test finding sections with empty input."""
    finder = SectionFinder()
    sections = finder.find_sections([], "Boston", "MA", 1855)
    assert len(sections) == 0


def test_find_sections_single_page():
    """Test finding sections with single page."""
    finder = SectionFinder()
    
    ocr_result = PageOCR(
        page_id="test_p001",
        text_md="# Associations\nBoston Society",
        text_plain="Associations\nBoston Society",
        ocr_confidence=0.95,
        blocks=[]
    )
    
    sections = finder.find_sections([ocr_result], "Boston", "MA", 1855)
    assert len(sections) > 0
