"""Hashing utilities for generating stable IDs."""

import hashlib
from typing import List


def make_association_id(
    name: str,
    city: str,
    year: int,
    source_pages: List[str]
) -> str:
    """
    Generate a stable association ID from key fields.
    
    Args:
        name: Association name
        city: City name
        year: Year
        source_pages: List of source page IDs
        
    Returns:
        SHA-256 hash as hex string
    """
    # Normalize inputs
    normalized_name = name.lower().strip()
    normalized_city = city.lower().strip() if city else ""
    sorted_pages = '-'.join(sorted(source_pages))
    
    # Create composite key
    key = f"{normalized_name}|{normalized_city}|{year}|{sorted_pages}"
    
    # Generate hash
    return hashlib.sha256(key.encode('utf-8')).hexdigest()


def make_section_id(page_ids: List[str], start_offset: int = 0) -> str:
    """
    Generate a stable section ID from page IDs and offset.
    
    Args:
        page_ids: List of page IDs in the section
        start_offset: Starting character offset in first page
        
    Returns:
        SHA-256 hash as hex string
    """
    sorted_pages = '-'.join(sorted(page_ids))
    key = f"{sorted_pages}|{start_offset}"
    return hashlib.sha256(key.encode('utf-8')).hexdigest()
