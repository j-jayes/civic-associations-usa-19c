"""Utilities for parsing and generating page IDs."""

import re
from typing import Optional, Tuple


def parse_page_id(page_id: str) -> Tuple[Optional[str], Optional[int]]:
    """
    Parse a page ID to extract collection and page number.
    
    Args:
        page_id: Page ID string (e.g., "boston_1855_p012")
        
    Returns:
        Tuple of (collection, page_number)
    """
    # Pattern: {collection}_p{number}
    match = re.match(r'^(.+)_p(\d+)$', page_id)
    
    if match:
        collection = match.group(1)
        page_number = int(match.group(2))
        return collection, page_number
    
    return None, None


def generate_page_id(collection: str, page_number: int) -> str:
    """
    Generate a page ID from collection and page number.
    
    Args:
        collection: Collection identifier
        page_number: Page number
        
    Returns:
        Page ID string
    """
    return f"{collection}_p{page_number:03d}"
